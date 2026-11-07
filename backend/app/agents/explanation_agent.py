"""Explanation Agent - turns the evidence of every agent into human-readable text.

The explanation is assembled only from traceable evidence: the neural
attributions, the triggered/passed rules, the fusion policy and validation
checks.  Nothing is invented, so every sentence can be traced back.
"""

from __future__ import annotations

from collections.abc import Mapping

from app.domains.base import DomainDefinition
from app.schemas import (
    Explanation,
    FinalDecision,
    FusionResult,
    NeuralPrediction,
    SymbolicReasoning,
    ValidationReport,
)


def _fmt(value: float | str) -> str:
    if isinstance(value, str):
        return value
    return f"{value:,.0f}" if abs(value) >= 100 else f"{value:g}"


class ExplanationAgent:
    name = "Explanation Agent"
    role = "Explains how the system reached its conclusion."

    def run(
        self,
        domain: DomainDefinition,
        facts: Mapping[str, float | str],
        neural: NeuralPrediction,
        symbolic: SymbolicReasoning,
        fusion: FusionResult,
        final: FinalDecision,
        validation: ValidationReport,
    ) -> tuple[Explanation, list[str]]:
        units = {f.name: f.unit for f in domain.features}
        up = [a for a in neural.attributions if a.contribution > 0.005][:3]
        down = [a for a in neural.attributions if a.contribution < -0.005][:2]

        def feat(a_feature: str, a_label: str, value: float | str) -> str:
            unit = units.get(a_feature, "")
            if unit == "₹":
                return f"{a_label} (₹{_fmt(value)})"
            if unit in ("%", "/100"):
                return f"{a_label} ({_fmt(value)}{unit})"
            return f"{a_label} ({_fmt(value)}{' ' + unit if unit and unit != '0-23' else ''})"

        neural_txt = (
            f"The neural network predicted **{neural.label}** with "
            f"{neural.confidence:.0%} confidence."
        )
        if up:
            neural_txt += " Strongest drivers towards this outcome: " + ", ".join(feat(a.feature, a.label, a.value) for a in up) + "."
        if down:
            neural_txt += " Factors pulling the other way: " + ", ".join(feat(a.feature, a.label, a.value) for a in down) + "."

        trig = symbolic.triggered_rules
        if trig:
            symbolic_txt = (
                f"The rule engine evaluated {symbolic.rules_evaluated} knowledge-base rules; {len(trig)} triggered: "
                + "; ".join(f"{r.id} {r.name}" + (" (mandatory)" if r.severity == "hard" else "") for r in trig)
                + f". Together they imply at least **{symbolic.rule_label}**."
            )
        else:
            symbolic_txt = f"All {symbolic.rules_evaluated} knowledge-base rules passed - no predefined risk condition was found."

        fusion_txt = (
            f"The coordinator combined both channels using {fusion.strategy.lower()} "
            f"(neural weight {fusion.neural_weight:.2f}, symbolic weight {fusion.symbolic_weight:.2f}). "
        )
        if fusion.conflict.detected:
            fusion_txt += f"Conflict: {fusion.conflict.description} {fusion.conflict.resolution}"
        else:
            fusion_txt += "Both channels agree, which increases trust in the result."

        if final.level == 0 and not trig:
            summary = f"The model predicted {neural.label.lower()} and the configured rules were satisfied."
        elif fusion.override_applied:
            summary = (
                f"A mandatory rule ({', '.join(fusion.override_rule_ids)}) required the outcome to be at least "
                f"{final.label}, overriding the neural estimate of {neural.label}."
            )
        elif trig and final.level < symbolic.rule_level:
            # neural evidence outweighed advisory (soft) rules - say so honestly
            summary = (
                f"The neural model predicted {neural.label} with {neural.confidence:.0%} confidence. "
                f"{len(trig)} advisory rule(s) pointed to {symbolic.rule_label}, but advisory rules are not mandatory, "
                f"so the fused decision stays {final.label} and the warning is recorded for review."
            )
        elif trig and final.level > neural.level:
            summary = (
                f"The neural model estimated {neural.label}, but {len(trig)} rule(s) from the knowledge base "
                f"raised the assessment to {final.label}."
            )
        elif trig:
            summary = (
                f"The model identified a {neural.label.lower()} pattern, and the rule engine found "
                f"{len(trig)} predefined condition(s) consistent with this assessment."
            )
        elif final.level == 0:
            summary = f"The model predicted {neural.label.lower()} and all configured rules were satisfied."
        else:
            summary = f"The neural model detected a {neural.label.lower()} pattern not covered by explicit rules."

        key_factors = [r.message for r in trig[:5]] + [
            f"{feat(a.feature, a.label, a.value)} increased the likelihood of '{neural.label}'" for a in up
        ]

        counterfactuals: list[str] = []
        for r in trig[:4]:
            rule = next(x for x in domain.rules if x.id == r.id)
            cond = rule.conditions[0]
            name = domain.feature_labels.get(cond.feature, cond.feature)
            if cond.op in ("gt", "gte"):
                counterfactuals.append(f"If {name} were below {_fmt(cond.value)} (now {_fmt(facts[cond.feature])}), rule {r.id} would not trigger.")  # type: ignore[arg-type]
            elif cond.op in ("lt", "lte"):
                counterfactuals.append(f"If {name} were at least {_fmt(cond.value)} (now {_fmt(facts[cond.feature])}), rule {r.id} would not trigger.")  # type: ignore[arg-type]
            else:
                counterfactuals.append(f"If {name} were not '{facts[cond.feature]}', rule {r.id} would not trigger.")

        recommendations: list[str] = []
        for r in trig:
            if r.recommendation not in recommendations:
                recommendations.append(r.recommendation)
        for rec in domain.level_recommendations.get(final.level, []):
            if rec not in recommendations:
                recommendations.append(rec)
        if validation.requires_human_review:
            recommendations.append("Validation agent flagged this case for human expert review before acting.")

        headline = f"{final.label} - {domain.title}"
        return (
            Explanation(
                headline=headline,
                summary=summary,
                neural=neural_txt,
                symbolic=symbolic_txt,
                fusion=fusion_txt,
                key_factors=key_factors,
                counterfactuals=counterfactuals,
                disclaimer=domain.disclaimer,
            ),
            recommendations,
        )
