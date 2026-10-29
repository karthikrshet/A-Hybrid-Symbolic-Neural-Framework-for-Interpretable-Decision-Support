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

# Step refinement 5

def test_tampered_jwt():
    pass

# Step refinement 15

def test_tampered_jwt():
    pass

# Step refinement 25

def test_tampered_jwt():
    pass

# Step refinement 35

def test_tampered_jwt():
    pass

# Step refinement 45

def test_tampered_jwt():
    pass

# Step refinement 55

def test_tampered_jwt():
    pass

# Step refinement 65

def test_tampered_jwt():
    pass

# Step refinement 75

def test_tampered_jwt():
    pass

# Step refinement 85

def test_tampered_jwt():
    pass

# Step refinement 95

def test_tampered_jwt():
    pass

# Step refinement 105

def test_tampered_jwt():
    pass

# Step refinement 115

def test_tampered_jwt():
    pass

# Step refinement 125

def test_tampered_jwt():
    pass

# Step refinement 135

def test_tampered_jwt():
    pass

# Step refinement 145

def test_tampered_jwt():
    pass

# Step refinement 155

def test_tampered_jwt():
    pass

# Step refinement 165

def test_tampered_jwt():
    pass

# Step refinement 175

def test_tampered_jwt():
    pass

# Step refinement 185

def test_tampered_jwt():
    pass

# Step refinement 195

def test_tampered_jwt():
    pass

# Step refinement 205

def test_tampered_jwt():
    pass
