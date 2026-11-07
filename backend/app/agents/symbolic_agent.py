"""Symbolic Reasoning Agent - applies the domain knowledge base (IF-THEN rules)."""

from __future__ import annotations

from collections.abc import Mapping

from app.core.rule_engine import condition_text, evaluate_rule
from app.domains.base import DomainDefinition
from app.schemas import RuleEvaluation, SymbolicReasoning


NO_RULE_PRIOR = [0.55, 0.30, 0.15]
SOFT_STRENGTH = 1.0  # how strongly soft rules shift belief (hard rules are always 1.0)


class SymbolicAgent:
    name = "Symbolic Reasoning Agent"
    role = "Applies domain rules and constraints from the knowledge base."

    def run(self, domain: DomainDefinition, facts: Mapping[str, float | str]) -> SymbolicReasoning:
        triggered: list[RuleEvaluation] = []
        passed: list[RuleEvaluation] = []
        for rule in domain.rules:
            fired, observed = evaluate_rule(rule, facts)
            ev = RuleEvaluation(
                id=rule.id,
                name=rule.name,
                description=rule.description,
                category=rule.category,
                status="TRIGGERED" if fired else "PASSED",
                severity=rule.severity,
                implies_level=rule.implies_level,
                implies_label=domain.class_by_level(rule.implies_level).label,
                condition_text=condition_text(rule, domain.feature_labels),
                observed=observed,
                recommendation=rule.recommendation,
                message=rule.description if fired else rule.pass_message,
            )
            (triggered if fired else passed).append(ev)

        triggered.sort(key=lambda r: (r.severity != "hard", -r.implies_level))
        rule_level = max((r.implies_level for r in triggered), default=0)
        hard = [r for r in triggered if r.severity == "hard"]
        status = "VIOLATIONS" if hard else ("WARNINGS" if triggered else "PASSED")
        return SymbolicReasoning(
            status=status,
            rule_level=rule_level,
            rule_label=domain.class_by_level(rule_level).label,
            rules_evaluated=len(domain.rules),
            triggered_rules=triggered,
            passed_rules=passed,
            violations=[f"{r.id}: {r.name}" for r in hard],
            distribution=self.distribution(domain, triggered),
        )

    @staticmethod
    def distribution(domain: DomainDefinition, triggered: list[RuleEvaluation]) -> dict[str, float]:
        """Symbolic belief over outcome classes ("at least level L" semantics)."""
        k = len(domain.classes)
        level = max((r.implies_level for r in triggered), default=0)
        prior = NO_RULE_PRIOR[:k]
        if not triggered:
            probs = list(prior)
        else:
            probs = [0.0] * k
            above = k - 1 - level
            probs[level] = 1.0 if above == 0 else 0.75
            for j in range(level + 1, k):
                probs[j] = 0.25 / above
            # several independent soft warnings raise the belief in the next level up
            soft_hits = sum(1 for r in triggered if r.severity == "soft")
            if level < k - 1 and soft_hits >= 3:
                probs[level], probs[level + 1] = 0.45, probs[level + 1] + 0.30
            if not any(r.severity == "hard" for r in triggered):
                probs = [SOFT_STRENGTH * a + (1 - SOFT_STRENGTH) * b for a, b in zip(probs, prior)]
        total = sum(probs)
        return {domain.class_by_level(i).label: round(p / total, 4) for i, p in enumerate(probs)}
