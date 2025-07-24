"""
JSON-based repository implementation for Todo persistence.

This module provides a concrete implementation of the TodoRepository
interface using JSON files for data storage. It handles serialization,
deserialization, and file I/O operations while maintaining the domain
contract.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from src.domain.exceptions import TodoDomainError, TodoNotFoundError
from src.domain.models import TodoItem
from src.infrastructure.persistence.file_utils import ensure_file_exists
from src.infrastructure.persistence.repository import TodoRepository


class JSONTodoRepository(TodoRepository):
    """
    JSON file-based implementation of TodoRepository.

    This repository stores todo items in a JSON file, providing persistent
    storage with human-readable format. It handles JSON serialization of
    complex types like UUID and datetime objects.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize the JSON repository with a file path.

        Args:
            file_path: Path to the JSON file for data storage

        Raises:
            TodoDomainError: If the file path is invalid or inaccessible
        """
        self.file_path = Path(file_path)
        ensure_file_exists(self.file_path, self._initialize_empty_json)

    def _initialize_empty_json(self) -> None:
        """
        Initialize an empty JSON file with an empty array.

        Raises:
            TodoDomainError: If JSON file creation fails
        """
        try:
            with open(self.file_path, "w") as f:
                json.dump([], f)
        except OSError as e:
            raise TodoDomainError(f"Failed to create JSON file: {e}") from e

    def _load_todos(self) -> list[dict[str, Any]]:
        """
        Load todos from JSON file.

        Returns:
            List of todo dictionaries

        Raises:
            TodoDomainError: If file reading or JSON parsing fails
        """
        try:
            with open(self.file_path) as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except OSError as e:
            raise TodoDomainError(f"Failed to read JSON file: {e}") from e
        except json.JSONDecodeError as e:
            raise TodoDomainError(f"Invalid JSON format: {e}") from e

    def _save_todos(self, todos: list[dict[str, Any]]) -> None:
        """
        Save todos to JSON file.

        Args:
            todos: List of todo dictionaries to save

        Raises:
            TodoDomainError: If file writing fails
        """
        try:
            with open(self.file_path, "w") as f:
                json.dump(todos, f, indent=2, default=self._json_serializer)
        except OSError as e:
            raise TodoDomainError(f"Failed to write JSON file: {e}") from e

    def _json_serializer(self, obj: Any) -> str:
        """
        Custom JSON serializer for complex types.

        Args:
            obj: Object to serialize

        Returns:
            String representation of the object

        Raises:
            TypeError: If object type is not serializable
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, UUID):
            return str(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def _todo_to_dict(self, todo: TodoItem) -> dict[str, Any]:
        """
        Convert TodoItem to dictionary for JSON storage.

        Args:
            todo: TodoItem to convert

        Returns:
            Dictionary representation of the todo
        """
        return {
            "id": str(todo.id),
            "title": todo.title,
            "description": todo.description,
            "due_date": todo.due_date.isoformat() if todo.due_date else None,
            "completed": todo.completed,
            "created_at": todo.created_at.isoformat(),
            "updated_at": todo.updated_at.isoformat(),
        }

    def _dict_to_todo(self, data: dict[str, Any]) -> TodoItem:
        """
        Convert dictionary to TodoItem.

        Args:
            data: Dictionary representation of todo

        Returns:
            TodoItem instance

        Raises:
            TodoDomainError: If data conversion fails
        """
        try:
            return TodoItem(
                id=UUID(data["id"]),
                title=data["title"],
                description=data.get("description"),
                due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
                completed=data["completed"],
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
            )
        except (KeyError, ValueError, TypeError) as e:
            raise TodoDomainError(f"Failed to convert data to TodoItem: {e}") from e

    def save(self, todo: TodoItem) -> None:
        """
        Save a todo item to the JSON repository.

        This method handles both create and update scenarios by checking
        if the todo already exists and replacing it if found.

        Args:
            todo: The TodoItem to save

        Raises:
            TodoDomainError: If the save operation fails
        """
        todos_data = self._load_todos()
        todo_dict = self._todo_to_dict(todo)

        # Find existing todo by ID and replace, or append if new
        found = False
        for i, existing_todo in enumerate(todos_data):
            if existing_todo["id"] == str(todo.id):
                todos_data[i] = todo_dict
                found = True
                break

        if not found:
            todos_data.append(todo_dict)

        self._save_todos(todos_data)

    def find_by_id(self, todo_id: UUID) -> TodoItem | None:
        """
        Find a todo item by its unique identifier.

        Args:
            todo_id: The unique identifier of the todo item

        Returns:
            The TodoItem if found, None otherwise

        Raises:
            TodoDomainError: If the find operation fails
        """
        todos_data = self._load_todos()

        for todo_data in todos_data:
            if todo_data["id"] == str(todo_id):
                return self._dict_to_todo(todo_data)

        return None

    def find_all(self) -> list[TodoItem]:
        """
        Retrieve all todo items from the repository.

        Returns:
            A list of all TodoItem instances, empty list if none exist

        Raises:
            TodoDomainError: If the retrieval operation fails
        """
        todos_data = self._load_todos()
        return [self._dict_to_todo(todo_data) for todo_data in todos_data]

    def update(self, todo: TodoItem) -> None:
        """
        Update an existing todo item in the repository.

        Args:
            todo: The TodoItem with updated information

        Raises:
            TodoNotFoundError: If the todo item doesn't exist
            TodoDomainError: If the update operation fails
        """
        todos_data = self._load_todos()
        todo_dict = self._todo_to_dict(todo)

        # Find existing todo by ID
        for i, existing_todo in enumerate(todos_data):
            if existing_todo["id"] == str(todo.id):
                todos_data[i] = todo_dict
                self._save_todos(todos_data)
                return

        raise TodoNotFoundError(f"Todo with ID {todo.id} not found")

    def delete(self, todo_id: UUID) -> None:
        """
        Delete a todo item from the repository.

        Args:
            todo_id: The unique identifier of the todo item to delete

        Raises:
            TodoNotFoundError: If the todo item doesn't exist
            TodoDomainError: If the delete operation fails
        """
        todos_data = self._load_todos()

        # Find and remove todo by ID
        for i, todo_data in enumerate(todos_data):
            if todo_data["id"] == str(todo_id):
                todos_data.pop(i)
                self._save_todos(todos_data)
                return

        raise TodoNotFoundError(f"Todo with ID {todo_id} not found")

    def exists(self, todo_id: UUID) -> bool:
        """
        Check if a todo item exists in the repository.

        Args:
            todo_id: The unique identifier of the todo item

        Returns:
            True if the todo item exists, False otherwise

        Raises:
            TodoDomainError: If the existence check fails
        """
        todos_data = self._load_todos()

        return any(todo_data["id"] == str(todo_id) for todo_data in todos_data)
