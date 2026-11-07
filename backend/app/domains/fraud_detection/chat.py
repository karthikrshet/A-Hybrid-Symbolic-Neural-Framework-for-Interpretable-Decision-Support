"""Conversational lexicon for the transaction fraud-detection domain."""

KEYWORDS = [
    "fraud", "fraudulent", "suspicious", "transaction", "transfer", "payment", "scam", "phishing", "card",
    "upi", "money laundering", "aml", "kyc", "hacked", "unauthorized", "unauthorised", "account takeover", "chargeback",
    "cyber", "security", "otp", "login attempts", "device",
]
ALIASES = {
    "amount": ["transaction amount", "amount", "transfer", "payment", "withdrawal", "purchase", "transferred", "transfer of", "payment of", "paid", "sent", "transaction of", "spent"],
    "avg_amount": ["average", "usually spends", "normally spends", "average transaction", "typical amount", "avg"],
    "hour_of_day": ["at hour", "hour", "time"],
    "transactions_24h": ["transactions in 24", "transactions today", "transactions in the last 24 hours", "transactions"],
    "distance_km": ["km away", "km from", "kilometers", "kilometres", "km", "distance"],
    "failed_attempts_1h": ["failed attempts", "failed login", "failed logins", "wrong otp", "failed otp", "wrong password"],
}
OPTION_ALIASES = {
    "international": {"Yes": ["international", "abroad", "overseas", "foreign", "cross-border", "outside india"], "No": ["domestic", "local"]},
    "new_device": {"Yes": ["new device", "unknown device", "unrecognised device", "unrecognized device", "new phone"], "No": ["usual device", "known device", "same device"]},
    "kyc_status": {"Pending": ["kyc pending", "pending kyc"], "Expired": ["kyc expired", "expired kyc"], "Verified": ["kyc verified", "verified kyc"]},
    "destination_risk": {"Blacklisted": ["blacklisted", "sanctioned", "blocked account"], "High": ["high-risk country", "high risk country", "high-risk destination", "high risk destination", "risky beneficiary"]},
}
PATTERNS: list[tuple[str, list[str]]] = [
    (r"\b(\d{1,2})(?::\d{2})?\s*(am|pm)\b", ["hour_ampm"]),
    (r"\bmidnight\b", ["hour_midnight"]),
]
KEY_FEATURES = ["amount", "avg_amount"]
EXAMPLES = [
    "Is this transaction suspicious? ₹85,000 transfer at 2 AM from a new device, abroad, customer's average is ₹4,000",
    "Payment of 2400 rupees, average 3000, domestic, usual device, KYC verified",
]
