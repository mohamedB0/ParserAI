from __future__ import annotations

from pathlib import Path
from typing import Any

import chardet
import pandas as pd

from financial_parser.core.models import Cell, SheetData, Table


def detect_encoding(file_path: str | Path) -> str:
    """Detect the encoding of a file."""
    with open(file_path, "rb") as f:
        raw = f.read(10000)
    result = chardet.detect(raw)
    return result.get("encoding", "utf-8") or "utf-8"


def read_csv(
    file_path: str | Path,
    encoding: str | None = None,
    delimiter: str | None = None,
    sheet_name: str = "CSV",
) -> tuple[list[SheetData], dict[str, Any]]:
    """Read a CSV file and return sheet data with metadata."""
    if encoding is None:
        encoding = detect_encoding(file_path)

    df = pd.read_csv(
        file_path,
        encoding=encoding,
        delimiter=delimiter,
        dtype=str,
        keep_default_na=False,
    )

    metadata: dict[str, Any] = {
        "encoding": encoding,
        "delimiter": delimiter or ",",
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
    }

    headers = list(df.columns)
    rows: list[list[Cell]] = []
    table_rows: list[list[Any]] = []

    for row_idx, (_, row) in enumerate(df.iterrows(), start=1):
        cells: list[Cell] = []
        row_values: list[Any] = []
        for col_idx, value in enumerate(row, start=1):
            cells.append(Cell(
                row=row_idx,
                col=col_idx,
                value=value,
                data_type="string",
            ))
            row_values.append(value)
        rows.append(cells)
        table_rows.append(row_values)

    table = Table(
        sheet_name=sheet_name,
        start_row=1,
        end_row=len(df),
        headers=headers,
        rows=table_rows,
        source_uri=f"{sheet_name}!A1:Z{len(df)}",
    )

    sheet = SheetData(
        name=sheet_name,
        tables=[table],
        total_rows=len(df),
        total_cols=len(df.columns),
    )

    return [sheet], metadata
