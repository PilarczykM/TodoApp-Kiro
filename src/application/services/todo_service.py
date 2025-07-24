"""
TodoService application service for orchestrating todo use cases.

This module contains the TodoService class that coordinates domain objects
to fulfill business use cases following Domain-Driven Design principles.
"""

from datetime import datetime
from uuid import UUID

from pydantic import ValidationError as PydanticValidationError

from src.domain.exceptions import TodoNotFoundError, ValidationError
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

    def update_todo(
        self,
        todo_id: UUID,
        title: str | None = None,
        description: str | None = None,
        due_date: datetime | None = None,
    ) -> TodoItem:
        """
        Update an existing todo item.

        This method orchestrates the update of an existing todo item by
        finding it, validating the new data, updating the fields, and
        persisting the changes.

        Args:
            todo_id: The UUID of the todo item to update
            title: Optional new title for the todo item
            description: Optional new description for the todo item
            due_date: Optional new due date for the todo item

        Returns:
            The updated TodoItem

        Raises:
            TodoNotFoundError: If the todo with given ID doesn't exist
            ValidationError: If the update data fails validation
            TodoDomainError: If the update operation fails
        """
        # Find existing todo
        existing_todo = self.repository.find_by_id(todo_id)
        if existing_todo is None:
            raise TodoNotFoundError(f"Todo with ID {todo_id} not found")

        # Prepare update data, keeping existing values if not provided
        update_data = {
            "title": title if title is not None else existing_todo.title,
            "description": description if description is not None else existing_todo.description,
            "due_date": due_date if due_date is not None else existing_todo.due_date,
            "completed": existing_todo.completed,
        }

        try:
            # Create updated todo with validation
            updated_todo = TodoItem(**update_data)
            updated_todo.id = existing_todo.id
            updated_todo.created_at = existing_todo.created_at
            # updated_at will be set automatically by the model

            # Persist changes
            self.repository.update(updated_todo)

            return updated_todo

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

    def complete_todo(self, todo_id: UUID) -> TodoItem:
        """
        Mark a todo item as completed.

        This method orchestrates the completion of a todo item by finding it,
        updating its status to completed, and persisting the changes.

        Args:
            todo_id: The UUID of the todo item to complete

        Returns:
            The completed TodoItem

        Raises:
            TodoNotFoundError: If the todo with given ID doesn't exist
            ValidationError: If the todo is already completed
            TodoDomainError: If the completion operation fails
        """
        # Find existing todo
        existing_todo = self.repository.find_by_id(todo_id)
        if existing_todo is None:
            raise TodoNotFoundError(f"Todo with ID {todo_id} not found")

        # Check if already completed
        if existing_todo.completed:
            raise ValidationError("Todo is already completed")

        # Update completion status using domain method
        existing_todo.mark_completed()

        # Persist changes
        self.repository.update(existing_todo)

        return existing_todo

    def delete_todo(self, todo_id: UUID) -> None:
        """
        Delete a todo item.

        This method orchestrates the deletion of a todo item by finding it
        and removing it from the repository.

        Args:
            todo_id: The UUID of the todo item to delete

        Raises:
            TodoNotFoundError: If the todo with given ID doesn't exist
            TodoDomainError: If the deletion operation fails
        """
        # Find existing todo to ensure it exists
        existing_todo = self.repository.find_by_id(todo_id)
        if existing_todo is None:
            raise TodoNotFoundError(f"Todo with ID {todo_id} not found")

        # Delete from repository
        self.repository.delete(todo_id)
