"""
TodoService application service for orchestrating todo use cases.

This module contains the TodoService class that coordinates domain objects
to fulfill business use cases following Domain-Driven Design principles.
"""

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
