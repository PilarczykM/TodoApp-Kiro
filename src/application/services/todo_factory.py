"""
TodoItem factory for creating and updating domain objects.

This module provides factory functions for creating TodoItem instances
with proper validation error handling, following the Factory pattern
to eliminate code duplication.
"""

from datetime import datetime
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from src.domain.exceptions import ValidationError
from src.domain.models import TodoItem


def _convert_pydantic_error(pydantic_error: PydanticValidationError) -> ValidationError:
    """
    Convert a Pydantic ValidationError to a domain ValidationError.

    Args:
        pydantic_error: The Pydantic ValidationError to convert

    Returns:
        A domain ValidationError with user-friendly messages
    """
    error_messages = []

    for error in pydantic_error.errors():
        error_type = error["type"]
        field_location = error.get("loc", ("field",))[0]

        # Handle specific error types with user-friendly messages
        if error_type == "value_error" and "ctx" in error:
            # Handle custom validator errors (from @field_validator)
            ctx_error = error["ctx"].get("error")
            if ctx_error:
                error_messages.append(str(ctx_error))
            else:
                error_messages.append(error["msg"])
        elif error_type == "string_too_short" and field_location == "title":
            # Handle empty title specifically
            error_messages.append("Title cannot be empty")
        elif error_type == "value_error" and "Due date cannot be in the past" in str(error):
            # Handle past due date validation
            error_messages.append("Due date cannot be in the past")
        elif error_type == "string_pattern_mismatch":
            error_messages.append(f"{field_location}: Invalid format")
        elif error_type == "missing":
            error_messages.append(f"{field_location}: Field is required")
        elif error_type == "int_parsing":
            error_messages.append(f"{field_location}: Must be a valid integer")
        elif error_type == "float_parsing":
            error_messages.append(f"{field_location}: Must be a valid number")
        elif error_type == "bool_type":
            error_messages.append(f"{field_location}: Must be true or false")
        elif error_type == "datetime_parsing":
            error_messages.append(f"{field_location}: Invalid date/time format")
        elif error_type == "string_too_long":
            error_messages.append(f"{field_location}: Text is too long")
        else:
            # Generic fallback for other error types
            field_name = field_location if field_location else "field"
            error_messages.append(f"{field_name}: {error['msg']}")

    return ValidationError("; ".join(error_messages))


class TodoItemFactory:
    """
    Factory for creating and updating TodoItem instances.

    This factory centralizes TodoItem creation logic and provides
    consistent error handling across the application layer.
    """

    @staticmethod
    def create_todo_item(
        title: str, description: str | None = None, due_date: datetime | None = None, **kwargs: Any
    ) -> TodoItem:
        """
        Create a new TodoItem with validation.

        Args:
            title: The title of the todo item
            description: Optional description of the todo item
            due_date: Optional due date for the todo item
            **kwargs: Additional fields for the TodoItem

        Returns:
            A validated TodoItem instance

        Raises:
            ValidationError: If the input data fails validation
        """
        try:
            return TodoItem(title=title, description=description, due_date=due_date, **kwargs)
        except PydanticValidationError as e:
            raise _convert_pydantic_error(e) from e

    @staticmethod
    def update_todo_item(existing_todo: TodoItem, update_data: dict[str, Any]) -> TodoItem:
        """
        Create an updated TodoItem instance with validation.

        Args:
            existing_todo: The existing TodoItem to update
            update_data: Dictionary containing the fields to update

        Returns:
            A new TodoItem instance with updated data

        Raises:
            ValidationError: If the update data fails validation
        """
        try:
            # Create updated todo with validation
            updated_todo = TodoItem(**update_data)

            # Preserve immutable fields from the original
            updated_todo.id = existing_todo.id
            updated_todo.created_at = existing_todo.created_at
            # updated_at will be set automatically by the model

            return updated_todo
        except PydanticValidationError as e:
            raise _convert_pydantic_error(e) from e

    @staticmethod
    def validate_todo_data(**data: Any) -> None:
        """
        Validate todo data without creating an instance.

        This is useful for validation-only scenarios where you don't
        need to create the actual TodoItem object.

        Args:
            **data: The data to validate

        Raises:
            ValidationError: If the data fails validation
        """
        try:
            TodoItem(**data)
        except PydanticValidationError as e:
            raise _convert_pydantic_error(e) from e
