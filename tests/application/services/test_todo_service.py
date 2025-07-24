"""
Tests for TodoService application service.

This module contains tests for the TodoService class that orchestrates
domain objects to fulfill use cases following TDD principles.
"""

from unittest.mock import Mock
from uuid import UUID

import pytest

from src.application.services.todo_service import TodoService
from src.domain.exceptions import TodoDomainError, TodoNotFoundError, ValidationError
from src.domain.models import TodoItem
from src.infrastructure.persistence.repository import TodoRepository


class TestTodoService:
    """Test suite for TodoService application service."""

    def setup_method(self):
        """Set up test dependencies for each test method."""
        self.mock_repo = Mock(spec=TodoRepository)
        self.service = TodoService(self.mock_repo)

    def test_should_initialize_with_repository_dependency(self):
        """Test that TodoService initializes correctly with repository dependency."""
        # Arrange & Act
        service = TodoService(self.mock_repo)

        # Assert
        assert service.repository is self.mock_repo

    def test_should_raise_error_when_initialized_without_repository(self):
        """Test that TodoService raises error when initialized without repository."""
        # Act & Assert
        with pytest.raises(TypeError):
            TodoService()

    def test_should_accept_repository_interface_implementation(self):
        """Test that TodoService accepts any TodoRepository implementation."""
        # Arrange
        mock_json_repo = Mock(spec=TodoRepository)
        mock_xml_repo = Mock(spec=TodoRepository)

        # Act
        service1 = TodoService(mock_json_repo)
        service2 = TodoService(mock_xml_repo)

        # Assert
        assert service1.repository is mock_json_repo
        assert service2.repository is mock_xml_repo

    def test_should_store_repository_reference_for_use_cases(self):
        """Test that TodoService stores repository reference for use case methods."""
        # Arrange
        mock_repo = Mock(spec=TodoRepository)

        # Act
        service = TodoService(mock_repo)

        # Assert
        assert hasattr(service, "repository")
        assert service.repository is mock_repo

    def test_should_be_ready_for_use_case_orchestration(self):
        """Test that TodoService is properly initialized for orchestrating use cases."""
        # Arrange & Act
        service = TodoService(self.mock_repo)

        # Assert
        assert service is not None
        assert service.repository is not None
        assert isinstance(service.repository, Mock)  # Mock implements TodoRepository spec


class TestCreateTodoUseCase:
    """Test suite for create todo use case."""

    def setup_method(self):
        """Set up test dependencies for each test method."""
        self.mock_repo = Mock(spec=TodoRepository)
        self.service = TodoService(self.mock_repo)

    def test_should_create_todo_with_valid_data(self):
        """Test creating a todo with valid title and description."""
        # Arrange
        title = "Buy groceries"
        description = "Milk, eggs, bread"

        # Act
        result = self.service.create_todo(title, description)

        # Assert
        assert result is not None
        assert result.title == title
        assert result.description == description
        assert result.completed is False
        assert result.created_at is not None
        self.mock_repo.save.assert_called_once()

    def test_should_create_todo_with_only_title(self):
        """Test creating a todo with only title (description optional)."""
        # Arrange
        title = "Important task"

        # Act
        result = self.service.create_todo(title)

        # Assert
        assert result is not None
        assert result.title == title
        assert result.description is None
        assert result.completed is False
        self.mock_repo.save.assert_called_once()

    def test_should_create_todo_with_due_date(self):
        """Test creating a todo with due date."""
        # Arrange
        from datetime import datetime, timedelta

        title = "Submit report"
        description = "Monthly status report"
        due_date = datetime.now() + timedelta(days=7)

        # Act
        result = self.service.create_todo(title, description, due_date)

        # Assert
        assert result is not None
        assert result.title == title
        assert result.description == description
        assert result.due_date == due_date
        self.mock_repo.save.assert_called_once()

    def test_should_raise_validation_error_for_empty_title(self):
        """Test that empty title raises validation error."""
        # Arrange
        title = ""
        description = "Some description"

        # Act & Assert
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            self.service.create_todo(title, description)

        self.mock_repo.save.assert_not_called()

    def test_should_raise_validation_error_for_whitespace_title(self):
        """Test that whitespace-only title raises validation error."""
        # Arrange
        title = "   "
        description = "Some description"

        # Act & Assert
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            self.service.create_todo(title, description)

        self.mock_repo.save.assert_not_called()

    def test_should_raise_validation_error_for_past_due_date(self):
        """Test that past due date raises validation error."""
        # Arrange
        from datetime import datetime, timedelta

        title = "Valid title"
        description = "Valid description"
        past_due_date = datetime.now() - timedelta(days=1)

        # Act & Assert
        with pytest.raises(ValidationError, match="Due date cannot be in the past"):
            self.service.create_todo(title, description, past_due_date)

        self.mock_repo.save.assert_not_called()

    def test_should_handle_repository_save_errors(self):
        """Test handling of repository save errors."""
        # Arrange
        title = "Valid title"
        description = "Valid description"
        self.mock_repo.save.side_effect = TodoDomainError("Save failed")

        # Act & Assert
        with pytest.raises(TodoDomainError, match="Save failed"):
            self.service.create_todo(title, description)

        self.mock_repo.save.assert_called_once()

    def test_should_return_todo_with_generated_id(self):
        """Test that created todo has a generated UUID."""
        # Arrange
        title = "Test todo"

        # Act
        result = self.service.create_todo(title)

        # Assert
        assert result.id is not None
        assert isinstance(result.id, UUID)

    def test_should_set_created_and_updated_timestamps(self):
        """Test that created todo has proper timestamps."""
        # Arrange
        from datetime import datetime

        title = "Test todo"
        before_creation = datetime.now()

        # Act
        result = self.service.create_todo(title)

        # Assert
        after_creation = datetime.now()
        assert before_creation <= result.created_at <= after_creation
        assert before_creation <= result.updated_at <= after_creation
        assert result.created_at == result.updated_at  # Should be same on creation


class TestListTodosUseCase:
    """Test suite for list todos use case."""

    def setup_method(self):
        """Set up test dependencies for each test method."""
        self.mock_repo = Mock(spec=TodoRepository)
        self.service = TodoService(self.mock_repo)

    def test_should_retrieve_all_todos_when_todos_exist(self):
        """Test retrieving all todos when repository contains todos."""
        # Arrange
        todo1 = TodoItem(title="Task 1", description="First task")
        todo2 = TodoItem(title="Task 2", description="Second task")
        expected_todos = [todo1, todo2]
        self.mock_repo.find_all.return_value = expected_todos

        # Act
        result = self.service.get_all_todos()

        # Assert
        assert result == expected_todos
        assert len(result) == 2
        assert result[0].title == "Task 1"
        assert result[1].title == "Task 2"
        self.mock_repo.find_all.assert_called_once()

    def test_should_return_empty_list_when_no_todos_exist(self):
        """Test retrieving todos when repository is empty."""
        # Arrange
        self.mock_repo.find_all.return_value = []

        # Act
        result = self.service.get_all_todos()

        # Assert
        assert result == []
        assert len(result) == 0
        self.mock_repo.find_all.assert_called_once()

    def test_should_handle_repository_find_all_errors(self):
        """Test handling of repository find_all errors."""
        # Arrange
        from src.domain.exceptions import TodoDomainError

        self.mock_repo.find_all.side_effect = TodoDomainError("Database error")

        # Act & Assert
        with pytest.raises(TodoDomainError, match="Database error"):
            self.service.get_all_todos()

        self.mock_repo.find_all.assert_called_once()

    def test_should_return_todos_with_all_properties(self):
        """Test that returned todos contain all expected properties."""
        # Arrange
        from datetime import datetime, timedelta

        due_date = datetime.now() + timedelta(days=1)
        todo = TodoItem(title="Complete task", description="Task description", due_date=due_date, completed=True)
        self.mock_repo.find_all.return_value = [todo]

        # Act
        result = self.service.get_all_todos()

        # Assert
        assert len(result) == 1
        returned_todo = result[0]
        assert returned_todo.title == "Complete task"
        assert returned_todo.description == "Task description"
        assert returned_todo.due_date == due_date
        assert returned_todo.completed is True
        assert returned_todo.id is not None
        assert returned_todo.created_at is not None
        assert returned_todo.updated_at is not None

    def test_should_preserve_todo_order_from_repository(self):
        """Test that todos are returned in the same order as from repository."""
        # Arrange
        todo1 = TodoItem(title="First")
        todo2 = TodoItem(title="Second")
        todo3 = TodoItem(title="Third")
        expected_order = [todo1, todo2, todo3]
        self.mock_repo.find_all.return_value = expected_order

        # Act
        result = self.service.get_all_todos()

        # Assert
        assert result == expected_order
        for i, todo in enumerate(result):
            assert todo.title == expected_order[i].title


class TestUpdateTodoUseCase:
    """Test suite for update todo use case."""

    def setup_method(self):
        """Set up test dependencies for each test method."""
        self.mock_repo = Mock(spec=TodoRepository)
        self.service = TodoService(self.mock_repo)

    def test_should_update_todo_with_valid_id_and_data(self):
        """Test updating a todo with valid ID and data."""
        # Arrange
        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Old title", description="Old description")
        existing_todo.id = todo_id
        self.mock_repo.find_by_id.return_value = existing_todo

        # Act
        result = self.service.update_todo(todo_id, title="New title", description="New description")

        # Assert
        assert result is not None
        assert result.title == "New title"
        assert result.description == "New description"
        assert result.id == todo_id
        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.update.assert_called_once_with(result)

    def test_should_update_todo_with_partial_data(self):
        """Test updating a todo with only some fields."""
        # Arrange
        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Old title", description="Old description")
        existing_todo.id = todo_id
        self.mock_repo.find_by_id.return_value = existing_todo

        # Act
        result = self.service.update_todo(todo_id, title="New title")

        # Assert
        assert result.title == "New title"
        assert result.description == "Old description"  # Should remain unchanged
        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.update.assert_called_once_with(result)

    def test_should_update_todo_due_date(self):
        """Test updating a todo's due date."""
        # Arrange
        from datetime import datetime, timedelta

        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Task", description="Description")
        existing_todo.id = todo_id
        new_due_date = datetime.now() + timedelta(days=7)
        self.mock_repo.find_by_id.return_value = existing_todo

        # Act
        result = self.service.update_todo(todo_id, due_date=new_due_date)

        # Assert
        assert result.due_date == new_due_date
        assert result.title == "Task"  # Should remain unchanged
        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.update.assert_called_once_with(result)

    def test_should_raise_not_found_error_for_invalid_id(self):
        """Test that invalid todo ID raises TodoNotFoundError."""
        # Arrange
        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        self.mock_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(TodoNotFoundError, match="Todo with ID .* not found"):
            self.service.update_todo(todo_id, title="New title")

        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.update.assert_not_called()

    def test_should_raise_validation_error_for_empty_title(self):
        """Test that empty title raises validation error."""
        # Arrange
        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Old title", description="Description")
        existing_todo.id = todo_id
        self.mock_repo.find_by_id.return_value = existing_todo

        # Act & Assert
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            self.service.update_todo(todo_id, title="")

        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.update.assert_not_called()

    def test_should_raise_validation_error_for_past_due_date(self):
        """Test that past due date raises validation error."""
        # Arrange
        from datetime import datetime, timedelta

        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Task", description="Description")
        existing_todo.id = todo_id
        past_due_date = datetime.now() - timedelta(days=1)
        self.mock_repo.find_by_id.return_value = existing_todo

        # Act & Assert
        with pytest.raises(ValidationError, match="Due date cannot be in the past"):
            self.service.update_todo(todo_id, due_date=past_due_date)

        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.update.assert_not_called()

    def test_should_handle_repository_update_errors(self):
        """Test handling of repository update errors."""
        # Arrange
        from src.domain.exceptions import TodoDomainError

        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Old title", description="Description")
        existing_todo.id = todo_id
        self.mock_repo.find_by_id.return_value = existing_todo
        self.mock_repo.update.side_effect = TodoDomainError("Update failed")

        # Act & Assert
        with pytest.raises(TodoDomainError, match="Update failed"):
            self.service.update_todo(todo_id, title="New title")

        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.update.assert_called_once()

    def test_should_update_timestamps_on_update(self):
        """Test that updated_at timestamp is updated."""
        # Arrange
        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Old title", description="Description")
        existing_todo.id = todo_id
        original_updated_at = existing_todo.updated_at
        self.mock_repo.find_by_id.return_value = existing_todo

        # Act
        result = self.service.update_todo(todo_id, title="New title")

        # Assert
        assert result.updated_at > original_updated_at
        self.mock_repo.update.assert_called_once_with(result)


class TestCompleteTodoUseCase:
    """Test suite for complete todo use case."""

    def setup_method(self):
        """Set up test dependencies for each test method."""
        self.mock_repo = Mock(spec=TodoRepository)
        self.service = TodoService(self.mock_repo)

    def test_should_complete_todo_with_valid_id(self):
        """Test completing a todo with valid ID."""
        # Arrange
        from datetime import datetime

        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Task", description="Description")
        existing_todo.id = todo_id
        existing_todo.completed = False
        self.mock_repo.find_by_id.return_value = existing_todo
        before_completion = datetime.now()

        # Act
        result = self.service.complete_todo(todo_id)

        # Assert
        after_completion = datetime.now()
        assert result is not None
        assert result.completed is True
        assert before_completion <= result.updated_at <= after_completion
        assert result.id == todo_id
        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.update.assert_called_once_with(result)

    def test_should_preserve_other_todo_properties_when_completing(self):
        """Test that completing a todo preserves other properties."""
        # Arrange
        from datetime import datetime, timedelta

        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        due_date = datetime.now() + timedelta(days=1)
        existing_todo = TodoItem(title="Important task", description="Task description", due_date=due_date)
        existing_todo.id = todo_id
        existing_todo.completed = False
        self.mock_repo.find_by_id.return_value = existing_todo

        # Act
        result = self.service.complete_todo(todo_id)

        # Assert
        assert result.title == "Important task"
        assert result.description == "Task description"
        assert result.due_date == due_date
        assert result.completed is True
        assert result.id == todo_id
        self.mock_repo.update.assert_called_once_with(result)

    def test_should_raise_not_found_error_for_invalid_id(self):
        """Test that invalid todo ID raises TodoNotFoundError."""
        # Arrange
        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        self.mock_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(TodoNotFoundError, match="Todo with ID .* not found"):
            self.service.complete_todo(todo_id)

        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.update.assert_not_called()

    def test_should_raise_validation_error_for_already_completed_todo(self):
        """Test that completing an already completed todo raises validation error."""
        # Arrange
        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Task", description="Description")
        existing_todo.id = todo_id
        existing_todo.completed = True  # Already completed
        self.mock_repo.find_by_id.return_value = existing_todo

        # Act & Assert
        with pytest.raises(ValidationError, match="Todo is already completed"):
            self.service.complete_todo(todo_id)

        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.update.assert_not_called()

    def test_should_handle_repository_update_errors(self):
        """Test handling of repository update errors during completion."""
        # Arrange
        from src.domain.exceptions import TodoDomainError

        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Task", description="Description")
        existing_todo.id = todo_id
        existing_todo.completed = False
        self.mock_repo.find_by_id.return_value = existing_todo
        self.mock_repo.update.side_effect = TodoDomainError("Update failed")

        # Act & Assert
        with pytest.raises(TodoDomainError, match="Update failed"):
            self.service.complete_todo(todo_id)

        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.update.assert_called_once()

    def test_should_set_completion_timestamp(self):
        """Test that completion updates the updated_at timestamp."""
        # Arrange
        from datetime import datetime

        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Task", description="Description")
        existing_todo.id = todo_id
        existing_todo.completed = False
        self.mock_repo.find_by_id.return_value = existing_todo
        original_updated_at = existing_todo.updated_at
        before_completion = datetime.now()

        # Act
        result = self.service.complete_todo(todo_id)

        # Assert
        after_completion = datetime.now()
        assert result.updated_at > original_updated_at
        assert before_completion <= result.updated_at <= after_completion
        self.mock_repo.update.assert_called_once_with(result)


class TestDeleteTodoUseCase:
    """Test suite for delete todo use case."""

    def setup_method(self):
        """Set up test dependencies for each test method."""
        self.mock_repo = Mock(spec=TodoRepository)
        self.service = TodoService(self.mock_repo)

    def test_should_delete_todo_with_valid_id(self):
        """Test deleting a todo with valid ID."""
        # Arrange
        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Task to delete", description="Description")
        existing_todo.id = todo_id
        self.mock_repo.find_by_id.return_value = existing_todo

        # Act
        result = self.service.delete_todo(todo_id)

        # Assert
        assert result is None  # Delete should not return anything
        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.delete.assert_called_once_with(todo_id)

    def test_should_raise_not_found_error_for_invalid_id(self):
        """Test that invalid todo ID raises TodoNotFoundError."""
        # Arrange
        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        self.mock_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(TodoNotFoundError, match="Todo with ID .* not found"):
            self.service.delete_todo(todo_id)

        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.delete.assert_not_called()

    def test_should_handle_repository_delete_errors(self):
        """Test handling of repository delete errors."""
        # Arrange
        from src.domain.exceptions import TodoDomainError

        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Task", description="Description")
        existing_todo.id = todo_id
        self.mock_repo.find_by_id.return_value = existing_todo
        self.mock_repo.delete.side_effect = TodoDomainError("Delete failed")

        # Act & Assert
        with pytest.raises(TodoDomainError, match="Delete failed"):
            self.service.delete_todo(todo_id)

        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.delete.assert_called_once_with(todo_id)

    def test_should_verify_todo_exists_before_deletion(self):
        """Test that delete verifies todo exists before attempting deletion."""
        # Arrange
        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Task", description="Description")
        existing_todo.id = todo_id
        self.mock_repo.find_by_id.return_value = existing_todo

        # Act
        self.service.delete_todo(todo_id)

        # Assert
        # Should call find_by_id first to verify existence
        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        # Then call delete
        self.mock_repo.delete.assert_called_once_with(todo_id)

    def test_should_delete_completed_todos(self):
        """Test that completed todos can be deleted."""
        # Arrange
        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        existing_todo = TodoItem(title="Completed task", description="Description")
        existing_todo.id = todo_id
        existing_todo.completed = True
        self.mock_repo.find_by_id.return_value = existing_todo

        # Act
        self.service.delete_todo(todo_id)

        # Assert
        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.delete.assert_called_once_with(todo_id)

    def test_should_delete_todos_with_due_dates(self):
        """Test that todos with due dates can be deleted."""
        # Arrange
        from datetime import datetime, timedelta

        todo_id = UUID("12345678-1234-5678-9012-123456789012")
        due_date = datetime.now() + timedelta(days=1)
        existing_todo = TodoItem(title="Task with due date", description="Description", due_date=due_date)
        existing_todo.id = todo_id
        self.mock_repo.find_by_id.return_value = existing_todo

        # Act
        self.service.delete_todo(todo_id)

        # Assert
        self.mock_repo.find_by_id.assert_called_once_with(todo_id)
        self.mock_repo.delete.assert_called_once_with(todo_id)
