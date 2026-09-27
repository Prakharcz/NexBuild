from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class RecurringTransaction(Base):
    """
    Identified recurring subscriptions or predictable income streams.
    """
    __tablename__ = "recurring_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    merchant = Column(String(255), nullable=False)
    category = Column(String(100), default="Uncategorized", nullable=False)
    average_amount = Column(Float, nullable=False)
    cadence = Column(String(50), nullable=False)  # weekly, biweekly, monthly, quarterly, yearly
    interval_days = Column(Integer, nullable=False)
    occurrence_count = Column(Integer, default=2, nullable=False)
    last_date = Column(Date, nullable=False)
    next_expected_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to user
    user = relationship("User", back_populates="recurring_patterns")
