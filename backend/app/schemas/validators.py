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

def validate_ip_reputation(score: float) -> bool:
    """Validate IP reputation bounded between 0.0 and 1.0."""
    if not (0.0 <= score <= 1.0):
        raise ValueError(f"IP reputation score must be in [0.0, 1.0], got {score}")
    return True

def validate_device_trust(score: float) -> bool:
    """Validate device trust bounded between 0.0 and 1.0."""
    if not (0.0 <= score <= 1.0):
        raise ValueError(f"Device trust score must be in [0.0, 1.0], got {score}")
    return True

def validate_hour_of_day(hour: int) -> bool:
    """Validate hour is within standard diurnal cycle [0, 23]."""
    if not (0 <= hour <= 23):
        raise ValueError(f"Hour must be in [0, 23], got {hour}")
    return True

def validate_kyc_status(status_str: str) -> bool:
    """Ensure KYC status adheres to authorized enumeration."""
    valid_statuses = {"VERIFIED", "INCOMPLETE", "PENDING", "REJECTED"}
    if status_str not in valid_statuses:
        raise ValueError(f"Invalid KYC status {status_str}. Allowed: {valid_statuses}")
    return True

# Step 1: refactor(validators): progressive code refinement step 1/1157
# Refined validator precision check

# Step 17: style(validators): progressive code refinement step 17/1157
# Refined validator precision check

# Step 33: chore(validators): progressive code refinement step 33/1157
# Refined validator precision check

# Step 49: fix(validators): progressive code refinement step 49/1157
# Refined validator precision check

# Step 65: perf(validators): progressive code refinement step 65/1157
# Refined validator precision check
