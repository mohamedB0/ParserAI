from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Cell(BaseModel):
    """A single cell with coordinates and metadata."""
    row: int
    col: int
    value: Any = None
    formula: str | None = None
    data_type: str = "string"
    is_merged: bool = False
    merged_parent: tuple[int, int] | None = None


class FinancialStatementType(str, Enum):
    """Types of financial statements."""
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    TRANSACTION_LOG = "transaction_log"
    GENERAL_LEDGER = "general_ledger"
    TRIAL_BALANCE = "trial_balance"
    UNKNOWN = "unknown"


class Table(BaseModel):
    """A logical table extracted from a spreadsheet."""
    sheet_name: str
    start_row: int
    end_row: int
    start_col: int = 1
    end_col: int = 1
    headers: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    source_uri: str = ""
    statement_type: FinancialStatementType = FinancialStatementType.UNKNOWN
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGChunk(BaseModel):
    """A chunk ready for RAG ingestion."""
    chunk_id: str
    content_text: str
    content_html: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    token_count: int = 0
    source_uri: str = ""
    dependencies: list[str] = Field(default_factory=list)


class SheetData(BaseModel):
    """Data extracted from a single sheet."""
    name: str
    tables: list[Table] = Field(default_factory=list)
    merged_cells: list[tuple[str, str]] = Field(default_factory=list)
    total_rows: int = 0
    total_cols: int = 0


class ParsedDocument(BaseModel):
    """Final parsed document output."""
    filename: str
    file_type: str
    sheets: list[SheetData] = Field(default_factory=list)
    chunks: list[RAGChunk] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_json(self, path: str) -> None:
        """Export to JSON file."""
        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2, default=str)

    def to_markdown(self, path: str) -> None:
        """Export to Markdown file."""
        from financial_parser.output.markdown_formatter import format_document_markdown
        content = format_document_markdown(self)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
