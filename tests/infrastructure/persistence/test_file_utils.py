"""
Tests for file utility functions.

This module tests the common file handling utilities used by repository
implementations to ensure they work correctly and handle edge cases.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.domain.exceptions import TodoDomainError
from src.infrastructure.persistence.file_utils import ensure_file_exists


class TestEnsureFileExists:
    """Test suite for ensure_file_exists utility function."""

    def test_should_create_file_when_not_exists(self):
        """Should call initialization when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.txt"
            mock_init = Mock()

            ensure_file_exists(file_path, mock_init)

            mock_init.assert_called_once()

    def test_should_create_parent_directories(self):
        """Should create parent directories when they don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "nested" / "path" / "test.txt"
            mock_init = Mock()

            ensure_file_exists(file_path, mock_init)

            assert file_path.parent.exists()
            mock_init.assert_called_once()

    def test_should_initialize_empty_file(self):
        """Should call initialization when file exists but is empty."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "empty.txt"
            file_path.touch()  # Create empty file
            mock_init = Mock()

            ensure_file_exists(file_path, mock_init)

            mock_init.assert_called_once()

    def test_should_not_initialize_non_empty_file(self):
        """Should not call initialization when file exists and has content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "content.txt"
            file_path.write_text("some content")
            mock_init = Mock()

            ensure_file_exists(file_path, mock_init)

            mock_init.assert_not_called()

    def test_should_handle_permission_errors(self):
        """Should raise TodoDomainError when file creation fails due to permissions."""
        invalid_path = Path("/root/invalid/path/test.txt")
        mock_init = Mock()

        with pytest.raises(TodoDomainError, match="Failed to initialize file"):
            ensure_file_exists(invalid_path, mock_init)

        mock_init.assert_not_called()

    def test_should_handle_initialization_callback_errors(self):
        """Should wrap initialization callback errors in TodoDomainError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.txt"
            mock_init = Mock(side_effect=OSError("Initialization failed"))

            with pytest.raises(TodoDomainError, match="Failed to initialize file"):
                ensure_file_exists(file_path, mock_init)

            mock_init.assert_called_once()
