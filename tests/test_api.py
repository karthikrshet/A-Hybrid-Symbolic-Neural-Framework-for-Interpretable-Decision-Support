import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"

def test_rules_list():
    response = client.get("/api/v1/rules/list")
    assert response.status_code == 200
    assert response.json()["total_rules"] > 0

def test_rules_root():
    response = client.get("/api/v1/rules")
    assert response.status_code == 200
    assert response.json()["total_rules"] > 0

def test_decision_analyze_api():
    payload = {
        "transaction_amount": 250.0,
        "transaction_frequency_24h": 2,
        "velocity_change_ratio": 1.0,
        "location_distance_km": 5.0,
        "hour_of_day": 14,
        "is_weekend": False,
        "is_sanctioned_destination": False,
        "kyc_status": "VERIFIED",
        "foreign_exchange_risk": 0.1,
        "ip_reputation_score": 0.95,
        "device_trust_score": 0.90,
        "user_failed_attempts_1h": 0,
        "past_chargeback_count": 0,
        "channel_type": "MOBILE"
    }
    response = client.post("/api/v1/decisions/analyze", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert "final_decision" in res
    assert "explanation" in res
    assert res["final_decision"] in ["APPROVE", "FLAG_MONITOR", "FLAG_SUSPICIOUS", "REJECT", "REQUIRES_HUMAN_REVIEW"]

def test_decision_history_api():
    response = client.get("/api/v1/decisions/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_datasets_endpoints():
    r_info = client.get("/api/v1/datasets/info")
    assert r_info.status_code == 200
    assert "total_records" in r_info.json()

    r_sample = client.get("/api/v1/datasets/sample?limit=5")
    assert r_sample.status_code == 200
    assert len(r_sample.json()) <= 5

def test_models_endpoints():
    response = client.get("/api/v1/models/info")
    assert response.status_code == 200
    data = response.json()
    assert "algorithm" in data
    assert "model_version" in data

def test_audit_endpoints():
    r_logs = client.get("/api/v1/audit/logs")
    assert r_logs.status_code == 200
    assert isinstance(r_logs.json(), list)

    r_verify = client.get("/api/v1/audit/verify")
    assert r_verify.status_code == 200
    assert "chain_valid" in r_verify.json()

def test_agents_telemetry():
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert len(data["agents"]) >= 5

def test_chat_message():
    payload = {
        "message": "Evaluate transaction of $500 for unverified KYC user"
    }
    response = client.post("/api/v1/chat/message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 0

def test_evaluations_benchmark():
    response = client.get("/api/v1/evaluations/benchmark")
    assert response.status_code == 200
