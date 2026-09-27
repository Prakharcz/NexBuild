from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class RecommendationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    category: str
    severity: str
    estimated_monthly_savings: float
    ai_explanation: Optional[str] = None
    status: str
    user_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationActionRequest(BaseModel):
    action: str  # "ACTED_ON", "APPROVED", "DISMISSED"
    user_notes: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    recommendation_id: Optional[int] = None
    recommendation_title: Optional[str] = None
    action: str
    decision_reason: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
