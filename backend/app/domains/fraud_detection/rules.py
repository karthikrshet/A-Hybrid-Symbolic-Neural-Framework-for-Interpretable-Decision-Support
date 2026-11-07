"""Cyber-security / fraud knowledge base - transaction fraud-detection rules (AML/KYC style)."""

from app.domains.base import cond, rule

LEGIT, SUSPICIOUS, FRAUD = 0, 1, 2

RULES = [
    rule(
        "FR-01", "Sanctioned / blacklisted destination",
        "Funds are being sent to a sanctioned or blacklisted beneficiary.",
        "Compliance",
        [cond("destination_risk", "eq", "Blacklisted")],
        FRAUD, "hard",
        "Block the transaction and file a suspicious-transaction report (STR).",
        "Destination is not blacklisted.",
    ),
    rule(
        "FR-02", "Brute-force authentication",
        "Five or more failed login / OTP attempts in the last hour.",
        "Authentication",
        [cond("failed_attempts_1h", "gte", 5)],
        FRAUD, "hard",
        "Lock the account temporarily and require step-up verification.",
        "Authentication attempts normal.",
    ),
    rule(
        "FR-03", "Large amount from new device",
        "Amount ≥ 10× the customer's average on an unrecognised device.",
        "Behaviour",
        [cond("amount_ratio", "gte", 10), cond("new_device", "eq", "Yes")],
        FRAUD, "hard",
        "Hold the transaction and confirm with the customer through a registered channel.",
        "No large transfer from an unrecognised device.",
    ),
    rule(
        "FR-04", "Unusual amount",
        "Amount at least 5× the customer's average transaction.",
        "Behaviour",
        [cond("amount_ratio", "gte", 5)],
        SUSPICIOUS, "soft",
        "Amount deviates strongly from history - request customer confirmation.",
        "Amount consistent with customer history.",
    ),
    rule(
        "FR-05", "High transaction velocity",
        "Ten or more transactions in the last 24 hours.",
        "Velocity",
        [cond("transactions_24h", "gte", 10)],
        SUSPICIOUS, "soft",
        "Velocity spike - review recent transactions for card-testing patterns.",
        "Transaction velocity normal.",
    ),
    rule(
        "FR-06", "Impossible travel / distant location",
        "Transaction location more than 1,000 km from the customer's usual location.",
        "Location",
        [cond("distance_km", "gt", 1000)],
        SUSPICIOUS, "soft",
        "Verify location with the customer (travel notice / geo-check).",
        "Location consistent with usual activity.",
    ),
    rule(
        "FR-07", "Odd-hour international transfer",
        "International transaction between midnight and 5 AM.",
        "Behaviour",
        [cond("hour_of_day", "lt", 5), cond("international", "eq", "Yes")],
        SUSPICIOUS, "soft",
        "Odd-hour cross-border payment - apply additional authentication.",
        "No odd-hour international activity.",
    ),
    rule(
        "FR-08", "Incomplete KYC",
        "Customer KYC is pending or expired.",
        "Compliance",
        [cond("kyc_status", "in", ["Pending", "Expired"])],
        SUSPICIOUS, "soft",
        "Complete KYC re-verification before allowing high-value transactions.",
        "KYC verified.",
    ),
    rule(
        "FR-09", "High-risk destination",
        "Beneficiary country/account flagged as high risk.",
        "Compliance",
        [cond("destination_risk", "eq", "High")],
        SUSPICIOUS, "soft",
        "Apply enhanced due diligence on the beneficiary.",
        "Destination risk acceptable.",
    ),
]
