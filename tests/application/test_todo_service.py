"""
Tests for TodoService application service.

This module contains tests for the TodoService class that orchestrates
domain objects to fulfill use cases following TDD principles.
"""

from unittest.mock import Mock

import pytest

from src.application.services.todo_service import TodoService
from src.infrastructure.persistence.repository import TodoRepository


class TestTodoService:
    """Test suite for TodoService application service."""

    def setup_method(self):
        """Set up test dependencies for each test method."""
        self.mock_repo = Mock(spec=TodoRepository)
        self.service = TodoService(self.mock_repo)

    def test_should_initialize_with_repository_dependency(self):
        """Test that TodoService initializes correctly with repository dependency."""
        # Arrange & Act
        service = TodoService(self.mock_repo)

        # Assert
        assert service.repository is self.mock_repo

    def test_should_raise_error_when_initialized_without_repository(self):
        """Test that TodoService raises error when initialized without repository."""
        # Act & Assert
        with pytest.raises(TypeError):
            TodoService()

    def test_should_accept_repository_interface_implementation(self):
        """Test that TodoService accepts any TodoRepository implementation."""
        # Arrange
        mock_json_repo = Mock(spec=TodoRepository)
        mock_xml_repo = Mock(spec=TodoRepository)

        # Act
        service1 = TodoService(mock_json_repo)
        service2 = TodoService(mock_xml_repo)

        # Assert
        assert service1.repository is mock_json_repo
        assert service2.repository is mock_xml_repo

    def test_should_store_repository_reference_for_use_cases(self):
        """Test that TodoService stores repository reference for use case methods."""
        # Arrange
        mock_repo = Mock(spec=TodoRepository)

        # Act
        service = TodoService(mock_repo)

        # Assert
        assert hasattr(service, "repository")
        assert service.repository is mock_repo

    def test_should_be_ready_for_use_case_orchestration(self):
        """Test that TodoService is properly initialized for orchestrating use cases."""
        # Arrange & Act
        service = TodoService(self.mock_repo)

        # Assert
        assert service is not None
        assert service.repository is not None
        assert isinstance(service.repository, Mock)  # Mock implements TodoRepository spec
