import pytest
from ai_engine.reasoning.rule_engine import rule_engine

def test_sanctioned_jurisdiction_override():
    facts = {"is_sanctioned_destination": True, "transaction_amount": 100.0}
    triggered, has_override, action = rule_engine.evaluate(facts)
    assert has_override is True
    assert action == "REJECT"
    assert any(r.rule_id == "RULE-AML-001" for r in triggered)

def test_clean_domestic_transaction():
    facts = {
        "is_sanctioned_destination": False,
        "transaction_amount": 150.0,
        "device_trust_score": 0.95,
        "user_failed_attempts_1h": 0
    }
    triggered, has_override, action = rule_engine.evaluate(facts)
    assert has_override is False
    assert any(r.rule_id == "RULE-CLEAR-008" for r in triggered)
