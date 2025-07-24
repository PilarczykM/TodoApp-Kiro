"""Tests for repository factory with strategy pattern."""

import pytest

from src.config.repository_factory import create_repository
from src.config.settings import Settings
from src.infrastructure.persistence.json_repository import JSONTodoRepository
from src.infrastructure.persistence.xml_repository import XMLTodoRepository


class TestRepositoryFactory:
    """Test suite for repository factory and storage type switching."""

    def test_should_create_json_repository_when_storage_type_is_json(self):
        """Test factory creates JSONTodoRepository for json storage type."""
        # Arrange
        settings = Settings(storage_type="json", storage_file="test.json")

        # Act
        repository = create_repository(settings)

        # Assert
        assert isinstance(repository, JSONTodoRepository)

    def test_should_create_xml_repository_when_storage_type_is_xml(self):
        """Test factory creates XMLTodoRepository for xml storage type."""
        # Arrange
        settings = Settings(storage_type="xml", storage_file="test.xml")

        # Act
        repository = create_repository(settings)

        # Assert
        assert isinstance(repository, XMLTodoRepository)

    def test_should_pass_storage_file_to_repository_constructor(self):
        """Test factory passes storage_file to repository constructor."""
        # Arrange
        settings = Settings(storage_type="json", storage_file="custom_todos.json")

        # Act
        repository = create_repository(settings)

        # Assert
        assert str(repository.file_path) == "custom_todos.json"

    def test_should_raise_error_for_unsupported_storage_type(self):
        """Test factory raises error for unsupported storage types."""
        # This test is theoretical since Pydantic validation prevents invalid types
        # But we test the factory's robustness

        # We can't create Settings with invalid storage_type due to Pydantic validation
        # So we'll test the factory function directly with a mock-like object
        class MockSettings:
            storage_type = "unsupported"
            storage_file = "test.txt"

        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported storage type"):
            create_repository(MockSettings())

    def test_should_handle_settings_object_with_all_required_attributes(self):
        """Test factory works with any object that has required attributes."""

        # Arrange
        class CustomSettings:
            def __init__(self):
                self.storage_type = "json"
                self.storage_file = "custom.json"

        settings = CustomSettings()

        # Act
        repository = create_repository(settings)

        # Assert
        assert isinstance(repository, JSONTodoRepository)
        assert str(repository.file_path) == "custom.json"
