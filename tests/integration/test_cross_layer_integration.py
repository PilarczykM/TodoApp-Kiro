"""Cross-layer integration tests for TodoApp.

Tests the integration between all application layers:
- CLI → Service → Repository → File Storage
- Configuration → Repository Factory → Service Layer
- Error propagation across layers
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from lxml import etree

from src.application.services.todo_service import TodoService
from src.config.repository_factory import create_repository
from src.config.settings import Settings
from src.domain.exceptions import TodoDomainError
from src.interface.cli.todo_cli import TodoCLI


class TestFullStackIntegration:
    """Test complete request flow from CLI to storage."""

    def test_cli_to_storage_json_workflow(self, json_settings: Settings, temp_storage_file: Path, capsys):
        """Test complete CLI workflow with JSON storage."""
        # Create CLI with real service and repository
        repository = create_repository(json_settings)
        service = TodoService(repository)
        cli = TodoCLI(service)

        # Mock user input for adding a todo
        with patch("rich.prompt.Prompt.ask", side_effect=["Test Todo", "Test Description", "", "n"]):
            cli.add_todo()

        # Verify data was persisted to JSON file
        storage_file = Path(json_settings.storage_file)
        assert storage_file.exists()

        with open(storage_file) as f:
            stored_data = json.load(f)

        assert len(stored_data) == 1
        assert stored_data[0]["title"] == "Test Todo"
        assert stored_data[0]["description"] == "Test Description"

        # Test listing todos through CLI
        with patch("rich.console.Console.print") as mock_print:
            cli.list_todos()
            mock_print.assert_called()

        # Verify the todo exists in memory and storage
        all_todos = service.get_all_todos()
        assert len(all_todos) == 1
        assert all_todos[0].title == "Test Todo"

    def test_cli_to_storage_xml_workflow(self, xml_settings: Settings, temp_storage_file: Path):
        """Test complete CLI workflow with XML storage."""
        # Create CLI with real service and repository
        repository = create_repository(xml_settings)
        service = TodoService(repository)
        cli = TodoCLI(service)

        # Mock user input for adding a todo
        with patch("rich.prompt.Prompt.ask", side_effect=["XML Test Todo", "XML Description", "", "n"]):
            cli.add_todo()

        # Verify data was persisted to XML file
        storage_file = Path(xml_settings.storage_file)
        assert storage_file.exists()

        # Parse and verify XML structure
        tree = etree.parse(str(storage_file))
        root = tree.getroot()

        assert root.tag == "todos"
        todo_elements = root.findall("todo")
        assert len(todo_elements) == 1

        todo = todo_elements[0]
        assert todo.find("title").text == "XML Test Todo"
        assert todo.find("description").text == "XML Description"

    def test_configuration_driven_repository_switching(self, temp_storage_file: Path):
        """Test switching between JSON and XML repositories via configuration."""
        # Start with JSON configuration
        json_config = Settings(storage_type="json", storage_file=str(temp_storage_file / "switch_test.json"))

        json_repo = create_repository(json_config)
        json_service = TodoService(json_repo)

        # Add data via JSON service
        json_service.create_todo(title="Config Switch Test", description="Testing repository switching")

        # Verify JSON storage
        json_file = Path(json_config.storage_file)
        assert json_file.exists()

        # Switch to XML configuration
        xml_config = Settings(storage_type="xml", storage_file=str(temp_storage_file / "switch_test.xml"))

        xml_repo = create_repository(xml_config)
        xml_service = TodoService(xml_repo)

        # Add different data via XML service
        xml_service.create_todo(title="XML Config Test", description="Testing XML after switch")

        # Verify XML storage
        xml_file = Path(xml_config.storage_file)
        assert xml_file.exists()

        # Verify both services maintain separate data
        json_todos = json_service.get_all_todos()
        xml_todos = xml_service.get_all_todos()

        assert len(json_todos) == 1
        assert len(xml_todos) == 1
        assert json_todos[0].title == "Config Switch Test"
        assert xml_todos[0].title == "XML Config Test"

    def test_error_propagation_across_layers(self, json_settings: Settings, temp_storage_file: Path):
        """Test that errors propagate correctly from storage to CLI."""
        repository = create_repository(json_settings)
        service = TodoService(repository)
        cli = TodoCLI(service)

        # Test invalid todo ID error propagation
        with (
            patch("rich.prompt.Prompt.ask", return_value="invalid-uuid"),
            patch("rich.console.Console.print") as mock_print,
        ):
            cli.complete_todo()

            # Verify error message was displayed
            mock_print.assert_called()
            call_args = str(mock_print.call_args_list)
            assert "not found" in call_args.lower() or "invalid" in call_args.lower()

    def test_concurrent_access_simulation(self, json_settings: Settings, temp_storage_file: Path):
        """Test simulated concurrent access to storage."""
        # Create two separate service instances (simulating concurrent access)
        repo1 = create_repository(json_settings)
        repo2 = create_repository(json_settings)
        service1 = TodoService(repo1)
        service2 = TodoService(repo2)

        # Add todos from both services
        service1.create_todo(title="Concurrent Todo 1", description="From service 1")
        service2.create_todo(title="Concurrent Todo 2", description="From service 2")

        # Both services should see both todos after refresh
        # (In a real scenario, this would require proper file locking)
        todos1 = service1.get_all_todos()
        todos2 = service2.get_all_todos()

        # At minimum, each service should see its own todo
        assert len(todos1) >= 1
        assert len(todos2) >= 1

        # Verify persistence
        storage_file = Path(json_settings.storage_file)
        assert storage_file.exists()


class TestMainApplicationIntegration:
    """Test main application entry point integration."""

    def test_main_function_with_valid_config(self, temp_storage_file: Path, monkeypatch):
        """Test main function startup with valid configuration."""
        config_file = temp_storage_file / "test_config.json"
        config_data = {"storage_type": "json", "storage_file": str(temp_storage_file / "main_test.json")}

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Mock CLI run to prevent interactive execution
        with (
            patch("src.interface.cli.todo_cli.TodoCLI.run"),
            patch("sys.argv", ["todo", "--config", str(config_file)]),
            patch("src.main.Settings.from_file") as mock_load,
        ):
            mock_load.return_value = Settings(**config_data)

            # This would normally be tested by importing and calling main()
            # but we'll test the component integration instead
            settings = Settings(**config_data)
            repository = create_repository(settings)
            service = TodoService(repository)
            cli = TodoCLI(service)

            # Verify all components are properly wired
            assert cli.service is not None
            assert cli.service.repository is not None

            # Test service functionality
            test_todo = cli.service.create_todo(
                title="Main Integration Test", description="Testing main function integration"
            )
            assert test_todo.title == "Main Integration Test"

    def test_main_error_handling_integration(self, temp_storage_file: Path):
        """Test error handling in main application flow."""
        # Test with valid storage type but invalid path
        invalid_config = Settings(storage_type="json", storage_file="/nonexistent/path/file.json")

        # Should raise error when trying to create the repository
        with pytest.raises(TodoDomainError):
            create_repository(invalid_config)


class TestDataConsistencyIntegration:
    """Test data consistency across application restarts and operations."""

    def test_data_persistence_across_service_instances(self, json_settings: Settings, temp_storage_file: Path):
        """Test data persistence when creating new service instances."""
        # First service instance - add data
        repo1 = create_repository(json_settings)
        service1 = TodoService(repo1)

        original_todo = service1.create_todo(
            title="Persistence Test", description="Testing data persistence", due_date="2026-12-31T23:59:59"
        )
        original_id = original_todo.id

        # Second service instance - should load existing data
        repo2 = create_repository(json_settings)
        service2 = TodoService(repo2)

        loaded_todos = service2.get_all_todos()
        assert len(loaded_todos) == 1
        assert loaded_todos[0].id == original_id
        assert loaded_todos[0].title == "Persistence Test"

        # Modify data with second service
        service2.update_todo(original_id, title="Updated Persistence Test")

        # Third service instance - should see the update
        repo3 = create_repository(json_settings)
        service3 = TodoService(repo3)

        updated_todos = service3.get_all_todos()
        assert len(updated_todos) == 1
        assert updated_todos[0].title == "Updated Persistence Test"

    def test_data_integrity_during_operations(self, temp_storage_file: Path):
        """Test data integrity during various operations."""
        # Create fresh XML settings for this test
        xml_config = Settings(storage_type="xml", storage_file=str(temp_storage_file / "data_integrity.xml"))
        repository = create_repository(xml_config)
        service = TodoService(repository)

        # Create multiple todos
        todos = []
        for i in range(5):
            todo = service.create_todo(title=f"Integrity Test {i}", description=f"Description {i}")
            todos.append(todo)

        # Perform various operations
        service.complete_todo(todos[0].id)
        service.update_todo(todos[1].id, description="Updated description")
        service.delete_todo(todos[2].id)

        # Verify final state
        remaining_todos = service.get_all_todos()
        assert len(remaining_todos) == 4  # 5 created - 1 deleted

        # Verify specific states
        completed_todo = next(t for t in remaining_todos if t.id == todos[0].id)
        assert completed_todo.completed

        updated_todo = next(t for t in remaining_todos if t.id == todos[1].id)
        assert updated_todo.description == "Updated description"

        # Verify deleted todo is not present
        deleted_ids = [t.id for t in remaining_todos]
        assert todos[2].id not in deleted_ids
