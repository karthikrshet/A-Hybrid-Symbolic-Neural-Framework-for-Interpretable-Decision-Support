import os
from typing import List
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Neuro-Symbolic Multi-Agent Decision Support Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "neurosymbolic-super-secret-key-2026-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./neurosymbolic.db")
    CORS_ORIGINS: List[str] = ["*"]
    MODEL_PATH: str = os.path.join(os.path.dirname(__file__), "../../../ml/artifacts/fraud_risk_model.joblib")
    RULES_PATH: str = os.path.join(os.path.dirname(__file__), "../../../knowledge_base/rules/financial_risk_rules.json")

settings = Settings()
