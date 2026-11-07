"""Neural Analysis Agent - learned pattern recognition with confidence scores.

Produces a probability distribution over the domain's outcome classes and a
local, perturbation-based feature attribution (occlusion against the training
baseline) so the neural evidence itself is traceable.
"""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from app.core.domain_manager import domain_manager
from app.domains.base import DomainDefinition
from app.schemas import FeatureAttribution, NeuralPrediction


class NeuralAgent:
    name = "Neural Analysis Agent"
    role = "Learns patterns from data and predicts the outcome with a confidence score."

    def predict_proba_batch(self, domain: DomainDefinition, rows: pd.DataFrame) -> list[list[float]]:
        bundle = domain_manager.get_model(domain.id)
        cols = domain.numeric_features + domain.categorical_features
        return bundle.pipeline.predict_proba(rows[cols]).tolist()

    def run(self, domain: DomainDefinition, inputs: Mapping[str, float | str], top_k: int = 6) -> NeuralPrediction:
        bundle = domain_manager.get_model(domain.id)
        stats = bundle.metadata["stats"]
        cols = domain.numeric_features + domain.categorical_features

        base_row = {c: inputs[c] for c in cols}
        rows = [base_row]
        for c in cols:  # occlusion: replace one feature with its training baseline
            perturbed = dict(base_row)
            perturbed[c] = stats["mean"][c] if c in stats["mean"] else stats["mode"][c]
            rows.append(perturbed)
        probs = bundle.pipeline.predict_proba(pd.DataFrame(rows)[cols])
        model_classes = [int(c) for c in bundle.pipeline.classes_]
        full = [0.0] * len(domain.classes)
        for idx, cls in enumerate(model_classes):
            full[cls] = float(probs[0][idx])
        level = max(range(len(full)), key=lambda i: full[i])
        col_idx = model_classes.index(level)

        attributions: list[FeatureAttribution] = []
        for i, c in enumerate(cols, start=1):
            contribution = float(probs[0][col_idx] - probs[i][col_idx])
            attributions.append(FeatureAttribution(
                feature=c, label=domain.feature_labels[c], value=inputs[c], contribution=round(contribution, 4),
            ))
        attributions.sort(key=lambda a: abs(a.contribution), reverse=True)

        cls = domain.class_by_level(level)
        return NeuralPrediction(
            result=cls.key,
            label=cls.label,
            level=level,
            confidence=round(full[level], 4),
            probabilities={domain.class_by_level(i).label: round(p, 4) for i, p in enumerate(full)},
            model=bundle.metadata["architecture"],
            attributions=attributions[:top_k],
        )
