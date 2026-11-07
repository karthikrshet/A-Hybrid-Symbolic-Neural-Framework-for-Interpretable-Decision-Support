"""Finance knowledge base - loan eligibility / credit-risk policy rules.

Modelled on typical Indian retail-lending policy (CIBIL score bands, FOIR /
debt-to-income limits, minimum income and employment criteria).
"""

from app.domains.base import cond, rule

LOW, MEDIUM, HIGH = 0, 1, 2

RULES = [
    rule(
        "FN-01", "Minimum credit score",
        "Credit score below 600 does not meet the minimum lending requirement.",
        "Credit history",
        [cond("credit_score", "lt", 600)],
        HIGH, "hard",
        "Improve the credit score (timely repayments, lower utilisation) before re-applying.",
        "Credit score requirement: Passed.",
    ),
    rule(
        "FN-02", "Fair credit band",
        "Credit score between 600 and 699 carries additional risk.",
        "Credit history",
        [cond("credit_score", "gte", 600), cond("credit_score", "lt", 700)],
        MEDIUM, "soft",
        "Consider a co-applicant or a smaller loan amount to offset the fair credit band.",
        "Credit score is in the good/excellent band.",
    ),
    rule(
        "FN-03", "Debt-to-income limit",
        "Total EMIs (existing + proposed) above 60% of monthly income.",
        "Affordability",
        [cond("dti_ratio", "gt", 0.60)],
        HIGH, "hard",
        "Reduce the requested amount, extend the tenure or close existing loans to lower DTI.",
        "Debt-to-income requirement: Passed.",
    ),
    rule(
        "FN-04", "Elevated debt-to-income",
        "Total EMIs between 40% and 60% of monthly income.",
        "Affordability",
        [cond("dti_ratio", "gt", 0.40), cond("dti_ratio", "lte", 0.60)],
        MEDIUM, "soft",
        "Debt burden is elevated - review repayment capacity carefully.",
        "Debt-to-income below 40%.",
    ),
    rule(
        "FN-05", "Minimum income",
        "Monthly income below ₹15,000.",
        "Income",
        [cond("monthly_income", "lt", 15000)],
        HIGH, "hard",
        "Income is below the minimum eligibility criterion.",
        "Income requirement: Passed.",
    ),
    rule(
        "FN-06", "No stable employment",
        "Applicant is currently unemployed.",
        "Employment",
        [cond("employment_type", "eq", "Unemployed")],
        HIGH, "hard",
        "Stable income source is required for credit approval.",
        "Employment requirement: Passed.",
    ),
    rule(
        "FN-07", "Repeated past defaults",
        "Two or more past loan defaults.",
        "Credit history",
        [cond("past_defaults", "gte", 2)],
        HIGH, "hard",
        "Multiple defaults on record - clear outstanding dues before applying.",
        "Fewer than two past defaults.",
    ),
    rule(
        "FN-08", "Past default on record",
        "Exactly one past loan default.",
        "Credit history",
        [cond("past_defaults", "eq", 1)],
        MEDIUM, "soft",
        "A past default exists - provide documentation of its resolution.",
        "No past defaults on record.",
    ),
    rule(
        "FN-09", "Short employment tenure",
        "Less than one year in current employment / business.",
        "Employment",
        [cond("years_employed", "lt", 1)],
        MEDIUM, "soft",
        "Short tenure - additional income proof may be requested.",
        "Employment tenure of one year or more.",
    ),
    rule(
        "FN-10", "High loan-to-income",
        "Requested loan exceeds 5× annual income.",
        "Affordability",
        [cond("loan_to_income", "gt", 5)],
        MEDIUM, "soft",
        "Loan amount is large relative to income - consider a lower principal.",
        "Loan amount within 5× annual income.",
    ),
]
