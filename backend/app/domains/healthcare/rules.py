"""Healthcare knowledge base - cardiometabolic health-risk rules.

Thresholds follow widely published screening guidance (ACC/AHA blood-pressure
categories, ADA fasting-glucose cut-offs, WHO BMI classes).  They are used for
decision *support* only and are not a diagnosis.
"""

from app.domains.base import cond, rule

LOW, MODERATE, HIGH = 0, 1, 2

RULES = [
    rule(
        "HC-01", "Hypertensive crisis",
        "Systolic BP ≥ 180 or diastolic BP ≥ 120 mmHg indicates a hypertensive crisis.",
        "Blood pressure",
        [cond("systolic_bp", "gte", 180), cond("diastolic_bp", "gte", 120)],
        HIGH, "hard",
        "Blood pressure is in the crisis range - seek urgent medical evaluation.",
        "Blood pressure below crisis threshold.", logic="any",
    ),
    rule(
        "HC-02", "Stage 2 hypertension",
        "Systolic BP ≥ 140 or diastolic BP ≥ 90 mmHg.",
        "Blood pressure",
        [cond("systolic_bp", "gte", 140), cond("diastolic_bp", "gte", 90)],
        MODERATE, "soft",
        "Blood pressure threshold exceeded - schedule a blood-pressure review with a clinician.",
        "Blood pressure within stage-2 threshold.", logic="any",
    ),
    rule(
        "HC-03", "Diabetic-range fasting glucose",
        "Fasting plasma glucose ≥ 126 mg/dL is in the diabetic range.",
        "Glucose",
        [cond("glucose", "gte", 126)],
        MODERATE, "soft",
        "Glucose threshold exceeded - request an HbA1c / repeat fasting glucose test.",
        "Fasting glucose below diabetic threshold.",
    ),
    rule(
        "HC-04", "Severe hyperglycaemia",
        "Fasting glucose ≥ 250 mg/dL requires prompt attention.",
        "Glucose",
        [cond("glucose", "gte", 250)],
        HIGH, "hard",
        "Severely elevated glucose - seek prompt medical attention.",
        "No severe hyperglycaemia.",
    ),
    rule(
        "HC-05", "Obesity (class II or above)",
        "BMI ≥ 35 kg/m² is associated with substantially increased cardiometabolic risk.",
        "Body composition",
        [cond("bmi", "gte", 35)],
        MODERATE, "soft",
        "Discuss a structured weight-management plan with a healthcare professional.",
        "BMI below class-II obesity threshold.",
    ),
    rule(
        "HC-06", "High total cholesterol",
        "Total cholesterol ≥ 240 mg/dL is classified as high.",
        "Lipids",
        [cond("cholesterol", "gte", 240)],
        MODERATE, "soft",
        "Cholesterol is high - a lipid profile and dietary review are advisable.",
        "Total cholesterol below high threshold.",
    ),
    rule(
        "HC-07", "Multiple metabolic risk factors",
        "Three or more of: BP ≥ 140, glucose ≥ 126, BMI ≥ 30, cholesterol ≥ 240.",
        "Combined risk",
        [cond("metabolic_risk_count", "gte", 3)],
        HIGH, "hard",
        "Several risk factors co-exist - a comprehensive cardiometabolic assessment is recommended.",
        "Fewer than three metabolic risk factors present.",
    ),
    rule(
        "HC-08", "Resting tachycardia",
        "Resting heart rate above 110 bpm.",
        "Cardiac",
        [cond("heart_rate", "gt", 110)],
        MODERATE, "soft",
        "Elevated resting heart rate - consider an ECG and clinical review.",
        "Resting heart rate within normal range.",
    ),
    rule(
        "HC-09", "Smoker over 50 with raised BP",
        "Current smoker, age ≥ 50 and systolic BP ≥ 130 mmHg.",
        "Lifestyle",
        [cond("smoking", "eq", "Current"), cond("age", "gte", 50), cond("systolic_bp", "gte", 130)],
        MODERATE, "soft",
        "Smoking cessation support is strongly recommended.",
        "Smoking/age/BP combination not present.",
    ),
]
