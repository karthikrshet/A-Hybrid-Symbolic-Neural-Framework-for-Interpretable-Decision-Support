"""Decision fusion: confidence-weighted combination + hard-rule override.

    fused = w_n · P_neural + w_s · P_symbolic

The symbolic weight grows when the neural model is unsure.  Afterwards every
*hard* rule acts as a constraint: the final outcome can never be less severe
than a mandatory rule requires (rule override).  Disagreements between the two
reasoning channels are detected and their resolution is recorded.
"""

from __future__ import annotations

from app.domains.base import DomainDefinition
from app.schemas import ConflictInfo, FinalDecision, FusionResult, NeuralPrediction, SymbolicReasoning

OVERRIDE_CONFIDENCE = 0.90


# Weights were selected by grid search on the *training* split (see README);
# the test split is used only for the reported benchmark.
def symbolic_weight(neural_confidence: float) -> float:
    if neural_confidence >= 0.85:
        return 0.10
    if neural_confidence >= 0.60:
        return 0.25
    return 0.40


def fuse(
    domain: DomainDefinition,
    neural: NeuralPrediction,
    symbolic: SymbolicReasoning,
    neural_only: bool = False,
) -> tuple[FusionResult, FinalDecision]:
    labels = [c.label for c in domain.classes]
    p_n = [neural.probabilities[label] for label in labels]
    p_s = [symbolic.distribution[label] for label in labels]

    w_s = 0.0 if neural_only else symbolic_weight(neural.confidence)
    w_n = 1.0 - w_s
    fused = [w_n * a + w_s * b for a, b in zip(p_n, p_s)]
    level = max(range(len(fused)), key=lambda i: fused[i])
    confidence = fused[level]

    hard = [r for r in symbolic.triggered_rules if r.severity == "hard"]
    hard_level = max((r.implies_level for r in hard), default=0)
    override_ids: list[str] = []
    if not neural_only and level < hard_level:
        override_ids = [r.id for r in hard if r.implies_level == hard_level]
        level = hard_level
        confidence = max(fused[level], OVERRIDE_CONFIDENCE)

    # ---- conflict analysis between neural and symbolic channels
    nl, rl = neural.level, symbolic.rule_level
    if nl < rl:
        conflict = ConflictInfo(
            detected=True,
            type="NEURAL_UNDERESTIMATES",
            description=f"Neural model predicted '{neural.label}' but triggered rules require at least '{symbolic.rule_label}'.",
            resolution=(
                f"Rule override applied ({', '.join(override_ids)}): mandatory rules take precedence."
                if override_ids else
                "Resolved by confidence-weighted fusion - symbolic evidence raised the severity."
                if level > nl else
                "Neural evidence was strong; soft-rule warning recorded for the reviewer."
            ),
        )
    elif nl > rl and (nl - rl) >= 1 and not symbolic.triggered_rules:
        conflict = ConflictInfo(
            detected=True,
            type="NEURAL_OVERESTIMATES",
            description=f"Neural model detected a '{neural.label}' pattern that no explicit rule captures.",
            resolution="Kept the learned pattern via weighted fusion; flagged so an expert can confirm or extend the knowledge base.",
        )
    else:
        conflict = ConflictInfo(detected=False, type="NONE", description="Neural prediction and symbolic reasoning are consistent.", resolution="No resolution needed.")

    strategy = "Neural only (baseline)" if neural_only else (
        "Hard-rule override" if override_ids else "Confidence-weighted fusion"
    )
    total = sum(fused) or 1.0
    result = FusionResult(
        strategy=strategy,
        neural_weight=round(w_n, 2),
        symbolic_weight=round(w_s, 2),
        fused_probabilities={label: round(p / total, 4) for label, p in zip(labels, fused)},
        override_applied=bool(override_ids),
        override_rule_ids=override_ids,
        conflict=conflict,
    )
    cls = domain.class_by_level(level)
    final = FinalDecision(result=cls.key, label=cls.label, level=level, confidence=round(confidence, 4), tone=cls.tone)
    return result, final
