"""Financial transaction domain validators and invariant checks."""

import math
from typing import Any, Dict

def validate_transaction_amount(amount: float) -> bool:
    """Ensure amount is strictly positive and within allowable single-transaction limits."""
    if amount <= 0 or math.isnan(amount) or math.isinf(amount):
        raise ValueError("Transaction amount must be a positive finite number")
    if amount > 10_000_000:
        raise ValueError("Single transaction exceeds statutory absolute limit of $10,000,000")
    return True
