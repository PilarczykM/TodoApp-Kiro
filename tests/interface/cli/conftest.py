"""
Shared fixtures for CLI tests.

This module provides common fixtures for testing CLI components,
including mocked dependencies and test utilities.
"""

from unittest.mock import Mock, patch

import pytest

from src.interface.cli.todo_cli import TodoCLI


@pytest.fixture
def mock_service():
    """Create a mock TodoService for testing."""
    return Mock()


@pytest.fixture
def todo_cli(mock_service):
    """Create a TodoCLI instance with mocked service."""
    return TodoCLI(mock_service)


@pytest.fixture
def mock_console():
    """Mock the Rich Console for testing output."""
    with patch("src.interface.cli.todo_cli.Console") as mock:
        yield mock.return_value


@pytest.fixture
def mock_prompt():
    """Mock the Rich Prompt for testing user input."""
    with patch("rich.prompt.Prompt.ask") as mock:
        yield mock


@pytest.fixture
def cli_with_mocked_console(mock_service, mock_console):
    """Create TodoCLI with mocked console for output testing."""
    cli = TodoCLI(mock_service)
    cli.console = mock_console
    return cli
