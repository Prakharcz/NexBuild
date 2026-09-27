from typing import Dict, List, Optional
import numpy as np


class AnomalyDetector:
    """
    Detects financial transaction anomalies using Interquartile Range (IQR)
    and Z-Score statistical outlier models.
    """

    @classmethod
    def detect_anomalies(
        cls,
        transactions: List[Dict],
        iqr_multiplier: float = 1.5,
        z_threshold: float = 2.5,
        min_samples: int = 5
    ) -> List[Dict]:
        """
        Flag outliers in transaction list using category-aware IQR and Z-score methods.
        Modifies or returns transactions with:
            - is_anomaly (bool)
            - anomaly_score (float)
            - anomaly_reason (str)
        """
        # Separate expense transactions (outflows)
        expense_indices = [
            i for i, t in enumerate(transactions)
            if t.get("amount", 0) < 0
        ]

        if len(expense_indices) < min_samples:
            # Not enough sample points to compute meaningful statistical distributions
            for t in transactions:
                t.setdefault("is_anomaly", False)
                t.setdefault("anomaly_score", 0.0)
                t.setdefault("anomaly_reason", None)
            return transactions

        expense_amounts = np.array([abs(transactions[i]["amount"]) for i in expense_indices])

        # Overall distribution metrics
        q1 = float(np.percentile(expense_amounts, 25))
        q3 = float(np.percentile(expense_amounts, 75))
        iqr = q3 - q1
        iqr_upper_bound = q3 + (iqr_multiplier * iqr)

        mean_expense = float(np.mean(expense_amounts))
        std_expense = float(np.std(expense_amounts))

        # Also group by category to catch category-specific spikes (e.g. $200 coffee vs $200 rent)
        cat_map: Dict[str, List[int]] = {}
        for idx in expense_indices:
            cat = transactions[idx].get("category", "Uncategorized")
            cat_map.setdefault(cat, []).append(idx)

        cat_iqr_bounds: Dict[str, float] = {}
        for cat, indices in cat_map.items():
            if len(indices) >= min_samples:
                cat_vals = np.array([abs(transactions[i]["amount"]) for i in indices])
                c_q1 = float(np.percentile(cat_vals, 25))
                c_q3 = float(np.percentile(cat_vals, 75))
                c_iqr = c_q3 - c_q1
                cat_iqr_bounds[cat] = c_q3 + (iqr_multiplier * c_iqr)

        # Evaluate each transaction
        for i, t in enumerate(transactions):
            amount = t.get("amount", 0)
            if amount >= 0:
                t["is_anomaly"] = False
                t["anomaly_score"] = 0.0
                t["anomaly_reason"] = None
                continue

            exp = abs(amount)
            category = t.get("category", "Uncategorized")

            # Calculate Z-score
            z_score = float((exp - mean_expense) / std_expense) if std_expense > 0 else 0.0

            # Check category-specific threshold first if available
            is_cat_outlier = False
            if category in cat_iqr_bounds and exp > cat_iqr_bounds[category] and exp > 30.0:
                is_cat_outlier = True

            # Global IQR outlier
            is_global_iqr_outlier = (exp > iqr_upper_bound) and (exp > 50.0)
            is_z_outlier = (z_score >= z_threshold) and (exp > 50.0)

            if is_cat_outlier or is_global_iqr_outlier or is_z_outlier:
                t["is_anomaly"] = True
                t["anomaly_score"] = round(max(z_score, (exp / max(iqr_upper_bound, 1.0))), 2)

                reasons = []
                if is_cat_outlier:
                    reasons.append(f"Unusual for {category} (limit: ${cat_iqr_bounds[category]:.2f})")
                if is_global_iqr_outlier:
                    reasons.append(f"Exceeds IQR upper bound (${iqr_upper_bound:.2f})")
                if is_z_outlier:
                    reasons.append(f"Z-score {z_score:.1f}σ above normal")

                t["anomaly_reason"] = " | ".join(reasons)
            else:
                t["is_anomaly"] = False
                t["anomaly_score"] = round(max(0.0, z_score), 2)
                t["anomaly_reason"] = None

        return transactions
