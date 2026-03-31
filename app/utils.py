"""
Utility Functions

Shared utility functions for the Grade Analysis application.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

from typing import Optional
from flask import current_app


def allowed_file(filename: Optional[str]) -> bool:
    """Check if file extension is allowed.

    Args:
        filename: Name of the file to check.

    Returns:
        True if extension is allowed, False otherwise.
    """
    if not filename:
        return False
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'xls', 'xlsx'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_float(value: Optional[str], default: float) -> float:
    """Convert string to float, return default if empty or invalid.

    Args:
        value: String value to convert.
        default: Default value to return if conversion fails.

    Returns:
        Converted float or default value.
    """
    try:
        result = float(value) if value else default
        return result if result else default
    except (ValueError, TypeError):
        return default
