import json
from fastapi import APIRouter
from ai_engine.reasoning.rule_engine import rule_engine

router = APIRouter(prefix="/rules", tags=["Symbolic Rules"])

@router.get("")
@router.get("/list")
def list_rules():
    return {"total_rules": len(rule_engine.rules), "rules": rule_engine.rules}

@router.post("/test")
def test_rules(facts: dict):
    triggered, has_override, primary_action = rule_engine.evaluate(facts)
    return {
        "triggered_count": len(triggered),
        "triggered_rules": [r.model_dump() for r in triggered],
        "has_hard_override": has_override,
        "primary_action": primary_action
    }
