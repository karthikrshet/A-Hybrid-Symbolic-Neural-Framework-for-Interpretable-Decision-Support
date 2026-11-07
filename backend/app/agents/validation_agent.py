"""Validation Agent - checks inputs before analysis and the decision afterwards.

Pre-analysis : type coercion, range checks, defaults for missing values, and an
               out-of-distribution check against the model's training data.
Post-decision: consistency with hard rules, agreement with soft rules, and the
               confidence threshold that decides whether a human should review.
"""

from __future__ import annotations

from collections.abc import Mapping

from app.core.domain_manager import domain_manager
from app.domains.base import DomainDefinition
from app.schemas import FinalDecision, FusionResult, SymbolicReasoning, ValidationReport

CONFIDENCE_THRESHOLD = 0.60
OOD_Z = 3.5


class ValidationAgent:
    name = "Validation Agent"
    role = "Checks inputs, consistency with rules and reliability of the decision."

    def validate_inputs(
        self, domain: DomainDefinition, raw: Mapping[str, float | str]
    ) -> tuple[dict[str, float | str], list[str], list[str]]:
        clean: dict[str, float | str] = {}
        issues: list[str] = []
        for f in domain.features:
            value = raw.get(f.name)
            if value is None or value == "":
                clean[f.name] = f.default
                issues.append(f"{f.label} missing - default value {f.default} used.")
                continue
            if f.kind == "select":
                match = next((o for o in f.options if o.lower() == str(value).strip().lower()), None)
                if match is None:
                    clean[f.name] = f.default
                    issues.append(f"{f.label} '{value}' not recognised - default '{f.default}' used.")
                else:
                    clean[f.name] = match
                continue
            try:
                num = float(value)
            except (TypeError, ValueError):
                clean[f.name] = f.default
                issues.append(f"{f.label} '{value}' is not numeric - default {f.default} used.")
                continue
            if f.min is not None and num < f.min:
                issues.append(f"{f.label} {num:g} below allowed minimum {f.min:g}; clipped.")
                num = f.min
            if f.max is not None and num > f.max:
                issues.append(f"{f.label} {num:g} above allowed maximum {f.max:g}; clipped.")
                num = f.max
            clean[f.name] = num

        ood: list[str] = []
        meta = domain_manager.get_model(domain.id).metadata
        for name, mean in meta["stats"]["mean"].items():
            std = meta["stats"]["std"][name] or 1.0
            z = abs(float(clean[name]) - mean) / std
            if z > OOD_Z:
                ood.append(f"{domain.feature_labels[name]} is unusual compared with training data (z = {z:.1f}).")
        return clean, issues, ood

    def validate_decision(
        self,
        input_issues: list[str],
        ood: list[str],
        symbolic: SymbolicReasoning,
        fusion: FusionResult,
        final: FinalDecision,
    ) -> ValidationReport:
        hard_level = max((r.implies_level for r in symbolic.triggered_rules if r.severity == "hard"), default=0)
        consistency_ok = final.level >= hard_level
        soft_ok = final.level >= symbolic.rule_level
        confidence_ok = final.confidence >= CONFIDENCE_THRESHOLD
        big_conflict = fusion.conflict.detected and fusion.conflict.type == "NEURAL_OVERESTIMATES" and not fusion.override_applied
        checks = [
            f"{'✔' if not input_issues else '⚠'} Input validation: {len(input_issues)} issue(s).",
            f"{'✔' if consistency_ok else '✖'} Hard-rule consistency: decision satisfies every mandatory rule.",
            f"{'✔' if soft_ok else '⚠'} Soft-rule agreement: decision {'is at or above' if soft_ok else 'is below'} the rule-implied level ({symbolic.rule_label}).",
            f"{'✔' if confidence_ok else '⚠'} Confidence {final.confidence:.0%} vs threshold {CONFIDENCE_THRESHOLD:.0%}.",
            f"{'✔' if not ood else '⚠'} Distribution check: {len(ood)} unusual value(s).",
        ]
        return ValidationReport(
            input_valid=not input_issues,
            input_issues=input_issues,
            out_of_distribution=ood,
            consistency_ok=consistency_ok,
            confidence_ok=confidence_ok,
            requires_human_review=(not confidence_ok) or (not consistency_ok) or bool(ood) or big_conflict,
            checks=checks,
        )
