from datetime import date, timedelta
from app.services.recurring_detector import RecurringDetector


def test_detect_monthly_recurring_and_price_spike():
    """Verify recurring detector identifies monthly cadence and calculates price jump percentage."""
    base_date = date(2026, 1, 5)
    transactions = [
        {"date": base_date, "merchant": "Netflix", "amount": -15.99, "category": "Entertainment", "description": "Netflix"},
        {"date": base_date + timedelta(days=30), "merchant": "Netflix", "amount": -15.99, "category": "Entertainment", "description": "Netflix"},
        {"date": base_date + timedelta(days=61), "merchant": "Netflix", "amount": -15.99, "category": "Entertainment", "description": "Netflix"},
        {"date": base_date + timedelta(days=91), "merchant": "Netflix", "amount": -19.99, "category": "Entertainment", "description": "Netflix"},
    ]

    recurring_list = RecurringDetector.detect_recurring(transactions)
    assert len(recurring_list) == 1

    netflix = recurring_list[0]
    assert netflix["merchant"] == "Netflix"
    assert netflix["cadence"] == "monthly"
    assert netflix["occurrence_count"] == 4
    # Jump from $15.99 to $19.99 is 25%
    assert netflix["price_change_pct"] > 20.0
