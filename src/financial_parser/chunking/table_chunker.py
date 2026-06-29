from __future__ import annotations

import hashlib
from typing import Any

import tiktoken

from financial_parser.core.models import RAGChunk, Table, TextBlock, FinancialStatementType


def _col_letter(idx: int) -> str:
    """Convert 1-based column index to Excel-style letter."""
    result = ""
    while idx > 0:
        idx, remainder = divmod(idx - 1, 26)
        result = chr(65 + remainder) + result
    return result or "A"


def _format_cell_value(value: Any) -> str:
    """Format a cell value for text output."""
    if value is None:
        return ""
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return f"{value:,.2f}"
    return str(value)


def table_to_pipe_text(table: Table) -> str:
    """Convert a table to pipe-delimited text."""
    lines: list[str] = []

    header_line = " | ".join(str(h) for h in table.headers)
    lines.append(header_line)
    lines.append(" | ".join(["---"] * len(table.headers)))

    for row in table.rows:
        cells = [_format_cell_value(c) for c in row]
        while len(cells) < len(table.headers):
            cells.append("")
        lines.append(" | ".join(cells[:len(table.headers)]))

    return "\n".join(lines)


def table_to_markdown(table: Table) -> str:
    """Convert a table to Markdown format."""
    lines: list[str] = []

    lines.append(f"**Sheet:** {table.sheet_name}")
    lines.append(f"**Source:** `{table.source_uri}`")
    if table.statement_type != FinancialStatementType.UNKNOWN:
        lines.append(f"**Type:** {table.statement_type.value.replace('_', ' ').title()}")
    lines.append("")

    header_line = "| " + " | ".join(str(h) for h in table.headers) + " |"
    lines.append(header_line)
    lines.append("| " + " | ".join(["---"] * len(table.headers)) + " |")

    for row in table.rows:
        cells = [_format_cell_value(c) for c in row]
        while len(cells) < len(table.headers):
            cells.append("")
        lines.append("| " + " | ".join(cells[:len(table.headers)]) + " |")

    return "\n".join(lines)


def table_to_html(table: Table) -> str:
    """Convert a table to HTML format."""
    lines: list[str] = ["<table>"]

    lines.append("  <thead><tr>")
    for h in table.headers:
        lines.append(f"    <th>{h}</th>")
    lines.append("  </tr></thead>")

    lines.append("  <tbody>")
    for row in table.rows:
        lines.append("  <tr>")
        cells = [_format_cell_value(c) for c in row]
        while len(cells) < len(table.headers):
            cells.append("")
        for c in cells[:len(table.headers)]:
            lines.append(f"    <td>{c}</td>")
        lines.append("  </tr>")
    lines.append("  </tbody>")
    lines.append("</table>")

    return "\n".join(lines)


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count tokens in text using tiktoken."""
    try:
        enc = tiktoken.get_encoding(encoding_name)
        return len(enc.encode(text))
    except Exception:
        return len(text.split())


def generate_chunk_id(filename: str, source_uri: str) -> str:
    """Generate a deterministic chunk ID."""
    content = f"{filename}:{source_uri}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def chunk_table(table: Table, filename: str) -> RAGChunk:
    """Convert a table into an RAG chunk."""
    text = table_to_pipe_text(table)
    html = table_to_html(table)
    token_count = count_tokens(text)
    chunk_id = generate_chunk_id(filename, table.source_uri)

    metadata: dict[str, Any] = {
        "sheet_name": table.sheet_name,
        "statement_type": table.statement_type.value,
        "row_count": len(table.rows),
        "column_count": len(table.headers),
    }

    return RAGChunk(
        chunk_id=chunk_id,
        content_text=text,
        content_html=html,
        metadata=metadata,
        token_count=token_count,
        source_uri=f"{filename}!{table.source_uri}",
    )


def chunk_tables(tables: list[Table], filename: str) -> list[RAGChunk]:
    """Convert multiple tables into RAG chunks."""
    return [chunk_table(t, filename) for t in tables]


def text_block_to_text(block: TextBlock) -> str:
    """Convert a text block to plain text."""
    return "\n".join(block.content)


def text_block_to_html(block: TextBlock) -> str:
    """Convert a text block to HTML."""
    lines = ["<div>"]
    for line in block.content:
        lines.append(f"  <p>{line}</p>")
    lines.append("</div>")
    return "\n".join(lines)


def chunk_text_block(block: TextBlock, filename: str) -> RAGChunk:
    """Convert a text block into an RAG chunk."""
    text = text_block_to_text(block)
    html = text_block_to_html(block)
    token_count = count_tokens(text)
    chunk_id = generate_chunk_id(filename, block.source_uri)

    metadata: dict[str, Any] = {
        "sheet_name": block.sheet_name,
        "line_count": len(block.content),
    }

    return RAGChunk(
        chunk_id=chunk_id,
        content_text=text,
        content_html=html,
        chunk_type="text",
        metadata=metadata,
        token_count=token_count,
        source_uri=f"{filename}!{block.source_uri}",
    )


def chunk_text_blocks(blocks: list[TextBlock], filename: str) -> list[RAGChunk]:
    """Convert multiple text blocks into RAG chunks."""
    return [chunk_text_block(b, filename) for b in blocks]
