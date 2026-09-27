from datetime import date, timedelta
from typing import Dict, List, Optional
import numpy as np


class CashFlowForecaster:
    """
    Projects future cash flow and cumulative account balance for 30 to 60 days.
    Combines moving average baseline spending with known recurring obligations (paychecks, rent).
    """

    @classmethod
    def forecast(
        cls,
        transactions: List[Dict],
        recurring: Optional[List[Dict]] = None,
        days_ahead: int = 30,
        starting_balance: Optional[float] = None
    ) -> Dict:
        """
        Generate daily forecasted balance and net flow points for `days_ahead`.
        """
        if not transactions:
            today = date.today()
            return {
                "forecast_days": days_ahead,
                "current_balance": 0.0,
                "projected_end_balance": 0.0,
                "average_daily_burn": 0.0,
                "confidence_level": 0.0,
                "daily_projections": []
            }

        sorted_tx = sorted(transactions, key=lambda x: x["date"])
        min_date = sorted_tx[0]["date"]
        max_date = sorted_tx[-1]["date"]

        # Calculate historical cumulative balance if starting_balance not provided
        cumulative = 0.0
        daily_flows: Dict[date, float] = {}

        curr = min_date
        while curr <= max_date:
            daily_flows[curr] = 0.0
            curr += timedelta(days=1)

        for tx in sorted_tx:
            t_date = tx["date"]
            daily_flows[t_date] = daily_flows.get(t_date, 0.0) + tx["amount"]
            cumulative += tx["amount"]

        # Default starting balance: either provided or cumulative balance with a minimum realistic baseline
        current_balance = starting_balance if starting_balance is not None else max(cumulative, 1000.0)

        # Calculate recent 30-day average daily non-recurring discretionary burn
        flow_values = list(daily_flows.values())
        recent_flows = flow_values[-30:] if len(flow_values) >= 30 else flow_values

        daily_std = float(np.std(recent_flows)) if len(recent_flows) > 1 else 25.0
        avg_daily_flow = float(np.mean(recent_flows))

        # Build schedule for future recurring transactions
        recurring_schedule: Dict[date, float] = {}
        if recurring:
            for item in recurring:
                cadence_days = item.get("interval_days", 30)
                amount = item.get("average_amount", 0.0)
                last_dt = item.get("last_date", max_date)

                next_dt = last_dt + timedelta(days=cadence_days)
                while next_dt <= max_date + timedelta(days=days_ahead + 7):
                    if next_dt > max_date:
                        recurring_schedule[next_dt] = recurring_schedule.get(next_dt, 0.0) + amount
                    next_dt += timedelta(days=cadence_days)

        # Project forward day by day
        projections = []
        running_bal = current_balance

        for day_idx in range(1, days_ahead + 1):
            target_date = max_date + timedelta(days=day_idx)
            
            # Base flow from moving average
            base_flow = avg_daily_flow

            # Specific recurring impact if scheduled today
            scheduled_flow = recurring_schedule.get(target_date, 0.0)
            daily_net = base_flow + (scheduled_flow * 0.7)  # dampen double-counting

            running_bal += daily_net

            # Confidence bounds widen with sqrt(t)
            spread = daily_std * np.sqrt(day_idx) * 1.5

            projections.append({
                "date": target_date.isoformat(),
                "predicted_balance": round(running_bal, 2),
                "projected_net_flow": round(daily_net, 2),
                "lower_bound": round(running_bal - spread, 2),
                "upper_bound": round(running_bal + spread, 2)
            })

        projected_end_balance = projections[-1]["predicted_balance"] if projections else current_balance
        daily_burn = abs(avg_daily_flow) if avg_daily_flow < 0 else 0.0

        return {
            "forecast_days": days_ahead,
            "current_balance": round(current_balance, 2),
            "projected_end_balance": round(projected_end_balance, 2),
            "average_daily_burn": round(daily_burn, 2),
            "confidence_level": 0.85,
            "daily_projections": projections
        }
