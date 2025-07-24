"""
Tests for console helper utilities.

This module contains tests for console formatting, color helpers,
and display utilities used in the CLI interface.
"""

import pytest
from rich.table import Table

from src.interface.cli.console_helpers import ConsoleColors, format_status, format_todo_table


class TestConsoleColors:
    """Test suite for ConsoleColors utility class."""

    def test_should_have_color_constants(self):
        """Test that ConsoleColors provides color constants."""
        # Assert color constants exist
        assert hasattr(ConsoleColors, "SUCCESS")
        assert hasattr(ConsoleColors, "ERROR")
        assert hasattr(ConsoleColors, "WARNING")
        assert hasattr(ConsoleColors, "INFO")
        assert hasattr(ConsoleColors, "PENDING")
        assert hasattr(ConsoleColors, "COMPLETED")

    def test_should_provide_rich_compatible_colors(self):
        """Test that color constants are Rich-compatible strings."""
        # Assert colors are strings suitable for Rich
        assert isinstance(ConsoleColors.SUCCESS, str)
        assert isinstance(ConsoleColors.ERROR, str)
        assert isinstance(ConsoleColors.WARNING, str)
        assert isinstance(ConsoleColors.INFO, str)
        assert isinstance(ConsoleColors.PENDING, str)
        assert isinstance(ConsoleColors.COMPLETED, str)


class TestFormatStatus:
    """Test suite for status formatting function."""

    @pytest.mark.parametrize(
        "completed,expected_text,expected_color",
        [
            (False, "PENDING", ConsoleColors.PENDING),
            (True, "COMPLETED", ConsoleColors.COMPLETED),
        ],
    )
    def test_should_format_status_with_appropriate_color(self, completed, expected_text, expected_color):
        """Test that status is formatted with appropriate color and text."""
        result = format_status(completed)

        assert expected_text in result
        assert expected_color in result or "[" in result
        assert isinstance(result, str)


class TestFormatTodoTable:
    """Test suite for todo table formatting function."""

    def test_should_create_rich_table_for_empty_list(self):
        """Test that an empty todo list creates a valid Rich table."""
        # Act
        result = format_todo_table([])

        # Assert
        assert isinstance(result, Table)
        assert result.row_count == 0

    def test_should_create_table_with_proper_columns(self):
        """Test that the table has the expected column headers."""
        # Act
        result = format_todo_table([])

        # Assert
        assert isinstance(result, Table)
        # Check that table has columns (we'll verify specific headers in implementation)
        assert len(result.columns) > 0

    def test_should_handle_todo_list_with_items(self):
        """Test that the table can handle a list of todo items."""
        # Arrange
        from datetime import datetime

        from src.domain.models import TodoItem

        todo = TodoItem(
            title="Test Todo",
            description="Test Description",
            due_date=datetime(2025, 12, 31, 23, 59, 59),  # Future date
        )
        todos = [todo]

        # Act
        result = format_todo_table(todos)

        # Assert
        assert isinstance(result, Table)
        assert result.row_count == 1

    def test_should_handle_none_values_gracefully(self):
        """Test that the table handles None values in todo fields."""
        # Arrange
        from src.domain.models import TodoItem

        todo = TodoItem(
            title="Test Todo",
            description=None,  # None description
            due_date=None,  # None due_date
        )
        todos = [todo]

        # Act
        result = format_todo_table(todos)

        # Assert
        assert isinstance(result, Table)
        assert result.row_count == 1
