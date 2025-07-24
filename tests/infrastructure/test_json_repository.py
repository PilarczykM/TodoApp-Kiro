"""
Tests for JSONTodoRepository implementation.

This module contains tests that verify the JSON-based repository
implementation follows the repository contract and handles file
operations correctly.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest

from src.domain.exceptions import TodoDomainError, TodoNotFoundError
from src.domain.models import TodoItem
from src.infrastructure.persistence.json_repository import JSONTodoRepository


class TestJSONTodoRepository:
    """Test suite for JSONTodoRepository implementation."""

    def setup_method(self):
        """Set up test environment with temporary file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as temp_file:
            self.temp_path = Path(temp_file.name)
        self.repo = JSONTodoRepository(str(self.temp_path))

    def teardown_method(self):
        """Clean up temporary file after each test."""
        if self.temp_path.exists():
            self.temp_path.unlink()

    def test_should_create_repository_with_file_path(self):
        """Should create JSONTodoRepository with file path."""
        repo = JSONTodoRepository("test.json")
        assert isinstance(repo, JSONTodoRepository)

    def test_should_create_empty_json_file_if_not_exists(self):
        """Should create empty JSON file if it doesn't exist."""
        # Remove the temp file to test creation
        self.temp_path.unlink()

        # Create repository - should create the file
        JSONTodoRepository(str(self.temp_path))

        # File should exist and contain empty list
        assert self.temp_path.exists()
        with open(self.temp_path) as f:
            data = json.load(f)
        assert data == []

    def test_should_save_todo_item_to_json_file(self):
        """Should save a todo item to JSON file."""
        todo = TodoItem(title="Test Todo", description="Test description")

        self.repo.save(todo)

        # Verify file contains the todo
        with open(self.temp_path) as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["title"] == "Test Todo"
        assert data[0]["description"] == "Test description"
        assert data[0]["completed"] is False

    def test_should_find_todo_by_id(self):
        """Should find todo item by ID."""
        todo = TodoItem(title="Findable Todo")
        self.repo.save(todo)

        found_todo = self.repo.find_by_id(todo.id)

        assert found_todo is not None
        assert found_todo.id == todo.id
        assert found_todo.title == "Findable Todo"

    def test_should_return_none_when_todo_not_found(self):
        """Should return None when todo ID doesn't exist."""
        non_existent_id = uuid4()

        result = self.repo.find_by_id(non_existent_id)

        assert result is None

    def test_should_find_all_todos(self):
        """Should return all todos from repository."""
        todo1 = TodoItem(title="First Todo")
        todo2 = TodoItem(title="Second Todo")

        self.repo.save(todo1)
        self.repo.save(todo2)

        all_todos = self.repo.find_all()

        assert len(all_todos) == 2
        titles = [todo.title for todo in all_todos]
        assert "First Todo" in titles
        assert "Second Todo" in titles

    def test_should_return_empty_list_when_no_todos(self):
        """Should return empty list when no todos exist."""
        all_todos = self.repo.find_all()

        assert all_todos == []

    def test_should_update_existing_todo(self):
        """Should update an existing todo item."""
        todo = TodoItem(title="Original Title")
        self.repo.save(todo)

        # Update the todo
        todo.update_details(title="Updated Title")
        self.repo.update(todo)

        # Verify update
        updated_todo = self.repo.find_by_id(todo.id)
        assert updated_todo.title == "Updated Title"

    def test_should_raise_error_when_updating_non_existent_todo(self):
        """Should raise TodoNotFoundError when updating non-existent todo."""
        todo = TodoItem(title="Non-existent Todo")

        with pytest.raises(TodoNotFoundError):
            self.repo.update(todo)

    def test_should_delete_todo_by_id(self):
        """Should delete todo item by ID."""
        todo = TodoItem(title="To be deleted")
        self.repo.save(todo)

        # Verify it exists
        assert self.repo.exists(todo.id) is True

        # Delete it
        self.repo.delete(todo.id)

        # Verify it's gone
        assert self.repo.exists(todo.id) is False
        assert self.repo.find_by_id(todo.id) is None

    def test_should_raise_error_when_deleting_non_existent_todo(self):
        """Should raise TodoNotFoundError when deleting non-existent todo."""
        non_existent_id = uuid4()

        with pytest.raises(TodoNotFoundError):
            self.repo.delete(non_existent_id)

    def test_should_check_if_todo_exists(self):
        """Should correctly check if todo exists."""
        todo = TodoItem(title="Existing Todo")
        self.repo.save(todo)

        assert self.repo.exists(todo.id) is True
        assert self.repo.exists(uuid4()) is False

    def test_should_handle_json_serialization_of_datetime(self):
        """Should properly serialize and deserialize datetime fields."""
        due_date = datetime(2025, 12, 31, 23, 59, 59)
        todo = TodoItem(title="Todo with date", due_date=due_date)

        self.repo.save(todo)
        retrieved_todo = self.repo.find_by_id(todo.id)

        assert retrieved_todo.due_date == due_date

    def test_should_handle_json_serialization_of_uuid(self):
        """Should properly serialize and deserialize UUID fields."""
        todo = TodoItem(title="Todo with UUID")
        original_id = todo.id

        self.repo.save(todo)
        retrieved_todo = self.repo.find_by_id(original_id)

        assert retrieved_todo.id == original_id
        assert isinstance(retrieved_todo.id, type(original_id))

    def test_should_preserve_todo_completion_status(self):
        """Should preserve completion status through save/load cycle."""
        todo = TodoItem(title="Completable Todo")
        todo.mark_completed()

        self.repo.save(todo)
        retrieved_todo = self.repo.find_by_id(todo.id)

        assert retrieved_todo.completed is True

    def test_should_handle_file_corruption_gracefully(self):
        """Should handle corrupted JSON file gracefully."""
        # Write invalid JSON to file
        with open(self.temp_path, "w") as f:
            f.write("invalid json content")

        with pytest.raises(TodoDomainError):
            self.repo.find_all()

    def test_should_handle_permission_errors(self):
        """Should handle file permission errors gracefully."""
        # Make file read-only
        os.chmod(self.temp_path, 0o444)

        todo = TodoItem(title="Permission Test")

        with pytest.raises(TodoDomainError):
            self.repo.save(todo)

        # Restore permissions for cleanup
        os.chmod(self.temp_path, 0o644)

    def test_should_maintain_data_consistency_across_operations(self):
        """Should maintain data consistency across multiple operations."""
        # Create multiple todos
        todos = [TodoItem(title=f"Todo {i}", description=f"Description {i}") for i in range(5)]

        # Save all todos
        for todo in todos:
            self.repo.save(todo)

        # Verify all are saved
        all_todos = self.repo.find_all()
        assert len(all_todos) == 5

        # Update one todo
        todos[0].update_details(title="Updated Todo 0")
        self.repo.update(todos[0])

        # Delete one todo
        self.repo.delete(todos[1].id)

        # Verify final state
        final_todos = self.repo.find_all()
        assert len(final_todos) == 4

        updated_todo = self.repo.find_by_id(todos[0].id)
        assert updated_todo.title == "Updated Todo 0"

        deleted_todo = self.repo.find_by_id(todos[1].id)
        assert deleted_todo is None

    def test_should_handle_empty_file_initialization(self):
        """Should handle initialization with empty file."""
        # Create empty file
        with open(self.temp_path, "w") as f:
            f.write("")

        # Should initialize with empty list
        repo = JSONTodoRepository(str(self.temp_path))
        todos = repo.find_all()
        assert todos == []

    def test_should_preserve_field_types_after_serialization(self):
        """Should preserve all field types after JSON serialization."""
        from datetime import timedelta

        future_date = datetime.now() + timedelta(days=1)
        todo = TodoItem(title="Type Test Todo", description="Test description", due_date=future_date, completed=True)

        self.repo.save(todo)
        retrieved_todo = self.repo.find_by_id(todo.id)

        # Check all field types are preserved
        assert isinstance(retrieved_todo.title, str)
        assert isinstance(retrieved_todo.description, str)
        assert isinstance(retrieved_todo.due_date, datetime)
        assert isinstance(retrieved_todo.completed, bool)
        assert isinstance(retrieved_todo.created_at, datetime)
        assert isinstance(retrieved_todo.updated_at, datetime)

    def test_should_create_parent_directory_if_not_exists(self):
        """Should create parent directory if it doesn't exist."""
        nested_path = self.temp_path.parent / "nested" / "deep" / "test.json"

        # Create repository with nested path
        JSONTodoRepository(str(nested_path))

        # Should create the file and parent directories
        assert nested_path.exists()
        assert nested_path.parent.exists()

    def test_should_handle_non_list_data_in_json_file(self):
        """Should handle non-list data in JSON file by returning empty list."""
        # Write non-list data to file
        with open(self.temp_path, "w") as f:
            json.dump({"not": "a list"}, f)

        todos = self.repo.find_all()
        assert todos == []

    def test_should_handle_json_serializer_error(self):
        """Should raise TypeError for non-serializable objects in JSON serializer."""

        # Test the _json_serializer method directly
        class NonSerializable:
            pass

        with pytest.raises(TypeError, match="Object of type .* is not JSON serializable"):
            self.repo._json_serializer(NonSerializable())

    def test_should_handle_data_conversion_errors_in_dict_to_todo(self):
        """Should handle data conversion errors when converting dict to TodoItem."""
        # Create invalid data that will cause conversion errors
        invalid_data = {
            "id": "invalid-uuid",  # Invalid UUID format
            "title": "Test",
            "completed": False,
            "created_at": "invalid-date",  # Invalid date format
            "updated_at": "2025-01-01T00:00:00",
        }

        with pytest.raises(TodoDomainError, match="Failed to convert data to TodoItem"):
            self.repo._dict_to_todo(invalid_data)

    def test_should_handle_missing_required_fields_in_dict_to_todo(self):
        """Should handle missing required fields when converting dict to TodoItem."""
        # Create data missing required fields
        incomplete_data = {
            "id": str(uuid4()),
            "title": "Test",
            # Missing required fields: completed, created_at, updated_at
        }

        with pytest.raises(TodoDomainError, match="Failed to convert data to TodoItem"):
            self.repo._dict_to_todo(incomplete_data)

    def test_should_handle_file_creation_errors_in_ensure_file_exists(self):
        """Should handle file creation errors in _ensure_file_exists."""
        # Create a path that will cause permission errors
        invalid_path = Path("/root/invalid/path/test.json")

        with pytest.raises(TodoDomainError, match="Failed to initialize file"):
            JSONTodoRepository(str(invalid_path))

    def test_should_handle_load_read_errors(self):
        """Should handle read errors during load operation."""
        # Mock the file opening to raise OSError
        import unittest.mock

        with (
            unittest.mock.patch("builtins.open", side_effect=OSError("Read failed")),
            pytest.raises(TodoDomainError, match="Failed to read JSON file"),
        ):
            self.repo.find_all()

    def test_should_handle_json_decode_error_in_load(self):
        """Should handle JSON decode errors during load operation."""
        # Write invalid JSON that will cause JSONDecodeError
        with open(self.temp_path, "w") as f:
            f.write('{"invalid": json}')  # Invalid JSON syntax

        with pytest.raises(TodoDomainError, match="Invalid JSON format"):
            self.repo.find_all()

    def test_should_handle_uuid_serialization_in_json_serializer(self):
        """Should handle UUID serialization in _json_serializer."""
        test_uuid = uuid4()
        result = self.repo._json_serializer(test_uuid)
        assert result == str(test_uuid)

    def test_should_handle_datetime_serialization_in_json_serializer(self):
        """Should handle datetime serialization in _json_serializer."""
        test_date = datetime.now()
        result = self.repo._json_serializer(test_date)
        assert result == test_date.isoformat()

    def test_should_update_existing_todo_in_save_method(self):
        """Should update existing todo when saving with same ID."""
        # Create and save a todo
        todo = TodoItem(title="Original Title")
        self.repo.save(todo)

        # Modify and save again (should update, not create new)
        todo.update_details(title="Updated Title")
        self.repo.save(todo)

        # Should still have only one todo
        all_todos = self.repo.find_all()
        assert len(all_todos) == 1
        assert all_todos[0].title == "Updated Title"
