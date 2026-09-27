import re
from typing import Dict, List, Tuple

# Comprehensive rule-based lookup table for financial transaction categorization.
# Ordered from specific keywords to general fallbacks.
DEFAULT_CATEGORY_RULES: Dict[str, List[str]] = {
    "Income": [
        "payroll", "direct deposit", "salary", "bonus", "dividend",
        "paycheck", "interest earned", "tax refund", "ach deposit", "stripe payout"
    ],
    "Housing": [
        "rent", "mortgage", "property management", "landlord", "hoa fee",
        "apartment", "leasing", "plumbing", "roofing", "hvac repair"
    ],
    "Utilities": [
        "electric", "power", "water", "sewage", "gas bill", "utility",
        "comcast", "xfinity", "verizon", "at&t", "spectrum", "coned", "pge",
        "waste management", "internet"
    ],
    "Groceries": [
        "trader joe", "whole foods", "safeway", "kroger", "aldi", "costco",
        "supermarket", "grocery", "walmart neighborhood", "heb", "publix",
        "wegmans", "sprouts", "food lion", "target grocery"
    ],
    "Food & Dining": [
        "starbucks", "chipotle", "mcdonald", "burger", "coffee", "restaurant",
        "bistro", "cafe", "pizza", "doordash", "uber eats", "grubhub", "dunkin",
        "sweetgreen", "panera", "bakery", "taco", "sushi", "bar & grill"
    ],
    "Transportation": [
        "uber", "lyft", "shell", "chevron", "bp oil", "gas station", "exxon",
        "mobil", "subway", "metro transit", "parking", "tollway", "amtrak",
        "delta air", "united airlines", "car wash", "auto repair"
    ],
    "Entertainment": [
        "netflix", "spotify", "hulu", "disney", "apple tv", "amazon prime",
        "youtube", "cinema", "theatre", "steam", "playstation", "xbox",
        "nintendo", "audible", "hbo max", "paramount"
    ],
    "Health & Fitness": [
        "planet fitness", "equinox", "gym", "pharmacy", "cvs", "walgreens",
        "doctor", "dental", "hospital", "clinic", "health", "optometry",
        "gnc", "fitness"
    ],
    "Shopping": [
        "amazon", "target", "best buy", "ebay", "walmart", "apple store",
        "ikea", "home depot", "lowe's", "nordstrom", "zara", "clothing",
        "electronics"
    ],
    "Investments & Savings": [
        "vanguard", "fidelity", "charles schwab", "robinhood", "etrade",
        "coinbase", "transfer to savings", "wealthfront", "betterment"
    ]
}


class Categorizer:
    """
    Deterministic rule-based transaction categorizer using keyword mapping
    with fallback to 'Uncategorized'.
    """

    def __init__(self, custom_rules: Dict[str, List[str]] | None = None):
        self.rules: Dict[str, List[str]] = custom_rules or DEFAULT_CATEGORY_RULES

    def clean_text(self, text: str) -> str:
        """
        Normalize text: lower-case, remove special punctuation, strip extra whitespace.
        """
        if not text:
            return ""
        lowered = text.lower()
        cleaned = re.sub(r"[^a-z0-9\s&]", " ", lowered)
        return " ".join(cleaned.split())

    def extract_merchant(self, description: str) -> str:
        """
        Extract a normalized clean merchant name from raw transaction description.
        E.g. "Trader Joe's #123 San Francisco CA" -> "Trader Joe's"
        """
        if not description:
            return "Unknown"
            
        cleaned = re.sub(r"#\d+", "", description)
        cleaned = re.sub(r"\d{3,}", "", cleaned)  # remove long transaction IDs
        cleaned = re.sub(r"\b(ca|ny|tx|fl|il|wa|usa|online|store|terminal|pos)\b", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        
        # Take first 3-4 significant words
        tokens = cleaned.split()
        if len(tokens) > 4:
            return " ".join(tokens[:4])
        return cleaned if cleaned else description[:30]

    def categorize(self, description: str, amount: float | None = None) -> Tuple[str, str]:
        """
        Assign a category and merchant name based on transaction description.
        If amount is strongly positive, check Income first.
        Returns: (category, merchant)
        """
        cleaned_desc = self.clean_text(description)
        merchant = self.extract_merchant(description)

        # High priority check for positive inflows that indicate income
        if amount is not None and amount > 0:
            for keyword in self.rules.get("Income", []):
                if keyword in cleaned_desc:
                    return "Income", merchant

        # Check all categories
        for category, keywords in self.rules.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", cleaned_desc) or kw in cleaned_desc:
                    return category, merchant

        # Default fallback
        if amount is not None and amount > 0:
            return "Income", merchant
            
        return "Uncategorized", merchant


categorizer = Categorizer()
