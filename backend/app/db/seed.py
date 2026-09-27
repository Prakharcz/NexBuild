import os
from pathlib import Path
from datetime import date
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.user import User
from app.models.transaction import Transaction
from app.models.goal import Goal
from app.models.recurring import RecurringTransaction
from app.models.recommendation import Recommendation
from app.services.csv_parser import CSVParser
from app.services.anomaly_detector import AnomalyDetector
from app.services.recurring_detector import RecurringDetector
from app.services.llm_advisor import llm_advisor


def seed_demo_data(db: Session) -> User:
    """
    Populates database with a realistic demo user, 6 months of banking records,
    detected recurring subscriptions, anomalies, savings goals, and AI recommendations.
    """
    demo_email = "demo@example.com"
    existing_user = db.query(User).filter(User.email == demo_email).first()
    if existing_user:
        return existing_user

    print("--- Seeding demo account and realistic financial history ---")

    # 1. Create demo user
    user = User(
        email=demo_email,
        hashed_password=get_password_hash("password123"),
        full_name="Alex Morgan",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 2. Locate sample CSV file
    possible_paths = [
        Path("/app/sample_data/transactions_sample.csv"),
        Path("sample_data/transactions_sample.csv"),
        Path("../sample_data/transactions_sample.csv"),
        Path(__file__).resolve().parent.parent.parent.parent / "sample_data" / "transactions_sample.csv",
    ]

    csv_path = None
    for p in possible_paths:
        if p.exists():
            csv_path = p
            break

    if csv_path:
        with open(csv_path, "rb") as f:
            content = f.read()
        raw_txs = CSVParser.parse_csv_content(content)
        annotated_txs = AnomalyDetector.detect_anomalies(raw_txs)

        for item in annotated_txs:
            tx = Transaction(
                user_id=user.id,
                date=item["date"],
                description=item["description"],
                merchant=item.get("merchant"),
                amount=item["amount"],
                category=item.get("category", "Uncategorized"),
                is_anomaly=item.get("is_anomaly", False),
                anomaly_score=item.get("anomaly_score"),
                anomaly_reason=item.get("anomaly_reason"),
            )
            db.add(tx)
        db.commit()

        # Run recurring detection
        tx_dicts = [
            {
                "date": item["date"],
                "merchant": item.get("merchant") or item["description"],
                "amount": item["amount"],
                "category": item.get("category", "Uncategorized"),
                "description": item["description"],
            }
            for item in annotated_txs
        ]
        recurring_list = RecurringDetector.detect_recurring(tx_dicts)
        for rec in recurring_list:
            db.add(
                RecurringTransaction(
                    user_id=user.id,
                    merchant=rec["merchant"],
                    category=rec["category"],
                    average_amount=rec["average_amount"],
                    cadence=rec["cadence"],
                    interval_days=rec["interval_days"],
                    occurrence_count=rec["occurrence_count"],
                    last_date=rec["last_date"],
                    next_expected_date=rec["next_expected_date"],
                    is_active=True,
                )
            )
        db.commit()

    # 3. Create realistic savings goals
    emergency_goal = Goal(
        user_id=user.id,
        name="Emergency Cash Reserve ($10k)",
        target_amount=10000.0,
        current_amount=4850.0,
        target_date=date(2026, 12, 31),
        category="Emergency Fund",
        status="in_progress",
    )
    vacation_goal = Goal(
        user_id=user.id,
        name="Autumn Travel Fund",
        target_amount=2500.0,
        current_amount=1400.0,
        target_date=date(2026, 11, 15),
        category="Travel",
        status="in_progress",
    )
    db.add_all([emergency_goal, vacation_goal])
    db.commit()

    # 4. Generate initial recommendation cards
    explanation_netflix = llm_advisor.explain_recurring_price_hike("Netflix", 15.99, 19.99, 25.0)
    rec1 = Recommendation(
        user_id=user.id,
        title="Netflix price increased by 25%",
        description="Your monthly subscription fee for Netflix increased from $15.99 to $19.99 in June.",
        category="recurring_spike",
        severity="medium",
        estimated_monthly_savings=4.0,
        ai_explanation=explanation_netflix,
        status="PENDING",
    )

    rec2 = Recommendation(
        user_id=user.id,
        title="Optimize Dining Out Budget",
        description="Food & Dining expenditures account for ~22% of monthly spending. Trimming 2 meals per month saves $120.",
        category="high_spend",
        severity="low",
        estimated_monthly_savings=120.0,
        ai_explanation="[AI Advisor] Restricting food delivery services like DoorDash/UberEats to weekends can generate an immediate $1,440 annual boost toward your Emergency Fund.",
        status="PENDING",
    )

    db.add_all([rec1, rec2])
    db.commit()

    print(f"--- Demo data successfully loaded for {demo_email} (password: password123) ---")
    return user


if __name__ == "__main__":
    from app.core.database import SessionLocal, Base, engine
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_demo_data(session)
