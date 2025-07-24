"""
TodoService application service for orchestrating todo use cases.

This module contains the TodoService class that coordinates domain objects
to fulfill business use cases following Domain-Driven Design principles.
"""

from datetime import datetime

from pydantic import ValidationError as PydanticValidationError

from src.domain.exceptions import ValidationError
from src.domain.models import TodoItem
from src.infrastructure.persistence.repository import TodoRepository


class TodoService:
    """
    Application service for orchestrating todo-related use cases.

    This service acts as a facade for the domain layer, coordinating
    domain objects and repository operations to fulfill business use cases.
    It follows the Application Service pattern from DDD.
    """

    def __init__(self, repository: TodoRepository) -> None:
        """
        Initialize TodoService with repository dependency.

        Args:
            repository: TodoRepository implementation for data persistence

        Raises:
            TypeError: If repository is not provided
        """
        self.repository = repository

    def create_todo(
        self,
        title: str,
        description: str | None = None,
        due_date: datetime | None = None,
    ) -> TodoItem:
        """
        Create a new todo item.

        This method orchestrates the creation of a new todo item by validating
        the input data, creating a domain object, and persisting it through
        the repository.

        Args:
            title: The title of the todo item
            description: Optional description of the todo item
            due_date: Optional due date for the todo item

        Returns:
            The created TodoItem

        Raises:
            ValidationError: If the input data fails validation
            TodoDomainError: If the save operation fails
        """
        try:
            # Create domain object with validation
            todo = TodoItem(
                title=title,
                description=description,
                due_date=due_date,
            )

            # Persist through repository
            self.repository.save(todo)

            return todo

        except PydanticValidationError as e:
            # Convert Pydantic validation errors to domain validation errors
            error_messages = []
            for error in e.errors():
                if error["type"] == "value_error" and "ctx" in error:
                    # Handle custom validator errors
                    error_messages.append(str(error["ctx"]["error"]))
                elif error["type"] == "string_too_short" and error["loc"][0] == "title":
                    # Handle empty title specifically
                    error_messages.append("Title cannot be empty")
                elif error["type"] == "value_error" and "Due date cannot be in the past" in str(error):
                    error_messages.append("Due date cannot be in the past")
                else:
                    # Handle other validation errors
                    field_name = error["loc"][0] if error["loc"] else "field"
                    error_messages.append(f"{field_name}: {error['msg']}")

            raise ValidationError("; ".join(error_messages)) from e

    def get_all_todos(self) -> list[TodoItem]:
        """
        Retrieve all todo items.

        This method orchestrates the retrieval of all todo items from
        the repository.

        Returns:
            A list of all TodoItem instances, empty list if none exist

        Raises:
            TodoDomainError: If the retrieval operation fails
        """
        return self.repository.find_all()
