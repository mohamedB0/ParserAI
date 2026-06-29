class ParserError(Exception):
    """Base exception for parser errors."""
    pass


class FileFormatError(ParserError):
    """Raised when file format is invalid or unsupported."""
    pass


class SheetNotFoundError(ParserError):
    """Raised when a specified sheet is not found."""
    pass


class FinancialParsingError(ParserError):
    """Raised when financial data parsing fails."""
    pass
