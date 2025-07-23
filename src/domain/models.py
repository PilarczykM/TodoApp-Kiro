"""
Domain models for the Todo application.

This module contains the core domain entities that represent
the business concepts and rules of the Todo application.
"""

from datetime import datetime
from typing import Any, ClassVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ValidationError, field_validator


class TodoItem(BaseModel):
    """
    TodoItem domain entity representing a task to be completed.

    This is the core domain entity that encapsulates all business rules
    and validation logic for todo items. It follows Domain-Driven Design
    principles by keeping business logic within the domain model.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the todo item")
    title: str = Field(min_length=1, max_length=200, description="Title of the todo item")
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional description of the todo item",
    )
    due_date: datetime | None = Field(default=None, description="Optional due date for the todo item")
    completed: bool = Field(default=False, description="Whether the todo item is completed")
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the todo item was created",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the todo item was last updated",
    )

    def __init__(self, **data: Any) -> None:
        """Initialize TodoItem with synchronized timestamps."""
        super().__init__(**data)
        # Ensure updated_at matches created_at on creation if not explicitly set
        if "updated_at" not in data:
            self.updated_at = self.created_at

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """
        Validate that title is not empty or whitespace only.

        Args:
            v: The title value to validate

        Returns:
            The validated title

        Raises:
            ValueError: If title is empty or whitespace only
        """
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: datetime | None) -> datetime | None:
        """
        Validate that due date is not in the past.

        Args:
            v: The due date value to validate

        Returns:
            The validated due date

        Raises:
            ValueError: If due date is in the past
        """
        if v is not None and v < datetime.now():
            raise ValueError("Due date cannot be in the past")
        return v

    def mark_completed(self) -> None:
        """
        Mark the todo item as completed.

        This method implements the business rule for completing a todo item.
        It sets the completed flag to True and updates the timestamp.
        """
        self.completed = True
        self.updated_at = datetime.now()

    def update_details(self, **kwargs: Any) -> None:
        """
        Update the details of the todo item.

        This method allows partial updates of todo item fields while
        maintaining validation rules and updating the timestamp.

        Args:
            title: New title for the todo item (optional)
            description: New description for the todo item (optional)
            due_date: New due date for the todo item (optional)

        Raises:
            ValidationError: If any of the provided values fail validation
        """
        # Create a dictionary of current values for validation
        current_data = self.model_dump()

        # Update with new values only for explicitly passed arguments
        for field, value in kwargs.items():
            if field in ["title", "description", "due_date"]:
                current_data[field] = value

        # Validate the updated data by creating a temporary instance
        try:
            temp_todo = TodoItem(**current_data)
            # If validation passes, update the current instance
            for field, value in kwargs.items():
                if field in ["title", "description", "due_date"]:
                    setattr(
                        self,
                        field,
                        getattr(temp_todo, field) if field == "title" else value,
                    )
        except ValidationError:
            # Re-raise the validation error
            raise

        # Always update the timestamp
        self.updated_at = datetime.now()

    class Config:
        """Pydantic configuration for the TodoItem model."""

        # Allow validation on assignment to catch errors during updates
        validate_assignment = True
        # Use enum values for serialization
        use_enum_values = True
        # Generate schema with examples
        json_schema_extra: ClassVar = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "due_date": "2024-12-31T23:59:59",
                "completed": False,
            }
        }
