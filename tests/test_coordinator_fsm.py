import pytest
import asyncio
from ai_engine.orchestration.coordinator import coordinator

@pytest.mark.asyncio
async def test_coordinator_workflow():
    sample = {
        "transaction_amount": 15000.0,
        "kyc_status": "INCOMPLETE",
        "is_sanctioned_destination": False,
        "transaction_frequency_24h": 5,
        "velocity_change_ratio": 3.0,
        "location_distance_km": 50.0,
        "hour_of_day": 2,
        "is_weekend": 1,
        "foreign_exchange_risk": 0.8,
        "ip_reputation_score": 0.3,
        "device_trust_score": 0.2,
        "user_failed_attempts_1h": 2,
        "past_chargeback_count": 1
    }
    result = await coordinator.execute_decision_pipeline(sample)
    assert "decision_id" in result
    assert result["final_decision"] in ["APPROVE", "FLAG_MONITOR", "FLAG_SUSPICIOUS", "REJECT", "REQUIRES_HUMAN_REVIEW"]
    assert len(result["execution_trace"]) >= 5
    assert result["validation_status"] == "VALID"
