# Financial Parser

A Python parser for XLSX and CSV files, built for RAG (Retrieval-Augmented Generation) systems in the financial domain.

## Features

- Parse XLSX files with merged cell resolution, multi-sheet support, and formula handling
- Parse CSV files with automatic encoding detection
- Auto-detect financial statement types (balance sheet, income statement, cash flow, transactions)
- Table-level chunking with token counting via tiktoken
- Output as structured JSON or human-readable Markdown
- Source URI tracking for every chunk (e.g., `report.xlsx!Balance Sheet!A1:D30`)

## Installation

```bash
pip install git+https://github.com/mohamedB0/ParserAI.git
```

Or clone and install locally:

```bash
git clone https://github.com/mohamedB0/ParserAI.git
cd ParserAI
pip install -e .
```

## Quick Start

```python
from financial_parser import FinancialParser

parser = FinancialParser()
doc = parser.parse("financial_report.xlsx")

# Iterate over RAG-ready chunks
for chunk in doc.chunks:
    print(chunk.source_uri)       # financial_report.xlsx!Sheet1!A1:D30
    print(chunk.token_count)      # 425
    print(chunk.content_text)     # pipe-delimited table

# Export to JSON or Markdown
doc.to_json("output.json")
doc.to_markdown("output.md")
```

## Usage

### Parse a file

```python
from financial_parser import FinancialParser

parser = FinancialParser()
doc = parser.parse("data.xlsx")
```

### Parse specific sheets only

```python
parser = FinancialParser(sheet_names=["Balance Sheet", "Income Statement"])
doc = parser.parse("report.xlsx")
```

### Access parsed data

```python
# List of sheets
for sheet in doc.sheets:
    print(sheet.name, sheet.total_rows, sheet.total_cols)

    # Each sheet contains detected tables
    for table in sheet.tables:
        print(table.headers)
        print(table.rows)
        print(table.statement_type)  # e.g., "balance_sheet"
```

### Export outputs

```python
# JSON export
doc.to_json("output.json")

# Markdown export
doc.to_markdown("output.md")
```

### RAG chunk structure

Each `RAGChunk` contains:

| Field          | Description                                          |
|----------------|------------------------------------------------------|
| `chunk_id`     | Deterministic hash-based identifier                  |
| `content_text` | Pipe-delimited table for LLM consumption             |
| `content_html` | HTML table representation                            |
| `token_count`  | Token count via tiktoken (cl100k_base encoding)      |
| `source_uri`   | File path + sheet + cell range for citation          |
| `metadata`     | Sheet name, statement type, row/column counts        |

## Supported Financial Statement Types

The parser auto-detects the following statement types based on keyword matching:

- **Balance Sheet** -- assets, liabilities, equity
- **Income Statement** -- revenue, COGS, gross profit, net income
- **Cash Flow Statement** -- operating/investing/financing activities
- **Transaction Log** -- payments, invoices, receipts
- **Trial Balance** -- debits, credits, account codes

## Project Structure

```
ParserAI/
├── pyproject.toml
├── src/financial_parser/
│   ├── __init__.py
│   ├── core/
│   │   ├── parser.py              # Main parser orchestrator
│   │   ├── models.py              # Pydantic data models
│   │   └── exceptions.py          # Custom exceptions
│   ├── xlsx/reader.py             # XLSX reader with merged cell handling
│   ├── csv/reader.py              # CSV reader with encoding detection
│   ├── financial/
│   │   └── statement_detector.py  # Financial statement type detection
│   ├── chunking/
│   │   └── table_chunker.py       # Table-level chunking + token counting
│   └── output/
│       ├── json_formatter.py      # JSON export
│       └── markdown_formatter.py  # Markdown export
└── tests/
```

## Dependencies

- `openpyxl` -- XLSX reading and merged cell resolution
- `pandas` -- CSV reading and data manipulation
- `tiktoken` -- Token counting for LLM context management
- `chardet` -- Automatic CSV encoding detection
- `pydantic` -- Data validation and serialization

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## License

MIT
