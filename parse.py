"""
Financial Parser CLI - Parse XLSX/CSV files for RAG systems.

Usage:
    python parse.py <file_path> [--output json|md|both] [--sheets Sheet1 Sheet2]
    python parse.py <file_path> --json <output.json>
    python parse.py <file_path> --md <output.md>
"""

import argparse
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent / "src"))

from financial_parser import FinancialParser


def main():
    parser = argparse.ArgumentParser(
        description="Parse XLSX/CSV files for RAG systems"
    )
    parser.add_argument("file", help="Path to XLSX or CSV file")
    parser.add_argument("--json", metavar="PATH", help="Export to JSON file")
    parser.add_argument("--md", metavar="PATH", help="Export to Markdown file")
    parser.add_argument(
        "--sheets",
        nargs="+",
        metavar="NAME",
        help="Parse specific sheets only (XLSX only)",
    )
    parser.add_argument(
        "--no-detect",
        action="store_true",
        help="Disable automatic financial statement type detection",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Print file info without exporting",
    )

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    fp = FinancialParser(
        sheet_names=args.sheets,
        detect_financial_type=not args.no_detect,
    )

    print(f"Parsing: {file_path.name}")
    doc = fp.parse(file_path)

    print(f"  Sheets: {len(doc.sheets)}")
    for s in doc.sheets:
        print(f"    {s.name}: {s.total_rows} rows, {len(s.tables)} tables")
    print(f"  Chunks: {len(doc.chunks)}")

    if args.info:
        return

    if args.json:
        doc.to_json(args.json)
        print(f"  JSON: {args.json}")

    if args.md:
        doc.to_markdown(args.md)
        print(f"  Markdown: {args.md}")

    if not args.json and not args.md:
        print("\nChunks:")
        for c in doc.chunks[:5]:
            print(f"  [{c.chunk_id}] tokens={c.token_count} source={c.source_uri}")
            lines = c.content_text.split("\n")
            for line in lines[:3]:
                print(f"    {line}")
            if len(lines) > 3:
                print(f"    ... ({len(lines)} lines total)")
        if len(doc.chunks) > 5:
            print(f"  ... and {len(doc.chunks) - 5} more chunks")


if __name__ == "__main__":
    main()
