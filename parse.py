"""
Financial Parser CLI - Parse XLSX/CSV files for RAG systems.

Usage:
    python parse.py <file_path>
    python parse.py <file_path> --json
    python parse.py <file_path> --md
    python parse.py <file_path> --json --md
    python parse.py <file_path> --sheets Sheet1 Sheet2
"""

import argparse
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent / "src"))

from financial_parser import FinancialParser

OUTPUT_DIR = Path(__file__).parent / "output"


def main():
    parser = argparse.ArgumentParser(
        description="Parse XLSX/CSV files for RAG systems"
    )
    parser.add_argument("file", help="Path to XLSX or CSV file")
    parser.add_argument(
        "--json", action="store_true", help="Export to JSON in output/ folder"
    )
    parser.add_argument(
        "--md", action="store_true", help="Export to Markdown in output/ folder"
    )
    parser.add_argument(
        "--all", action="store_true", help="Export both JSON and Markdown"
    )
    parser.add_argument(
        "--outdir", metavar="DIR", help="Custom output directory (default: output/)"
    )
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

    out_dir = Path(args.outdir) if args.outdir else OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = file_path.stem

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

    export_json = args.json or args.all
    export_md = args.md or args.all

    if not export_json and not export_md:
        export_json = True
        export_md = True

    if export_json:
        json_path = out_dir / f"{stem}.json"
        doc.to_json(json_path)
        print(f"  JSON: {json_path}")

    if export_md:
        md_path = out_dir / f"{stem}.md"
        doc.to_markdown(md_path)
        print(f"  Markdown: {md_path}")

    if not export_json and not export_md:
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
