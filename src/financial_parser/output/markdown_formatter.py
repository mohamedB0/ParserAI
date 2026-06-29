from __future__ import annotations

from financial_parser.core.models import ParsedDocument, SheetData
from financial_parser.chunking.table_chunker import table_to_markdown


def format_sheet_markdown(sheet: SheetData) -> str:
    """Format a single sheet as Markdown."""
    lines: list[str] = []
    lines.append(f"## Sheet: {sheet.name}")
    lines.append(f"*{sheet.total_rows} rows x {sheet.total_cols} columns*\n")

    for table in sheet.tables:
        lines.append(table_to_markdown(table))
        lines.append("")

    return "\n".join(lines)


def format_document_markdown(doc: ParsedDocument) -> str:
    """Format a parsed document as Markdown string."""
    lines: list[str] = []
    lines.append(f"# {doc.filename}\n")
    lines.append(f"**File type:** {doc.file_type}")
    lines.append(f"**Sheets:** {len(doc.sheets)}")
    lines.append(f"**Chunks:** {len(doc.chunks)}")
    lines.append("")

    for sheet in doc.sheets:
        lines.append(format_sheet_markdown(sheet))
        lines.append("---\n")

    lines.append("## RAG Chunks\n")
    for chunk in doc.chunks:
        lines.append(f"### Chunk `{chunk.chunk_id}`")
        lines.append(f"- **Source:** `{chunk.source_uri}`")
        lines.append(f"- **Tokens:** {chunk.token_count}")
        lines.append(f"- **Type:** {chunk.metadata.get('statement_type', 'unknown')}")
        lines.append("")
        lines.append("```")
        lines.append(chunk.content_text)
        lines.append("```\n")

    return "\n".join(lines)
