from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.recurring import RecurringTransaction
from app.schemas.analytics import ForecastResponse
from app.services.forecaster import CashFlowForecaster

router = APIRouter(prefix="/forecasting", tags=["Forecasting"])


@router.get("/", response_model=ForecastResponse)
def get_cash_flow_forecast(
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Project future account balance and cash flow for the next 30 to 90 days.
    Uses historical daily moving averages and detected recurring obligations.
    """
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.date.asc())
        .all()
    )

    recurring = (
        db.query(RecurringTransaction)
        .filter(RecurringTransaction.user_id == current_user.id, RecurringTransaction.is_active == True)
        .all()
    )

    tx_dicts = [
        {
            "date": t.date,
            "amount": t.amount,
            "description": t.description,
            "category": t.category,
        }
        for t in transactions
    ]

    rec_dicts = [
        {
            "merchant": r.merchant,
            "average_amount": r.average_amount,
            "interval_days": r.interval_days,
            "last_date": r.last_date,
        }
        for r in recurring
    ]

    forecast_data = CashFlowForecaster.forecast(
        transactions=tx_dicts,
        recurring=rec_dicts,
        days_ahead=days
    )

    return forecast_data
