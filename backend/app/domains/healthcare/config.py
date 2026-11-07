"""Healthcare domain - health (cardiometabolic) risk assessment."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd

from app.domains.base import DomainDefinition, finalize_labels
from app.domains.healthcare.rules import RULES
from app.schemas import FeatureSpec, OutcomeClass, ScenarioPreset

FEATURES = [
    FeatureSpec(name="age", label="Age", kind="number", unit="years", min=18, max=90, step=1, default=45, group="Demographics"),
    FeatureSpec(name="gender", label="Gender", kind="select", options=["Female", "Male"], default="Male", group="Demographics"),
    FeatureSpec(name="systolic_bp", label="Systolic BP", kind="number", unit="mmHg", min=80, max=220, step=1, default=145, group="Vitals"),
    FeatureSpec(name="diastolic_bp", label="Diastolic BP", kind="number", unit="mmHg", min=50, max=140, step=1, default=95, group="Vitals"),
    FeatureSpec(name="heart_rate", label="Resting heart rate", kind="number", unit="bpm", min=40, max=160, step=1, default=78, group="Vitals"),
    FeatureSpec(name="glucose", label="Fasting glucose", kind="number", unit="mg/dL", min=60, max=350, step=1, default=160, group="Lab results"),
    FeatureSpec(name="cholesterol", label="Total cholesterol", kind="number", unit="mg/dL", min=100, max=350, step=1, default=210, group="Lab results"),
    FeatureSpec(name="bmi", label="BMI", kind="number", unit="kg/m²", min=14, max=55, step=0.1, default=29, group="Lab results"),
    FeatureSpec(name="smoking", label="Smoking status", kind="select", options=["Never", "Former", "Current"], default="Never", group="Lifestyle"),
    FeatureSpec(name="physical_activity", label="Physical activity", kind="select", options=["Low", "Moderate", "High"], default="Moderate", group="Lifestyle"),
    FeatureSpec(name="family_history", label="Family history of CVD/diabetes", kind="select", options=["No", "Yes"], default="No", group="Lifestyle"),
]

CLASSES = [
    OutcomeClass(level=0, key="LOW_RISK", label="Low Risk", tone="success", description="No significant risk pattern detected."),
    OutcomeClass(level=1, key="MODERATE_RISK", label="Moderate Risk", tone="warning", description="Some risk indicators present; follow-up advised."),
    OutcomeClass(level=2, key="HIGH_RISK", label="Elevated Risk", tone="danger", description="Elevated-risk pattern; professional assessment advised."),
]

DERIVED = {
    "pulse_pressure": "Pulse pressure: systolic − diastolic BP (mmHg)",
    "metabolic_risk_count": "Metabolic risk factors: count of BP ≥ 140, glucose ≥ 126, BMI ≥ 30, cholesterol ≥ 240",
}


def derive(x: Mapping[str, float | str]) -> dict[str, float]:
    sbp, dbp = float(x["systolic_bp"]), float(x["diastolic_bp"])
    count = (
        int(sbp >= 140 or dbp >= 90)
        + int(float(x["glucose"]) >= 126)
        + int(float(x["bmi"]) >= 30)
        + int(float(x["cholesterol"]) >= 240)
    )
    return {"pulse_pressure": sbp - dbp, "metabolic_risk_count": float(count)}


def generate(n: int, rng: np.random.Generator) -> pd.DataFrame:
    age = rng.integers(18, 90, n)
    gender = rng.choice(["Female", "Male"], n)
    activity = rng.choice(["Low", "Moderate", "High"], n, p=[0.4, 0.4, 0.2])
    smoking = rng.choice(["Never", "Former", "Current"], n, p=[0.55, 0.25, 0.2])
    family = rng.choice(["No", "Yes"], n, p=[0.65, 0.35])
    act = np.select([activity == "Low", activity == "High"], [1.0, -1.0], 0.0)
    bmi = np.clip(rng.normal(27 + 2.0 * act, 5.0, n), 15, 54)
    sbp = np.clip(rng.normal(102 + 0.45 * age + 0.6 * (bmi - 25), 15, n), 85, 218)
    dbp = np.clip(sbp * 0.62 + rng.normal(6, 7, n), 52, 138)
    glucose = np.clip(rng.lognormal(np.log(92 + 1.6 * np.maximum(bmi - 24, 0) + 0.25 * age), 0.24, n), 62, 345)
    chol = np.clip(rng.normal(175 + 0.7 * age + 1.2 * (bmi - 25), 32, n), 105, 345)
    hr = np.clip(rng.normal(74 + 3 * act + 4 * (smoking == "Current"), 11, n), 42, 158)
    df = pd.DataFrame({
        "age": age, "gender": gender, "systolic_bp": sbp.round(), "diastolic_bp": dbp.round(),
        "heart_rate": hr.round(), "glucose": glucose.round(), "cholesterol": chol.round(), "bmi": bmi.round(1),
        "smoking": smoking, "physical_activity": activity, "family_history": family,
    })
    latent = (
        0.035 * (age - 45)
        + 0.045 * (sbp - 125)
        + 0.022 * (glucose - 100)
        + 0.09 * (bmi - 26)
        + 0.012 * (chol - 200)
        + 0.02 * (hr - 75)
        + 0.6 * (smoking == "Current") + 0.2 * (smoking == "Former")
        + 0.45 * (family == "Yes") + 0.35 * act + 0.15 * (gender == "Male")
        + rng.normal(0, 0.55, n)
    )
    return finalize_labels(df, latent, (1.3, 2.9), RULES, derive, rng)


DOMAIN = DomainDefinition(
    id="healthcare",
    name="Healthcare",
    title="Health Risk Assessment",
    tagline="Cardiometabolic risk screening",
    description="Combines a neural risk model with clinical screening rules (blood pressure, glucose, BMI, lipids) to flag elevated health-risk patterns with transparent justification.",
    icon="heart-pulse",
    task_type="Risk prediction (3-class)",
    subject="patient",
    features=FEATURES,
    classes=CLASSES,
    rules=RULES,
    derive=derive,
    derived_features=DERIVED,
    generate=generate,
    presets=[
        ScenarioPreset(id="healthy", name="Healthy adult", description="Normal vitals, active lifestyle",
                       inputs={"age": 32, "gender": "Female", "systolic_bp": 116, "diastolic_bp": 74, "heart_rate": 68, "glucose": 88, "cholesterol": 172, "bmi": 22.4, "smoking": "Never", "physical_activity": "High", "family_history": "No"}),
        ScenarioPreset(id="elevated", name="Elevated risk", description="BP 145/95, glucose 160, BMI 29",
                       inputs={"age": 45, "gender": "Male", "systolic_bp": 145, "diastolic_bp": 95, "heart_rate": 80, "glucose": 160, "cholesterol": 215, "bmi": 29, "smoking": "Former", "physical_activity": "Low", "family_history": "Yes"}),
        ScenarioPreset(id="crisis", name="Hypertensive crisis", description="BP 186/122 - hard rule override",
                       inputs={"age": 38, "gender": "Male", "systolic_bp": 186, "diastolic_bp": 122, "heart_rate": 84, "glucose": 98, "cholesterol": 190, "bmi": 24.5, "smoking": "Never", "physical_activity": "Moderate", "family_history": "No"}),
    ],
    level_recommendations={
        0: ["Maintain current healthy habits and routine annual check-ups."],
        1: ["Book a follow-up consultation to review the flagged indicators.", "Adopt lifestyle changes: balanced diet, regular exercise, reduced salt and sugar."],
        2: ["Seek appropriate professional medical assessment soon.", "Do not change any medication without consulting a clinician."],
    },
    disclaimer="Illustrative decision-support output, not a medical diagnosis. Always consult a qualified healthcare professional.",
)
