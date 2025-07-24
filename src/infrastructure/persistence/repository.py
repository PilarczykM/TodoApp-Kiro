"""
Repository interface for Todo persistence.

This module defines the abstract repository interface that follows
Domain-Driven Design principles by defining the contract for data
persistence without coupling to specific storage implementations.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.models import TodoItem


class TodoRepository(ABC):
    """
    Abstract repository interface for TodoItem persistence.

    This interface defines the contract that all concrete repository
    implementations must follow. It uses domain language and returns
    domain objects, keeping the domain layer independent of infrastructure
    concerns.
    """

    @abstractmethod
    def save(self, todo: TodoItem) -> None:
        """
        Save a todo item to the repository.

        This method persists a new todo item or updates an existing one
        based on the todo's ID. The implementation should handle both
        create and update scenarios transparently.

        Args:
            todo: The TodoItem to save

        Raises:
            TodoDomainError: If the save operation fails due to business rules
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def find_all(self) -> list[TodoItem]:
        """
        Retrieve all todo items from the repository.

        Returns:
            A list of all TodoItem instances, empty list if none exist

        Raises:
            TodoDomainError: If the retrieval operation fails
        """
        pass

    @abstractmethod
    def update(self, todo: TodoItem) -> None:
        """
        Update an existing todo item in the repository.

        Args:
            todo: The TodoItem with updated information

        Raises:
            TodoNotFoundError: If the todo item doesn't exist
            TodoDomainError: If the update operation fails
        """
        pass

    @abstractmethod
    def delete(self, todo_id: UUID) -> None:
        """
        Delete a todo item from the repository.

        Args:
            todo_id: The unique identifier of the todo item to delete

        Raises:
            TodoNotFoundError: If the todo item doesn't exist
            TodoDomainError: If the delete operation fails
        """
        pass

    @abstractmethod
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
        pass
