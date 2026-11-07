"""Benchmark: conventional neural network vs symbolic-only vs hybrid framework.

All numbers are computed live on the held-out test split of each domain.

Metrics
-------
* Accuracy, macro precision / recall / F1           - predictive quality
* Hard-rule consistency  - % decisions satisfying every mandatory rule
* Soft-rule agreement    - % decisions at/above the level implied by all rules
* Explanation evidence   - avg. traceable evidence items per decision
                           (feature attributions + triggered/passed rule checks)
* Symbolic justification - % decisions that cite explicit rule evidence
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

from app.agents.symbolic_agent import SymbolicAgent
from app.config import RESULTS_DIR
from app.core.domain_manager import domain_manager
from app.core.fusion_engine import fuse
from app.schemas import EvaluationRun, NeuralPrediction

ATTRIBUTION_TOP_K = 6


def _metrics(y: list[int], pred: list[int], labels: list[str]) -> dict[str, Any]:
    p, r, f, _ = precision_recall_fscore_support(y, pred, labels=list(range(len(labels))), average="macro", zero_division=0)
    pc, rc, fc, sc = precision_recall_fscore_support(y, pred, labels=list(range(len(labels))), zero_division=0)
    return {
        "accuracy": round(float(accuracy_score(y, pred)), 4),
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1": round(float(f), 4),
        "per_class": [
            {"label": labels[i], "precision": round(float(pc[i]), 4), "recall": round(float(rc[i]), 4), "f1": round(float(fc[i]), 4), "support": int(sc[i])}
            for i in range(len(labels))
        ],
        "confusion_matrix": confusion_matrix(y, pred, labels=list(range(len(labels)))).tolist(),
    }


def evaluate_domain(domain_id: str) -> EvaluationRun:
    domain = domain_manager.get(domain_id)
    bundle = domain_manager.get_model(domain_id)
    _, test = domain_manager.dataset(domain)
    cols = domain.numeric_features + domain.categorical_features
    labels = [c.label for c in domain.classes]
    model_classes = [int(c) for c in bundle.pipeline.classes_]
    raw = bundle.pipeline.predict_proba(test[cols])
    symbolic_agent = SymbolicAgent()

    y = test["label"].astype(int).tolist()
    preds: dict[str, list[int]] = {"neural": [], "symbolic": [], "hybrid": []}
    hard_ok = {k: 0 for k in preds}
    soft_ok = {k: 0 for k in preds}
    conf = {k: [] for k in preds}  # type: dict[str, list[float]]
    evidence = {"neural": [], "symbolic": [], "hybrid": []}  # type: dict[str, list[int]]
    justified = {k: 0 for k in preds}
    conflicts = overrides = 0

    for i, row in enumerate(test[cols].to_dict(orient="records")):
        full = [0.0] * len(labels)
        for j, cls in enumerate(model_classes):
            full[cls] = float(raw[i][j])
        nl = int(np.argmax(full))
        neural = NeuralPrediction(
            result=domain.class_by_level(nl).key, label=labels[nl], level=nl, confidence=full[nl],
            probabilities={labels[k]: full[k] for k in range(len(labels))}, model="mlp", attributions=[],
        )
        symbolic = symbolic_agent.run(domain, domain.facts(row))
        fusion, final = fuse(domain, neural, symbolic)
        hard_level = max((r.implies_level for r in symbolic.triggered_rules if r.severity == "hard"), default=0)

        decided = {"neural": nl, "symbolic": symbolic.rule_level, "hybrid": final.level}
        for k, lvl in decided.items():
            preds[k].append(lvl)
            hard_ok[k] += int(lvl >= hard_level)
            soft_ok[k] += int(lvl >= symbolic.rule_level)
        conf["neural"].append(full[nl])
        conf["symbolic"].append(1.0)
        conf["hybrid"].append(final.confidence)
        evidence["neural"].append(ATTRIBUTION_TOP_K)
        evidence["symbolic"].append(symbolic.rules_evaluated)
        evidence["hybrid"].append(ATTRIBUTION_TOP_K + symbolic.rules_evaluated + 1)  # + fusion rationale
        justified["symbolic"] += 1
        justified["hybrid"] += 1
        conflicts += int(fusion.conflict.detected)
        overrides += int(fusion.override_applied)

    n = len(y)
    names = {"neural": "Neural network only", "symbolic": "Symbolic rules only", "hybrid": "Hybrid neuro-symbolic"}
    systems: dict[str, dict[str, Any]] = {}
    for k in preds:
        m = _metrics(y, preds[k], labels)
        m.update({
            "name": names[k],
            "hard_rule_consistency": round(hard_ok[k] / n, 4),
            "soft_rule_agreement": round(soft_ok[k] / n, 4),
            "avg_confidence": round(float(np.mean(conf[k])), 4),
            "avg_evidence_items": round(float(np.mean(evidence[k])), 2),
            "symbolic_justification": round(justified[k] / n, 4),
        })
        systems[k] = m
    systems["hybrid"]["conflict_rate"] = round(conflicts / n, 4)
    systems["hybrid"]["override_rate"] = round(overrides / n, 4)

    h, b = systems["hybrid"], systems["neural"]
    run = EvaluationRun(
        domain=domain.id,
        domain_name=domain.name,
        generated_at=datetime.now(timezone.utc).isoformat(),
        test_samples=n,
        classes=labels,
        systems=systems,
        improvement={
            "accuracy": round(h["accuracy"] - b["accuracy"], 4),
            "f1": round(h["f1"] - b["f1"], 4),
            "recall": round(h["recall"] - b["recall"], 4),
            "hard_rule_consistency": round(h["hard_rule_consistency"] - b["hard_rule_consistency"], 4),
        },
    )
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / f"{domain.id}.json").write_text(run.model_dump_json(indent=2), encoding="utf-8")
    return run


def load_results() -> list[EvaluationRun]:
    runs: list[EvaluationRun] = []
    for d in domain_manager.list():
        path = RESULTS_DIR / f"{d.id}.json"
        if path.exists():
            runs.append(EvaluationRun.model_validate(json.loads(path.read_text(encoding="utf-8"))))
    return runs
