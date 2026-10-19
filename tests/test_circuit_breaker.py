import pytest
from ai_engine.orchestration.circuit_breaker import AgentCircuitBreaker, CircuitState

def test_circuit_breaker_transitions():
    cb = AgentCircuitBreaker(failure_threshold=2, recovery_timeout_s=0.1)
    assert cb.state == CircuitState.CLOSED
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False
