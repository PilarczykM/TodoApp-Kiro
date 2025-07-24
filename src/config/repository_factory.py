"""Repository factory with strategy pattern for creating storage backends."""

from typing import Protocol

from src.infrastructure.persistence.json_repository import JSONTodoRepository
from src.infrastructure.persistence.repository import TodoRepository
from src.infrastructure.persistence.xml_repository import XMLTodoRepository


class SettingsProtocol(Protocol):
    """Protocol for settings objects that can be used with the repository factory."""

    storage_type: str
    storage_file: str


def create_repository(settings: SettingsProtocol) -> TodoRepository:
    """Create a repository instance based on configuration settings.

    This factory function implements the strategy pattern to create
    the appropriate repository implementation based on the storage_type
    specified in the settings.

    Args:
        settings: Settings object with storage_type and storage_file attributes

    Returns:
        TodoRepository instance (JsonTodoRepository or XmlTodoRepository)

    Raises:
        ValueError: If storage_type is not supported
    """
    if settings.storage_type == "json":
        return JSONTodoRepository(settings.storage_file)
    elif settings.storage_type == "xml":
        return XMLTodoRepository(settings.storage_file)
    else:
        raise ValueError(f"Unsupported storage type: {settings.storage_type}")
