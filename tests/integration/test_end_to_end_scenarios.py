"""End-to-end scenario tests for TodoApp.

Tests complete user workflows and application scenarios:
- Complete CRUD workflows with real persistence
- Application startup and shutdown scenarios
- Data consistency across application restarts
- Performance scenarios with realistic usage patterns
"""

import json
import time
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import pytest

from src.application.services.todo_service import TodoService
from src.config.repository_factory import create_repository
from src.config.settings import Settings
from src.interface.cli.todo_cli import TodoCLI


class TestCompleteUserWorkflows:
    """Test complete user workflows from start to finish."""

    def test_complete_todo_lifecycle_json(self, temp_storage_file: Path):
        """Test complete todo lifecycle with JSON storage."""
        config = Settings(storage_type="json", storage_file=str(temp_storage_file / "lifecycle.json"))

        repo = create_repository(config)
        service = TodoService(repo)
        cli = TodoCLI(service)

        # Step 1: Add a new todo via CLI
        with patch(
            "rich.prompt.Prompt.ask",
            side_effect=[
                "Complete Lifecycle Test",  # title
                "Testing the complete todo lifecycle",  # description
                "2026-12-31T23:59:59",  # due_date
                "n",  # add another
            ],
        ):
            cli.add_todo()

        # Verify todo was created
        todos = service.get_all_todos()
        assert len(todos) == 1
        todo = todos[0]
        assert todo.title == "Complete Lifecycle Test"
        assert not todo.completed

        # Step 2: List todos via CLI
        with patch("rich.console.Console.print") as mock_print:
            cli.list_todos()
            mock_print.assert_called()

        # Step 3: Update the todo via CLI
        with patch(
            "rich.prompt.Prompt.ask",
            side_effect=[
                str(todo.id),  # todo_id
                "Updated Lifecycle Test",  # new title
                "Updated description for lifecycle test",  # new description
                "",  # keep due date
                "n",  # don't update another
            ],
        ):
            cli.update_todo()

        # Verify update
        updated_todos = service.get_all_todos()
        updated_todo = updated_todos[0]
        assert updated_todo.title == "Updated Lifecycle Test"
        assert updated_todo.description == "Updated description for lifecycle test"

        # Step 4: Complete the todo via CLI
        with patch(
            "rich.prompt.Prompt.ask",
            side_effect=[
                str(todo.id),  # todo_id
                "n",  # don't complete another
            ],
        ):
            cli.complete_todo()

        # Verify completion
        completed_todos = service.get_all_todos()
        completed_todo = completed_todos[0]
        assert completed_todo.completed

        # Step 5: View completed todo in list
        with patch("rich.console.Console.print") as mock_print:
            cli.list_todos()
            mock_print.assert_called()

        # Step 6: Delete the todo via CLI
        with patch(
            "rich.prompt.Prompt.ask",
            side_effect=[
                str(todo.id),  # todo_id
                "y",  # confirm deletion
                "n",  # don't delete another
            ],
        ):
            cli.delete_todo()

        # Verify deletion
        final_todos = service.get_all_todos()
        assert len(final_todos) == 0

        # Verify persistence - storage file should reflect empty state
        storage_file = Path(config.storage_file)
        if storage_file.exists():
            with open(storage_file) as f:
                data = json.load(f)
                assert len(data) == 0

    def test_multiple_todos_workflow_xml(self, temp_storage_file: Path):
        """Test workflow with multiple todos using XML storage."""
        config = Settings(storage_type="xml", storage_file=str(temp_storage_file / "multiple_todos.xml"))

        repo = create_repository(config)
        service = TodoService(repo)
        cli = TodoCLI(service)

        # Add multiple todos
        todos_data = [
            ("Work Task", "Complete project documentation", "2026-06-30T17:00:00"),
            ("Personal Task", "Buy groceries for the week", None),
            ("Study Task", "Review Python testing patterns", "2026-06-15T20:00:00"),
        ]

        created_todos = []
        for title, description, due_date in todos_data:
            due_input = due_date if due_date else ""
            with patch("rich.prompt.Prompt.ask", side_effect=[title, description, due_input, "n"]):
                cli.add_todo()

            # Get the last created todo
            all_todos = service.get_all_todos()
            created_todos.append(all_todos[-1])

        # Verify all todos were created
        assert len(service.get_all_todos()) == 3

        # Complete one todo
        work_todo = next(t for t in created_todos if t.title == "Work Task")
        with patch("rich.prompt.Prompt.ask", side_effect=[str(work_todo.id), "n"]):
            cli.complete_todo()

        # Update another todo
        personal_todo = next(t for t in created_todos if t.title == "Personal Task")
        with patch(
            "rich.prompt.Prompt.ask",
            side_effect=[
                str(personal_todo.id),
                "Personal Task - Updated",
                "Buy groceries and household items",
                "",
                "n",
            ],
        ):
            cli.update_todo()

        # Delete the study task
        study_todo = next(t for t in created_todos if t.title == "Study Task")
        with patch("rich.prompt.Prompt.ask", side_effect=[str(study_todo.id), "y", "n"]):
            cli.delete_todo()

        # Verify final state
        final_todos = service.get_all_todos()
        assert len(final_todos) == 2

        # Check completed work todo
        final_work_todo = next((t for t in final_todos if "Work Task" in t.title), None)
        assert final_work_todo is not None
        assert final_work_todo.completed

        # Check updated personal todo
        final_personal_todo = next((t for t in final_todos if "Personal Task" in t.title), None)
        assert final_personal_todo is not None
        assert final_personal_todo.title == "Personal Task - Updated"
        assert "household items" in final_personal_todo.description

    def test_bulk_operations_workflow(self, temp_storage_file: Path, large_dataset: list[dict]):
        """Test workflow with bulk operations."""
        config = Settings(storage_type="json", storage_file=str(temp_storage_file / "bulk_operations.json"))

        repo = create_repository(config)
        service = TodoService(repo)

        # Bulk create todos
        created_todos = []
        for todo_data in large_dataset[:20]:  # Use first 20 for manageable test
            todo = service.create_todo(**todo_data)
            created_todos.append(todo)

        assert len(service.get_all_todos()) == 20

        # Bulk complete every other todo
        for i in range(0, len(created_todos), 2):
            service.complete_todo(created_todos[i].id)

        # Bulk update descriptions for remaining incomplete todos
        incomplete_todos = [t for t in service.get_all_todos() if not t.completed]
        for todo in incomplete_todos[:5]:  # Update first 5 incomplete
            service.update_todo(todo.id, description=f"Bulk updated: {todo.description}")

        # Verify results
        final_todos = service.get_all_todos()
        completed_count = sum(1 for t in final_todos if t.completed)
        updated_count = sum(1 for t in final_todos if t.description and "Bulk updated:" in t.description)

        assert completed_count == 10  # Every other todo completed
        assert updated_count == 5  # 5 todos updated


class TestApplicationStartupShutdown:
    """Test application startup and shutdown scenarios."""

    def test_clean_startup_with_existing_data(self, temp_storage_file: Path, sample_todos: list[dict]):
        """Test application startup with existing data file."""
        config = Settings(storage_type="json", storage_file=str(temp_storage_file / "startup_test.json"))

        # Pre-populate storage file
        storage_data = []
        for _, todo_data in enumerate(sample_todos):
            storage_data.append(
                {
                    "id": str(uuid4()),
                    "title": todo_data["title"],
                    "description": todo_data["description"],
                    "due_date": todo_data["due_date"],
                    "completed": False,
                    "created_at": "2026-01-01T10:00:00",
                    "updated_at": "2026-01-01T10:00:00",
                }
            )

        with open(config.storage_file, "w") as f:
            json.dump(storage_data, f)

        # Start application (create repository and service)
        repo = create_repository(config)
        service = TodoService(repo)

        # Verify existing data was loaded
        loaded_todos = service.get_all_todos()
        assert len(loaded_todos) == len(sample_todos)

        titles = {todo.title for todo in loaded_todos}
        expected_titles = {todo_data["title"] for todo_data in sample_todos}
        assert titles == expected_titles

    def test_startup_with_empty_storage(self, temp_storage_file: Path):
        """Test application startup with no existing data."""
        config = Settings(storage_type="json", storage_file=str(temp_storage_file / "empty_startup.json"))

        # Ensure storage file doesn't exist
        storage_file = Path(config.storage_file)
        if storage_file.exists():
            storage_file.unlink()

        # Start application
        repo = create_repository(config)
        service = TodoService(repo)

        # Should start with empty todo list
        todos = service.get_all_todos()
        assert len(todos) == 0

        # Should be able to add todos normally
        todo = service.create_todo(title="First Todo", description="After startup")
        assert todo is not None

        # Storage file should be created
        assert storage_file.exists()

    def test_graceful_shutdown_data_persistence(self, temp_storage_file: Path):
        """Test that data persists across application shutdown/startup."""
        config = Settings(storage_type="xml", storage_file=str(temp_storage_file / "shutdown_test.xml"))

        # First session - add data
        repo1 = create_repository(config)
        service1 = TodoService(repo1)

        todo1 = service1.create_todo(title="Pre-shutdown Todo", description="Created before shutdown")
        service1.create_todo(title="Another Pre-shutdown Todo", description="Also created before shutdown")

        # Complete one todo
        service1.complete_todo(todo1.id)

        # Simulate application shutdown (lose references)
        del service1, repo1

        # Second session - verify data persistence
        repo2 = create_repository(config)
        service2 = TodoService(repo2)

        loaded_todos = service2.get_all_todos()
        assert len(loaded_todos) == 2

        # Verify todo states persisted
        completed_todo = next((t for t in loaded_todos if t.completed), None)
        assert completed_todo is not None
        assert completed_todo.title == "Pre-shutdown Todo"

        incomplete_todo = next((t for t in loaded_todos if not t.completed), None)
        assert incomplete_todo is not None
        assert incomplete_todo.title == "Another Pre-shutdown Todo"


class TestDataConsistencyScenarios:
    """Test data consistency across various scenarios."""

    def test_concurrent_session_data_consistency(self, temp_storage_file: Path):
        """Test data consistency between concurrent application sessions."""
        config = Settings(storage_type="json", storage_file=str(temp_storage_file / "concurrent_sessions.json"))

        # Session 1 - Add initial data
        repo1 = create_repository(config)
        service1 = TodoService(repo1)

        service1.create_todo(title="Session 1 Todo", description="Created in first session")

        # Session 2 - Should see session 1 data and add more
        repo2 = create_repository(config)
        service2 = TodoService(repo2)

        session2_todos = service2.get_all_todos()
        assert len(session2_todos) == 1
        assert session2_todos[0].title == "Session 1 Todo"

        service2.create_todo(title="Session 2 Todo", description="Created in second session")

        # Session 1 should see updates from session 2 after refresh
        # Note: In real implementation, this might require explicit refresh
        repo1_fresh = create_repository(config)
        service1_fresh = TodoService(repo1_fresh)

        all_todos = service1_fresh.get_all_todos()
        assert len(all_todos) == 2

        titles = {todo.title for todo in all_todos}
        assert "Session 1 Todo" in titles
        assert "Session 2 Todo" in titles

    def test_data_integrity_after_interruption(self, temp_storage_file: Path):
        """Test data integrity after simulated interruption."""
        config = Settings(storage_type="json", storage_file=str(temp_storage_file / "interruption_test.json"))

        repo = create_repository(config)
        service = TodoService(repo)

        # Add several todos
        todos = []
        for i in range(5):
            todo = service.create_todo(title=f"Interruption Test {i}", description=f"Todo number {i}")
            todos.append(todo)

        # Perform some operations
        service.complete_todo(todos[1].id)
        service.update_todo(todos[2].id, title="Updated Todo 2")

        # Simulate interruption by creating new service instance
        interrupted_repo = create_repository(config)
        interrupted_service = TodoService(interrupted_repo)

        # Verify data integrity after "interruption"
        recovered_todos = interrupted_service.get_all_todos()
        assert len(recovered_todos) == 5

        # Verify specific operations persisted
        completed_todo = next((t for t in recovered_todos if t.completed), None)
        assert completed_todo is not None

        updated_todo = next((t for t in recovered_todos if "Updated" in t.title), None)
        assert updated_todo is not None
        assert updated_todo.title == "Updated Todo 2"


class TestPerformanceScenarios:
    """Test realistic performance scenarios."""

    @pytest.mark.slow
    def test_large_dataset_performance(self, temp_storage_file: Path, large_dataset: list[dict]):
        """Test performance with large dataset operations."""
        config = Settings(storage_type="json", storage_file=str(temp_storage_file / "performance_test.json"))

        repo = create_repository(config)
        service = TodoService(repo)

        # Measure bulk creation time
        start_time = time.time()
        created_todos = []
        for todo_data in large_dataset:
            todo = service.create_todo(**todo_data)
            created_todos.append(todo)

        creation_time = time.time() - start_time

        # Should complete in reasonable time (adjust threshold as needed)
        assert creation_time < 10.0  # 10 seconds for 100 todos
        assert len(created_todos) == len(large_dataset)

        # Measure retrieval time
        start_time = time.time()
        all_todos = service.get_all_todos()
        retrieval_time = time.time() - start_time

        assert retrieval_time < 1.0  # 1 second for retrieval
        assert len(all_todos) == len(large_dataset)

        # Measure bulk update time
        start_time = time.time()
        for i, todo in enumerate(all_todos[:20]):  # Update first 20
            service.update_todo(todo.id, description=f"Performance test update {i}")

        update_time = time.time() - start_time
        assert update_time < 5.0  # 5 seconds for 20 updates

    @pytest.mark.slow
    def test_memory_usage_with_large_dataset(self, temp_storage_file: Path, large_dataset: list[dict]):
        """Test memory usage patterns with large datasets."""
        config = Settings(storage_type="xml", storage_file=str(temp_storage_file / "memory_test.xml"))

        repo = create_repository(config)
        service = TodoService(repo)

        # Add large dataset
        for todo_data in large_dataset:
            service.create_todo(**todo_data)

        # Perform multiple retrieval operations
        for _ in range(10):
            todos = service.get_all_todos()
            assert len(todos) == len(large_dataset)

            # Perform some operations
            if todos:
                service.get_todo_by_id(todos[0].id)
                # Only complete if not already completed
                if not todos[-1].completed:
                    service.complete_todo(todos[-1].id)

        # Test should complete without memory issues
        final_todos = service.get_all_todos()
        assert len(final_todos) == len(large_dataset)

    def test_file_size_growth_patterns(self, temp_storage_file: Path):
        """Test file size growth with increasing data."""
        config = Settings(storage_type="json", storage_file=str(temp_storage_file / "file_growth.json"))

        repo = create_repository(config)
        service = TodoService(repo)
        storage_file = Path(config.storage_file)

        # Track file size growth
        file_sizes = []

        # Add todos in batches and track file size
        for batch in range(5):
            # Add 10 todos
            for i in range(10):
                service.create_todo(
                    title=f"Batch {batch} Todo {i}", description=f"Description for batch {batch}, todo {i}"
                )

            # Record file size
            if storage_file.exists():
                file_sizes.append(storage_file.stat().st_size)

        # File size should grow with more data
        assert len(file_sizes) >= 3
        assert file_sizes[-1] > file_sizes[0]  # File should grow

        # Growth should be roughly linear for this simple case
        growth_rates = []
        for i in range(1, len(file_sizes)):
            growth_rates.append(file_sizes[i] - file_sizes[i - 1])

        # Growth rates should be positive and relatively consistent
        assert all(rate > 0 for rate in growth_rates)
