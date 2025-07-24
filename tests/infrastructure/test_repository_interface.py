"""
Tests for TodoRepository abstract interface.

This module contains tests that verify the TodoRepository interface
follows the contract expected by the domain layer.
"""

from abc import ABC
from uuid import UUID, uuid4

import pytest

from src.domain.models import TodoItem
from src.infrastructure.persistence.repository import TodoRepository


class TestTodoRepositoryInterface:
    """Test suite for TodoRepository abstract interface."""

    def test_should_be_abstract_base_class(self):
        """TodoRepository should be an abstract base class."""
        assert issubclass(TodoRepository, ABC)

        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            TodoRepository()

    def test_should_have_save_method_signature(self):
        """TodoRepository should define save method signature."""
        # Check that save method exists and is abstract
        assert hasattr(TodoRepository, "save")
        assert getattr(TodoRepository.save, "__isabstractmethod__", False)

    def test_should_have_find_by_id_method_signature(self):
        """TodoRepository should define find_by_id method signature."""
        # Check that find_by_id method exists and is abstract
        assert hasattr(TodoRepository, "find_by_id")
        assert getattr(TodoRepository.find_by_id, "__isabstractmethod__", False)

    def test_should_have_find_all_method_signature(self):
        """TodoRepository should define find_all method signature."""
        # Check that find_all method exists and is abstract
        assert hasattr(TodoRepository, "find_all")
        assert getattr(TodoRepository.find_all, "__isabstractmethod__", False)

    def test_should_have_update_method_signature(self):
        """TodoRepository should define update method signature."""
        # Check that update method exists and is abstract
        assert hasattr(TodoRepository, "update")
        assert getattr(TodoRepository.update, "__isabstractmethod__", False)

    def test_should_have_delete_method_signature(self):
        """TodoRepository should define delete method signature."""
        # Check that delete method exists and is abstract
        assert hasattr(TodoRepository, "delete")
        assert getattr(TodoRepository.delete, "__isabstractmethod__", False)

    def test_should_have_exists_method_signature(self):
        """TodoRepository should define exists method signature."""
        # Check that exists method exists and is abstract
        assert hasattr(TodoRepository, "exists")
        assert getattr(TodoRepository.exists, "__isabstractmethod__", False)


class ConcreteTodoRepository(TodoRepository):
    """Concrete implementation for testing interface compliance."""

    def save(self, todo: TodoItem) -> None:
        pass

    def find_by_id(self, todo_id: UUID) -> TodoItem | None:
        return None

    def find_all(self) -> list[TodoItem]:
        return []

    def update(self, todo: TodoItem) -> None:
        pass

    def delete(self, todo_id: UUID) -> None:
        pass

    def exists(self, todo_id: UUID) -> bool:
        return False


class TestTodoRepositoryImplementation:
    """Test suite for concrete TodoRepository implementation."""

    def test_should_allow_concrete_implementation(self):
        """Should be able to create concrete implementation of TodoRepository."""
        repo = ConcreteTodoRepository()
        assert isinstance(repo, TodoRepository)

    def test_concrete_implementation_should_have_all_methods(self):
        """Concrete implementation should implement all abstract methods."""
        repo = ConcreteTodoRepository()

        # Test that all methods are callable
        assert callable(repo.save)
        assert callable(repo.find_by_id)
        assert callable(repo.find_all)
        assert callable(repo.update)
        assert callable(repo.delete)
        assert callable(repo.exists)

    def test_save_method_should_accept_todo_item(self):
        """Save method should accept TodoItem parameter."""
        repo = ConcreteTodoRepository()
        todo = TodoItem(title="Test Todo")

        # Should not raise an exception
        repo.save(todo)

    def test_find_by_id_should_accept_uuid_and_return_optional_todo(self):
        """Find by id method should accept UUID and return Optional[TodoItem]."""
        repo = ConcreteTodoRepository()
        todo_id = uuid4()

        result = repo.find_by_id(todo_id)
        assert result is None or isinstance(result, TodoItem)

    def test_find_all_should_return_list_of_todos(self):
        """Find all method should return List[TodoItem]."""
        repo = ConcreteTodoRepository()

        result = repo.find_all()
        assert isinstance(result, list)

    def test_update_method_should_accept_todo_item(self):
        """Update method should accept TodoItem parameter."""
        repo = ConcreteTodoRepository()
        todo = TodoItem(title="Updated Todo")

        # Should not raise an exception
        repo.update(todo)

    def test_delete_method_should_accept_uuid(self):
        """Delete method should accept UUID parameter."""
        repo = ConcreteTodoRepository()
        todo_id = uuid4()

        # Should not raise an exception
        repo.delete(todo_id)

    def test_exists_method_should_accept_uuid_and_return_bool(self):
        """Exists method should accept UUID and return bool."""
        repo = ConcreteTodoRepository()
        todo_id = uuid4()

        result = repo.exists(todo_id)
        assert isinstance(result, bool)
