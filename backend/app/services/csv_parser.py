import io
import re
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
from app.services.categorizer import categorizer


class CSVParser:
    """
    Flexible CSV bank statement parser supporting major institutional export formats.
    Automatically identifies column headers, normalizes dates, and standardizes amounts.
    """

    DATE_ALIASES = [
        "date", "transaction date", "posting date", "trans date", "posted date",
        "trans_date", "post_date", "timestamp"
    ]
    DESC_ALIASES = [
        "description", "merchant", "payee", "memo", "name", "narrative",
        "details", "transaction details"
    ]
    AMOUNT_ALIASES = ["amount", "total", "sum", "transaction amount", "value"]
    DEBIT_ALIASES = ["debit", "withdrawal", "outflow", "payments"]
    CREDIT_ALIASES = ["credit", "deposit", "inflow"]
    CATEGORY_ALIASES = ["category", "type", "tag"]

    @classmethod
    def find_matching_column(cls, columns: List[str], aliases: List[str]) -> Optional[str]:
        """
        Match a header column against known aliases (case-insensitive, whitespace-trimmed).
        """
        normalized_cols = {col.strip().lower(): col for col in columns}
        for alias in aliases:
            if alias.lower() in normalized_cols:
                return normalized_cols[alias.lower()]
            # Substring match if exact match not found
            for norm, original in normalized_cols.items():
                if alias.lower() == norm or alias.lower() in norm:
                    return original
        return None

    @classmethod
    def parse_date(cls, value: str) -> Optional[date]:
        """
        Parse date strings into a standard datetime.date object.
        Supports ISO (YYYY-MM-DD), US (MM/DD/YYYY), and European (DD/MM/YYYY) formats.
        """
        if pd.isna(value) or not str(value).strip():
            return None

        clean_str = str(value).strip()
        date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%m-%d-%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%b %d, %Y",
            "%d %b %Y",
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%y",
            "%d/%m/%y"
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(clean_str, fmt).date()
            except ValueError:
                continue

        # Fallback to pandas to_datetime
        try:
            parsed = pd.to_datetime(clean_str)
            return parsed.date()
        except Exception:
            return None

    @classmethod
    def clean_amount(cls, value: any) -> Optional[float]:
        """
        Normalize amount values into a signed float.
        Positive = Inflow / Income / Credit.
        Negative = Outflow / Expense / Debit.
        Handles parentheses ($50.00), commas, currency signs.
        """
        if pd.isna(value):
            return None
        if isinstance(value, (int, float)):
            return float(value)

        val_str = str(value).strip()
        if not val_str:
            return None

        # Check for parenthesis convention: (50.00) means negative -50.00
        is_negative = False
        if val_str.startswith("(") and val_str.endswith(")"):
            is_negative = True
            val_str = val_str[1:-1]
        elif "-" in val_str:
            is_negative = True

        # Remove currency symbols, commas, quotes
        cleaned = re.sub(r"[^\d.]", "", val_str)
        if not cleaned:
            return None

        try:
            num = float(cleaned)
            return -num if is_negative else num
        except ValueError:
            return None

    @classmethod
    def parse_csv_content(cls, file_content: bytes) -> List[Dict]:
        """
        Parse raw bytes of a CSV statement and return a list of standardized transaction dictionaries.
        """
        # Try utf-8 first, fallback to latin-1
        try:
            text = file_content.decode("utf-8")
        except UnicodeDecodeError:
            text = file_content.decode("latin-1")

        # Read CSV with pandas, trying comma and tab delimiters
        try:
            df = pd.read_csv(io.StringIO(text))
        except Exception:
            df = pd.read_csv(io.StringIO(text), sep=";")

        cols = list(df.columns)
        date_col = cls.find_matching_column(cols, cls.DATE_ALIASES)
        desc_col = cls.find_matching_column(cols, cls.DESC_ALIASES)
        amount_col = cls.find_matching_column(cols, cls.AMOUNT_ALIASES)
        debit_col = cls.find_matching_column(cols, cls.DEBIT_ALIASES)
        credit_col = cls.find_matching_column(cols, cls.CREDIT_ALIASES)
        cat_col = cls.find_matching_column(cols, cls.CATEGORY_ALIASES)

        if not date_col or not desc_col:
            raise ValueError(f"Could not identify required 'Date' or 'Description' columns. Found columns: {cols}")

        if not amount_col and not (debit_col or credit_col):
            raise ValueError(f"Could not identify transaction 'Amount' or Debit/Credit columns. Found columns: {cols}")

        parsed_transactions = []

        for _, row in df.iterrows():
            # Date
            trans_date = cls.parse_date(row[date_col])
            if not trans_date:
                continue

            # Description
            description = str(row[desc_col]).strip()
            if not description or description.lower() == "nan":
                continue

            # Amount
            final_amount = None
            if amount_col and pd.notna(row.get(amount_col)):
                final_amount = cls.clean_amount(row[amount_col])
            elif debit_col or credit_col:
                debit_val = cls.clean_amount(row.get(debit_col)) if debit_col else None
                credit_val = cls.clean_amount(row.get(credit_col)) if credit_col else None

                if credit_val is not None and credit_val > 0:
                    final_amount = credit_val
                elif debit_val is not None and debit_val > 0:
                    final_amount = -debit_val
                elif debit_val is not None:
                    final_amount = debit_val

            if final_amount is None:
                continue

            # Category & Merchant
            explicit_category = str(row[cat_col]).strip() if cat_col and pd.notna(row.get(cat_col)) else None
            auto_category, merchant = categorizer.categorize(description, final_amount)

            category = explicit_category if explicit_category and explicit_category != "nan" else auto_category

            parsed_transactions.append({
                "date": trans_date,
                "description": description,
                "merchant": merchant,
                "amount": round(final_amount, 2),
                "category": category,
            })

        # Sort chronologically
        parsed_transactions.sort(key=lambda x: x["date"])
        return parsed_transactions
