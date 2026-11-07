"""Deterministic IF-THEN rule engine used by the Symbolic Reasoning Agent.

Rules are pure data (:class:`RuleSpec`), so a domain's knowledge base can be
inspected, displayed and audited without reading code.
"""

from __future__ import annotations

from collections.abc import Mapping

from app.schemas import ConditionSpec, RuleSpec

Facts = Mapping[str, float | str]

_OP_TEXT: dict[str, str] = {
    "gt": ">",
    "gte": "≥",
    "lt": "<",
    "lte": "≤",
    "eq": "=",
    "neq": "≠",
    "in": "in",
}


def _check(condition: ConditionSpec, facts: Facts) -> bool:
    if condition.feature not in facts:
        return False
    actual = facts[condition.feature]
    expected = condition.value
    op = condition.op
    if op == "in":
        return isinstance(expected, list) and str(actual) in expected
    if op in ("eq", "neq"):
        try:
            same = float(actual) == float(expected)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            same = str(actual) == str(expected)
        return same if op == "eq" else not same
    try:
        a = float(actual)
        b = float(expected)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False
    if op == "gt":
        return a > b
    if op == "gte":
        return a >= b
    if op == "lt":
        return a < b
    return a <= b  # lte


def evaluate_rule(rule: RuleSpec, facts: Facts) -> tuple[bool, dict[str, float | str]]:
    """Return whether the rule fires plus the observed values it inspected."""
    results = [_check(c, facts) for c in rule.conditions]
    fired = all(results) if rule.logic == "all" else any(results)
    observed: dict[str, float | str] = {}
    for c in rule.conditions:
        if c.feature in facts:
            v = facts[c.feature]
            observed[c.feature] = round(float(v), 3) if isinstance(v, (int, float)) else v
    return fired, observed


def condition_text(rule: RuleSpec, labels: Mapping[str, str]) -> str:
    joiner = " AND " if rule.logic == "all" else " OR "
    parts: list[str] = []
    for c in rule.conditions:
        name = labels.get(c.feature, c.feature)
        if isinstance(c.value, list):
            value = ", ".join(c.value)
        elif isinstance(c.value, float):
            value = f"{c.value:,g}" if abs(c.value) < 1e6 else f"{c.value:,.0f}"
        else:
            value = c.value
        parts.append(f"{name} {_OP_TEXT[c.op]} {value}")
    return "IF " + joiner.join(parts)


def rule_implied_level(rules: list[RuleSpec], facts: Facts, hard_only: bool = False) -> int:
    """Highest outcome level demanded by the rules that fire (0 when none fire)."""
    level = 0
    for rule in rules:
        if hard_only and rule.severity != "hard":
            continue
        fired, _ = evaluate_rule(rule, facts)
        if fired:
            level = max(level, rule.implies_level)
    return level
