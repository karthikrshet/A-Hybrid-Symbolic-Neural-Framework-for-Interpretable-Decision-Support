from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class RuleSeverity(str, Enum):
    CRITICAL_HARD_OVERRIDE = "CRITICAL_HARD_OVERRIDE"
    HIGH_RISK_SOFT = "HIGH_RISK_SOFT"
    MEDIUM_RISK_SOFT = "MEDIUM_RISK_SOFT"
    LOW_RISK_CLEARANCE = "LOW_RISK_CLEARANCE"

class SymbolicRule(BaseModel):
    rule_id: str
    name: str
    description: str
    category: str
    severity: RuleSeverity
    is_hard_override: bool
    conditions: Dict[str, Any] = Field(description="Dictionary of operator conditions (e.g. gt, lt, eq, in)")
    action: str = Field(description="Resulting classification flag")
    regulatory_reference: Optional[str] = None
