from __future__ import annotations

from pathlib import Path
from typing import Any

from financial_parser.core.exceptions import FileFormatError
from financial_parser.core.models import ParsedDocument, SheetData
from financial_parser.financial.statement_detector import detect_all_tables
from financial_parser.chunking.table_chunker import chunk_tables


class FinancialParser:
    """Main parser orchestrator for financial documents."""

    def __init__(
        self,
        resolve_formulas: bool = True,
        sheet_names: list[str] | None = None,
        detect_financial_type: bool = True,
    ):
        self.resolve_formulas = resolve_formulas
        self.sheet_names = sheet_names
        self.detect_financial_type = detect_financial_type

    def parse(self, file_path: str | Path) -> ParsedDocument:
        """Parse a file and return a ParsedDocument."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = path.suffix.lower()
        filename = path.name

        if suffix == ".xlsx":
            return self._parse_xlsx(path, filename)
        elif suffix == ".csv":
            return self._parse_csv(path, filename)
        else:
            raise FileFormatError(f"Unsupported file format: {suffix}")

    def _parse_xlsx(self, path: Path, filename: str) -> ParsedDocument:
        """Parse an XLSX file."""
        from financial_parser.xlsx.reader import read_xlsx

        sheets, metadata = read_xlsx(
            path,
            sheet_names=self.sheet_names,
            resolve_formulas=self.resolve_formulas,
        )

        if self.detect_financial_type:
            for sheet in sheets:
                detect_all_tables(sheets[0].tables if sheets else [])

        all_tables = []
        for sheet in sheets:
            all_tables.extend(sheet.tables)

        chunks = chunk_tables(all_tables, filename)

        return ParsedDocument(
            filename=filename,
            file_type="xlsx",
            sheets=sheets,
            chunks=chunks,
            metadata=metadata,
        )

    def _parse_csv(self, path: Path, filename: str) -> ParsedDocument:
        """Parse a CSV file."""
        from financial_parser.csv.reader import read_csv

        sheets, metadata = read_csv(path)

        if self.detect_financial_type:
            for sheet in sheets:
                detect_all_tables(sheet.tables)

        all_tables = []
        for sheet in sheets:
            all_tables.extend(sheet.tables)

        chunks = chunk_tables(all_tables, filename)

        return ParsedDocument(
            filename=filename,
            file_type="csv",
            sheets=sheets,
            chunks=chunks,
            metadata=metadata,
        )
