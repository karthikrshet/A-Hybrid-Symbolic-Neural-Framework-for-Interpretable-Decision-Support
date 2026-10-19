import pytest
from backend.app.schemas.validators import (
    validate_transaction_amount, validate_velocity_change,
    validate_geographic_distance, validate_ip_reputation,
    validate_device_trust, validate_hour_of_day, validate_kyc_status
)

def test_amount_positive():
    assert validate_transaction_amount(100.0) is True
    with pytest.raises(ValueError):
        validate_transaction_amount(-5.0)

def test_amount_limit():
    with pytest.raises(ValueError):
        validate_transaction_amount(15_000_000.0)

def test_geo_distance_bounds():
    assert validate_geographic_distance(500.0) is True
    with pytest.raises(ValueError):
        validate_geographic_distance(30000.0)

def test_reputation_scores():
    assert validate_ip_reputation(0.85) is True
    with pytest.raises(ValueError):
        validate_ip_reputation(1.5)

def test_kyc_statuses():
    assert validate_kyc_status("VERIFIED") is True
    with pytest.raises(ValueError):
        validate_kyc_status("UNAUTHORIZED_STATUS")
