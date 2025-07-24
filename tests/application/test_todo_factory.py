"""
Tests for TodoItemFactory and PydanticErrorConverter.

This module contains tests for the factory pattern implementation
that eliminates code duplication in TodoItem creation and validation.
"""

from datetime import datetime, timedelta

import pytest

from src.application.services.todo_factory import TodoItemFactory, _convert_pydantic_error
from src.domain.exceptions import ValidationError
from src.domain.models import TodoItem


class TestPydanticErrorConverter:
    """Test suite for _convert_pydantic_error function."""

    def test_should_convert_string_too_short_error_for_title(self):
        """Test conversion of string_too_short error for title field."""
        # Arrange & Act
        try:
            TodoItem(title="")
        except Exception as e:
            result = _convert_pydantic_error(e)

        # Assert
        assert isinstance(result, ValidationError)
        assert "Title cannot be empty" in str(result)

    def test_should_convert_value_error_from_custom_validator(self):
        """Test conversion of value_error from custom field validator."""
        # Arrange & Act
        try:
            TodoItem(title="   ")  # Whitespace only
        except Exception as e:
            result = _convert_pydantic_error(e)

        # Assert
        assert isinstance(result, ValidationError)
        assert "Title cannot be empty" in str(result)

    def test_should_convert_past_due_date_error(self):
        """Test conversion of past due date validation error."""
        # Arrange & Act
        past_date = datetime.now() - timedelta(days=1)
        try:
            TodoItem(title="Test", due_date=past_date)
        except Exception as e:
            result = _convert_pydantic_error(e)

        # Assert
        assert isinstance(result, ValidationError)
        assert "Due date cannot be in the past" in str(result)

    def test_should_convert_missing_field_error(self):
        """Test conversion of missing required field error."""
        # Arrange & Act
        try:
            TodoItem()  # Missing required title
        except Exception as e:
            result = _convert_pydantic_error(e)

        # Assert
        assert isinstance(result, ValidationError)
        assert "title: Field is required" in str(result)

    def test_should_handle_multiple_validation_errors(self):
        """Test conversion of multiple validation errors."""
        # Arrange & Act
        past_date = datetime.now() - timedelta(days=1)
        try:
            TodoItem(title="", due_date=past_date)
        except Exception as e:
            result = _convert_pydantic_error(e)

        # Assert
        assert isinstance(result, ValidationError)
        error_message = str(result)
        assert "Title cannot be empty" in error_message
        assert "Due date cannot be in the past" in error_message

    def test_should_handle_generic_error_types(self):
        """Test conversion of generic error types with fallback handling."""
        # This test would require a custom error type that's not specifically handled
        # For now, we'll test the fallback behavior with a known error type
        try:
            TodoItem(title="x" * 201)  # Exceeds max_length
        except Exception as e:
            result = _convert_pydantic_error(e)

        # Assert
        assert isinstance(result, ValidationError)
        assert "title:" in str(result)


class TestTodoItemFactory:
    """Test suite for TodoItemFactory."""

    def test_should_create_todo_item_with_valid_data(self):
        """Test creating a TodoItem with valid data."""
        # Arrange
        title = "Test todo"
        description = "Test description"
        due_date = datetime.now() + timedelta(days=1)

        # Act
        result = TodoItemFactory.create_todo_item(title=title, description=description, due_date=due_date)

        # Assert
        assert isinstance(result, TodoItem)
        assert result.title == title
        assert result.description == description
        assert result.due_date == due_date
        assert result.completed is False
        assert result.id is not None

    def test_should_create_todo_item_with_minimal_data(self):
        """Test creating a TodoItem with only required fields."""
        # Arrange
        title = "Minimal todo"

        # Act
        result = TodoItemFactory.create_todo_item(title=title)

        # Assert
        assert isinstance(result, TodoItem)
        assert result.title == title
        assert result.description is None
        assert result.due_date is None
        assert result.completed is False

    def test_should_raise_validation_error_for_invalid_data(self):
        """Test that factory raises ValidationError for invalid data."""
        # Act & Assert
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            TodoItemFactory.create_todo_item(title="")

    def test_should_raise_validation_error_for_past_due_date(self):
        """Test that factory raises ValidationError for past due date."""
        # Arrange
        past_date = datetime.now() - timedelta(days=1)

        # Act & Assert
        with pytest.raises(ValidationError, match="Due date cannot be in the past"):
            TodoItemFactory.create_todo_item(title="Test", due_date=past_date)

    def test_should_update_todo_item_with_valid_data(self):
        """Test updating a TodoItem with valid data."""
        # Arrange
        existing_todo = TodoItem(title="Original", description="Original desc")
        update_data = {
            "title": "Updated title",
            "description": "Updated description",
            "due_date": datetime.now() + timedelta(days=1),
            "completed": False,
        }

        # Act
        result = TodoItemFactory.update_todo_item(existing_todo, update_data)

        # Assert
        assert isinstance(result, TodoItem)
        assert result.title == "Updated title"
        assert result.description == "Updated description"
        assert result.id == existing_todo.id
        assert result.created_at == existing_todo.created_at
        assert result.updated_at >= existing_todo.updated_at

    def test_should_preserve_immutable_fields_during_update(self):
        """Test that update preserves immutable fields like id and created_at."""
        # Arrange
        existing_todo = TodoItem(title="Original", description="Original desc")
        original_id = existing_todo.id
        original_created_at = existing_todo.created_at

        update_data = {
            "title": "Updated title",
            "description": existing_todo.description,
            "due_date": existing_todo.due_date,
            "completed": existing_todo.completed,
        }

        # Act
        result = TodoItemFactory.update_todo_item(existing_todo, update_data)

        # Assert
        assert result.id == original_id
        assert result.created_at == original_created_at
        assert result.title == "Updated title"

    def test_should_raise_validation_error_for_invalid_update_data(self):
        """Test that update raises ValidationError for invalid data."""
        # Arrange
        existing_todo = TodoItem(title="Original", description="Original desc")
        update_data = {
            "title": "",  # Invalid empty title
            "description": existing_todo.description,
            "due_date": existing_todo.due_date,
            "completed": existing_todo.completed,
        }

        # Act & Assert
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            TodoItemFactory.update_todo_item(existing_todo, update_data)

    def test_should_validate_todo_data_without_creating_instance(self):
        """Test validation-only functionality."""
        # Arrange
        valid_data = {"title": "Valid title", "description": "Valid description"}
        invalid_data = {"title": "", "description": "Valid description"}

        # Act & Assert - Valid data should not raise
        TodoItemFactory.validate_todo_data(**valid_data)

        # Invalid data should raise
        with pytest.raises(ValidationError):
            TodoItemFactory.validate_todo_data(**invalid_data)

    def test_should_handle_additional_kwargs_in_create(self):
        """Test that factory handles additional keyword arguments."""
        # Arrange
        title = "Test todo"
        completed = True

        # Act
        result = TodoItemFactory.create_todo_item(title=title, completed=completed)

        # Assert
        assert result.title == title
        assert result.completed is True
