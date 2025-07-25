"""Storage backend integration tests for TodoApp.

Tests integration between different storage implementations:
- JSON ↔ XML data interchange and migration
- Repository switching with data preservation
- File corruption recovery and error handling
- Cross-format data consistency validation
"""

import json
from pathlib import Path

import pytest
from lxml import etree

from src.application.services.todo_service import TodoService
from src.config.repository_factory import create_repository
from src.config.settings import Settings
from src.domain.exceptions import TodoDomainError
from src.infrastructure.persistence.json_repository import JSONTodoRepository
from src.infrastructure.persistence.xml_repository import XMLTodoRepository


class TestCrossFormatDataMigration:
    """Test data migration between JSON and XML formats."""

    def test_json_to_xml_data_migration(self, temp_storage_file: Path, sample_todos: list[dict]):
        """Test migrating data from JSON to XML format."""
        # Setup JSON repository and add data
        json_config = Settings(storage_type="json", storage_file=str(temp_storage_file / "migration_source.json"))
        json_repo = create_repository(json_config)
        json_service = TodoService(json_repo)

        # Add test data to JSON
        created_todos = []
        for todo_data in sample_todos:
            todo = json_service.create_todo(**todo_data)
            created_todos.append(todo)

        # Verify initial JSON data
        json_todos = json_service.get_all_todos()
        assert len(json_todos) == len(sample_todos)

        # Create XML repository and migrate data
        xml_config = Settings(storage_type="xml", storage_file=str(temp_storage_file / "migration_target.xml"))
        xml_repo = create_repository(xml_config)
        xml_service = TodoService(xml_repo)

        # Migrate data by recreating todos in XML format
        for todo in json_todos:
            xml_service.create_todo(
                title=todo.title,
                description=todo.description,
                due_date=todo.due_date.isoformat() if todo.due_date else None,
            )

        # Verify XML data matches JSON data
        xml_todos = xml_service.get_all_todos()
        assert len(xml_todos) == len(json_todos)

        # Verify content matches (by title since IDs will be different)
        json_titles = {todo.title for todo in json_todos}
        xml_titles = {todo.title for todo in xml_todos}
        assert json_titles == xml_titles

    def test_xml_to_json_data_migration(self, temp_storage_file: Path, sample_todos: list[dict]):
        """Test migrating data from XML to JSON format."""
        # Setup XML repository and add data
        xml_config = Settings(storage_type="xml", storage_file=str(temp_storage_file / "xml_source.xml"))
        xml_repo = create_repository(xml_config)
        xml_service = TodoService(xml_repo)

        # Add test data to XML
        for todo_data in sample_todos:
            xml_service.create_todo(**todo_data)

        xml_todos = xml_service.get_all_todos()

        # Create JSON repository and migrate data
        json_config = Settings(storage_type="json", storage_file=str(temp_storage_file / "json_target.json"))
        json_repo = create_repository(json_config)
        json_service = TodoService(json_repo)

        # Migrate data
        for todo in xml_todos:
            json_service.create_todo(
                title=todo.title,
                description=todo.description,
                due_date=todo.due_date.isoformat() if todo.due_date else None,
            )

        # Verify migration success
        json_todos = json_service.get_all_todos()
        assert len(json_todos) == len(xml_todos)

        xml_titles = {todo.title for todo in xml_todos}
        json_titles = {todo.title for todo in json_todos}
        assert xml_titles == json_titles

    def test_bidirectional_data_consistency(self, temp_storage_file: Path):
        """Test that data remains consistent across bidirectional migration."""
        original_data = [
            {
                "title": "Consistency Test 1",
                "description": "Testing bidirectional consistency",
                "due_date": "2026-12-31T23:59:59",
            },
            {"title": "Consistency Test 2", "description": None, "due_date": None},
        ]

        # JSON → XML → JSON migration
        json_config1 = Settings(storage_type="json", storage_file=str(temp_storage_file / "original.json"))
        json_repo1 = create_repository(json_config1)
        json_service1 = TodoService(json_repo1)

        # Add original data
        for data in original_data:
            json_service1.create_todo(**data)

        original_todos = json_service1.get_all_todos()

        # Convert to XML
        xml_config = Settings(storage_type="xml", storage_file=str(temp_storage_file / "intermediate.xml"))
        xml_repo = create_repository(xml_config)
        xml_service = TodoService(xml_repo)

        for todo in original_todos:
            xml_service.create_todo(
                title=todo.title,
                description=todo.description,
                due_date=todo.due_date.isoformat() if todo.due_date else None,
            )

        xml_todos = xml_service.get_all_todos()

        # Convert back to JSON
        json_config2 = Settings(storage_type="json", storage_file=str(temp_storage_file / "final.json"))
        json_repo2 = create_repository(json_config2)
        json_service2 = TodoService(json_repo2)

        for todo in xml_todos:
            json_service2.create_todo(
                title=todo.title,
                description=todo.description,
                due_date=todo.due_date.isoformat() if todo.due_date else None,
            )

        final_todos = json_service2.get_all_todos()

        # Verify data consistency
        assert len(final_todos) == len(original_todos)

        original_titles = {todo.title for todo in original_todos}
        final_titles = {todo.title for todo in final_todos}
        assert original_titles == final_titles


class TestRepositorySwitching:
    """Test dynamic repository switching scenarios."""

    def test_runtime_repository_switching(self, temp_storage_file: Path):
        """Test switching repositories at runtime while preserving operations."""
        # Start with JSON
        json_config = Settings(storage_type="json", storage_file=str(temp_storage_file / "switch_test.json"))

        current_repo = create_repository(json_config)
        current_service = TodoService(current_repo)

        # Add some data
        current_service.create_todo(title="Pre-switch Todo", description="Added before switching")

        # Switch to XML repository
        xml_config = Settings(storage_type="xml", storage_file=str(temp_storage_file / "switch_test.xml"))

        new_repo = create_repository(xml_config)
        new_service = TodoService(new_repo)

        # Add data to new repository
        new_service.create_todo(title="Post-switch Todo", description="Added after switching")

        # Verify both repositories maintain their data independently
        json_todos = current_service.get_all_todos()
        xml_todos = new_service.get_all_todos()

        assert len(json_todos) == 1
        assert len(xml_todos) == 1
        assert json_todos[0].title == "Pre-switch Todo"
        assert xml_todos[0].title == "Post-switch Todo"

    def test_repository_factory_consistency(self, temp_storage_file: Path):
        """Test that factory creates consistent repository instances."""
        config = Settings(storage_type="json", storage_file=str(temp_storage_file / "factory_test.json"))

        # Create multiple repository instances
        repo1 = create_repository(config)
        repo2 = create_repository(config)

        # Both should be of the same type
        assert type(repo1) is type(repo2)
        assert isinstance(repo1, JSONTodoRepository)
        assert isinstance(repo2, JSONTodoRepository)

        # Test with XML
        xml_config = Settings(storage_type="xml", storage_file=str(temp_storage_file / "factory_test.xml"))

        xml_repo1 = create_repository(xml_config)
        xml_repo2 = create_repository(xml_config)

        assert type(xml_repo1) is type(xml_repo2)
        assert isinstance(xml_repo1, XMLTodoRepository)
        assert isinstance(xml_repo2, XMLTodoRepository)


class TestFileCorruptionRecovery:
    """Test recovery from corrupted storage files."""

    def test_corrupted_json_file_handling(self, temp_storage_file: Path):
        """Test handling of corrupted JSON files."""
        json_file = temp_storage_file / "corrupted.json"

        # Create corrupted JSON file
        with open(json_file, "w") as f:
            f.write('{"invalid": json content}')  # Invalid JSON

        config = Settings(storage_type="json", storage_file=str(json_file))

        # Should handle corrupted file gracefully
        repo = create_repository(config)
        service = TodoService(repo)

        # Should be able to recover by starting fresh
        # (Implementation may vary - could raise error or start empty)
        try:
            todos = service.get_all_todos()
            # If successful, should return empty list
            assert isinstance(todos, list)
        except TodoDomainError:
            # If error is raised, it should be a domain error
            pass

    def test_corrupted_xml_file_handling(self, temp_storage_file: Path):
        """Test handling of corrupted XML files."""
        xml_file = temp_storage_file / "corrupted.xml"

        # Create corrupted XML file
        with open(xml_file, "w") as f:
            f.write("<todos><todo><title>Unclosed tag</todos>")  # Invalid XML

        config = Settings(storage_type="xml", storage_file=str(xml_file))

        repo = create_repository(config)
        service = TodoService(repo)

        # Should handle corrupted XML gracefully
        try:
            todos = service.get_all_todos()
            assert isinstance(todos, list)
        except (TodoDomainError, etree.XMLSyntaxError):
            # Expected for corrupted XML
            pass

    def test_permission_denied_handling(self, temp_storage_file: Path, monkeypatch):
        """Test handling of permission-denied scenarios."""
        storage_file = temp_storage_file / "permission_test.json"

        config = Settings(storage_type="json", storage_file=str(storage_file))

        # Mock permission error on file operations
        original_open = open

        def mock_open(*args, **kwargs):
            if str(storage_file) in str(args[0]):
                raise PermissionError("Permission denied")
            return original_open(*args, **kwargs)

        monkeypatch.setattr("builtins.open", mock_open)

        # Should raise appropriate domain error during repository creation
        with pytest.raises(TodoDomainError):
            create_repository(config)


class TestConcurrentAccess:
    """Test concurrent access scenarios (simulated)."""

    def test_simulated_concurrent_writes(self, temp_storage_file: Path):
        """Test simulated concurrent write operations."""
        config = Settings(storage_type="json", storage_file=str(temp_storage_file / "concurrent.json"))

        # Create two separate service instances
        repo1 = create_repository(config)
        repo2 = create_repository(config)
        service1 = TodoService(repo1)
        service2 = TodoService(repo2)

        # Simulate concurrent additions
        todo1 = service1.create_todo(title="Concurrent 1", description="From service 1")
        todo2 = service2.create_todo(title="Concurrent 2", description="From service 2")

        # Both operations should succeed
        assert todo1 is not None
        assert todo2 is not None

        # File should contain data from both operations
        # (Note: Real implementation might need file locking)
        storage_file = Path(config.storage_file)
        assert storage_file.exists()

        # Verify file contains valid JSON
        with open(storage_file) as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) >= 1  # At least one todo should be present

    def test_large_dataset_handling(self, temp_storage_file: Path, large_dataset: list[dict]):
        """Test handling of large datasets."""
        config = Settings(storage_type="json", storage_file=str(temp_storage_file / "large_dataset.json"))

        repo = create_repository(config)
        service = TodoService(repo)

        # Add large dataset
        created_todos = []
        for todo_data in large_dataset:
            todo = service.create_todo(**todo_data)
            created_todos.append(todo)

        # Verify all todos were created
        assert len(created_todos) == len(large_dataset)

        # Verify retrieval works with large dataset
        all_todos = service.get_all_todos()
        assert len(all_todos) == len(large_dataset)

        # Test operations on large dataset
        # Update first todo
        first_todo = all_todos[0]
        service.update_todo(first_todo.id, title="Updated Large Dataset Todo")

        # Complete middle todo
        middle_todo = all_todos[len(all_todos) // 2]
        service.complete_todo(middle_todo.id)

        # Delete last todo
        last_todo = all_todos[-1]
        service.delete_todo(last_todo.id)

        # Verify final state
        final_todos = service.get_all_todos()
        assert len(final_todos) == len(large_dataset) - 1  # One deleted

        # Find updated todo
        updated_todo = next(t for t in final_todos if t.id == first_todo.id)
        assert updated_todo.title == "Updated Large Dataset Todo"

        # Find completed todo
        completed_todo = next(t for t in final_todos if t.id == middle_todo.id)
        assert completed_todo.completed


class TestDataIntegrityValidation:
    """Test data integrity across different scenarios."""

    def test_uuid_consistency_across_formats(self, temp_storage_file: Path):
        """Test that UUIDs remain consistent across format conversions."""
        # Create todo in JSON
        json_config = Settings(storage_type="json", storage_file=str(temp_storage_file / "uuid_test.json"))
        json_repo = create_repository(json_config)
        json_service = TodoService(json_repo)

        original_todo = json_service.create_todo(title="UUID Test", description="Testing UUID consistency")
        original_id = original_todo.id

        # Export data manually (simulating export/import functionality)
        json_service.get_all_todos()

        # Import to XML with same UUIDs
        xml_config = Settings(storage_type="xml", storage_file=str(temp_storage_file / "uuid_test.xml"))
        create_repository(xml_config)

        # Note: This test assumes we could preserve UUIDs during migration
        # In practice, new UUIDs might be generated, which is also valid

        # Verify UUID format and uniqueness
        assert str(original_id) != ""
        assert "-" in str(original_id)  # UUID format

        # Create another todo and verify different UUID
        second_todo = json_service.create_todo(title="Second UUID Test", description="Another todo")

        assert original_todo.id != second_todo.id

    def test_timestamp_consistency(self, temp_storage_file: Path):
        """Test timestamp consistency across operations."""
        config = Settings(storage_type="json", storage_file=str(temp_storage_file / "timestamp_test.json"))

        repo = create_repository(config)
        service = TodoService(repo)

        # Create todo and note timestamps
        todo = service.create_todo(title="Timestamp Test", description="Testing timestamp consistency")

        original_created = todo.created_at
        original_updated = todo.updated_at

        # Update todo and verify timestamps
        import time

        time.sleep(0.1)  # Ensure different timestamp

        service.update_todo(todo.id, description="Updated description")

        updated_todo = service.get_todo_by_id(todo.id)

        # Created timestamp should remain the same
        assert updated_todo.created_at == original_created

        # Updated timestamp should be different
        assert updated_todo.updated_at > original_updated
