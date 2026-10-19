import pytest
from ai_engine.reasoning.operators import op_between, op_regex, op_set_contains, op_subset, op_fuzzy_near

def test_op_between():
    assert op_between(5.0, [1.0, 10.0]) is True
    assert op_between(0.5, [1.0, 10.0]) is False

def test_op_regex():
    assert op_regex("REF-AML-9921", r"^REF-AML-\d{4}$") is True
    assert op_regex("MALFORMED", r"^REF-AML-\d{4}$") is False

def test_op_fuzzy_near():
    assert op_fuzzy_near(101.0, 100.0, tolerance=0.05) is True
    assert op_fuzzy_near(115.0, 100.0, tolerance=0.05) is False
