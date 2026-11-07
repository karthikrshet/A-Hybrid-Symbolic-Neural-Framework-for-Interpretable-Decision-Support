"""Cyber-security domain - financial transaction fraud detection."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd

from app.domains.base import DomainDefinition, finalize_labels
from app.domains.fraud_detection.rules import RULES
from app.schemas import FeatureSpec, OutcomeClass, ScenarioPreset

FEATURES = [
    FeatureSpec(name="amount", label="Transaction amount", kind="number", unit="₹", min=1, max=5000000, step=100, default=85000, group="Transaction"),
    FeatureSpec(name="avg_amount", label="Customer's average amount", kind="number", unit="₹", min=100, max=500000, step=100, default=4000, group="Transaction"),
    FeatureSpec(name="hour_of_day", label="Hour of day", kind="number", unit="0-23", min=0, max=23, step=1, default=2, group="Transaction"),
    FeatureSpec(name="international", label="International", kind="select", options=["No", "Yes"], default="Yes", group="Transaction"),
    FeatureSpec(name="transactions_24h", label="Transactions in last 24h", kind="number", unit="", min=0, max=100, step=1, default=6, group="Behaviour"),
    FeatureSpec(name="distance_km", label="Distance from usual location", kind="number", unit="km", min=0, max=15000, step=10, default=1400, group="Behaviour"),
    FeatureSpec(name="new_device", label="New / unrecognised device", kind="select", options=["No", "Yes"], default="Yes", group="Behaviour"),
    FeatureSpec(name="failed_attempts_1h", label="Failed login attempts (1h)", kind="number", unit="", min=0, max=20, step=1, default=1, group="Security"),
    FeatureSpec(name="kyc_status", label="KYC status", kind="select", options=["Verified", "Pending", "Expired"], default="Verified", group="Security"),
    FeatureSpec(name="destination_risk", label="Destination risk", kind="select", options=["Low", "High", "Blacklisted"], default="Low", group="Security"),
]

CLASSES = [
    OutcomeClass(level=0, key="LEGITIMATE", label="Legitimate", tone="success", description="Transaction pattern looks normal."),
    OutcomeClass(level=1, key="SUSPICIOUS", label="Suspicious", tone="warning", description="Unusual pattern; verification recommended."),
    OutcomeClass(level=2, key="FRAUDULENT", label="Likely Fraud", tone="danger", description="Strong fraud indicators; block or hold advised."),
]

DERIVED = {
    "amount_ratio": "Amount ratio: transaction amount / customer's average amount",
}


def derive(x: Mapping[str, float | str]) -> dict[str, float]:
    return {"amount_ratio": round(float(x["amount"]) / max(float(x["avg_amount"]), 1.0), 3)}


def generate(n: int, rng: np.random.Generator) -> pd.DataFrame:
    fraud = rng.random(n) < 0.16  # hidden fraud intent
    avg = np.clip(rng.lognormal(np.log(3500), 0.8, n), 150, 450000).round(-1)
    ratio = np.where(fraud, rng.lognormal(np.log(4.5), 0.9, n), rng.lognormal(np.log(1.0), 0.55, n))
    amount = np.clip(avg * ratio, 10, 4900000).round(-1)
    hour = np.where(fraud & (rng.random(n) < 0.5), rng.integers(0, 6, n), rng.integers(6, 24, n))
    intl = np.where(rng.random(n) < np.where(fraud, 0.45, 0.07), "Yes", "No")
    tx24 = np.clip(rng.poisson(np.where(fraud, 7, 2.5)), 0, 99)
    dist = np.clip(np.where(fraud, rng.lognormal(np.log(500), 1.3, n), rng.lognormal(np.log(12), 1.2, n)), 0, 14900).round()
    new_dev = np.where(rng.random(n) < np.where(fraud, 0.6, 0.08), "Yes", "No")
    failed = np.clip(rng.poisson(np.where(fraud, 1.8, 0.15)), 0, 20)
    kyc = rng.choice(["Verified", "Pending", "Expired"], n, p=[0.86, 0.08, 0.06])
    dest = np.where(rng.random(n) < np.where(fraud, 0.25, 0.03), "High", "Low")
    dest = np.where(rng.random(n) < np.where(fraud, 0.08, 0.002), "Blacklisted", dest)
    df = pd.DataFrame({
        "amount": amount, "avg_amount": avg, "hour_of_day": hour, "international": intl,
        "transactions_24h": tx24, "distance_km": dist, "new_device": new_dev,
        "failed_attempts_1h": failed, "kyc_status": kyc, "destination_risk": dest,
    })
    latent = (
        0.75 * np.log1p(ratio) + 0.12 * tx24 + 0.35 * np.log1p(dist / 50)
        + 0.8 * (new_dev == "Yes") + 0.6 * (intl == "Yes") + 0.5 * (hour < 5)
        + 0.45 * failed + 0.4 * (kyc != "Verified") + 1.0 * (dest == "High")
        + 1.2 * fraud + rng.normal(0, 0.45, n)
    )
    return finalize_labels(df, latent, (2.1, 3.9), RULES, derive, rng)


DOMAIN = DomainDefinition(
    id="fraud_detection",
    name="Cyber Security",
    title="Transaction Fraud Detection",
    tagline="Suspicious transaction analysis",
    description="Detects suspicious financial transactions by combining a neural anomaly model with AML/KYC fraud-detection rules (velocity, device, location, sanctions).",
    icon="shield-alert",
    task_type="Fraud classification (3-class)",
    subject="transaction",
    features=FEATURES,
    classes=CLASSES,
    rules=RULES,
    derive=derive,
    derived_features=DERIVED,
    generate=generate,
    presets=[
        ScenarioPreset(id="routine", name="Routine purchase", description="₹2,400 local card payment",
                       inputs={"amount": 2400, "avg_amount": 3000, "hour_of_day": 14, "international": "No", "transactions_24h": 2, "distance_km": 4, "new_device": "No", "failed_attempts_1h": 0, "kyc_status": "Verified", "destination_risk": "Low"}),
        ScenarioPreset(id="unusual", name="Unusual transfer", description="6× average, 1,400 km away",
                       inputs={"amount": 24000, "avg_amount": 4000, "hour_of_day": 22, "international": "No", "transactions_24h": 4, "distance_km": 1400, "new_device": "No", "failed_attempts_1h": 0, "kyc_status": "Verified", "destination_risk": "Low"}),
        ScenarioPreset(id="takeover", name="Account takeover", description="₹85k at 2 AM, new device, abroad",
                       inputs={"amount": 85000, "avg_amount": 4000, "hour_of_day": 2, "international": "Yes", "transactions_24h": 6, "distance_km": 1400, "new_device": "Yes", "failed_attempts_1h": 1, "kyc_status": "Verified", "destination_risk": "Low"}),
    ],
    level_recommendations={
        0: ["Allow the transaction; continue passive monitoring."],
        1: ["Hold for step-up verification (OTP / call-back) before release."],
        2: ["Block the transaction and notify the customer and fraud-operations team."],
    },
    disclaimer="Fraud scoring supports analysts; final action should follow the institution's fraud-operations policy.",
)
