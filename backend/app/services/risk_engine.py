from datetime import date
from typing import Dict, List
import numpy as np


class RiskEngine:
    """
    Evaluates personal financial health and risk metrics based on liquidity runway,
    spending volatility, and net savings rate.
    """

    @classmethod
    def calculate_risk_profile(
        cls,
        transactions: List[Dict],
        current_balance: float | None = None
    ) -> Dict:
        """
        Compute holistic risk profile (score 0-100), contributing factors,
        and diagnostic risk grading.
        """
        if not transactions:
            return {
                "score": 50,
                "risk_level": "Moderate Risk",
                "liquidity_runway_months": 0.0,
                "spending_volatility_cv": 0.0,
                "savings_rate_pct": 0.0,
                "monthly_burn_rate": 0.0,
                "factors": [],
                "summary_message": "Insufficient transaction data to compute a comprehensive risk profile."
            }

        inflows = [t["amount"] for t in transactions if t["amount"] > 0]
        outflows = [abs(t["amount"]) for t in transactions if t["amount"] < 0]

        total_income = sum(inflows)
        total_expenses = sum(outflows)

        # Estimate timespan in months
        dates = [t["date"] for t in transactions]
        min_date = min(dates)
        max_date = max(dates)
        days = max((max_date - min_date).days, 1)
        months = max(days / 30.4, 0.5)

        monthly_burn = total_expenses / months
        monthly_income = total_income / months

        # Compute running or simulated current balance
        if current_balance is not None:
            balance = current_balance
        else:
            net_cum = total_income - total_expenses
            balance = max(net_cum, 500.0)

        # 1. Liquidity Runway (Months of survival without income)
        runway_months = balance / monthly_burn if monthly_burn > 0 else 12.0
        runway_months = round(runway_months, 2)

        if runway_months >= 6.0:
            liquidity_pts = 40.0
            liquidity_status = "Optimal"
            liquidity_desc = f"Solid cash buffer: {runway_months:.1f} months of expenses covered."
        elif runway_months >= 3.0:
            liquidity_pts = 30.0
            liquidity_status = "Adequate"
            liquidity_desc = f"Healthy reserve: {runway_months:.1f} months of liquidity available."
        elif runway_months >= 1.5:
            liquidity_pts = 20.0
            liquidity_status = "Fair"
            liquidity_desc = f"Moderate runway ({runway_months:.1f} mo); aim to reach at least 3 months."
        elif runway_months >= 0.5:
            liquidity_pts = 10.0
            liquidity_status = "Vulnerable"
            liquidity_desc = f"Low emergency cushion: only {runway_months:.1f} months of runway."
        else:
            liquidity_pts = 0.0
            liquidity_status = "Critical"
            liquidity_desc = "Immediate cash danger: less than 2 weeks of runway reserves."

        # 2. Spending Volatility (Coefficient of Variation of weekly outflows)
        # Group outflows by calendar week
        weekly_spending: Dict[str, float] = {}
        for t in transactions:
            if t["amount"] < 0:
                week_key = t["date"].strftime("%Y-W%W")
                weekly_spending[week_key] = weekly_spending.get(week_key, 0.0) + abs(t["amount"])

        week_vals = list(weekly_spending.values())
        if len(week_vals) > 1 and np.mean(week_vals) > 0:
            cv = float(np.std(week_vals) / np.mean(week_vals))
        else:
            cv = 0.30

        volatility_cv = round(cv, 2)

        if volatility_cv <= 0.30:
            volatility_pts = 30.0
            volatility_status = "Low Volatility"
            volatility_desc = f"Predictable expenditure habits (CV: {volatility_cv:.2f})."
        elif volatility_cv <= 0.60:
            volatility_pts = 22.0
            volatility_status = "Moderate Volatility"
            volatility_desc = f"Mild expenditure fluctuation (CV: {volatility_cv:.2f})."
        elif volatility_cv <= 0.90:
            volatility_pts = 12.0
            volatility_status = "Elevated Volatility"
            volatility_desc = f"Noticeable spending spikes week to week (CV: {volatility_cv:.2f})."
        else:
            volatility_pts = 5.0
            volatility_status = "High Volatility"
            volatility_desc = f"Extremely erratic spending patterns (CV: {volatility_cv:.2f})."

        # 3. Savings Rate / Cash Flow Margin
        if total_income > 0:
            savings_rate = ((total_income - total_expenses) / total_income) * 100.0
        else:
            savings_rate = 0.0
        savings_rate = round(savings_rate, 1)

        if savings_rate >= 20.0:
            savings_pts = 30.0
            savings_status = "Strong"
            savings_desc = f"High savings surplus: retaining {savings_rate:.1f}% of net income."
        elif savings_rate >= 10.0:
            savings_pts = 22.0
            savings_status = "Good"
            savings_desc = f"Positive cash flow margin: {savings_rate:.1f}% savings rate."
        elif savings_rate >= 0.0:
            savings_pts = 12.0
            savings_status = "Break-even"
            savings_desc = f"Living paycheck to paycheck ({savings_rate:.1f}% margin)."
        else:
            savings_pts = 0.0
            savings_status = "Deficit"
            savings_desc = f"Deficit spending: expenses exceed income by {abs(savings_rate):.1f}%."

        # Composite Score (0 - 100)
        total_score = int(round(liquidity_pts + volatility_pts + savings_pts))
        total_score = max(5, min(99, total_score))

        # Risk Classification
        if total_score >= 80:
            risk_level = "Low Risk"
            summary = "Financially resilient with strong emergency buffer and stable cash flow."
        elif total_score >= 60:
            risk_level = "Moderate Risk"
            summary = "Stable financial foundation, with opportunities to boost savings reserves."
        elif total_score >= 40:
            risk_level = "Elevated Risk"
            summary = "Vulnerable to unexpected financial shocks. Recommend trimming recurring costs."
        else:
            risk_level = "High Risk"
            summary = "High financial stress risk. Immediate action needed to halt negative cash flow."

        factors = [
            {
                "name": "Liquidity Buffer",
                "score": round(liquidity_pts, 1),
                "status": liquidity_status,
                "description": liquidity_desc
            },
            {
                "name": "Spending Volatility",
                "score": round(volatility_pts, 1),
                "status": volatility_status,
                "description": volatility_desc
            },
            {
                "name": "Savings Margin",
                "score": round(savings_pts, 1),
                "status": savings_status,
                "description": savings_desc
            }
        ]

        return {
            "score": total_score,
            "risk_level": risk_level,
            "liquidity_runway_months": runway_months,
            "spending_volatility_cv": volatility_cv,
            "savings_rate_pct": savings_rate,
            "monthly_burn_rate": round(monthly_burn, 2),
            "factors": factors,
            "summary_message": summary
        }
