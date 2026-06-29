import csv
import os
import tempfile

from financial_parser.csv.reader import read_csv, detect_encoding


def _make_csv(content: str) -> str:
    """Create a temp CSV file and return its path (file closed)."""
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    return path


def test_detect_encoding():
    """Test encoding detection."""
    path = _make_csv("Name,Age\nAlice,30\nBob,25\n")
    try:
        encoding = detect_encoding(path)
        assert encoding is not None
    finally:
        os.unlink(path)


def test_read_csv():
    """Test basic CSV reading."""
    content = "Date,Description,Amount\n2024-01-01,Payment,100.00\n2024-01-02,Receipt,250.50\n"
    path = _make_csv(content)
    try:
        sheets, metadata = read_csv(path)
        assert len(sheets) == 1
        sheet = sheets[0]
        assert sheet.total_rows == 2
        assert sheet.total_cols == 3
        assert len(sheet.tables) == 1
        table = sheet.tables[0]
        assert table.headers == ["Date", "Description", "Amount"]
        assert len(table.rows) == 2
    finally:
        os.unlink(path)
