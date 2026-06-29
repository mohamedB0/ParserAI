from __future__ import annotations

import json
from typing import Any

from financial_parser.core.models import ParsedDocument, RAGChunk


def format_chunk_json(chunk: RAGChunk) -> dict[str, Any]:
    """Format a single chunk as JSON-serializable dict."""
    return {
        "chunk_id": chunk.chunk_id,
        "content_text": chunk.content_text,
        "content_html": chunk.content_html,
        "metadata": chunk.metadata,
        "token_count": chunk.token_count,
        "source_uri": chunk.source_uri,
        "dependencies": chunk.dependencies,
    }


def format_document_json(doc: ParsedDocument) -> str:
    """Format a parsed document as JSON string."""
    data = {
        "filename": doc.filename,
        "file_type": doc.file_type,
        "metadata": doc.metadata,
        "sheets": [
            {
                "name": s.name,
                "total_rows": s.total_rows,
                "total_cols": s.total_cols,
                "tables": [
                    {
                        "sheet_name": t.sheet_name,
                        "start_row": t.start_row,
                        "end_row": t.end_row,
                        "headers": t.headers,
                        "rows": t.rows,
                        "source_uri": t.source_uri,
                        "statement_type": t.statement_type.value,
                    }
                    for t in s.tables
                ],
            }
            for s in doc.sheets
        ],
        "chunks": [format_chunk_json(c) for c in doc.chunks],
    }
    return json.dumps(data, indent=2, default=str)
