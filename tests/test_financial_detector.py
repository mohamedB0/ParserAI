from financial_parser.financial.statement_detector import detect_statement_type
from financial_parser.core.models import Table, FinancialStatementType


def test_detect_balance_sheet():
    """Test balance sheet detection."""
    table = Table(
        sheet_name="Sheet1",
        start_row=1,
        end_row=5,
        headers=["Item", "Amount"],
        rows=[
            ["Assets", ""],
            ["Current Assets", "100000"],
            ["Cash", "50000"],
            ["Liabilities", ""],
            ["Accounts Payable", "25000"],
        ],
    )
    result = detect_statement_type(table)
    assert result == FinancialStatementType.BALANCE_SHEET


def test_detect_income_statement():
    """Test income statement detection."""
    table = Table(
        sheet_name="Sheet1",
        start_row=1,
        end_row=4,
        headers=["Item", "Q1", "Q2"],
        rows=[
            ["Revenue", "100000", "120000"],
            ["Cost of Goods Sold", "60000", "70000"],
            ["Gross Profit", "40000", "50000"],
            ["Net Income", "30000", "40000"],
        ],
    )
    result = detect_statement_type(table)
    assert result == FinancialStatementType.INCOME_STATEMENT


def test_detect_unknown():
    """Test unknown type detection."""
    table = Table(
        sheet_name="Sheet1",
        start_row=1,
        end_row=3,
        headers=["Name", "City"],
        rows=[
            ["Alice", "New York"],
            ["Bob", "Boston"],
            ["Charlie", "Chicago"],
        ],
    )
    result = detect_statement_type(table)
    assert result == FinancialStatementType.UNKNOWN
