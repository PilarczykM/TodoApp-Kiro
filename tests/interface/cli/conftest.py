"""
Shared fixtures and helper functions for CLI tests.

This module provides common fixtures for testing CLI components,
including mocked dependencies and test utilities that reduce code
duplication and improve test maintainability.

Fixtures:
- mock_service: Mock TodoService for unit testing
- todo_cli: TodoCLI instance with mocked service
- mock_console: Mock Rich Console for testing output
- mock_prompt: Mock Rich Prompt for testing user input
- cli_with_mocked_console: TodoCLI with mocked console attached

Helper Functions:
- create_mock_todo: Create mock todo objects with standard attributes
- create_test_todo_item: Create real TodoItem instances for testing
- setup_mock_prompt_sequence: Configure mock prompt with user inputs
- assert_console_message_contains: Check console output for expected messages
- assert_error_message_displayed: Check if error messages were displayed
- assert_success_message_displayed: Check if success messages were displayed
- setup_update_todo_test: Complete mock setup for update todo workflows
- create_update_todo_inputs: Generate standard update todo user inputs
- create_add_todo_inputs: Generate standard add todo user inputs
- setup_add_todo_test: Complete mock setup for add todo workflows

These utilities help reduce test code duplication and provide consistent
patterns for testing CLI interactions with proper mocking and assertions.
"""

from datetime import datetime
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import pytest

from src.domain.models import TodoItem
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


# Helper functions for test setup
def create_mock_todo(
    title: str = "Test Todo",
    description: str | None = "Test Description",
    due_date: datetime | None = None,
    completed: bool = False,
    todo_id: UUID | None = None,
) -> Mock:
    """Create a mock todo with common attributes for testing."""
    mock_todo = Mock()
    mock_todo.id = todo_id or uuid4()
    mock_todo.title = title
    mock_todo.description = description
    mock_todo.due_date = due_date
    mock_todo.completed = completed
    return mock_todo


def create_test_todo_item(
    title: str = "Test Todo",
    description: str | None = "Test Description",
    due_date: datetime | None = None,
    completed: bool = False,
    todo_id: UUID | None = None,
) -> TodoItem:
    """Create a real TodoItem instance for testing."""
    if due_date is None:
        due_date = datetime(2025, 12, 31)

    todo_data = {
        "title": title,
        "description": description,
        "due_date": due_date,
        "completed": completed,
    }

    if todo_id is not None:
        todo_data["id"] = todo_id

    return TodoItem(**todo_data)


def setup_mock_prompt_sequence(mock_prompt, inputs: list[str]) -> None:
    """Set up mock prompt with a sequence of user inputs."""
    mock_prompt.side_effect = inputs


def assert_console_message_contains(console_mock, expected_text: str, case_sensitive: bool = False) -> bool:
    """Check if console.print was called with a message containing expected text."""
    print_calls = console_mock.print.call_args_list
    text_to_search = expected_text if case_sensitive else expected_text.lower()

    for call in print_calls:
        call_str = str(call)
        call_text = call_str if case_sensitive else call_str.lower()
        if text_to_search in call_text:
            return True

    return False


def assert_error_message_displayed(console_mock) -> bool:
    """Check if any error message was displayed to console."""
    return assert_console_message_contains(console_mock, "error")


def assert_success_message_displayed(console_mock) -> bool:
    """Check if any success message was displayed to console."""
    return assert_console_message_contains(console_mock, "success")


def setup_update_todo_test(
    mock_prompt,
    cli_with_mocked_console,
    todo_id: UUID,
    current_todo: TodoItem,
    updated_todo: TodoItem,
    user_inputs: list[str],
) -> None:
    """Set up common mock configuration for update todo tests."""
    setup_mock_prompt_sequence(mock_prompt, user_inputs)
    cli_with_mocked_console.service.repository.find_by_id.return_value = current_todo
    cli_with_mocked_console.service.update_todo.return_value = updated_todo


def create_update_todo_inputs(
    todo_id: UUID,
    new_title: str = "Updated Title",
    new_description: str = "Updated Description",
    new_due_date: str = "2026-01-15",
) -> list[str]:
    """Create standard user inputs for update todo workflow."""
    return [
        str(todo_id),
        new_title,
        new_description,
        new_due_date,
    ]


def create_add_todo_inputs(
    title: str = "Test Todo", description: str = "Test Description", due_date: str = "2025-12-31"
) -> list[str]:
    """Create standard user inputs for add todo workflow."""
    return [title, description, due_date]


def setup_add_todo_test(mock_prompt, cli_with_mocked_console, user_inputs: list[str], created_todo: Mock) -> None:
    """Set up common mock configuration for add todo tests."""
    setup_mock_prompt_sequence(mock_prompt, user_inputs)
    cli_with_mocked_console.service.create_todo.return_value = created_todo
