import numpy as np
import pandas as pd
import os

def generate_financial_dataset(n_samples: int = 5000, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    
    # 1. Generate core numerical transaction features
    amounts = np.random.exponential(scale=250.0, size=n_samples) + 10.0
    freq_24h = np.random.poisson(lam=3, size=n_samples) + 1
    velocity_ratio = np.random.lognormal(mean=0.0, sigma=0.5, size=n_samples)
    distance_km = np.random.exponential(scale=20.0, size=n_samples)
    hour = np.random.randint(0, 24, size=n_samples)
    is_weekend = np.random.choice([0, 1], p=[0.72, 0.28], size=n_samples)
    
    # 2. Risk markers
    sanctioned = np.random.choice([0, 1], p=[0.985, 0.015], size=n_samples)
    kyc_incomplete = np.random.choice([0, 1], p=[0.90, 0.10], size=n_samples)
    forex_risk = np.random.beta(a=1.5, b=5.0, size=n_samples)
    ip_rep = np.random.beta(a=8.0, b=1.5, size=n_samples)
    device_trust = np.random.beta(a=7.0, b=1.5, size=n_samples)
    failed_attempts = np.random.poisson(lam=0.4, size=n_samples)
    chargebacks = np.random.poisson(lam=0.15, size=n_samples)
    channel = np.random.choice(["MOBILE", "WEB", "ATM", "API"], p=[0.60, 0.25, 0.10, 0.05], size=n_samples)
    
    # 3. Ground truth fraud probability formula (non-linear empirical interaction)
    logits = (
        0.003 * (amounts - 250) +
        0.35 * (freq_24h - 3) +
        0.60 * (velocity_ratio - 1.0) +
        0.02 * (distance_km - 20) +
        1.80 * (1.0 - ip_rep) +
        1.50 * (1.0 - device_trust) +
        1.20 * failed_attempts +
        2.50 * chargebacks +
        4.00 * sanctioned +
        2.00 * kyc_incomplete -
        4.0
    )
    probs = 1.0 / (1.0 + np.exp(-logits))
    is_fraud = (np.random.rand(n_samples) < probs).astype(int)
    
    df = pd.DataFrame({
        "transaction_amount": np.round(amounts, 2),
        "transaction_frequency_24h": freq_24h,
        "velocity_change_ratio": np.round(velocity_ratio, 2),
        "location_distance_km": np.round(distance_km, 2),
        "hour_of_day": hour,
        "is_weekend": is_weekend,
        "is_sanctioned_destination": sanctioned,
        "kyc_incomplete": kyc_incomplete,
        "foreign_exchange_risk": np.round(forex_risk, 3),
        "ip_reputation_score": np.round(ip_rep, 3),
        "device_trust_score": np.round(device_trust, 3),
        "user_failed_attempts_1h": failed_attempts,
        "past_chargeback_count": chargebacks,
        "channel_type": channel,
        "is_fraud": is_fraud
    })
    return df

if __name__ == "__main__":
    out_dir = os.path.dirname(__file__)
    df = generate_financial_dataset()
    path = os.path.join(out_dir, "transactions_synthetic.csv")
    df.to_csv(path, index=False)
    print(f"Dataset generated at {path} with {len(df)} records. Fraud rate: {df['is_fraud'].mean():.2%}")
