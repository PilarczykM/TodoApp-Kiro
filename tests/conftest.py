"""Global test fixtures and utilities for TodoApp tests.

This module provides shared fixtures, factories, and utilities used across all test modules.
Follows pytest best practices for fixture organization and test data management.
"""

import tempfile
from collections.abc import Generator
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest

from src.application.factories.todo_factory import TodoItemFactory
from src.application.services.todo_service import TodoService
from src.config.repository_factory import create_repository
from src.config.settings import Settings
from src.domain.models import TodoItem


# Session-scoped fixtures for expensive resources
@pytest.fixture(scope="session")
def temp_test_directory() -> Generator[Path, None, None]:
    """Create a session-scoped temporary directory for all tests."""
    with tempfile.TemporaryDirectory(prefix="todoapp_tests_") as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope="session")
def base_todo_data() -> dict:
    """Provide base todo data template for test factories."""
    return {"title": "Test Todo", "description": "A test todo item", "due_date": None, "completed": False}


# Function-scoped fixtures for test isolation
@pytest.fixture
def temp_storage_directory(temp_test_directory: Path) -> Path:
    """Create a unique temporary directory for each test function."""
    test_dir = temp_test_directory / f"test_{uuid4().hex[:8]}"
    test_dir.mkdir(exist_ok=True)
    return test_dir


@pytest.fixture
def json_storage_path(temp_storage_directory: Path) -> Path:
    """Provide a JSON storage file path for tests."""
    return temp_storage_directory / "test_todos.json"


@pytest.fixture
def xml_storage_path(temp_storage_directory: Path) -> Path:
    """Provide an XML storage file path for tests."""
    return temp_storage_directory / "test_todos.xml"


@pytest.fixture
def json_settings(json_storage_path: Path) -> Settings:
    """Create settings configured for JSON storage."""
    return Settings(storage_type="json", storage_file=str(json_storage_path))


@pytest.fixture
def xml_settings(xml_storage_path: Path) -> Settings:
    """Create settings configured for XML storage."""
    return Settings(storage_type="xml", storage_file=str(xml_storage_path))


@pytest.fixture
def json_repository(json_settings: Settings):
    """Create a JSON repository for testing."""
    return create_repository(json_settings)


@pytest.fixture
def xml_repository(xml_settings: Settings):
    """Create an XML repository for testing."""
    return create_repository(xml_settings)


@pytest.fixture
def json_service(json_repository) -> TodoService:
    """Create a TodoService with JSON repository."""
    return TodoService(json_repository)


@pytest.fixture
def xml_service(xml_repository) -> TodoService:
    """Create a TodoService with XML repository."""
    return TodoService(xml_repository)


# Todo data factories and generators
class TodoDataFactory:
    """Factory class for generating test todo data."""

    @staticmethod
    def create_basic_todo(**overrides) -> dict:
        """Create basic todo data with optional field overrides."""
        base_data = {"title": "Test Todo", "description": "Test description", "due_date": None}
        base_data.update(overrides)
        return base_data

    @staticmethod
    def create_todo_with_due_date(days_ahead: int = 7, **overrides) -> dict:
        """Create todo data with due date set days ahead."""
        due_date = datetime.now() + timedelta(days=days_ahead)
        data = TodoDataFactory.create_basic_todo(due_date=due_date.isoformat(), **overrides)
        return data

    @staticmethod
    def create_overdue_todo(**overrides) -> dict:
        """Create todo data with past due date."""
        past_date = datetime.now() - timedelta(days=1)
        return TodoDataFactory.create_basic_todo(due_date=past_date.isoformat(), **overrides)

    @staticmethod
    def create_todos_batch(count: int, **base_overrides) -> list[dict]:
        """Create multiple todo data items."""
        todos = []
        for i in range(count):
            todo_data = TodoDataFactory.create_basic_todo(
                title=f"Batch Todo {i + 1}", description=f"Description for todo {i + 1}", **base_overrides
            )
            todos.append(todo_data)
        return todos

    @staticmethod
    def create_edge_case_todos() -> list[dict]:
        """Create todos with edge case data for boundary testing."""
        return [
            # Minimal data
            {"title": "A", "description": None, "due_date": None},
            # Maximum length title
            {"title": "x" * 200, "description": "Max title test", "due_date": None},
            # Maximum length description
            {"title": "Max desc test", "description": "x" * 1000, "due_date": None},
            # Unicode characters
            {"title": "Unicode Test 🚀", "description": "Testing with émojis and spëcial chars", "due_date": None},
            # Edge case dates
            {"title": "Far future", "description": "Test far future date", "due_date": "2099-12-31T23:59:59"},
            {"title": "Y2K test", "description": "Test year 2000", "due_date": "2000-01-01T00:00:00"},
        ]


@pytest.fixture
def todo_factory() -> TodoDataFactory:
    """Provide TodoDataFactory instance for tests."""
    return TodoDataFactory()


@pytest.fixture
def sample_todo_data(todo_factory: TodoDataFactory) -> dict:
    """Provide a single sample todo data item."""
    return todo_factory.create_basic_todo()


@pytest.fixture
def sample_todos_batch(todo_factory: TodoDataFactory) -> list[dict]:
    """Provide a batch of sample todo data items."""
    return todo_factory.create_todos_batch(5)


@pytest.fixture
def edge_case_todos(todo_factory: TodoDataFactory) -> list[dict]:
    """Provide edge case todo data for boundary testing."""
    return todo_factory.create_edge_case_todos()


@pytest.fixture
def large_todo_dataset(todo_factory: TodoDataFactory) -> list[dict]:
    """Provide large dataset for performance testing."""
    # Mix of different todo types
    dataset = []

    # Regular todos
    dataset.extend(todo_factory.create_todos_batch(50))

    # Todos with due dates
    for i in range(25):
        dataset.append(todo_factory.create_todo_with_due_date(days_ahead=i + 1, title=f"Due Date Todo {i + 1}"))

    # Overdue todos
    for i in range(15):
        dataset.append(todo_factory.create_overdue_todo(title=f"Overdue Todo {i + 1}"))

    # Edge case todos
    dataset.extend(todo_factory.create_edge_case_todos())

    return dataset


# TodoItem model fixtures
@pytest.fixture
def sample_todo_item(sample_todo_data: dict) -> TodoItem:
    """Create a sample TodoItem instance."""
    return TodoItemFactory.create(**sample_todo_data)


@pytest.fixture
def completed_todo_item(sample_todo_data: dict) -> TodoItem:
    """Create a completed TodoItem instance."""
    todo = TodoItemFactory.create(**sample_todo_data)
    todo.mark_completed()
    return todo


@pytest.fixture
def todo_with_due_date() -> TodoItem:
    """Create a TodoItem with due date."""
    future_date = datetime.now() + timedelta(days=7)
    return TodoItemFactory.create(title="Todo with Due Date", description="Has a due date", due_date=future_date)


@pytest.fixture
def overdue_todo_item() -> TodoItem:
    """Create an overdue TodoItem."""
    past_date = datetime.now() - timedelta(days=1)
    return TodoItemFactory.create(title="Overdue Todo", description="This todo is overdue", due_date=past_date)


# Service fixtures with pre-populated data
@pytest.fixture
def populated_json_service(json_service: TodoService, sample_todos_batch: list[dict]) -> TodoService:
    """Create JSON service populated with sample data."""
    for todo_data in sample_todos_batch:
        json_service.create_todo(**todo_data)
    return json_service


@pytest.fixture
def populated_xml_service(xml_service: TodoService, sample_todos_batch: list[dict]) -> TodoService:
    """Create XML service populated with sample data."""
    for todo_data in sample_todos_batch:
        xml_service.create_todo(**todo_data)
    return xml_service


# Performance testing fixtures
@pytest.fixture
def performance_json_service(json_service: TodoService, large_todo_dataset: list[dict]) -> TodoService:
    """Create JSON service with large dataset for performance testing."""
    for todo_data in large_todo_dataset:
        json_service.create_todo(**todo_data)
    return json_service


# Parametrization helpers
def pytest_generate_tests(metafunc):
    """Generate parameterized tests for common scenarios."""

    # Parametrize repository types for cross-repository tests
    if "repository_service" in metafunc.fixturenames:
        metafunc.parametrize("repository_service", ["json_service", "xml_service"], indirect=True)

    # Parametrize storage settings for cross-storage tests
    if "storage_settings" in metafunc.fixturenames:
        metafunc.parametrize("storage_settings", ["json_settings", "xml_settings"], indirect=True)


@pytest.fixture
def repository_service(request, json_service: TodoService, xml_service: TodoService) -> TodoService:
    """Indirect fixture for parametrized repository testing."""
    if request.param == "json_service":
        return json_service
    elif request.param == "xml_service":
        return xml_service
    else:
        raise ValueError(f"Unknown repository service: {request.param}")


@pytest.fixture
def storage_settings(request, json_settings: Settings, xml_settings: Settings) -> Settings:
    """Indirect fixture for parametrized settings testing."""
    if request.param == "json_settings":
        return json_settings
    elif request.param == "xml_settings":
        return xml_settings
    else:
        raise ValueError(f"Unknown settings type: {request.param}")


# Test utilities and helpers
class TestDataValidator:
    """Utility class for validating test data consistency."""

    @staticmethod
    def validate_todo_item(todo: TodoItem, expected_data: dict) -> bool:
        """Validate that TodoItem matches expected data."""
        if todo.title != expected_data.get("title"):
            return False
        return todo.description == expected_data.get("description")

    @staticmethod
    def validate_todos_list(todos: list[TodoItem], expected_count: int) -> bool:
        """Validate todos list meets expected criteria."""
        return len(todos) == expected_count

    @staticmethod
    def compare_todo_lists(list1: list[TodoItem], list2: list[TodoItem]) -> bool:
        """Compare two todo lists for equality (by content, not ID)."""
        if len(list1) != len(list2):
            return False

        # Sort by title for comparison
        sorted1 = sorted(list1, key=lambda t: t.title)
        sorted2 = sorted(list2, key=lambda t: t.title)

        for todo1, todo2 in zip(sorted1, sorted2, strict=False):
            if (
                todo1.title != todo2.title
                or todo1.description != todo2.description
                or todo1.completed != todo2.completed
            ):
                return False
        return True


@pytest.fixture
def test_validator() -> TestDataValidator:
    """Provide TestDataValidator utility for tests."""
    return TestDataValidator()


# Cleanup utilities to ensure test isolation
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Automatically cleanup after each test to ensure isolation."""
    # Setup code (if needed)
    yield
    # Cleanup code
    # Any cleanup that needs to happen after each test
    pass
