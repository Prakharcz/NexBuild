from datetime import date, timedelta
from app.services.anomaly_detector import AnomalyDetector


def test_detect_statistical_outlier():
    """Verify an extreme spending spike is flagged by IQR/Z-score."""
    base_date = date(2026, 6, 1)
    # Typical grocery transactions around $40 - $70
    transactions = [
        {"date": base_date + timedelta(days=i), "amount": -50.0, "category": "Groceries", "description": "Trader Joe's"}
        for i in range(15)
    ]
    # Add an extreme outlier expense
    transactions.append({
        "date": base_date + timedelta(days=16),
        "amount": -1450.0,
        "category": "Housing",
        "description": "Emergency Pipe Burst Repair"
    })

    annotated = AnomalyDetector.detect_anomalies(transactions)

    # Normal transactions should not be flagged
    assert annotated[0]["is_anomaly"] is False

    # Outlier should be flagged
    outlier = [t for t in annotated if t["amount"] == -1450.0][0]
    assert outlier["is_anomaly"] is True
    assert outlier["anomaly_score"] > 2.0
    assert outlier["anomaly_reason"] is not None


def test_anomaly_ignores_income_inflows():
    """Verify positive income deposits are not flagged as expense anomalies."""
    base_date = date(2026, 6, 1)
    transactions = [
        {"date": base_date + timedelta(days=i), "amount": -30.0, "category": "Dining", "description": "Lunch"}
        for i in range(10)
    ]
    transactions.append({
        "date": base_date + timedelta(days=11),
        "amount": 5000.0,
        "category": "Income",
        "description": "Bonus Check"
    })

    annotated = AnomalyDetector.detect_anomalies(transactions)
    income_tx = [t for t in annotated if t["amount"] == 5000.0][0]
    assert income_tx["is_anomaly"] is False
