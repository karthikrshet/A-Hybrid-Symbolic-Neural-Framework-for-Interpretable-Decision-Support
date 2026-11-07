"""Conversational lexicon for the finance (loan eligibility) domain."""

KEYWORDS = [
    "loan", "credit", "credit score", "cibil", "emi", "income", "salary", "eligible", "eligibility", "borrow",
    "lending", "mortgage", "debt", "tenure", "bank loan", "personal loan", "home loan", "repay", "applicant",
]
ALIASES = {
    "monthly_income": ["monthly income", "income", "salary", "earns", "earn", "earning", "i make", "take home", "monthly salary", "income of"],
    "credit_score": ["credit score", "cibil", "cibil score", "score"],
    "existing_emi": ["existing emi", "existing loan", "current emi", "emi", "existing loans", "other emi"],
    "loan_amount": ["loan amount", "loan of", "loan", "borrow", "requested", "amount requested", "wants"],
    "loan_tenure_months": ["tenure", "month tenure", "loan term"],
    "years_employed": ["years employed", "years of experience", "experience", "working for", "years in job", "employed for"],
    "past_defaults": ["defaults", "default", "missed payments"],
    "age": ["age", "aged", "years old"],
}
OPTION_ALIASES = {
    "employment_type": {
        "Unemployed": ["unemployed", "no job", "jobless", "not working"],
        "Self-Employed": ["self-employed", "self employed", "business", "freelancer", "own business", "entrepreneur"],
        "Salaried": ["salaried", "employee", "works at", "job at", "private job", "government job", "employed"],
    },
}
PATTERNS: list[tuple[str, list[str]]] = [
    (r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s*(?:tenure|loan term|term)", ["loan_tenure_years"]),
    (r"(?:for|over|tenure of)\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b", ["loan_tenure_years"]),
    (r"(?:for|over|tenure of)\s+(\d+)\s*months?\b", ["loan_tenure_months"]),
    (r"no\s+(?:past\s+)?defaults?", ["past_defaults_zero"]),
]
KEY_FEATURES = ["monthly_income", "credit_score", "loan_amount"]
EXAMPLES = [
    "Check loan eligibility: income ₹60,000/month, credit score 720, existing EMI ₹10,000, loan ₹5 lakh, salaried",
    "Self-employed, earns 45k, CIBIL 640, wants a 9 lakh loan for 5 years",
]
