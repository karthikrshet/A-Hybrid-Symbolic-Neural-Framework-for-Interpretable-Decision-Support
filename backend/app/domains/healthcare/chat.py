"""Conversational lexicon for the healthcare domain (used by the chat Coordinator)."""

KEYWORDS = [
    "health", "patient", "blood pressure", "bp", "glucose", "sugar", "diabetes", "diabetic", "bmi", "cholesterol",
    "heart", "cardiac", "hypertension", "medical", "doctor", "pulse", "obese", "obesity", "smoker", "risk of disease",
]
ALIASES = {
    "age": ["age", "aged", "years old", "year old", "year-old", "years-old", "yrs old", "yr old", "y/o"],
    "systolic_bp": ["systolic", "systolic bp", "systolic blood pressure"],
    "diastolic_bp": ["diastolic", "diastolic bp", "diastolic blood pressure"],
    "heart_rate": ["heart rate", "pulse", "hr", "bpm", "resting heart rate"],
    "glucose": ["glucose", "sugar", "blood sugar", "fasting glucose", "fbs", "glucose level"],
    "cholesterol": ["cholesterol", "total cholesterol", "chol"],
    "bmi": ["bmi", "body mass index"],
}
OPTION_ALIASES = {
    "gender": {"Female": ["female", "woman", "lady", "she", "her"], "Male": ["male", "man", "he", "his", "gentleman"]},
    "smoking": {"Current": ["smoker", "smokes", "smoking", "cigarette"], "Former": ["former smoker", "quit smoking", "ex-smoker", "used to smoke"], "Never": ["non-smoker", "never smoked", "doesn't smoke", "does not smoke", "no smoking"]},
    "physical_activity": {"Low": ["sedentary", "inactive", "no exercise", "low activity"], "High": ["very active", "exercises daily", "athlete", "high activity", "active lifestyle"], "Moderate": ["moderately active", "moderate activity", "walks regularly"]},
    "family_history": {"Yes": ["family history", "father had", "mother had", "runs in the family", "parents have"], "No": ["no family history"]},
}
PATTERNS = [
    (r"(?<![\d.])(\d{2,3})\s*(?:/|over)\s*(\d{2,3})(?![\d.])", ["systolic_bp", "diastolic_bp"]),
    (r"(?:mom|mum|mother|dad|father|patient|wife|husband|grand(?:ma|pa|mother|father)|he|she|i am|i'm|im)\s+(?:is\s+)?(\d{1,3})(?:\s*(?:years?|yrs?|y/?o))?\b(?!\s*(?:/|over|%|mg|mmhg|bpm|kg))", ["age"]),
]
KEY_FEATURES = ["systolic_bp", "glucose", "bmi", "age"]
EXAMPLES = [
    "Assess health risk: 45-year-old male, BP 145/95, glucose 160, BMI 29",
    "Patient aged 60, blood pressure 185/120, sugar 110 - is this risky?",
]
