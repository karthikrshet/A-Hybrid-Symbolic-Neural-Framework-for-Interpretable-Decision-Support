import pytest

from app.agents.coordinator_agent import coordinator
from app.core.domain_manager import domain_manager

DOMAINS = ["healthcare", "finance", "fraud_detection", "it_troubleshooting", "education"]


def test_all_domains_discovered() -> None:
    assert [d.id for d in domain_manager.list()] == DOMAINS


@pytest.mark.parametrize("domain_id", DOMAINS)
def test_every_preset_produces_traceable_decision(domain_id: str) -> None:
    domain = domain_manager.get(domain_id)
    for preset in domain.presets:
        r = coordinator.decide(domain_id, preset.inputs)
        probs = r.neural_prediction.probabilities
        assert abs(sum(probs.values()) - 1) < 1e-3
        assert r.neural_prediction.attributions, "neural evidence must be present"
        assert r.symbolic_reasoning.rules_evaluated == len(domain.rules)
        assert len(r.symbolic_reasoning.triggered_rules) + len(r.symbolic_reasoning.passed_rules) == len(domain.rules)
        assert r.validation.consistency_ok
        assert [s.order for s in r.agent_trace] == list(range(1, len(r.agent_trace) + 1))
        assert r.explanation.summary and r.recommendations


def test_hard_rule_overrides_neural_prediction() -> None:
    preset = next(p for p in domain_manager.get("finance").presets if p.id == "subprime")
    r = coordinator.decide("finance", preset.inputs)
    assert r.final_decision.level == 2
    assert "FN-01" in [t.id for t in r.symbolic_reasoning.triggered_rules]


def test_input_validation_clips_and_defaults() -> None:
    r = coordinator.decide("healthcare", {"age": 300, "systolic_bp": 120})
    assert not r.validation.input_valid
    assert r.inputs["age"] == 90
    assert any("missing" in i for i in r.validation.input_issues)
