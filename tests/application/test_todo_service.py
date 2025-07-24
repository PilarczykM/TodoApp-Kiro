"""
Tests for TodoService application service.

This module contains tests for the TodoService class that orchestrates
domain objects to fulfill use cases following TDD principles.
"""

from unittest.mock import Mock
from uuid import UUID

import pytest

from src.application.services.todo_service import TodoService
from src.domain.exceptions import TodoDomainError, ValidationError
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
