from datetime import date, timedelta
from typing import Dict, List, Optional
import numpy as np


class RecurringDetector:
    """
    Identifies recurring transactions by grouping by merchant, analyzing
    interval frequencies (weekly, biweekly, monthly), and checking amount stability.
    """

    CADENCE_INTERVALS = {
        "weekly": (5, 9, 7),
        "biweekly": (12, 17, 14),
        "monthly": (25, 35, 30),
        "quarterly": (80, 100, 91),
        "yearly": (350, 380, 365),
    }

    @classmethod
    def determine_cadence(cls, intervals: List[int]) -> Optional[tuple[str, int]]:
        """
        Match average interval in days to a standard cadence.
        Returns (cadence_name, expected_days) or None if erratic.
        """
        if not intervals:
            return None

        avg_interval = float(np.mean(intervals))
        std_interval = float(np.std(intervals)) if len(intervals) > 1 else 0.0

        # Intervals shouldn't be completely chaotic (std deviation under 8 days for monthly)
        if std_interval > 10.0:
            return None

        for cadence, (min_d, max_d, target_d) in cls.CADENCE_INTERVALS.items():
            if min_d <= avg_interval <= max_d:
                return cadence, target_d

        return None

    @classmethod
    def detect_recurring(cls, transactions: List[Dict]) -> List[Dict]:
        """
        Analyze transaction history to detect recurring patterns.
        
        Args:
            transactions: list of dicts with 'date', 'merchant', 'amount', 'category', 'description'
        
        Returns:
            list of recurring pattern dicts
        """
        # Group by cleaned merchant
        merchant_groups: Dict[str, List[Dict]] = {}
        for t in transactions:
            m = t.get("merchant") or "Unknown"
            if m not in merchant_groups:
                merchant_groups[m] = []
            merchant_groups[m].append(t)

        detected_recurring: List[Dict] = []

        for merchant, items in merchant_groups.items():
            if len(items) < 2:
                continue

            # Sort chronologically
            sorted_items = sorted(items, key=lambda x: x["date"])
            dates = [x["date"] for x in sorted_items]
            amounts = [x["amount"] for x in sorted_items]

            # Calculate intervals between consecutive transactions
            intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

            # Ignore immediate duplicates on the exact same day
            valid_intervals = [inv for inv in intervals if inv > 0]
            if not valid_intervals:
                continue

            cadence_info = cls.determine_cadence(valid_intervals)
            if not cadence_info:
                continue

            cadence, interval_days = cadence_info
            avg_amount = float(np.mean(amounts))
            last_date = dates[-1]
            next_date = last_date + timedelta(days=interval_days)

            # Check for amount price changes (e.g., subscription price increase)
            price_change_pct = 0.0
            if len(amounts) >= 2:
                earlier_mean = float(np.mean(amounts[:-1]))
                latest_amount = float(amounts[-1])
                if abs(earlier_mean) > 0.01:
                    price_change_pct = ((abs(latest_amount) - abs(earlier_mean)) / abs(earlier_mean)) * 100.0

            category = sorted_items[-1].get("category", "Uncategorized")

            detected_recurring.append({
                "merchant": merchant,
                "category": category,
                "average_amount": round(avg_amount, 2),
                "latest_amount": round(amounts[-1], 2),
                "cadence": cadence,
                "interval_days": interval_days,
                "occurrence_count": len(sorted_items),
                "last_date": last_date,
                "next_expected_date": next_date,
                "price_change_pct": round(price_change_pct, 1),
                "is_active": True,
            })

        return detected_recurring
