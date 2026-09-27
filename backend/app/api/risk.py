from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.analytics import RiskScoreResponse
from app.services.risk_engine import RiskEngine

router = APIRouter(prefix="/risk", tags=["Risk Assessment"])


@router.get("/score", response_model=RiskScoreResponse)
def get_risk_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Calculate financial health / risk score (0-100), liquidity runway buffer in months,
    and weekly spending volatility coefficient.
    """
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.date.asc())
        .all()
    )

    tx_dicts = [
        {
            "date": t.date,
            "amount": t.amount,
            "category": t.category,
            "description": t.description,
        }
        for t in transactions
    ]

    risk_profile = RiskEngine.calculate_risk_profile(tx_dicts)
    return risk_profile
