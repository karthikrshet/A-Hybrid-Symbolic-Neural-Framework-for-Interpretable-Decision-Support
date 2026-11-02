from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = "Analyst"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TransactionInput(BaseModel):
    transaction_amount: float = Field(..., gt=0, description="Amount in USD/INR")
    transaction_frequency_24h: int = Field(default=1, ge=0)
    velocity_change_ratio: float = Field(default=1.0, ge=0.0)
    location_distance_km: float = Field(default=5.0, ge=0.0)
    hour_of_day: int = Field(default=14, ge=0, le=23)
    is_weekend: bool = False
    is_sanctioned_destination: bool = False
    kyc_status: str = Field(default="VERIFIED", description="'VERIFIED', 'INCOMPLETE', 'PENDING'")
    foreign_exchange_risk: float = Field(default=0.1, ge=0.0, le=1.0)
    ip_reputation_score: float = Field(default=0.95, ge=0.0, le=1.0)
    device_trust_score: float = Field(default=0.90, ge=0.0, le=1.0)
    user_failed_attempts_1h: int = Field(default=0, ge=0)
    past_chargeback_count: int = Field(default=0, ge=0)
    channel_type: str = Field(default="MOBILE", description="'WEB', 'MOBILE', 'ATM', 'API'")

class DecisionResponse(BaseModel):
    decision_id: str
    correlation_id: str
    final_decision: str
    confidence_score: float
    requires_human_review: bool
    neural_analysis: Dict[str, Any]
    symbolic_analysis: Dict[str, Any]
    validation_status: str
    explanation: Dict[str, Any]
    execution_trace: List[Dict[str, Any]]
    latency_ms: float

class ChatMessageRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    structured_context: Optional[Dict[str, Any]] = None
    model: Optional[str] = "neurosymbolic-multiagent"
    api_key: Optional[str] = None

class ChatMessageResponse(BaseModel):
    conversation_id: str
    reply: str
    workflow_state: str
    decision: Optional[Dict[str, Any]] = None
    agent_traces: List[Dict[str, Any]] = Field(default_factory=list)
