"""Integration test fixtures and utilities."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from src.application.services.todo_service import TodoService
from src.config.repository_factory import create_repository
from src.config.settings import Settings
from src.infrastructure.persistence.json_repository import JSONTodoRepository
from src.infrastructure.persistence.xml_repository import XMLTodoRepository


@pytest.fixture(scope="session")
def temp_integration_directory() -> Generator[Path, None, None]:
    """Create a session-scoped temporary directory for integration tests."""
    with tempfile.TemporaryDirectory(prefix="todo_integration_") as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def temp_storage_file(temp_integration_directory: Path, request) -> Path:
    """Create a temporary storage path for each test."""
    # Create unique directory for each test based on test name
    test_name = request.node.name.replace("::", "_").replace("[", "_").replace("]", "_")
    storage_file = temp_integration_directory / f"storage_{test_name}_{id(request)}"
    storage_file.mkdir(exist_ok=True)
    return storage_file


@pytest.fixture
def json_settings(temp_storage_file: Path) -> Settings:
    """Create settings configured for JSON storage."""
    return Settings(storage_type="json", storage_file=str(temp_storage_file / "todos.json"))


@pytest.fixture
def xml_settings(temp_storage_file: Path) -> Settings:
    """Create settings configured for XML storage."""
    return Settings(storage_type="xml", storage_file=str(temp_storage_file / "todos.xml"))


@pytest.fixture
def json_repository(json_settings: Settings) -> JSONTodoRepository:
    """Create a JSON repository for integration testing."""
    return create_repository(json_settings)


@pytest.fixture
def xml_repository(xml_settings: Settings) -> XMLTodoRepository:
    """Create an XML repository for integration testing."""
    return create_repository(xml_settings)


@pytest.fixture
def json_service(json_repository: JSONTodoRepository) -> TodoService:
    """Create a TodoService with JSON repository."""
    return TodoService(json_repository)


@pytest.fixture
def xml_service(xml_repository: XMLTodoRepository) -> TodoService:
    """Create a TodoService with XML repository."""
    return TodoService(xml_repository)


@pytest.fixture
def sample_todos() -> list[dict]:
    """Provide sample todo data for integration tests."""
    return [
        {
            "title": "Integration Test Todo 1",
            "description": "First test todo for integration testing",
            "due_date": "2026-12-31T23:59:59",
        },
        {
            "title": "Integration Test Todo 2",
            "description": "Second test todo for integration testing",
            "due_date": None,
        },
        {"title": "Integration Test Todo 3", "description": None, "due_date": "2026-06-15T10:00:00"},
    ]


@pytest.fixture
def populated_json_service(json_service: TodoService, sample_todos: list[dict]) -> TodoService:
    """Create a JSON service populated with sample data."""
    for todo_data in sample_todos:
        json_service.create_todo(**todo_data)
    return json_service


@pytest.fixture
def populated_xml_service(xml_service: TodoService, sample_todos: list[dict]) -> TodoService:
    """Create an XML service populated with sample data."""
    for todo_data in sample_todos:
        xml_service.create_todo(**todo_data)
    return xml_service


@pytest.fixture
def large_dataset() -> list[dict]:
    """Generate a large dataset for performance testing."""
    return [
        {
            "title": f"Performance Test Todo {i}",
            "description": f"Description for todo number {i} in performance test batch",
            "due_date": "2026-12-31T23:59:59" if i % 2 == 0 else None,
        }
        for i in range(1, 101)  # 100 todos for performance testing
    ]
