from datetime import date
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class CategoryBreakdownItem(BaseModel):
    category: str
    total_amount: float
    percentage: float
    transaction_count: int


class MonthlyTrendItem(BaseModel):
    month: str  # YYYY-MM
    income: float
    expenses: float
    net_savings: float
    savings_rate: float


class SpendingSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_cash_flow: float
    savings_rate: float
    total_transactions: int
    current_estimated_balance: float
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None


class ForecastPoint(BaseModel):
    date: str
    predicted_balance: float
    projected_net_flow: float
    lower_bound: float
    upper_bound: float


class ForecastResponse(BaseModel):
    forecast_days: int
    current_balance: float
    projected_end_balance: float
    average_daily_burn: float
    confidence_level: float
    daily_projections: List[ForecastPoint]


class RiskFactor(BaseModel):
    name: str
    score: float
    status: str
    description: str


class RiskScoreResponse(BaseModel):
    score: int  # 0 to 100 (higher = healthier / lower risk)
    risk_level: str  # "Low Risk", "Moderate Risk", "Elevated Risk", "High Risk"
    liquidity_runway_months: float
    spending_volatility_cv: float
    savings_rate_pct: float
    monthly_burn_rate: float
    factors: List[RiskFactor]
    summary_message: str
