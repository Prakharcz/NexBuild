from app.services.categorizer import categorizer


def test_categorize_common_merchants():
    """Verify rule-based keyword mapping for staple daily spending."""
    cat, merch = categorizer.categorize("STARBUCKS STORE #10425 SEATTLE", -6.50)
    assert cat == "Food & Dining"
    assert "starbucks" in merch.lower()

    cat, merch = categorizer.categorize("TRADER JOE'S GROCERY SAN FRANCISCO", -92.50)
    assert cat == "Groceries"
    assert "trader joe" in merch.lower()

    cat, merch = categorizer.categorize("NETFLIX.COM DIGITAL SUBSCRIPTION", -19.99)
    assert cat == "Entertainment"

    cat, merch = categorizer.categorize("COMCAST XFINITY INTERNET BILL", -79.99)
    assert cat == "Utilities"

    cat, merch = categorizer.categorize("OAKWOOD PROPERTY MANAGEMENT RENT", -1500.00)
    assert cat == "Housing"

    cat, merch = categorizer.categorize("UBER TRIP HELP.UBER.COM", -24.50)
    assert cat == "Transportation"


def test_categorize_income():
    """Verify that positive income deposits are categorized accurately."""
    cat, merch = categorizer.categorize("ACME CORP PAYROLL DIRECT DEPOSIT", 3200.00)
    assert cat == "Income"

    cat, merch = categorizer.categorize("STRIPE PAYOUT TRANSFER", 850.00)
    assert cat == "Income"


def test_categorize_fallback_uncategorized():
    """Verify unknown and ambiguous descriptions default gracefully to Uncategorized."""
    cat, merch = categorizer.categorize("XYZ RANDOM MISCELLANEOUS EXPENSE 987", -45.00)
    assert cat == "Uncategorized"


def test_merchant_extraction_cleans_noise():
    """Verify transaction numbers and state abbreviations are stripped from merchant name."""
    merch = categorizer.extract_merchant("Whole Foods Market #9823 CA")
    assert "Whole Foods" in merch
    assert "#9823" not in merch
