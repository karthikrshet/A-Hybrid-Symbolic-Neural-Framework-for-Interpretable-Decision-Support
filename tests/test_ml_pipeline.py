import pytest
from ml.datasets.generator import generate_financial_dataset
from ml.preprocessing.preprocessor import FinancialFeaturePreprocessor, FEATURE_COLUMNS
from ai_engine.inference.model_manager import model_manager

def test_dataset_generation():
    df = generate_financial_dataset(n_samples=100)
    assert len(df) == 100
    assert "is_fraud" in df.columns
    assert set(FEATURE_COLUMNS).issubset(df.columns)

def test_model_inference():
    sample = {
        "transaction_amount": 5000.0,
        "transaction_frequency_24h": 3,
        "velocity_change_ratio": 2.0,
        "location_distance_km": 15.0,
        "hour_of_day": 14,
        "is_weekend": 0,
        "is_sanctioned_destination": 0,
        "kyc_status": "VERIFIED",
        "foreign_exchange_risk": 0.1,
        "ip_reputation_score": 0.90,
        "device_trust_score": 0.85,
        "user_failed_attempts_1h": 0,
        "past_chargeback_count": 0
    }
    prob, label, attributions = model_manager.predict(sample)
    assert 0.0 <= prob <= 1.0
    assert label in ["LOW_RISK", "MEDIUM_RISK", "HIGH_RISK"]
    assert len(attributions) > 0
