"""Domain Configuration Manager.

Discovers domain plug-ins under ``app/domains``, and loads (or trains on demand)
each domain's neural model.  This is the only component that knows where
datasets and model artefacts live.
"""

from __future__ import annotations

import importlib
import json
import pkgutil
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import app.domains as domains_pkg
from app.config import DATASET_DIR, DATASET_SIZE, RANDOM_SEED
from app.domains.base import DomainDefinition

HIDDEN_LAYERS = (64, 32)


@dataclass
class ModelBundle:
    pipeline: Pipeline
    metadata: dict[str, Any]


class DomainManager:
    def __init__(self) -> None:
        self._domains: dict[str, DomainDefinition] = {}
        self._models: dict[str, ModelBundle] = {}
        self._lock = threading.Lock()
        self._discover()

    # ------------------------------------------------------------------ domains
    def _discover(self) -> None:
        for info in pkgutil.iter_modules(domains_pkg.__path__):
            if not info.ispkg:
                continue
            module = importlib.import_module(f"app.domains.{info.name}.config")
            domain: DomainDefinition = module.DOMAIN
            self._domains[domain.id] = domain

    def list(self) -> list[DomainDefinition]:
        order = ["healthcare", "finance", "fraud_detection", "it_troubleshooting", "education"]
        return sorted(self._domains.values(), key=lambda d: order.index(d.id) if d.id in order else 99)

    def get(self, domain_id: str) -> DomainDefinition:
        if domain_id not in self._domains:
            raise KeyError(domain_id)
        return self._domains[domain_id]

    # ------------------------------------------------------------------- models
    @staticmethod
    def model_dir(domain_id: str) -> Path:
        return Path(domains_pkg.__file__).parent / domain_id / "model"

    def model_ready(self, domain_id: str) -> bool:
        return domain_id in self._models or (self.model_dir(domain_id) / "model.joblib").exists()

    def metadata(self, domain_id: str) -> dict[str, Any] | None:
        path = self.model_dir(domain_id) / "metadata.json"
        if domain_id in self._models:
            return self._models[domain_id].metadata
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return None

    def get_model(self, domain_id: str) -> ModelBundle:
        if domain_id in self._models:
            return self._models[domain_id]
        with self._lock:
            if domain_id in self._models:
                return self._models[domain_id]
            path = self.model_dir(domain_id)
            try:
                # joblib only ever loads artefacts this app trained and wrote itself
                # (app/domains/<id>/model, git-ignored); never load third-party files here.
                bundle = ModelBundle(
                    pipeline=joblib.load(path / "model.joblib"),
                    metadata=json.loads((path / "metadata.json").read_text(encoding="utf-8")),
                )
            except Exception:  # missing or incompatible artefact -> retrain
                bundle = self._train(self.get(domain_id))
            self._models[domain_id] = bundle
            return bundle

    def train(self, domain_id: str) -> ModelBundle:
        with self._lock:
            bundle = self._train(self.get(domain_id))
            self._models[domain_id] = bundle
            return bundle

    # ------------------------------------------------------------------ dataset
    def dataset(self, domain: DomainDefinition) -> tuple[pd.DataFrame, pd.DataFrame]:
        train_path = DATASET_DIR / f"{domain.id}_train.csv"
        test_path = DATASET_DIR / f"{domain.id}_test.csv"
        if train_path.exists() and test_path.exists():
            return pd.read_csv(train_path), pd.read_csv(test_path)
        rng = np.random.default_rng(RANDOM_SEED + sum(map(ord, domain.id)))
        df = domain.generate(DATASET_SIZE, rng)
        train, test = train_test_split(df, test_size=0.25, stratify=df["label"], random_state=RANDOM_SEED)
        DATASET_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(DATASET_DIR / f"{domain.id}.csv", index=False)
        train.to_csv(train_path, index=False)
        test.to_csv(test_path, index=False)
        return train.reset_index(drop=True), test.reset_index(drop=True)

    def _train(self, domain: DomainDefinition) -> ModelBundle:
        train, test = self.dataset(domain)
        cols = domain.numeric_features + domain.categorical_features
        pre = ColumnTransformer([
            ("num", StandardScaler(), domain.numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), domain.categorical_features),
        ])
        mlp = MLPClassifier(
            hidden_layer_sizes=HIDDEN_LAYERS, activation="relu", solver="adam", alpha=1e-3,
            learning_rate_init=1e-3, max_iter=600, early_stopping=True, validation_fraction=0.15,
            n_iter_no_change=25, random_state=RANDOM_SEED,
        )
        pipe = Pipeline([("preprocess", pre), ("mlp", mlp)])
        pipe.fit(train[cols], train["label"])
        pred = pipe.predict(test[cols])
        stats: dict[str, Any] = {"mean": {}, "std": {}, "median": {}, "mode": {}}
        for f in domain.numeric_features:
            stats["mean"][f] = float(train[f].mean())
            stats["std"][f] = float(train[f].std() or 1.0)
            stats["median"][f] = float(train[f].median())
        for f in domain.categorical_features:
            stats["mode"][f] = str(train[f].mode().iloc[0])
        metadata: dict[str, Any] = {
            "domain": domain.id,
            "model": "MLPClassifier (feed-forward neural network)",
            "architecture": f"Input({len(cols)} features) → Dense{HIDDEN_LAYERS[0]}-ReLU → Dense{HIDDEN_LAYERS[1]}-ReLU → Softmax({len(domain.classes)})",
            "hidden_layers": list(HIDDEN_LAYERS),
            "epochs": int(mlp.n_iter_),
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "train_samples": int(len(train)),
            "test_samples": int(len(test)),
            "features": cols,
            "class_distribution": {domain.class_by_level(int(k)).label: int(v) for k, v in train["label"].value_counts().sort_index().items()},
            "test_accuracy": round(float(accuracy_score(test["label"], pred)), 4),
            "test_f1_macro": round(float(f1_score(test["label"], pred, average="macro")), 4),
            "loss_curve": [round(float(x), 4) for x in mlp.loss_curve_][::max(1, len(mlp.loss_curve_) // 60)],
            "stats": stats,
        }
        out = self.model_dir(domain.id)
        out.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipe, out / "model.joblib")
        (out / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        return ModelBundle(pipeline=pipe, metadata=metadata)


domain_manager = DomainManager()
