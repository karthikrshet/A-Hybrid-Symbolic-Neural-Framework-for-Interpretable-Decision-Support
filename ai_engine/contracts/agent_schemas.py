from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class WorkflowState(str, Enum):
    RECEIVED = "RECEIVED"
    CLASSIFIED = "CLASSIFIED"
    PLANNED = "PLANNED"
    EXECUTING = "EXECUTING"
    FUSING = "FUSING"
    VALIDATING = "VALIDATING"
    EXPLAINING = "EXPLAINING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"

class AgentType(str, Enum):
    COORDINATOR = "COORDINATOR"
    NEURAL = "NEURAL"
    SYMBOLIC = "SYMBOLIC"
    VALIDATION = "VALIDATION"
    EXPLANATION = "EXPLANATION"

class DecisionOutcome(str, Enum):
    APPROVE = "APPROVE"
    FLAG_MONITOR = "FLAG_MONITOR"
    FLAG_SUSPICIOUS = "FLAG_SUSPICIOUS"
    REJECT = "REJECT"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"

class FeatureAttribution(BaseModel):
    feature_name: str
    feature_value: Any
    attribution_score: float
    importance_rank: int
    direction: str = Field(description="'increases_risk' or 'decreases_risk'")

class TriggeredRuleInfo(BaseModel):
    rule_id: str
    rule_name: str
    severity: str
    category: str
    reason: str
    condition_matched: str
    override_applied: bool = False
