from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class GoalBase(BaseModel):
    name: str
    target_amount: float
    current_amount: Optional[float] = 0.0
    target_date: Optional[date] = None
    category: Optional[str] = "General Savings"


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    target_date: Optional[date] = None
    category: Optional[str] = None
    status: Optional[str] = None


class GoalResponse(GoalBase):
    id: int
    user_id: int
    status: str
    progress_percentage: float
    remaining_amount: float
    monthly_savings_needed: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
