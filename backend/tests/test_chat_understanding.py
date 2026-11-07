"""Regression battery: realistic chat questions -> correct domain, parameters and outcome."""

import pytest

from app.core.chat_engine import get_engine

CASES = [
    # message, domain picker, expected domain, expected kind, expected parameters, expected final label
    ("Is this transaction suspicious? ₹85,000 transfer at 2 AM from a new device, abroad, customer's average is 300", "finance",
     "fraud_detection", "decision", {"amount": 85000, "avg_amount": 300, "hour_of_day": 2}, "Likely Fraud"),
    ("payment of 2400 rupees, average 3000, domestic, usual device, KYC verified", None,
     "fraud_detection", "decision", {"amount": 2400, "avg_amount": 3000}, "Legitimate"),
    ("Check loan eligibility: income ₹60,000/month, credit score 720, existing EMI ₹10,000, loan ₹5 lakh, salaried", None,
     "finance", "decision", {"monthly_income": 60000, "credit_score": 720, "loan_amount": 500000}, "Low Risk"),
    ("My salary is 25000 and CIBIL is 550, I need a loan of 2 lakh", None,
     "finance", "decision", {"monthly_income": 25000, "credit_score": 550, "loan_amount": 200000}, "High Risk"),
    ("i earn fifty thousand a month, credit score seven hundred, want a loan of five lakh", None,
     "finance", "decision", {"monthly_income": 50000, "credit_score": 700, "loan_amount": 500000}, None),
    ("Patient aged 60, blood pressure 185/120, sugar 110 - is this risky?", None,
     "healthcare", "decision", {"age": 60, "systolic_bp": 185, "diastolic_bp": 120, "glucose": 110}, "Elevated Risk"),
    ("my mom is 58, her sugar was around two hundred and BP 150 over 95, should we worry?", None,
     "healthcare", "decision", {"age": 58, "glucose": 200, "systolic_bp": 150, "diastolic_bp": 95}, "Elevated Risk"),
    ("healthy 25 year old woman, bp 110/70, sugar 85, bmi 21, non-smoker", None,
     "healthcare", "decision", {"age": 25, "systolic_bp": 110, "glucose": 85, "bmi": 21}, "Low Risk"),
    ("My service has CPU 95%, memory 92%, API response time 8 seconds, error rate 25% and is unhealthy", None,
     "it_troubleshooting", "decision", {"cpu_utilization": 95, "response_time_ms": 8000, "error_rate": 25}, "Critical Failure Risk"),
    ("server cpu 30% memory 40% latency 150 ms errors 0.2% healthy", None,
     "it_troubleshooting", "decision", {"cpu_utilization": 30, "response_time_ms": 150}, "Healthy"),
    ("Attendance 92%, assignment 84, exam 81, mock 78, no backlogs - how is this student doing?", None,
     "education", "decision", {"attendance": 92, "assignment_score": 84, "backlogs": 0}, "On Track"),
    ("student attendance 55, 4 backlogs, exam 30, mock 28", None,
     "education", "decision", {"attendance": 55, "backlogs": 4}, "At Risk"),
    ("is my server ok", None, "it_troubleshooting", "clarify", {}, None),
    ("can I get a loan?", None, "finance", "clarify", {}, None),
]


@pytest.mark.parametrize("message,picker,domain,kind,params,label", CASES, ids=[c[0][:40] for c in CASES])
def test_chat_answers(message: str, picker: str | None, domain: str, kind: str, params: dict[str, float], label: str | None) -> None:
    msg, _, result = get_engine().respond(message, {}, None, picker)
    assert msg["routing"]["domain"] == domain
    assert msg["kind"] == kind
    for name, value in params.items():
        assert float(msg["routing"]["extracted"][name]) == pytest.approx(value), name
    if label:
        assert result is not None and result.final_decision.label == label


def test_explanation_never_claims_rules_raised_a_low_outcome() -> None:
    _, _, r = get_engine().respond("income 54000, credit score 705, existing emi 9500, loan 5.7 lakh, salaried, 6 years employed", {})
    assert r is not None
    if r.final_decision.level < r.symbolic_reasoning.rule_level:
        assert "advisory" in r.explanation.summary
    assert "raised the assessment to Low" not in r.explanation.summary
