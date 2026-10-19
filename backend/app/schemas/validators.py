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

def validate_velocity_change(ratio: float) -> bool:
    """Ensure velocity ratio is non-negative and finite."""
    if ratio < 0 or math.isnan(ratio):
        raise ValueError("Velocity change ratio cannot be negative")
    return True

def validate_geographic_distance(dist_km: float) -> bool:
    """Ensure geographic distance is physically valid on Earth surface (<= 20,015 km)."""
    if dist_km < 0 or dist_km > 20015.0:
        raise ValueError("Geographic distance must be between 0 and 20,015 km")
    return True
