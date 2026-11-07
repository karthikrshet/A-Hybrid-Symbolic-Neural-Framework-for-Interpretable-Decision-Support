from app.core.rule_engine import condition_text, evaluate_rule, rule_implied_level
from app.domains.base import cond, rule

R1 = rule("T-1", "High value", "x above 10", "Test", [cond("x", "gt", 10)], 2, "hard", "act")
R2 = rule("T-2", "Category", "c is A or y low", "Test", [cond("c", "eq", "A"), cond("y", "lt", 5)], 1, "soft", "act", logic="any")


def test_gt_rule_fires_and_records_observed() -> None:
    fired, observed = evaluate_rule(R1, {"x": 12})
    assert fired and observed == {"x": 12}
    assert not evaluate_rule(R1, {"x": 10})[0]


def test_any_logic_and_numeric_equality() -> None:
    assert evaluate_rule(R2, {"c": "B", "y": 3})[0]
    assert evaluate_rule(R2, {"c": "A", "y": 9})[0]
    assert not evaluate_rule(R2, {"c": "B", "y": 9})[0]
    eq = rule("T-3", "eq", "", "T", [cond("n", "eq", 1)], 1, "soft", "")
    assert evaluate_rule(eq, {"n": 1.0})[0]


def test_implied_level_and_text() -> None:
    assert rule_implied_level([R1, R2], {"x": 11, "c": "A", "y": 9}) == 2
    assert rule_implied_level([R1, R2], {"x": 11, "c": "A", "y": 9}, hard_only=True) == 2
    assert rule_implied_level([R1, R2], {"x": 1, "c": "B", "y": 9}) == 0
    assert condition_text(R1, {"x": "X"}) == "IF X > 10"
