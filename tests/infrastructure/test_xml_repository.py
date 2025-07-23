"""
Tests for XMLTodoRepository implementation.

This module contains tests that verify the XML-based repository
implementation follows the repository contract and handles XML
operations correctly using lxml.
"""

import os
import tempfile
import pytest
from pathlib import Path
from uuid import uuid4
from datetime import datetime
from lxml import etree

from src.domain.models import TodoItem
from src.domain.exceptions import TodoNotFoundError, TodoDomainError
from src.infrastructure.persistence.xml_repository import XMLTodoRepository


class TestXMLTodoRepository:
    """Test suite for XMLTodoRepository implementation."""

    def setup_method(self):
        """Set up test environment with temporary XML file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".xml") as temp_file:
            self.temp_path = Path(temp_file.name)
        self.repo = XMLTodoRepository(str(self.temp_path))

    def teardown_method(self):
        """Clean up temporary file after each test."""
        if self.temp_path.exists():
            self.temp_path.unlink()

    def test_should_create_repository_with_file_path(self):
        """Should create XMLTodoRepository with file path."""
        repo = XMLTodoRepository("test.xml")
        assert isinstance(repo, XMLTodoRepository)

    def test_should_create_empty_xml_file_if_not_exists(self):
        """Should create empty XML file with root element if it doesn't exist."""
        # Remove the temp file to test creation
        self.temp_path.unlink()
        
        # Create repository - should create the file
        XMLTodoRepository(str(self.temp_path))
        
        # File should exist and contain root element
        assert self.temp_path.exists()
        tree = etree.parse(str(self.temp_path))
        root = tree.getroot()
        assert root.tag == "todos"
        assert len(root) == 0

    def test_should_save_todo_item_to_xml_file(self):
        """Should save a todo item to XML file."""
        todo = TodoItem(title="Test Todo", description="Test description")
        
        self.repo.save(todo)
        
        # Verify file contains the todo
        tree = etree.parse(str(self.temp_path))
        root = tree.getroot()
        
        assert len(root) == 1
        todo_elem = root[0]
        assert todo_elem.tag == "todo"
        assert todo_elem.find("title").text == "Test Todo"
        assert todo_elem.find("description").text == "Test description"
        assert todo_elem.find("completed").text == "false"

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

    def test_should_handle_xml_serialization_of_datetime(self):
        """Should properly serialize and deserialize datetime fields."""
        due_date = datetime(2025, 12, 31, 23, 59, 59)
        todo = TodoItem(title="Todo with date", due_date=due_date)
        
        self.repo.save(todo)
        retrieved_todo = self.repo.find_by_id(todo.id)
        
        assert retrieved_todo.due_date == due_date

    def test_should_handle_xml_serialization_of_uuid(self):
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

    def test_should_handle_xml_corruption_gracefully(self):
        """Should handle corrupted XML file gracefully."""
        # Write invalid XML to file
        with open(self.temp_path, 'w') as f:
            f.write("invalid xml content")
        
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
        todos = [
            TodoItem(title=f"Todo {i}", description=f"Description {i}")
            for i in range(5)
        ]
        
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
        with open(self.temp_path, 'w') as f:
            f.write("")
        
        # Should initialize with empty root element
        repo = XMLTodoRepository(str(self.temp_path))
        todos = repo.find_all()
        assert todos == []

    def test_should_preserve_field_types_after_serialization(self):
        """Should preserve all field types after XML serialization."""
        from datetime import timedelta
        future_date = datetime.now() + timedelta(days=1)
        todo = TodoItem(
            title="Type Test Todo",
            description="Test description",
            due_date=future_date,
            completed=True
        )
        
        self.repo.save(todo)
        retrieved_todo = self.repo.find_by_id(todo.id)
        
        # Check all field types are preserved
        assert isinstance(retrieved_todo.title, str)
        assert isinstance(retrieved_todo.description, str)
        assert isinstance(retrieved_todo.due_date, datetime)
        assert isinstance(retrieved_todo.completed, bool)
        assert isinstance(retrieved_todo.created_at, datetime)
        assert isinstance(retrieved_todo.updated_at, datetime)

    def test_should_handle_none_description_in_xml(self):
        """Should handle None description properly in XML."""
        todo = TodoItem(title="Todo without description")
        
        self.repo.save(todo)
        retrieved_todo = self.repo.find_by_id(todo.id)
        
        assert retrieved_todo.description is None

    def test_should_handle_none_due_date_in_xml(self):
        """Should handle None due_date properly in XML."""
        todo = TodoItem(title="Todo without due date")
        
        self.repo.save(todo)
        retrieved_todo = self.repo.find_by_id(todo.id)
        
        assert retrieved_todo.due_date is None

    def test_should_validate_xml_schema_structure(self):
        """Should maintain proper XML schema structure."""
        todo = TodoItem(title="Schema Test", description="Test description")
        self.repo.save(todo)
        
        # Parse and validate XML structure
        tree = etree.parse(str(self.temp_path))
        root = tree.getroot()
        
        assert root.tag == "todos"
        todo_elem = root[0]
        assert todo_elem.tag == "todo"
        
        # Check required elements exist
        required_elements = ["id", "title", "completed", "created_at", "updated_at"]
        for elem_name in required_elements:
            assert todo_elem.find(elem_name) is not None
        
        # Check optional elements
        assert todo_elem.find("description") is not None
        # due_date should be None for this test
        due_date_elem = todo_elem.find("due_date")
        assert due_date_elem is None or due_date_elem.text is None

    def test_should_handle_special_characters_in_xml(self):
        """Should handle special XML characters properly."""
        todo = TodoItem(
            title="Todo with <special> & \"characters\"",
            description="Description with <tags> & 'quotes'"
        )
        
        self.repo.save(todo)
        retrieved_todo = self.repo.find_by_id(todo.id)
        
        assert retrieved_todo.title == "Todo with <special> & \"characters\""
        assert retrieved_todo.description == "Description with <tags> & 'quotes'"