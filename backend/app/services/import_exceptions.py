"""
Import exception hierarchy

Defines exception types for import operations.
"""

from typing import Any, Dict
from typing import Optional


class ImportError(Exception):
    """Base exception for all import errors"""

    def __init__(
        self,
        message: str,
        row_number: Optional[int] = None,
        field: Optional[str] = None
    ):
        self.message = message
        self.row_number = row_number
        self.field = field
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for API responses

        Returns:
            Dict with row, field, and message
        """
        return {
            "row": self.row_number if self.row_number is not None else "unknown",
            "field": self.field,
            "message": self.message
        }

    def __str__(self) -> str:
        """String representation"""
        parts = []
        if self.row_number:
            parts.append(f"第{self.row_number}行")
        if self.field:
            parts.append(f"字段 '{self.field}'")
        parts.append(self.message)
        return ": ".join(parts)


class ParseError(ImportError):
    """Excel parsing error"""
    pass


class ValidationError(ImportError):
    """Data validation error"""
    pass


class EntityNotFoundError(ImportError):
    """Foreign key entity not found error"""
    pass
