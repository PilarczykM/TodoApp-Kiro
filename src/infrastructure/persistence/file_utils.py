"""
File utilities for repository implementations.

This module provides common file handling utilities used by different
repository implementations to avoid code duplication.
"""

from collections.abc import Callable
from pathlib import Path

from src.domain.exceptions import TodoDomainError


def ensure_file_exists(file_path: Path, initialize_empty_file: Callable[[], None]) -> None:
    """
    Ensure a file exists and is properly initialized.

    This utility function handles the common pattern of checking if a file exists,
    creating parent directories if needed, and initializing empty files with
    appropriate content.

    Args:
        file_path: Path to the file that should exist
        initialize_empty_file: Callback function to initialize an empty file
                              with appropriate content (e.g., empty JSON array,
                              empty XML document)

    Raises:
        TodoDomainError: If file creation or initialization fails
    """
    try:
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            initialize_empty_file()
        elif file_path.stat().st_size == 0:
            # Handle empty file
            initialize_empty_file()
    except OSError as e:
        raise TodoDomainError(f"Failed to initialize file {file_path}: {e}") from e
