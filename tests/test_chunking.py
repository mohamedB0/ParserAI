from financial_parser.chunking.table_chunker import (
    table_to_pipe_text,
    table_to_markdown,
    table_to_html,
    count_tokens,
    chunk_table,
)
from financial_parser.core.models import Table, FinancialStatementType


def _make_table() -> Table:
    return Table(
        sheet_name="Balance Sheet",
        start_row=1,
        end_row=4,
        headers=["Item", "Current Year", "Prior Year"],
        rows=[
            ["Total Assets", "500000", "450000"],
            ["Total Liabilities", "200000", "180000"],
            ["Shareholders Equity", "300000", "270000"],
            ["Total Liabilities & Equity", "500000", "450000"],
        ],
        source_uri="Sheet1!A1:D4",
        statement_type=FinancialStatementType.BALANCE_SHEET,
    )


def test_pipe_text():
    table = _make_table()
    text = table_to_pipe_text(table)
    assert "Item | Current Year | Prior Year" in text
    assert "Total Assets" in text
    assert "500000" in text


def test_markdown():
    table = _make_table()
    md = table_to_markdown(table)
    assert "**Sheet:** Balance Sheet" in md
    assert "| Item | Current Year | Prior Year |" in md
    assert "Balance Sheet" in md


def test_html():
    table = _make_table()
    html = table_to_html(table)
    assert "<table>" in html
    assert "<th>Item</th>" in html
    assert "<td>Total Assets</td>" in html


def test_count_tokens():
    text = "Hello world, this is a test"
    tokens = count_tokens(text)
    assert tokens > 0
    assert isinstance(tokens, int)


def test_chunk_table():
    table = _make_table()
    chunk = chunk_table(table, "financials.xlsx")
    assert chunk.chunk_id
    assert chunk.content_text
    assert chunk.content_html
    assert chunk.token_count > 0
    assert "financials.xlsx!Sheet1!A1:D4" in chunk.source_uri
    assert chunk.metadata["statement_type"] == "balance_sheet"
