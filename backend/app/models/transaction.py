from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Transaction(Base):
    """
    Financial transaction model storing parsed banking entries, category, and anomaly markers.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    description = Column(String(500), nullable=False)
    merchant = Column(String(255), nullable=True, index=True)
    # Amount convention: positive = income / inflow, negative = expense / outflow
    amount = Column(Float, nullable=False)
    category = Column(String(100), default="Uncategorized", nullable=False, index=True)
    is_recurring = Column(Boolean, default=False, nullable=False)
    
    # Anomaly detection attributes
    is_anomaly = Column(Boolean, default=False, nullable=False)
    anomaly_score = Column(Float, nullable=True)
    anomaly_reason = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationship to user
    user = relationship("User", back_populates="transactions")
