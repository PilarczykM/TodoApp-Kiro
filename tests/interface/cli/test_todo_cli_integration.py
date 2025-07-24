"""
Integration tests for TodoCLI with real service dependencies.

This module contains integration tests that validate complete CLI workflows
with minimal mocking, using real service instances and file-based storage.
These tests focus on end-to-end functionality and data persistence.

Test Categories:
- TestTodoCLIEndToEndWorkflows: Complete workflow testing with real services
- TestTodoCLIDataPersistence: Data integrity and persistence across CLI instances

Key Features:
- Uses real JSONTodoRepository with temporary files
- Minimal mocking (only console output and user input)
- Tests complete workflows from user input to data persistence
- Validates error handling with real service layer exceptions
- Ensures data consistency across multiple operations

These integration tests complement the unit tests by providing confidence
that the CLI works correctly with real dependencies and actual file I/O.
"""

from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest

from src.application.services.todo_service import TodoService
from src.infrastructure.persistence.json_repository import JSONTodoRepository
from src.interface.cli.todo_cli import TodoCLI


@pytest.fixture
def temp_json_file(tmp_path):
    """Create a temporary JSON file for testing."""
    return tmp_path / "test_todos.json"


@pytest.fixture
def real_repository(temp_json_file):
    """Create a real JSON repository with temporary file."""
    return JSONTodoRepository(str(temp_json_file))


@pytest.fixture
def real_service(real_repository):
    """Create a real TodoService with real repository."""
    return TodoService(real_repository)


@pytest.fixture
def cli_with_real_service(real_service):
    """Create TodoCLI with real service dependencies."""
    return TodoCLI(real_service)


class TestTodoCLIEndToEndWorkflows:
    """Integration tests for complete CLI workflows."""

    def test_complete_add_and_list_workflow(self, cli_with_real_service):
        """Test complete workflow of adding a todo and then listing it."""
        with (
            patch("rich.prompt.Prompt.ask") as mock_prompt,
            patch.object(cli_with_real_service, "console") as mock_console,
        ):
            # Mock user inputs for adding a todo
            mock_prompt.side_effect = [
                "Integration Test Todo",  # title
                "Test description for integration",  # description
                "2025-12-31",  # due_date
            ]

            # Execute add todo workflow
            result = cli_with_real_service.add_todo()

            assert result is True
            mock_console.print.assert_called()

            # Verify todo was actually saved by listing todos
            todos = cli_with_real_service.service.get_all_todos()
            assert len(todos) == 1
            assert todos[0].title == "Integration Test Todo"
            assert todos[0].description == "Test description for integration"

    def test_add_update_complete_workflow(self, cli_with_real_service):
        """Test workflow of adding, updating, and completing a todo."""
        with (
            patch("rich.prompt.Prompt.ask") as mock_prompt,
            patch.object(cli_with_real_service, "console"),
        ):
            # Step 1: Add a todo
            mock_prompt.side_effect = [
                "Original Title",
                "Original Description",
                "2025-12-31",
            ]

            cli_with_real_service.add_todo()
            todos = cli_with_real_service.service.get_all_todos()
            assert len(todos) == 1
            todo_id = todos[0].id

            # Step 2: Update the todo
            mock_prompt.side_effect = [
                str(todo_id),
                "Updated Title",
                "Updated Description",
                "2026-01-15",
            ]

            result = cli_with_real_service.update_todo()
            assert result is True

            # Verify update
            updated_todos = cli_with_real_service.service.get_all_todos()
            assert len(updated_todos) == 1
            assert updated_todos[0].title == "Updated Title"
            assert updated_todos[0].description == "Updated Description"
            assert not updated_todos[0].completed

            # Step 3: Complete the todo
            mock_prompt.side_effect = [str(todo_id)]

            result = cli_with_real_service.complete_todo()
            assert result is True

            # Verify completion
            completed_todos = cli_with_real_service.service.get_all_todos()
            assert len(completed_todos) == 1
            assert completed_todos[0].completed

    def test_add_and_delete_workflow(self, cli_with_real_service):
        """Test workflow of adding a todo and then deleting it."""
        with (
            patch("rich.prompt.Prompt.ask") as mock_prompt,
            patch.object(cli_with_real_service, "console"),
        ):
            # Step 1: Add a todo
            mock_prompt.side_effect = [
                "Todo to Delete",
                "This will be deleted",
                "",
            ]

            cli_with_real_service.add_todo()
            todos = cli_with_real_service.service.get_all_todos()
            assert len(todos) == 1
            todo_id = todos[0].id

            # Step 2: Delete the todo
            mock_prompt.side_effect = [
                str(todo_id),  # todo ID
                "yes",  # confirmation
            ]

            result = cli_with_real_service.delete_todo()
            assert result is True

            # Verify deletion
            remaining_todos = cli_with_real_service.service.get_all_todos()
            assert len(remaining_todos) == 0

    def test_list_todos_with_multiple_items(self, cli_with_real_service):
        """Test listing multiple todos with various states."""
        # Add multiple todos directly through service
        service = cli_with_real_service.service

        # Add completed todo
        completed_todo = service.create_todo(
            title="Completed Task", description="This is done", due_date=datetime(2025, 11, 30)
        )
        service.complete_todo(completed_todo.id)

        # Add pending todo
        service.create_todo(title="Pending Task", description="This is pending", due_date=datetime(2025, 12, 31))

        # Add todo without due date
        service.create_todo(title="No Due Date Task", description="No deadline")

        with patch.object(cli_with_real_service, "console") as mock_console:
            result = cli_with_real_service.list_todos()
            assert result is True
            mock_console.print.assert_called()

            # Verify all todos are retrieved
            todos = service.get_all_todos()
            assert len(todos) == 3

    def test_error_handling_with_real_service(self, cli_with_real_service):
        """Test error handling with real service layer."""
        with (
            patch("rich.prompt.Prompt.ask") as mock_prompt,
            patch.object(cli_with_real_service, "console") as mock_console,
        ):
            # Test update with non-existent ID
            fake_id = uuid4()
            mock_prompt.side_effect = [str(fake_id)]

            result = cli_with_real_service.update_todo()
            assert result is True  # Should continue loop
            mock_console.print.assert_called()

            # Test delete with non-existent ID
            mock_prompt.side_effect = [str(fake_id)]

            result = cli_with_real_service.delete_todo()
            assert result is True  # Should continue loop
            mock_console.print.assert_called()

            # Test complete with non-existent ID
            mock_prompt.side_effect = [str(fake_id)]

            result = cli_with_real_service.complete_todo()
            assert result is True  # Should continue loop
            mock_console.print.assert_called()


class TestTodoCLIDataPersistence:
    """Test data persistence across CLI operations."""

    def test_data_persistence_across_cli_instances(self, temp_json_file, real_repository):
        """Test that data persists across different CLI instances."""
        # Create first CLI instance and add data
        service1 = TodoService(real_repository)
        cli1 = TodoCLI(service1)

        with patch("rich.prompt.Prompt.ask") as mock_prompt, patch.object(cli1, "console"):
            mock_prompt.side_effect = [
                "Persistent Todo",
                "This should persist",
                "2025-12-31",
            ]

            cli1.add_todo()

        # Create second CLI instance and verify data
        repository2 = JSONTodoRepository(str(temp_json_file))
        service2 = TodoService(repository2)

        todos = service2.get_all_todos()
        assert len(todos) == 1
        assert todos[0].title == "Persistent Todo"
        assert todos[0].description == "This should persist"

    def test_file_operations_integrity(self, cli_with_real_service):
        """Test that file operations maintain data integrity."""
        service = cli_with_real_service.service

        # Add multiple todos
        todo1 = service.create_todo(title="Todo 1", description="First todo")
        todo2 = service.create_todo(title="Todo 2", description="Second todo")
        todo3 = service.create_todo(title="Todo 3", description="Third todo")

        # Update one todo
        service.update_todo(todo2.id, title="Updated Todo 2")

        # Complete one todo
        service.complete_todo(todo3.id)

        # Delete one todo
        service.delete_todo(todo1.id)

        # Verify final state
        final_todos = service.get_all_todos()
        assert len(final_todos) == 2

        # Find todos by title
        titles = [todo.title for todo in final_todos]
        assert "Updated Todo 2" in titles
        assert "Todo 3" in titles
        assert "Todo 1" not in titles

        # Verify completion status
        todo3_final = next(todo for todo in final_todos if todo.title == "Todo 3")
        assert todo3_final.completed
