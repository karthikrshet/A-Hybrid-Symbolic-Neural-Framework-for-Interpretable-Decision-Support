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
