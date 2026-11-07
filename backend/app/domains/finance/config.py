"""Finance domain - loan eligibility / credit-risk assessment."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd

from app.domains.base import DomainDefinition, finalize_labels
from app.domains.finance.rules import RULES
from app.schemas import FeatureSpec, OutcomeClass, ScenarioPreset

ANNUAL_RATE = 0.105  # reference interest rate used to estimate the proposed EMI

FEATURES = [
    FeatureSpec(name="monthly_income", label="Monthly income", kind="number", unit="₹", min=5000, max=500000, step=1000, default=60000, group="Income"),
    FeatureSpec(name="employment_type", label="Employment", kind="select", options=["Salaried", "Self-Employed", "Unemployed"], default="Salaried", group="Income"),
    FeatureSpec(name="years_employed", label="Years in employment", kind="number", unit="years", min=0, max=40, step=0.5, default=6, group="Income"),
    FeatureSpec(name="credit_score", label="Credit score", kind="number", unit="", min=300, max=900, step=1, default=720, group="Credit profile"),
    FeatureSpec(name="past_defaults", label="Past defaults", kind="number", unit="", min=0, max=5, step=1, default=0, group="Credit profile"),
    FeatureSpec(name="existing_emi", label="Existing EMI", kind="number", unit="₹/month", min=0, max=300000, step=500, default=10000, group="Credit profile"),
    FeatureSpec(name="loan_amount", label="Loan amount requested", kind="number", unit="₹", min=50000, max=10000000, step=10000, default=500000, group="Loan request"),
    FeatureSpec(name="loan_tenure_months", label="Loan tenure", kind="number", unit="months", min=6, max=360, step=6, default=60, group="Loan request"),
    FeatureSpec(name="age", label="Applicant age", kind="number", unit="years", min=21, max=70, step=1, default=34, group="Loan request"),
]

CLASSES = [
    OutcomeClass(level=0, key="LOW_RISK", label="Low Risk", tone="success", description="Applicant profile satisfies eligibility criteria."),
    OutcomeClass(level=1, key="MEDIUM_RISK", label="Medium Risk", tone="warning", description="Eligible with conditions; further review recommended."),
    OutcomeClass(level=2, key="HIGH_RISK", label="High Risk", tone="danger", description="Profile does not meet risk appetite."),
]

DERIVED = {
    "proposed_emi": "Proposed EMI: estimated monthly instalment at 10.5% p.a.",
    "dti_ratio": "Debt-to-income ratio: (existing EMI + proposed EMI) / monthly income",
    "loan_to_income": "Loan-to-income: loan amount / annual income",
}


def _emi(principal: float, months: float) -> float:
    r = ANNUAL_RATE / 12
    months = max(months, 1.0)
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


def derive(x: Mapping[str, float | str]) -> dict[str, float]:
    income = max(float(x["monthly_income"]), 1.0)
    emi = _emi(float(x["loan_amount"]), float(x["loan_tenure_months"]))
    return {
        "proposed_emi": round(emi, 2),
        "dti_ratio": round((float(x["existing_emi"]) + emi) / income, 4),
        "loan_to_income": round(float(x["loan_amount"]) / (income * 12), 4),
    }


def generate(n: int, rng: np.random.Generator) -> pd.DataFrame:
    employment = rng.choice(["Salaried", "Self-Employed", "Unemployed"], n, p=[0.62, 0.32, 0.06])
    income = np.where(employment == "Unemployed", rng.uniform(5000, 20000, n),
                      np.clip(rng.lognormal(np.log(55000), 0.6, n), 8000, 495000)).round(-2)
    years = np.where(employment == "Unemployed", 0, np.clip(rng.gamma(2.0, 3.5, n), 0, 40)).round(1)
    credit = np.clip(rng.normal(705, 75, n), 300, 900).round()
    defaults = np.clip(rng.poisson(np.maximum(0.05, (720 - credit) / 180), n), 0, 5)
    existing = (income * np.clip(rng.beta(1.6, 6, n), 0, 0.8)).round(-2)
    loan = np.clip(income * 12 * rng.lognormal(np.log(0.9), 0.65, n), 50000, 9900000).round(-3)
    tenure = rng.choice([24, 36, 48, 60, 84, 120, 180, 240], n)
    age = rng.integers(21, 70, n)
    df = pd.DataFrame({
        "monthly_income": income, "employment_type": employment, "years_employed": years,
        "credit_score": credit, "past_defaults": defaults, "existing_emi": existing,
        "loan_amount": loan, "loan_tenure_months": tenure, "age": age,
    })
    derived = pd.DataFrame([derive(r) for r in df.to_dict(orient="records")])
    latent = (
        -0.012 * (credit - 700)
        + 4.0 * (derived["dti_ratio"].to_numpy() - 0.35)
        + 0.18 * (derived["loan_to_income"].to_numpy() - 2)
        + 0.6 * defaults
        - 0.04 * np.minimum(years, 10)
        + 0.35 * (employment == "Self-Employed")
        - 0.25 * np.log(income / 50000)
        + rng.normal(0, 0.45, n)
    )
    return finalize_labels(df, latent, (0.35, 1.45), RULES, derive, rng)


DOMAIN = DomainDefinition(
    id="finance",
    name="Finance",
    title="Loan Eligibility & Credit Risk",
    tagline="Credit risk assessment",
    description="Predicts the credit-risk category of a loan application and validates it against lending policy: credit score bands, debt-to-income limits, income and employment criteria.",
    icon="landmark",
    task_type="Classification (3-class)",
    subject="applicant",
    features=FEATURES,
    classes=CLASSES,
    rules=RULES,
    derive=derive,
    derived_features=DERIVED,
    generate=generate,
    presets=[
        ScenarioPreset(id="prime", name="Salaried, good credit", description="₹60k income, score 720, ₹5L loan",
                       inputs={"monthly_income": 60000, "employment_type": "Salaried", "years_employed": 6, "credit_score": 720, "past_defaults": 0, "existing_emi": 10000, "loan_amount": 500000, "loan_tenure_months": 60, "age": 34}),
        ScenarioPreset(id="stretched", name="Stretched borrower", description="High DTI, fair credit",
                       inputs={"monthly_income": 45000, "employment_type": "Self-Employed", "years_employed": 2, "credit_score": 655, "past_defaults": 1, "existing_emi": 12000, "loan_amount": 900000, "loan_tenure_months": 60, "age": 29}),
        ScenarioPreset(id="subprime", name="Below minimum score", description="Score 560 - hard rule override",
                       inputs={"monthly_income": 85000, "employment_type": "Salaried", "years_employed": 8, "credit_score": 560, "past_defaults": 0, "existing_emi": 5000, "loan_amount": 400000, "loan_tenure_months": 48, "age": 41}),
    ],
    level_recommendations={
        0: ["Low predicted risk; proceed with standard verification of income and identity documents."],
        1: ["Proceed with enhanced verification (income proof, bank statements).", "Consider a reduced amount or longer tenure to improve affordability."],
        2: ["Not recommended under current policy; communicate the failing criteria to the applicant."],
    },
    disclaimer="This is a decision-support result, not an actual loan approval.",
)
