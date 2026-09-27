from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TransactionBase(BaseModel):
    date: date
    description: str
    merchant: Optional[str] = None
    amount: float
    category: Optional[str] = "Uncategorized"
    is_recurring: Optional[bool] = False


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    description: Optional[str] = None
    merchant: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    is_recurring: Optional[bool] = None


class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    is_anomaly: bool
    anomaly_score: Optional[float] = None
    anomaly_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionBatchResponse(BaseModel):
    total_parsed: int
    total_saved: int
    anomalies_detected: int
    message: str
