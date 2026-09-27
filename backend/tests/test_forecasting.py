from datetime import date, timedelta
from app.services.forecaster import CashFlowForecaster


def test_forecast_empty_transactions():
    """Verify forecaster handles empty history safely without throwing exceptions."""
    result = CashFlowForecaster.forecast([], days_ahead=30)
    assert result["forecast_days"] == 30
    assert result["current_balance"] == 0.0
    assert len(result["daily_projections"]) == 0


def test_forecast_projection_length_and_bounds():
    """Verify projection matches requested days and produces valid statistical confidence bounds."""
    base_date = date(2026, 5, 1)
    transactions = [
        {"date": base_date + timedelta(days=i), "amount": -40.0, "category": "Food & Dining"}
        for i in range(30)
    ]
    # Add two paychecks
    transactions.append({"date": base_date, "amount": 2500.0, "category": "Income"})
    transactions.append({"date": base_date + timedelta(days=15), "amount": 2500.0, "category": "Income"})

    result = CashFlowForecaster.forecast(transactions, days_ahead=30, starting_balance=3500.0)

    assert result["forecast_days"] == 30
    assert result["current_balance"] == 3500.0
    assert len(result["daily_projections"]) == 30

    # Ensure bounds integrity
    for pt in result["daily_projections"]:
        assert pt["upper_bound"] >= pt["predicted_balance"]
        assert pt["lower_bound"] <= pt["predicted_balance"]


def test_forecast_with_recurring_obligations():
    """Verify recurring obligations impact cash flow projection dates."""
    base_date = date(2026, 5, 1)
    transactions = [
        {"date": base_date + timedelta(days=i * 2), "amount": -30.0, "category": "Groceries"}
        for i in range(15)
    ]
    recurring = [
        {
            "merchant": "Apartment Rent",
            "average_amount": -1200.0,
            "interval_days": 30,
            "last_date": base_date + timedelta(days=28)
        }
    ]

    result = CashFlowForecaster.forecast(
        transactions=transactions,
        recurring=recurring,
        days_ahead=35,
        starting_balance=4000.0
    )

    assert result["projected_end_balance"] < 4000.0
    assert len(result["daily_projections"]) == 35
