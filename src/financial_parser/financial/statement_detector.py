from __future__ import annotations

import re
from typing import Any

from financial_parser.core.models import FinancialStatementType, Table


BALANCE_SHEET_KEYWORDS = [
    "balance sheet", "assets", "liabilities", "equity", "total assets",
    "total liabilities", "shareholders equity", "current assets",
    "non-current assets", "current liabilities", "long-term debt",
    "retained earnings", "accumulated depreciation", "accounts receivable",
    "accounts payable", "inventory", "cash and equivalents",
]

INCOME_STATEMENT_KEYWORDS = [
    "income statement", "profit and loss", "revenue", "cost of goods sold",
    "gross profit", "operating income", "net income", "earnings per share",
    "operating expenses", "selling general administrative", "depreciation",
    "amortization", "interest expense", "tax expense", "ebitda",
    "cost of revenue", "research and development",
]

CASH_FLOW_KEYWORDS = [
    "cash flow", "operating activities", "investing activities",
    "financing activities", "net cash", "free cash flow",
    "capital expenditures", "dividends paid", "share repurchase",
    "beginning cash", "ending cash",
]

TRANSACTION_KEYWORDS = [
    "transaction", "payment", "invoice", "receipt", "debit", "credit",
    "balance", "account number", "transaction date", "description",
    "amount", "running balance", "reference", "check number",
]

TRIAL_BALANCE_KEYWORDS = [
    "trial balance", "debit", "credit", "account code", "account name",
    "journal entry", "general ledger",
]


def _text_matches_keywords(text: str, keywords: list[str], threshold: float = 0.3) -> bool:
    """Check if text contains enough keywords to match a statement type."""
    text_lower = text.lower()
    matches = sum(1 for kw in keywords if kw in text_lower)
    return matches >= max(1, int(len(keywords) * threshold))


def _row_texts(table: Table) -> list[str]:
    """Extract all text values from a table."""
    texts: list[str] = []
    for row in table.rows:
        for cell in row:
            if cell is not None:
                texts.append(str(cell))
    return texts


def detect_statement_type(table: Table) -> FinancialStatementType:
    """Detect the financial statement type of a table."""
    all_text = " ".join(_row_texts(table))
    header_text = " ".join(str(h) for h in table.headers)

    combined = f"{header_text} {all_text}"

    scores: dict[FinancialStatementType, int] = {
        FinancialStatementType.BALANCE_SHEET: 0,
        FinancialStatementType.INCOME_STATEMENT: 0,
        FinancialStatementType.CASH_FLOW: 0,
        FinancialStatementType.TRANSACTION_LOG: 0,
        FinancialStatementType.TRIAL_BALANCE: 0,
    }

    if _text_matches_keywords(combined, BALANCE_SHEET_KEYWORDS, 0.2):
        scores[FinancialStatementType.BALANCE_SHEET] = sum(
            1 for kw in BALANCE_SHEET_KEYWORDS if kw in combined.lower()
        )

    if _text_matches_keywords(combined, INCOME_STATEMENT_KEYWORDS, 0.2):
        scores[FinancialStatementType.INCOME_STATEMENT] = sum(
            1 for kw in INCOME_STATEMENT_KEYWORDS if kw in combined.lower()
        )

    if _text_matches_keywords(combined, CASH_FLOW_KEYWORDS, 0.2):
        scores[FinancialStatementType.CASH_FLOW] = sum(
            1 for kw in CASH_FLOW_KEYWORDS if kw in combined.lower()
        )

    if _text_matches_keywords(combined, TRANSACTION_KEYWORDS, 0.2):
        scores[FinancialStatementType.TRANSACTION_LOG] = sum(
            1 for kw in TRANSACTION_KEYWORDS if kw in combined.lower()
        )

    if _text_matches_keywords(combined, TRIAL_BALANCE_KEYWORDS, 0.2):
        scores[FinancialStatementType.TRIAL_BALANCE] = sum(
            1 for kw in TRIAL_BALANCE_KEYWORDS if kw in combined.lower()
        )

    best_type = max(scores, key=lambda k: scores[k])
    if scores[best_type] == 0:
        return FinancialStatementType.UNKNOWN
    return best_type


def detect_all_tables(tables: list[Table]) -> list[Table]:
    """Detect and assign statement types to all tables."""
    for table in tables:
        table.statement_type = detect_statement_type(table)
    return tables
