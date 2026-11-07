"""Domain plug-in contract.

A domain is *configuration*, not code inside the agents: an input schema, the
outcome classes, a knowledge base of IF-THEN rules, derived facts, a dataset
generator and scenario presets.  The common agents never import a domain
directly - they receive a :class:`DomainDefinition` from the Domain Manager.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from app.core.rule_engine import rule_implied_level
from app.schemas import ConditionSpec, FeatureSpec, OutcomeClass, RuleSpec, ScenarioPreset

DeriveFn = Callable[[Mapping[str, float | str]], dict[str, float]]
GenerateFn = Callable[[int, np.random.Generator], pd.DataFrame]


@dataclass
class DomainDefinition:
    id: str
    name: str
    title: str
    tagline: str
    description: str
    icon: str
    task_type: str
    features: list[FeatureSpec]
    classes: list[OutcomeClass]
    rules: list[RuleSpec]
    derive: DeriveFn
    derived_features: dict[str, str]
    generate: GenerateFn
    presets: list[ScenarioPreset]
    level_recommendations: dict[int, list[str]]
    disclaimer: str
    subject: str = "case"
    feature_labels: dict[str, str] = field(init=False)

    def __post_init__(self) -> None:
        self.feature_labels = {f.name: f.label for f in self.features}
        self.feature_labels.update(_pretty_derived(self.derived_features))

    @property
    def numeric_features(self) -> list[str]:
        return [f.name for f in self.features if f.kind == "number"]

    @property
    def categorical_features(self) -> list[str]:
        return [f.name for f in self.features if f.kind == "select"]

    def class_by_level(self, level: int) -> OutcomeClass:
        return self.classes[max(0, min(level, len(self.classes) - 1))]

    def facts(self, inputs: Mapping[str, float | str]) -> dict[str, float | str]:
        facts: dict[str, float | str] = dict(inputs)
        facts.update(self.derive(inputs))
        return facts


def cond(feature: str, op: str, value: float | str | list[str]) -> ConditionSpec:
    return ConditionSpec(feature=feature, op=op, value=value)  # type: ignore[arg-type]


def rule(
    id: str,
    name: str,
    description: str,
    category: str,
    conditions: list[ConditionSpec],
    implies_level: int,
    severity: str,
    recommendation: str,
    pass_message: str = "",
    logic: str = "all",
) -> RuleSpec:
    return RuleSpec(
        id=id,
        name=name,
        description=description,
        category=category,
        conditions=conditions,
        logic=logic,  # type: ignore[arg-type]
        implies_level=implies_level,
        severity=severity,  # type: ignore[arg-type]
        recommendation=recommendation,
        pass_message=pass_message or f"{name}: requirement satisfied.",
    )


def _pretty_derived(derived: dict[str, str]) -> dict[str, str]:
    """Derived-feature descriptions look like 'Debt-to-income ratio: ...'; use the prefix as label."""
    out: dict[str, str] = {}
    for key, desc in derived.items():
        out[key] = desc.split(":")[0].strip() if ":" in desc else key.replace("_", " ").title()
    return out


def finalize_labels(
    df: pd.DataFrame,
    latent: np.ndarray,
    thresholds: tuple[float, float],
    domain_rules: list[RuleSpec],
    derive: DeriveFn,
    rng: np.random.Generator,
    label_noise: float = 0.03,
) -> pd.DataFrame:
    """Turn a latent risk score into ground-truth levels.

    1. Threshold the latent score into three ordinal levels.
    2. Domain policy: hard rules define a minimum outcome (e.g. a hypertensive
       crisis is always high risk).  This is the expert knowledge the neural
       model has to *learn* from data but the symbolic agent *knows*.
    3. Inject a little label noise to mimic real-world annotation error.
    """
    levels = np.digitize(latent, thresholds).astype(int)
    hard = [r for r in domain_rules if r.severity == "hard"]
    records = df.to_dict(orient="records")
    for i, row in enumerate(records):
        facts: dict[str, float | str] = dict(row)
        facts.update(derive(row))
        levels[i] = max(levels[i], rule_implied_level(hard, facts))
    flip = rng.random(len(levels)) < label_noise
    shift = rng.choice([-1, 1], size=len(levels))
    levels = np.where(flip, np.clip(levels + shift, 0, 2), levels)
    out = df.copy()
    out["label"] = levels
    return out
