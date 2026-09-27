from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.recurring import RecurringTransaction
from app.models.recommendation import Recommendation
from app.models.audit_log import AuditLog
from app.schemas.recommendation import (
    RecommendationResponse,
    RecommendationActionRequest,
    AuditLogResponse,
)
from app.services.risk_engine import RiskEngine
from app.services.llm_advisor import llm_advisor

router = APIRouter(prefix="/recommendations", tags=["Recommendations & Audit"])


@router.get("/", response_model=List[RecommendationResponse])
def get_recommendations(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List recommendation cards for user, optionally filtered by status (PENDING, APPROVED, ACTED_ON, DISMISSED).
    """
    query = db.query(Recommendation).filter(Recommendation.user_id == current_user.id)
    if status_filter:
        query = query.filter(Recommendation.status == status_filter.upper())
    return query.order_by(Recommendation.created_at.desc()).all()


@router.post("/generate", response_model=List[RecommendationResponse])
def generate_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Evaluate user's transactions and recurring rules to generate actionable,
    rule-based recommendations enriched by LLM explanations.
    """
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.date.asc())
        .all()
    )

    recurring = (
        db.query(RecurringTransaction)
        .filter(RecurringTransaction.user_id == current_user.id)
        .all()
    )

    tx_dicts = [
        {
            "date": t.date,
            "merchant": t.merchant or t.description,
            "amount": t.amount,
            "category": t.category,
            "description": t.description,
            "is_anomaly": t.is_anomaly,
            "anomaly_reason": t.anomaly_reason,
        }
        for t in transactions
    ]

    new_recommendations = []

    # 1. Rule: Recurring price hike detection (e.g. Netflix increased 20%)
    # Compare earlier amounts vs recent amounts for recurring merchants
    for r in recurring:
        matching_txs = [
            t for t in tx_dicts
            if (t.get("merchant") and r.merchant.lower() in t["merchant"].lower())
        ]
        if len(matching_txs) >= 3:
            amounts = [abs(t["amount"]) for t in matching_txs]
            earlier_avg = sum(amounts[:-1]) / len(amounts[:-1])
            latest = amounts[-1]
            if earlier_avg > 0:
                pct_increase = ((latest - earlier_avg) / earlier_avg) * 100.0
                if pct_increase >= 15.0:
                    title = f"{r.merchant} price increased by {pct_increase:.0f}%"
                    existing = (
                        db.query(Recommendation)
                        .filter(Recommendation.user_id == current_user.id, Recommendation.title == title)
                        .first()
                    )
                    if not existing:
                        explanation = llm_advisor.explain_recurring_price_hike(
                            r.merchant, earlier_avg, latest, pct_increase
                        )
                        diff = latest - earlier_avg
                        rec = Recommendation(
                            user_id=current_user.id,
                            title=title,
                            description=f"Your subscription charge for {r.merchant} rose from ${earlier_avg:.2f} to ${latest:.2f}.",
                            category="recurring_spike",
                            severity="medium",
                            estimated_monthly_savings=round(diff, 2),
                            ai_explanation=explanation,
                            status="PENDING",
                        )
                        db.add(rec)
                        new_recommendations.append(rec)

    # 2. Rule: Liquidity Runway warning
    if transactions:
        risk_profile = RiskEngine.calculate_risk_profile(tx_dicts)
        runway = risk_profile["liquidity_runway_months"]
        burn = risk_profile["monthly_burn_rate"]

        if runway < 2.0 and burn > 0:
            title = f"Low Emergency Liquidity Buffer ({runway:.1f} months runway)"
            existing = (
                db.query(Recommendation)
                .filter(Recommendation.user_id == current_user.id, Recommendation.title == title)
                .first()
            )
            if not existing:
                explanation = llm_advisor.explain_liquidity_alert(runway, burn)
                rec = Recommendation(
                    user_id=current_user.id,
                    title=title,
                    description=f"Your current cash buffer can only support {runway:.1f} months of expenses. Aim to build a 3-month cushion.",
                    category="liquidity_buffer",
                    severity="high",
                    estimated_monthly_savings=round(burn * 0.15, 2),
                    ai_explanation=explanation,
                    status="PENDING",
                )
                db.add(rec)
                new_recommendations.append(rec)

    # 3. Rule: Category Overspending
    expenses = [abs(t["amount"]) for t in tx_dicts if t["amount"] < 0]
    total_expenses = sum(expenses)
    if total_expenses > 500:
        dining_spend = sum(abs(t["amount"]) for t in tx_dicts if t["amount"] < 0 and t["category"] == "Food & Dining")
        dining_pct = (dining_spend / total_expenses) * 100.0
        if dining_pct > 25.0:
            title = f"Food & Dining represents {dining_pct:.0f}% of total outflow"
            existing = (
                db.query(Recommendation)
                .filter(Recommendation.user_id == current_user.id, Recommendation.title == title)
                .first()
            )
            if not existing:
                explanation = llm_advisor.explain_high_category_spend("Food & Dining", dining_spend, dining_pct)
                rec = Recommendation(
                    user_id=current_user.id,
                    title=title,
                    description=f"You spent ${dining_spend:.2f} on dining out. Reining in takeouts could save over $150/mo.",
                    category="high_spend",
                    severity="medium",
                    estimated_monthly_savings=150.0,
                    ai_explanation=explanation,
                    status="PENDING",
                )
                db.add(rec)
                new_recommendations.append(rec)

    # 4. Rule: Flagged Severe Anomalies
    anomalies = [t for t in tx_dicts if t.get("is_anomaly") and abs(t["amount"]) > 500]
    for anom in anomalies[:2]:
        title = f"Review Unusual Spike: {anom['description']} (${abs(anom['amount']):.2f})"
        existing = (
            db.query(Recommendation)
            .filter(Recommendation.user_id == current_user.id, Recommendation.title == title)
            .first()
        )
        if not existing:
            explanation = llm_advisor.explain_anomaly_spike(
                anom["description"], anom["amount"], anom.get("anomaly_reason", "Outlier")
            )
            rec = Recommendation(
                user_id=current_user.id,
                title=title,
                description=f"High outlier charge detected on {anom['date']}: ${abs(anom['amount']):.2f}.",
                category="anomaly_review",
                severity="high",
                estimated_monthly_savings=0.0,
                ai_explanation=explanation,
                status="PENDING",
            )
            db.add(rec)
            new_recommendations.append(rec)

    db.commit()

    all_recs = db.query(Recommendation).filter(Recommendation.user_id == current_user.id).order_by(Recommendation.created_at.desc()).all()
    return all_recs


@router.post("/{recommendation_id}/action", response_model=RecommendationResponse)
def act_on_recommendation(
    recommendation_id: int,
    action_req: RecommendationActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Human-Approval Workflow:
    Explicit user confirmation is strictly required to transition a recommendation
    from PENDING to ACTED_ON, APPROVED, or DISMISSED.
    Every decision is permanently recorded in the immutable AuditLog.
    """
    rec = (
        db.query(Recommendation)
        .filter(Recommendation.id == recommendation_id, Recommendation.user_id == current_user.id)
        .first()
    )
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found."
        )

    valid_actions = ["ACTED_ON", "APPROVED", "DISMISSED"]
    action_norm = action_req.action.upper()
    if action_norm not in valid_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action '{action_req.action}'. Must be one of: {valid_actions}"
        )

    # Update recommendation status
    rec.status = action_norm
    rec.user_notes = action_req.user_notes

    # Create immutable audit record
    audit_entry = AuditLog(
        user_id=current_user.id,
        recommendation_id=rec.id,
        action=action_norm,
        recommendation_title=rec.title,
        decision_reason=action_req.user_notes or f"User confirmed {action_norm} via human-approval workflow.",
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(rec)

    return rec


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve chronological audit trail of all human-in-the-loop decisions.
    """
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )
    return logs
