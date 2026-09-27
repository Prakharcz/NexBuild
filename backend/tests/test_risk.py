from datetime import date, timedelta
from app.services.risk_engine import RiskEngine


def test_risk_score_healthy_finances():
    """Verify strong liquidity runway and positive savings margin yields Low Risk score."""
    base_date = date(2026, 3, 1)
    transactions = []
    
    # 6 months of data: $5,000 income, $2,500 expenses each month
    for m in range(6):
        m_date = base_date + timedelta(days=m * 30)
        transactions.append({"date": m_date, "amount": 5000.0, "category": "Income", "description": "Salary"})
        transactions.append({"date": m_date + timedelta(days=1), "amount": -1500.0, "category": "Housing", "description": "Rent"})
        transactions.append({"date": m_date + timedelta(days=10), "amount": -1000.0, "category": "Living", "description": "Essentials"})

    # Starting balance = $18,000 (which covers >6 months of $2500/mo spend)
    profile = RiskEngine.calculate_risk_profile(transactions, current_balance=18000.0)

    assert profile["score"] >= 75
    assert profile["risk_level"] in ["Low Risk", "Moderate Risk"]
    assert profile["liquidity_runway_months"] >= 6.0
    assert profile["savings_rate_pct"] > 40.0
    assert len(profile["factors"]) == 3


def test_risk_score_vulnerable_finances():
    """Verify low liquidity and deficit spending produces elevated or high risk."""
    base_date = date(2026, 3, 1)
    transactions = []

    for m in range(3):
        m_date = base_date + timedelta(days=m * 30)
        transactions.append({"date": m_date, "amount": 2000.0, "category": "Income", "description": "Income"})
        transactions.append({"date": m_date + timedelta(days=5), "amount": -2400.0, "category": "Expenses", "description": "Spend"})

    # Low balance of $200 (less than 1 month runway)
    profile = RiskEngine.calculate_risk_profile(transactions, current_balance=200.0)

    assert profile["score"] < 50
    assert profile["risk_level"] in ["Elevated Risk", "High Risk"]
    assert profile["liquidity_runway_months"] < 1.0
