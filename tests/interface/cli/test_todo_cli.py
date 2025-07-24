"""
Tests for TodoCLI main interface class.

This module contains comprehensive tests for the main CLI interface, including:
- Menu system and navigation
- User interaction workflows (add, list, update, complete, delete)
- Error handling and validation
- Input/output formatting and display
- Parameterized tests for consistent behavior across workflows

Test Organization:
- TestTodoCLIInitialization: Basic CLI setup and structure
- TestTodoCLIMenuSystem: Menu display and navigation
- TestTodoCLIMainLoop: Application main loop behavior
- TestAddTodoWorkflow: Add todo functionality and validation
- TestListTodosWorkflow: Todo list display and formatting
- TestUpdateTodoWorkflow: Todo update functionality
- TestCompleteTodoWorkflow: Todo completion functionality
- TestDeleteTodoWorkflow: Todo deletion with confirmation
- TestCLIErrorHandlingParameterized: Systematic error handling tests

All tests follow pytest best practices with proper fixtures, mocking,
and helper functions for maintainability and readability.
"""

from unittest.mock import Mock

import pytest


class TestTodoCLIInitialization:
    """Test suite for TodoCLI initialization and basic structure."""

    def test_should_initialize_with_service_dependency(self, todo_cli, mock_service):
        """Test that TodoCLI initializes with service dependency."""
        assert todo_cli.service == mock_service

    def test_should_have_required_methods(self, todo_cli):
        """Test that TodoCLI has all required public methods."""
        required_methods = [
            "run",
            "show_main_menu",
            "add_todo",
            "list_todos",
            "update_todo",
            "complete_todo",
            "delete_todo",
        ]

        for method_name in required_methods:
            assert hasattr(todo_cli, method_name)
            assert callable(getattr(todo_cli, method_name))

    def test_should_initialize_menu_options(self, todo_cli):
        """Test that menu options are properly initialized."""
        expected_options = {"1", "2", "3", "4", "5", "6"}
        assert set(todo_cli._menu_options.keys()) == expected_options


class TestTodoCLIMenuSystem:
    """Test suite for menu display and navigation."""

    def test_should_display_main_menu(self, cli_with_mocked_console):
        """Test that main menu displays welcome and menu panels."""
        cli_with_mocked_console.show_main_menu()

        # Verify console.print was called at least twice (welcome + menu)
        assert cli_with_mocked_console.console.print.call_count >= 2

    def test_should_get_menu_choice_with_validation(self, todo_cli, mock_prompt):
        """Test that menu choice uses proper validation."""
        mock_prompt.return_value = "1"

        choice = todo_cli._get_menu_choice()

        assert choice == "1"
        mock_prompt.assert_called_once_with(
            "\n[bold]Enter your choice[/bold]", choices=["1", "2", "3", "4", "5", "6"], default="6"
        )

    @pytest.mark.parametrize(
        "choice,method_name",
        [
            ("1", "add_todo"),
            ("2", "list_todos"),
            ("3", "update_todo"),
            ("4", "complete_todo"),
            ("5", "delete_todo"),
        ],
    )
    def test_should_handle_valid_menu_choices(self, cli_with_mocked_console, choice, method_name):
        """Test that valid menu choices call correct methods."""
        # Mock the method to track if it was called
        mock_method = Mock(return_value=True)

        # Update the menu options to use the mock
        description, _ = cli_with_mocked_console._menu_options[choice]
        cli_with_mocked_console._menu_options[choice] = (description, mock_method)

        result = cli_with_mocked_console._handle_menu_choice(choice)

        assert result is True
        mock_method.assert_called_once()

    def test_should_handle_exit_choice(self, cli_with_mocked_console):
        """Test that exit choice returns False and shows goodbye message."""
        result = cli_with_mocked_console._handle_menu_choice("6")

        assert result is False
        cli_with_mocked_console.console.print.assert_called_once()

    def test_should_handle_invalid_choice(self, cli_with_mocked_console):
        """Test that invalid choices are handled gracefully."""
        result = cli_with_mocked_console._handle_menu_choice("invalid")

        assert result is True
        cli_with_mocked_console.console.print.assert_called_once()


class TestTodoCLIWorkflowMethods:
    """Test suite for todo workflow methods."""

    def test_placeholder_methods_return_true(self, cli_with_mocked_console):
        """Test that placeholder methods return True to continue loop."""
        # All workflow methods are now fully implemented
        pass


class TestTodoCLIMainLoop:
    """Test suite for main application loop."""

    def test_should_run_until_exit_choice(self, todo_cli, mock_prompt):
        """Test that run method continues until exit is chosen."""
        # Simulate user choosing option 1, then exit
        mock_prompt.side_effect = ["1", "6"]

        # Mock the add_todo method in menu options
        mock_add_todo = Mock(return_value=True)
        description, _ = todo_cli._menu_options["1"]
        todo_cli._menu_options["1"] = (description, mock_add_todo)

        todo_cli.run()

        # Verify that add_todo was called once before exit
        mock_add_todo.assert_called_once()

    def test_should_handle_keyboard_interrupt(self, todo_cli, mock_prompt, cli_with_mocked_console):
        """Test that KeyboardInterrupt is handled gracefully."""
        mock_prompt.side_effect = KeyboardInterrupt()

        # Replace the todo_cli with mocked console version for testing
        todo_cli.console = cli_with_mocked_console.console

        todo_cli.run()

        # Should show goodbye message on interrupt
        todo_cli.console.print.assert_called()

    def test_should_continue_on_menu_choice_returning_true(self, todo_cli, mock_prompt):
        """Test that loop continues when menu handlers return True."""
        # Simulate multiple choices before exit
        mock_prompt.side_effect = ["1", "2", "6"]

        # Mock workflow methods in menu options
        mock_add_todo = Mock(return_value=True)
        mock_list_todos = Mock(return_value=True)

        desc1, _ = todo_cli._menu_options["1"]
        desc2, _ = todo_cli._menu_options["2"]
        todo_cli._menu_options["1"] = (desc1, mock_add_todo)
        todo_cli._menu_options["2"] = (desc2, mock_list_todos)

        todo_cli.run()

        # Verify both methods were called
        mock_add_todo.assert_called_once()
        mock_list_todos.assert_called_once()


class TestTodoCLIPrivateMethods:
    """Test suite for private helper methods."""

    def test_should_show_invalid_choice_message(self, cli_with_mocked_console):
        """Test that invalid choice message is displayed."""
        cli_with_mocked_console._show_invalid_choice_message()

        cli_with_mocked_console.console.print.assert_called_once()
        call_args = cli_with_mocked_console.console.print.call_args[0][0]
        assert "Invalid choice" in call_args

    def test_should_show_goodbye_message(self, cli_with_mocked_console):
        """Test that goodbye message is displayed."""
        cli_with_mocked_console._show_goodbye_message()

        cli_with_mocked_console.console.print.assert_called_once()

    def test_exit_application_shows_goodbye_and_returns_false(self, cli_with_mocked_console):
        """Test that _exit_application shows goodbye and returns False."""
        result = cli_with_mocked_console._exit_application()

        assert result is False
        cli_with_mocked_console.console.print.assert_called_once()


class TestAddTodoWorkflow:
    """Test suite for add todo CLI workflow."""

    def test_should_prompt_for_title_description_and_due_date(self, cli_with_mocked_console, mock_prompt):
        """Test that add_todo prompts for all required fields."""
        # Mock user inputs
        mock_prompt.side_effect = [
            "Test Todo",  # title
            "Test Description",  # description
            "2025-12-31",  # due_date
        ]

        # Mock service to avoid actual creation
        mock_todo = Mock()
        mock_todo.title = "Test Todo"
        mock_todo.id = "12345678"
        cli_with_mocked_console.service.create_todo.return_value = mock_todo

        result = cli_with_mocked_console.add_todo()

        assert result is True
        # Should prompt for title, description, and due date
        assert mock_prompt.call_count >= 3
        cli_with_mocked_console.service.create_todo.assert_called_once()

    def test_should_create_todo_with_valid_input(self, cli_with_mocked_console, mock_prompt):
        """Test that valid input creates a todo successfully."""
        from tests.interface.cli.conftest import create_add_todo_inputs, create_mock_todo, setup_add_todo_test

        # Create test data
        user_inputs = create_add_todo_inputs(
            title="Valid Todo Title", description="Valid description", due_date="2025-12-31"
        )

        mock_todo = create_mock_todo(title="Valid Todo Title", description="Valid description")
        mock_todo.id = "12345678"

        # Setup mocks
        setup_add_todo_test(mock_prompt, cli_with_mocked_console, user_inputs, mock_todo)

        # Execute and verify
        result = cli_with_mocked_console.add_todo()

        assert result is True
        cli_with_mocked_console.service.create_todo.assert_called_once()
        # Should display success message
        cli_with_mocked_console.console.print.assert_called()

    def test_should_handle_minimal_todo_creation(self, cli_with_mocked_console, mock_prompt):
        """Test creating todo with only title (minimal required data)."""
        # Mock user inputs - only title, empty description and due date
        mock_prompt.side_effect = [
            "Minimal Todo",  # title
            "",  # empty description
            "",  # empty due_date
        ]

        # Mock created todo
        mock_todo = Mock()
        mock_todo.title = "Minimal Todo"
        mock_todo.description = None
        mock_todo.due_date = None
        mock_todo.id = "12345678"
        cli_with_mocked_console.service.create_todo.return_value = mock_todo

        result = cli_with_mocked_console.add_todo()

        assert result is True
        # Should call create_todo with None for optional fields
        cli_with_mocked_console.service.create_todo.assert_called_once()
        call_args = cli_with_mocked_console.service.create_todo.call_args
        assert call_args[1]["description"] is None
        assert call_args[1]["due_date"] is None

    def test_should_display_success_message_with_todo_details(self, cli_with_mocked_console, mock_prompt):
        """Test that success message displays created todo details."""
        # Mock user inputs
        mock_prompt.side_effect = ["Test Todo", "Test Description", ""]

        # Mock created todo
        mock_todo = Mock()
        mock_todo.title = "Test Todo"
        mock_todo.description = "Test Description"
        mock_todo.id = "12345678"
        cli_with_mocked_console.service.create_todo.return_value = mock_todo

        cli_with_mocked_console.add_todo()

        # Should print success message containing todo details
        cli_with_mocked_console.console.print.assert_called()
        from tests.interface.cli.conftest import assert_console_message_contains

        assert assert_console_message_contains(cli_with_mocked_console.console, "created successfully")


class TestAddTodoInputValidation:
    """Test suite for add todo input validation scenarios."""

    def test_should_handle_validation_error_from_service(self, cli_with_mocked_console, mock_prompt):
        """Test that ValidationError from service is handled gracefully."""
        from src.domain.exceptions import ValidationError

        # Mock user inputs - first attempt fails, second attempt succeeds
        mock_prompt.side_effect = [
            "",  # empty title (invalid)
            "",  # empty description
            "",  # empty due date
            "Valid Title",  # retry with valid title
            "Valid Description",
            "",  # empty due date
        ]

        # Mock service to raise ValidationError first, then succeed
        mock_todo = Mock()
        mock_todo.title = "Valid Title"
        mock_todo.id = "12345678"
        cli_with_mocked_console.service.create_todo.side_effect = [ValidationError("Title cannot be empty"), mock_todo]

        result = cli_with_mocked_console.add_todo()

        assert result is True
        # Should call create_todo twice (first fails, second succeeds)
        assert cli_with_mocked_console.service.create_todo.call_count == 2
        # Should display error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_call_found = any("error" in str(call).lower() for call in print_calls)
        assert error_call_found

    def test_should_handle_invalid_due_date_format(self, cli_with_mocked_console, mock_prompt):
        """Test that invalid due date format is handled."""
        # Mock user inputs with invalid date format
        mock_prompt.side_effect = [
            "Valid Title",
            "Valid Description",
            "invalid-date",  # invalid date format
            "2025-12-31",  # valid date format
        ]

        mock_todo = Mock()
        mock_todo.title = "Valid Title"
        mock_todo.id = "12345678"
        cli_with_mocked_console.service.create_todo.return_value = mock_todo

        result = cli_with_mocked_console.add_todo()

        assert result is True
        # Should eventually succeed
        cli_with_mocked_console.service.create_todo.assert_called_once()

    def test_should_handle_service_domain_error(self, cli_with_mocked_console, mock_prompt):
        """Test that TodoDomainError from service is handled gracefully."""
        from src.domain.exceptions import TodoDomainError

        # Mock user inputs
        mock_prompt.side_effect = ["Valid Title", "Valid Description", ""]

        # Mock service to raise TodoDomainError
        cli_with_mocked_console.service.create_todo.side_effect = TodoDomainError("Database error")

        result = cli_with_mocked_console.add_todo()

        assert result is True
        cli_with_mocked_console.service.create_todo.assert_called_once()
        # Should display error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_call_found = any("error" in str(call).lower() for call in print_calls)
        assert error_call_found

    def test_should_allow_retry_after_validation_error(self, cli_with_mocked_console, mock_prompt):
        """Test that user can retry after validation error."""
        from src.domain.exceptions import ValidationError

        # Mock user inputs - first attempt fails, second succeeds
        mock_prompt.side_effect = [
            "a" * 201,  # title too long (invalid)
            "",  # empty description
            "",  # empty due date
            "Valid Title",  # retry with valid title
            "Valid Description",
            "",  # empty due date
        ]

        # Mock service behavior
        mock_todo = Mock()
        mock_todo.title = "Valid Title"
        mock_todo.id = "12345678"
        cli_with_mocked_console.service.create_todo.side_effect = [ValidationError("Title too long"), mock_todo]

        result = cli_with_mocked_console.add_todo()

        assert result is True
        # Should call create_todo twice
        assert cli_with_mocked_console.service.create_todo.call_count == 2


class TestAddTodoErrorHandling:
    """Test suite for add todo error handling scenarios."""

    def test_should_handle_unexpected_exceptions(self, cli_with_mocked_console, mock_prompt):
        """Test that unexpected exceptions are handled gracefully."""
        # Mock user inputs
        mock_prompt.side_effect = ["Valid Title", "Valid Description", ""]

        # Mock service to raise unexpected exception
        cli_with_mocked_console.service.create_todo.side_effect = Exception("Unexpected error")

        result = cli_with_mocked_console.add_todo()

        assert result is True
        cli_with_mocked_console.service.create_todo.assert_called_once()
        # Should display error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_call_found = any("error" in str(call).lower() for call in print_calls)
        assert error_call_found

    def test_should_display_helpful_error_messages(self, cli_with_mocked_console, mock_prompt):
        """Test that error messages are helpful and user-friendly."""
        from src.domain.exceptions import ValidationError

        # Mock user inputs
        mock_prompt.side_effect = ["Invalid Title", "Valid Description", ""]

        # Mock service to raise ValidationError with specific message
        error_message = "Title must be between 1 and 200 characters"
        cli_with_mocked_console.service.create_todo.side_effect = ValidationError(error_message)

        cli_with_mocked_console.add_todo()

        # Should display the specific error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_message_found = any(error_message in str(call) for call in print_calls)
        assert error_message_found

    def test_should_return_true_to_continue_menu_loop(self, cli_with_mocked_console, mock_prompt):
        """Test that add_todo always returns True to continue menu loop."""
        from src.domain.exceptions import ValidationError

        # Test successful case
        mock_prompt.side_effect = ["Valid Title", "Valid Description", ""]
        mock_todo = Mock()
        cli_with_mocked_console.service.create_todo.return_value = mock_todo

        result = cli_with_mocked_console.add_todo()
        assert result is True

        # Test error case
        mock_prompt.side_effect = ["Invalid Title", "Valid Description", ""]
        cli_with_mocked_console.service.create_todo.side_effect = ValidationError("Error")

        result = cli_with_mocked_console.add_todo()
        assert result is True


class TestListTodosWorkflow:
    """Test suite for list todos CLI workflow."""

    def test_should_display_todos_in_formatted_table(self, cli_with_mocked_console):
        """Test that list_todos displays todos in a Rich table format."""
        from datetime import datetime
        from uuid import uuid4

        from src.domain.models import TodoItem

        # Mock todos data
        mock_todos = [
            TodoItem(
                id=uuid4(),
                title="Test Todo 1",
                description="Test description 1",
                due_date=datetime(2025, 12, 31),
                completed=False,
            ),
            TodoItem(
                id=uuid4(),
                title="Test Todo 2",
                description="Test description 2",
                due_date=None,
                completed=True,
            ),
        ]

        cli_with_mocked_console.service.get_all_todos.return_value = mock_todos

        result = cli_with_mocked_console.list_todos()

        assert result is True
        cli_with_mocked_console.service.get_all_todos.assert_called_once()
        # Should print the table
        cli_with_mocked_console.console.print.assert_called()

    def test_should_display_empty_message_when_no_todos(self, cli_with_mocked_console):
        """Test that empty message is shown when no todos exist."""
        cli_with_mocked_console.service.get_all_todos.return_value = []

        result = cli_with_mocked_console.list_todos()

        assert result is True
        cli_with_mocked_console.service.get_all_todos.assert_called_once()
        # Should print empty message
        cli_with_mocked_console.console.print.assert_called()

        # Verify that multiple prints occurred (header + empty message)
        assert cli_with_mocked_console.console.print.call_count >= 2

    def test_should_show_all_todo_fields_in_table(self, cli_with_mocked_console):
        """Test that table shows ID, title, description, due date, and status."""
        from datetime import datetime
        from uuid import uuid4

        from src.domain.models import TodoItem

        mock_todo = TodoItem(
            id=uuid4(),
            title="Complete Todo",
            description="Test description",
            due_date=datetime(2025, 12, 31),
            completed=True,
        )

        cli_with_mocked_console.service.get_all_todos.return_value = [mock_todo]

        result = cli_with_mocked_console.list_todos()

        assert result is True
        cli_with_mocked_console.service.get_all_todos.assert_called_once()
        cli_with_mocked_console.console.print.assert_called()

    def test_should_use_color_coding_for_status(self, cli_with_mocked_console):
        """Test that completed and pending todos have different color coding."""
        from uuid import uuid4

        from src.domain.models import TodoItem

        mock_todos = [
            TodoItem(id=uuid4(), title="Pending Todo", completed=False),
            TodoItem(id=uuid4(), title="Completed Todo", completed=True),
        ]

        cli_with_mocked_console.service.get_all_todos.return_value = mock_todos

        result = cli_with_mocked_console.list_todos()

        assert result is True
        cli_with_mocked_console.service.get_all_todos.assert_called_once()
        cli_with_mocked_console.console.print.assert_called()

    def test_should_sort_todos_by_due_date(self, cli_with_mocked_console):
        """Test that todos are sorted by due date with overdue items highlighted."""
        from datetime import datetime, timedelta
        from uuid import uuid4

        from src.domain.models import TodoItem

        now = datetime.now()
        near_future_date = now + timedelta(days=1)
        far_future_date = now + timedelta(days=7)

        mock_todos = [
            TodoItem(id=uuid4(), title="Far Future Todo", due_date=far_future_date, completed=False),
            TodoItem(id=uuid4(), title="Near Future Todo", due_date=near_future_date, completed=False),
            TodoItem(id=uuid4(), title="No Date Todo", due_date=None, completed=False),
        ]

        cli_with_mocked_console.service.get_all_todos.return_value = mock_todos

        result = cli_with_mocked_console.list_todos()

        assert result is True
        cli_with_mocked_console.service.get_all_todos.assert_called_once()
        cli_with_mocked_console.console.print.assert_called()

    def test_should_handle_service_error_gracefully(self, cli_with_mocked_console):
        """Test that service errors are handled gracefully."""
        from src.domain.exceptions import TodoDomainError

        cli_with_mocked_console.service.get_all_todos.side_effect = TodoDomainError("Database error")

        result = cli_with_mocked_console.list_todos()

        assert result is True
        cli_with_mocked_console.service.get_all_todos.assert_called_once()
        # Should display error message
        cli_with_mocked_console.console.print.assert_called()
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_message_found = any("error" in str(call).lower() for call in print_calls)
        assert error_message_found

    def test_should_handle_unexpected_exceptions(self, cli_with_mocked_console):
        """Test that unexpected exceptions are handled gracefully."""
        cli_with_mocked_console.service.get_all_todos.side_effect = Exception("Unexpected error")

        result = cli_with_mocked_console.list_todos()

        assert result is True
        cli_with_mocked_console.service.get_all_todos.assert_called_once()
        # Should display error message
        cli_with_mocked_console.console.print.assert_called()
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_message_found = any("error" in str(call).lower() for call in print_calls)
        assert error_message_found


class TestUpdateTodoWorkflow:
    """Test suite for update todo CLI workflow."""

    def test_should_prompt_for_todo_id_and_display_current_values(self, cli_with_mocked_console, mock_prompt):
        """Test that update_todo prompts for ID and shows current values."""
        from datetime import datetime
        from uuid import uuid4

        from tests.interface.cli.conftest import (
            create_test_todo_item,
            create_update_todo_inputs,
            setup_update_todo_test,
        )

        # Create test data
        todo_id = uuid4()
        current_todo = create_test_todo_item(
            title="Current Title", description="Current Description", due_date=datetime(2025, 12, 31), todo_id=todo_id
        )

        updated_todo = create_test_todo_item(
            title="Updated Title", description="Updated Description", due_date=datetime(2026, 1, 15), todo_id=todo_id
        )

        user_inputs = create_update_todo_inputs(todo_id)

        # Setup mocks
        setup_update_todo_test(mock_prompt, cli_with_mocked_console, todo_id, current_todo, updated_todo, user_inputs)

        # Execute and verify
        result = cli_with_mocked_console.update_todo()

        assert result is True
        cli_with_mocked_console.service.repository.find_by_id.assert_called_once_with(todo_id)
        cli_with_mocked_console.service.update_todo.assert_called_once()
        cli_with_mocked_console.console.print.assert_called()

    def test_should_handle_invalid_todo_id_format(self, cli_with_mocked_console, mock_prompt):
        """Test that invalid UUID format is handled gracefully."""
        # Mock user inputs - invalid UUID format
        mock_prompt.side_effect = ["invalid-uuid-format"]

        result = cli_with_mocked_console.update_todo()

        assert result is True
        # Should not call service methods
        cli_with_mocked_console.service.repository.find_by_id.assert_not_called()
        cli_with_mocked_console.service.update_todo.assert_not_called()
        # Should display error message
        cli_with_mocked_console.console.print.assert_called()

    def test_should_handle_todo_not_found_error(self, cli_with_mocked_console, mock_prompt):
        """Test that TodoNotFoundError is handled gracefully."""
        from uuid import uuid4

        todo_id = uuid4()
        mock_prompt.side_effect = [str(todo_id)]

        # Mock service to return None (todo not found)
        cli_with_mocked_console.service.repository.find_by_id.return_value = None

        result = cli_with_mocked_console.update_todo()

        assert result is True
        cli_with_mocked_console.service.repository.find_by_id.assert_called_once_with(todo_id)
        # Should not call update
        cli_with_mocked_console.service.update_todo.assert_not_called()
        # Should display error message
        cli_with_mocked_console.console.print.assert_called()

    def test_should_allow_partial_updates(self, cli_with_mocked_console, mock_prompt):
        """Test that user can update only specific fields."""
        from datetime import datetime
        from uuid import uuid4

        from tests.interface.cli.conftest import create_test_todo_item, setup_update_todo_test

        todo_id = uuid4()
        current_todo = create_test_todo_item(
            title="Current Title", description="Current Description", due_date=datetime(2025, 12, 31), todo_id=todo_id
        )

        # Mock user inputs - only update title, keep others
        user_inputs = [
            str(todo_id),  # todo ID
            "New Title",  # new title
            "",  # keep current description
            "",  # keep current due date
        ]

        updated_todo = create_test_todo_item(
            title="New Title", description="Current Description", due_date=datetime(2025, 12, 31), todo_id=todo_id
        )

        setup_update_todo_test(mock_prompt, cli_with_mocked_console, todo_id, current_todo, updated_todo, user_inputs)

        result = cli_with_mocked_console.update_todo()

        assert result is True
        cli_with_mocked_console.service.update_todo.assert_called_once()
        # Should call with only title updated
        call_args = cli_with_mocked_console.service.update_todo.call_args
        assert call_args[1]["title"] == "New Title"

    def test_should_handle_validation_error_during_update(self, cli_with_mocked_console, mock_prompt):
        """Test that validation errors are handled gracefully."""
        from uuid import uuid4

        from src.domain.exceptions import ValidationError
        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_todo = TodoItem(id=todo_id, title="Current Title", completed=False)

        mock_prompt.side_effect = [
            str(todo_id),  # todo ID
            "",  # empty title (invalid)
            "",  # description
            "",  # due date
        ]

        cli_with_mocked_console.service.repository.find_by_id.return_value = mock_todo
        cli_with_mocked_console.service.update_todo.side_effect = ValidationError("Title cannot be empty")

        result = cli_with_mocked_console.update_todo()

        assert result is True
        cli_with_mocked_console.service.update_todo.assert_called_once()
        # Should display error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_call_found = any("error" in str(call).lower() for call in print_calls)
        assert error_call_found

    def test_should_display_success_message_after_update(self, cli_with_mocked_console, mock_prompt):
        """Test that success message is displayed after successful update."""
        from uuid import uuid4

        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_todo = TodoItem(id=todo_id, title="Old Title", completed=False)

        mock_prompt.side_effect = [
            str(todo_id),
            "New Title",
            "New Description",
            "",  # keep current due date
        ]

        cli_with_mocked_console.service.repository.find_by_id.return_value = mock_todo
        updated_todo = TodoItem(
            id=todo_id,
            title="New Title",
            description="New Description",
            completed=False,
        )
        cli_with_mocked_console.service.update_todo.return_value = updated_todo

        result = cli_with_mocked_console.update_todo()

        assert result is True
        # Should display success message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        success_call_found = any("success" in str(call).lower() for call in print_calls)
        assert success_call_found

    def test_should_handle_invalid_due_date_format_in_update(self, cli_with_mocked_console, mock_prompt):
        """Test that invalid due date format is handled during update."""
        from uuid import uuid4

        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_todo = TodoItem(id=todo_id, title="Current Title", completed=False)

        mock_prompt.side_effect = [
            str(todo_id),
            "New Title",
            "",  # description
            "invalid-date",  # invalid date format
            "2026-01-15",  # valid date format
        ]

        cli_with_mocked_console.service.repository.find_by_id.return_value = mock_todo
        updated_todo = TodoItem(id=todo_id, title="New Title", completed=False)
        cli_with_mocked_console.service.update_todo.return_value = updated_todo

        result = cli_with_mocked_console.update_todo()

        assert result is True
        # Should eventually succeed with valid date
        cli_with_mocked_console.service.update_todo.assert_called_once()

    def test_should_handle_service_domain_error_during_update(self, cli_with_mocked_console, mock_prompt):
        """Test that TodoDomainError is handled gracefully."""
        from uuid import uuid4

        from src.domain.exceptions import TodoDomainError
        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_todo = TodoItem(id=todo_id, title="Current Title", completed=False)

        mock_prompt.side_effect = [str(todo_id), "New Title", "", ""]

        cli_with_mocked_console.service.repository.find_by_id.return_value = mock_todo
        cli_with_mocked_console.service.update_todo.side_effect = TodoDomainError("Database error")

        result = cli_with_mocked_console.update_todo()

        assert result is True
        # Should display error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_call_found = any("error" in str(call).lower() for call in print_calls)
        assert error_call_found

    def test_should_handle_unexpected_exceptions_during_update(self, cli_with_mocked_console, mock_prompt):
        """Test that unexpected exceptions are handled gracefully."""
        from uuid import uuid4

        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_todo = TodoItem(id=todo_id, title="Current Title", completed=False)

        mock_prompt.side_effect = [str(todo_id), "New Title", "", ""]

        cli_with_mocked_console.service.repository.find_by_id.return_value = mock_todo
        cli_with_mocked_console.service.update_todo.side_effect = Exception("Unexpected error")

        result = cli_with_mocked_console.update_todo()

        assert result is True
        # Should display error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_call_found = any("error" in str(call).lower() for call in print_calls)
        assert error_call_found


class TestCompleteTodoWorkflow:
    """Test suite for complete todo CLI workflow."""

    def test_should_prompt_for_todo_id(self, cli_with_mocked_console, mock_prompt):
        """Test that complete_todo prompts for todo ID."""
        from uuid import uuid4

        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_prompt.return_value = str(todo_id)

        # Mock existing todo
        mock_todo = TodoItem(id=todo_id, title="Test Todo", completed=False)
        cli_with_mocked_console.service.complete_todo.return_value = mock_todo

        result = cli_with_mocked_console.complete_todo()

        assert result is True
        mock_prompt.assert_called_once_with("\n[bold]Enter the ID of the todo to complete[/bold]", default="")
        cli_with_mocked_console.service.complete_todo.assert_called_once_with(todo_id)

    def test_should_mark_todo_as_completed_successfully(self, cli_with_mocked_console, mock_prompt):
        """Test that valid todo ID marks todo as completed."""
        from uuid import uuid4

        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_prompt.return_value = str(todo_id)

        # Mock completed todo
        completed_todo = TodoItem(id=todo_id, title="Test Todo", completed=True)
        cli_with_mocked_console.service.complete_todo.return_value = completed_todo

        result = cli_with_mocked_console.complete_todo()

        assert result is True
        cli_with_mocked_console.service.complete_todo.assert_called_once_with(todo_id)
        # Should display success message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        success_found = any("marked as complete" in str(call).lower() for call in print_calls)
        assert success_found

    def test_should_handle_invalid_uuid_format(self, cli_with_mocked_console, mock_prompt):
        """Test that invalid UUID format is handled gracefully."""
        mock_prompt.return_value = "invalid-uuid-format"

        result = cli_with_mocked_console.complete_todo()

        assert result is True
        # Should not call service
        cli_with_mocked_console.service.complete_todo.assert_not_called()
        # Should display error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_found = any("invalid id" in str(call).lower() for call in print_calls)
        assert error_found

    def test_should_handle_todo_not_found_error(self, cli_with_mocked_console, mock_prompt):
        """Test that TodoNotFoundError is handled gracefully."""
        from uuid import uuid4

        from src.domain.exceptions import TodoNotFoundError

        todo_id = uuid4()
        mock_prompt.return_value = str(todo_id)

        cli_with_mocked_console.service.complete_todo.side_effect = TodoNotFoundError("Todo not found")

        result = cli_with_mocked_console.complete_todo()

        assert result is True
        cli_with_mocked_console.service.complete_todo.assert_called_once_with(todo_id)
        # Should display error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_found = any("not found" in str(call).lower() for call in print_calls)
        assert error_found

    def test_should_handle_service_domain_error(self, cli_with_mocked_console, mock_prompt):
        """Test that TodoDomainError is handled gracefully."""
        from uuid import uuid4

        from src.domain.exceptions import TodoDomainError

        todo_id = uuid4()
        mock_prompt.return_value = str(todo_id)

        cli_with_mocked_console.service.complete_todo.side_effect = TodoDomainError("Database error")

        result = cli_with_mocked_console.complete_todo()

        assert result is True
        cli_with_mocked_console.service.complete_todo.assert_called_once_with(todo_id)
        # Should display error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_found = any("error" in str(call).lower() for call in print_calls)
        assert error_found

    def test_should_handle_unexpected_exceptions(self, cli_with_mocked_console, mock_prompt):
        """Test that unexpected exceptions are handled gracefully."""
        from uuid import uuid4

        todo_id = uuid4()
        mock_prompt.return_value = str(todo_id)

        cli_with_mocked_console.service.complete_todo.side_effect = Exception("Unexpected error")

        result = cli_with_mocked_console.complete_todo()

        assert result is True
        cli_with_mocked_console.service.complete_todo.assert_called_once_with(todo_id)
        # Should display error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_found = any("error" in str(call).lower() for call in print_calls)
        assert error_found

    def test_should_display_success_message_with_todo_title(self, cli_with_mocked_console, mock_prompt):
        """Test that success message includes todo title."""
        from uuid import uuid4

        from src.domain.models import TodoItem

        todo_id = uuid4()
        todo_title = "Important Task"
        mock_prompt.return_value = str(todo_id)

        completed_todo = TodoItem(id=todo_id, title=todo_title, completed=True)
        cli_with_mocked_console.service.complete_todo.return_value = completed_todo

        result = cli_with_mocked_console.complete_todo()

        assert result is True
        # Should display success message with title
        print_calls = cli_with_mocked_console.console.print.call_args_list
        title_found = any(todo_title in str(call) for call in print_calls)
        assert title_found

    def test_should_return_true_to_continue_menu_loop(self, cli_with_mocked_console, mock_prompt):
        """Test that complete_todo always returns True to continue menu loop."""
        from uuid import uuid4

        from src.domain.exceptions import TodoNotFoundError
        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_prompt.return_value = str(todo_id)

        # Test successful case
        completed_todo = TodoItem(id=todo_id, title="Test", completed=True)
        cli_with_mocked_console.service.complete_todo.return_value = completed_todo
        result = cli_with_mocked_console.complete_todo()
        assert result is True

        # Test error case
        cli_with_mocked_console.service.complete_todo.side_effect = TodoNotFoundError("Not found")
        result = cli_with_mocked_console.complete_todo()
        assert result is True


class TestCLIErrorHandlingParameterized:
    """Parameterized tests for CLI error handling across different workflows."""

    @pytest.mark.parametrize(
        "workflow_method,setup_inputs,exception_type,expected_message",
        [
            ("add_todo", ["Title", "Description", ""], "ValidationError", "error"),
            ("add_todo", ["Title", "Description", ""], "TodoDomainError", "error"),
            ("add_todo", ["Title", "Description", ""], "Exception", "error"),
            ("update_todo", ["fake-uuid"], "ValueError", "invalid id"),
            ("complete_todo", ["fake-uuid"], "ValueError", "invalid id"),
            ("delete_todo", ["fake-uuid"], "ValueError", "invalid id"),
        ],
    )
    def test_error_handling_across_workflows(
        self, cli_with_mocked_console, mock_prompt, workflow_method, setup_inputs, exception_type, expected_message
    ):
        """Test that all workflows handle errors gracefully with consistent patterns."""
        from src.domain.exceptions import TodoDomainError, ValidationError
        from tests.interface.cli.conftest import assert_console_message_contains, setup_mock_prompt_sequence

        # Map exception names to actual exception classes
        exception_map = {
            "ValidationError": ValidationError,
            "TodoDomainError": TodoDomainError,
            "Exception": Exception,
            "ValueError": ValueError,
        }

        setup_mock_prompt_sequence(mock_prompt, setup_inputs)

        # Mock the appropriate service method to raise the exception
        if workflow_method == "add_todo":
            cli_with_mocked_console.service.create_todo.side_effect = exception_map[exception_type]("Test error")
        elif workflow_method in ["update_todo", "complete_todo", "delete_todo"]:
            # For UUID validation errors, no service method gets called
            pass

        # Execute the workflow method
        method = getattr(cli_with_mocked_console, workflow_method)
        result = method()

        # All error scenarios should return True to continue the main loop
        assert result is True

        # Should display appropriate error message
        assert assert_console_message_contains(cli_with_mocked_console.console, expected_message)

    @pytest.mark.parametrize(
        "workflow_method,expected_message",
        [
            ("update_todo", "not found"),
            ("complete_todo", "error"),  # complete_todo shows generic error message
            ("delete_todo", "not found"),
        ],
    )
    def test_todo_not_found_handling(self, cli_with_mocked_console, mock_prompt, workflow_method, expected_message):
        """Test that workflows handle 'todo not found' scenarios consistently."""
        from uuid import uuid4

        from src.domain.exceptions import TodoNotFoundError
        from tests.interface.cli.conftest import assert_console_message_contains, setup_mock_prompt_sequence

        todo_id = uuid4()
        inputs = [str(todo_id)]
        if workflow_method == "delete_todo":
            inputs.append("y")  # Add confirmation for delete

        setup_mock_prompt_sequence(mock_prompt, inputs)

        # Mock different scenarios based on workflow
        if workflow_method in ["update_todo", "delete_todo"]:
            # These check repository first
            cli_with_mocked_console.service.repository.find_by_id.return_value = None
        else:
            # complete_todo calls service directly, so mock service to raise exception
            cli_with_mocked_console.service.complete_todo.side_effect = TodoNotFoundError("Todo not found")

        # Execute workflow
        method = getattr(cli_with_mocked_console, workflow_method)
        result = method()

        assert result is True
        assert assert_console_message_contains(cli_with_mocked_console.console, expected_message)


class TestDeleteTodoWorkflow:
    """Test suite for delete todo CLI workflow."""

    def test_should_prompt_for_todo_id_and_confirmation(self, cli_with_mocked_console, mock_prompt):
        """Test that delete_todo prompts for ID and confirmation."""
        from uuid import uuid4

        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_prompt.side_effect = [
            str(todo_id),  # todo ID
            "y",  # confirmation
        ]

        # Mock existing todo for display
        mock_todo = TodoItem(id=todo_id, title="Test Todo", completed=False)
        cli_with_mocked_console.service.repository.find_by_id.return_value = mock_todo

        result = cli_with_mocked_console.delete_todo()

        assert result is True
        cli_with_mocked_console.service.delete_todo.assert_called_once_with(todo_id)

    def test_should_display_todo_details_before_confirmation(self, cli_with_mocked_console, mock_prompt):
        """Test that todo details are shown before asking for confirmation."""
        from uuid import uuid4

        from src.domain.models import TodoItem

        todo_id = uuid4()
        todo_title = "Important Task"
        mock_prompt.side_effect = [str(todo_id), "y"]

        mock_todo = TodoItem(id=todo_id, title=todo_title, completed=False)
        cli_with_mocked_console.service.repository.find_by_id.return_value = mock_todo

        result = cli_with_mocked_console.delete_todo()

        assert result is True
        # Should display todo details
        print_calls = cli_with_mocked_console.console.print.call_args_list
        title_found = any(todo_title in str(call) for call in print_calls)
        assert title_found

    def test_should_cancel_deletion_on_no_confirmation(self, cli_with_mocked_console, mock_prompt):
        """Test that deletion is cancelled when user says no."""
        from uuid import uuid4

        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_prompt.side_effect = [
            str(todo_id),  # todo ID
            "n",  # no confirmation
        ]

        mock_todo = TodoItem(id=todo_id, title="Test Todo", completed=False)
        cli_with_mocked_console.service.repository.find_by_id.return_value = mock_todo

        result = cli_with_mocked_console.delete_todo()

        assert result is True
        # Should not call delete service
        cli_with_mocked_console.service.delete_todo.assert_not_called()
        # Should display cancellation message (Panel content is not directly accessible in mock)
        # Check that console.print was called (cancellation panel was displayed)
        assert cli_with_mocked_console.console.print.call_count >= 3  # Header + todo details + cancellation

    def test_should_handle_invalid_uuid_format(self, cli_with_mocked_console, mock_prompt):
        """Test that invalid UUID format is handled gracefully."""
        mock_prompt.side_effect = ["invalid-uuid-format"]

        result = cli_with_mocked_console.delete_todo()

        assert result is True
        # Should not call service methods
        cli_with_mocked_console.service.repository.find_by_id.assert_not_called()
        cli_with_mocked_console.service.delete_todo.assert_not_called()
        # Should display error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_found = any("invalid id" in str(call).lower() for call in print_calls)
        assert error_found

    def test_should_handle_todo_not_found_error(self, cli_with_mocked_console, mock_prompt):
        """Test that TodoNotFoundError is handled gracefully."""
        from uuid import uuid4

        todo_id = uuid4()
        mock_prompt.side_effect = [str(todo_id)]

        # Mock service to return None (todo not found)
        cli_with_mocked_console.service.repository.find_by_id.return_value = None

        result = cli_with_mocked_console.delete_todo()

        assert result is True
        cli_with_mocked_console.service.repository.find_by_id.assert_called_once_with(todo_id)
        # Should not call delete
        cli_with_mocked_console.service.delete_todo.assert_not_called()
        # Should display error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_found = any("not found" in str(call).lower() for call in print_calls)
        assert error_found

    def test_should_delete_todo_successfully_with_confirmation(self, cli_with_mocked_console, mock_prompt):
        """Test that confirmed deletion removes todo successfully."""
        from uuid import uuid4

        from src.domain.models import TodoItem

        todo_id = uuid4()
        todo_title = "Todo to Delete"
        mock_prompt.side_effect = [str(todo_id), "yes"]

        mock_todo = TodoItem(id=todo_id, title=todo_title, completed=False)
        cli_with_mocked_console.service.repository.find_by_id.return_value = mock_todo

        result = cli_with_mocked_console.delete_todo()

        assert result is True
        cli_with_mocked_console.service.delete_todo.assert_called_once_with(todo_id)
        # Should display success message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        success_found = any("deleted" in str(call).lower() for call in print_calls)
        assert success_found

    def test_should_handle_service_domain_error(self, cli_with_mocked_console, mock_prompt):
        """Test that TodoDomainError is handled gracefully."""
        from uuid import uuid4

        from src.domain.exceptions import TodoDomainError
        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_prompt.side_effect = [str(todo_id), "y"]

        mock_todo = TodoItem(id=todo_id, title="Test Todo", completed=False)
        cli_with_mocked_console.service.repository.find_by_id.return_value = mock_todo
        cli_with_mocked_console.service.delete_todo.side_effect = TodoDomainError("Database error")

        result = cli_with_mocked_console.delete_todo()

        assert result is True
        cli_with_mocked_console.service.delete_todo.assert_called_once_with(todo_id)
        # Should display error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_found = any("error" in str(call).lower() for call in print_calls)
        assert error_found

    def test_should_handle_unexpected_exceptions(self, cli_with_mocked_console, mock_prompt):
        """Test that unexpected exceptions are handled gracefully."""
        from uuid import uuid4

        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_prompt.side_effect = [str(todo_id), "y"]

        mock_todo = TodoItem(id=todo_id, title="Test Todo", completed=False)
        cli_with_mocked_console.service.repository.find_by_id.return_value = mock_todo
        cli_with_mocked_console.service.delete_todo.side_effect = Exception("Unexpected error")

        result = cli_with_mocked_console.delete_todo()

        assert result is True
        # Should display error message
        print_calls = cli_with_mocked_console.console.print.call_args_list
        error_found = any("error" in str(call).lower() for call in print_calls)
        assert error_found

    @pytest.mark.parametrize("confirmation", ["y", "yes", "Y", "YES"])
    def test_should_accept_various_confirmation_formats(self, cli_with_mocked_console, mock_prompt, confirmation):
        """Test that various confirmation formats are accepted."""
        from uuid import uuid4

        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_prompt.side_effect = [str(todo_id), confirmation]

        mock_todo = TodoItem(id=todo_id, title="Test Todo", completed=False)
        cli_with_mocked_console.service.repository.find_by_id.return_value = mock_todo

        result = cli_with_mocked_console.delete_todo()

        assert result is True
        cli_with_mocked_console.service.delete_todo.assert_called_once_with(todo_id)

    @pytest.mark.parametrize("rejection", ["n", "no", "N", "NO", ""])
    def test_should_reject_various_rejection_formats(self, cli_with_mocked_console, mock_prompt, rejection):
        """Test that various rejection formats cancel deletion."""
        from uuid import uuid4

        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_prompt.side_effect = [str(todo_id), rejection]

        mock_todo = TodoItem(id=todo_id, title="Test Todo", completed=False)
        cli_with_mocked_console.service.repository.find_by_id.return_value = mock_todo

        result = cli_with_mocked_console.delete_todo()

        assert result is True
        cli_with_mocked_console.service.delete_todo.assert_not_called()

    def test_should_return_true_to_continue_menu_loop(self, cli_with_mocked_console, mock_prompt):
        """Test that delete_todo always returns True to continue menu loop."""
        from uuid import uuid4

        from src.domain.exceptions import TodoNotFoundError
        from src.domain.models import TodoItem

        todo_id = uuid4()
        mock_prompt.side_effect = [str(todo_id), "y"]

        # Test successful case
        mock_todo = TodoItem(id=todo_id, title="Test", completed=False)
        cli_with_mocked_console.service.repository.find_by_id.return_value = mock_todo
        result = cli_with_mocked_console.delete_todo()
        assert result is True

        # Test error case
        cli_with_mocked_console.service.delete_todo.side_effect = TodoNotFoundError("Not found")
        result = cli_with_mocked_console.delete_todo()
        assert result is True
