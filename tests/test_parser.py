import json
import os
import tempfile

from financial_parser.core.parser import FinancialParser
from financial_parser.core.models import ParsedDocument


def _make_csv(content: str) -> str:
    """Create a temp CSV file and return its path (file closed)."""
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def test_parse_csv():
    """Test end-to-end CSV parsing."""
    path = _make_csv("Date,Description,Amount\n2024-01-01,Payment,100.00\n2024-01-02,Receipt,250.50\n")
    try:
        parser = FinancialParser()
        doc = parser.parse(path)
        assert isinstance(doc, ParsedDocument)
        assert doc.filename.endswith(".csv")
        assert doc.file_type == "csv"
        assert len(doc.sheets) == 1
        assert len(doc.chunks) == 1
        assert doc.chunks[0].token_count > 0
    finally:
        os.unlink(path)


def test_parse_csv_to_json():
    """Test CSV to JSON export."""
    csv_path = _make_csv("Category,Value\nRevenue,1000\nExpenses,500\n")
    output_path = csv_path.replace(".csv", "_output.json")
    try:
        parser = FinancialParser()
        doc = parser.parse(csv_path)
        doc.to_json(output_path)

        with open(output_path, "r") as out:
            data = json.load(out)

        assert data["file_type"] == "csv"
        assert len(data["chunks"]) == 1
        assert "content_text" in data["chunks"][0]
    finally:
        if os.path.exists(csv_path):
            os.unlink(csv_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_parse_csv_to_markdown():
    """Test CSV to Markdown export."""
    csv_path = _make_csv("Account,Balance\nChecking,5000\nSavings,15000\n")
    output_path = csv_path.replace(".csv", "_output.md")
    try:
        parser = FinancialParser()
        doc = parser.parse(csv_path)
        doc.to_markdown(output_path)

        with open(output_path, "r") as out:
            content = out.read()

        assert "Checking" in content
        assert "5000" in content
    finally:
        if os.path.exists(csv_path):
            os.unlink(csv_path)
        if os.path.exists(output_path):
            os.unlink(output_path)
