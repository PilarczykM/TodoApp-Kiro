"""
Tests for TodoCLI main interface class.

This module contains tests for the main CLI interface, menu system,
and user interaction workflows following pytest best practices.
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

    @pytest.mark.parametrize("method_name", ["list_todos", "update_todo", "complete_todo", "delete_todo"])
    def test_workflow_methods_return_true(self, cli_with_mocked_console, method_name):
        """Test that workflow methods return True to continue loop."""
        method = getattr(cli_with_mocked_console, method_name)
        result = method()

        assert result is True
        cli_with_mocked_console.console.print.assert_called_once()


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
        # Mock user inputs
        mock_prompt.side_effect = [
            "Valid Todo Title",  # title
            "Valid description",  # description
            "2025-12-31",  # due_date
        ]

        # Mock created todo
        mock_todo = Mock()
        mock_todo.title = "Valid Todo Title"
        mock_todo.description = "Valid description"
        mock_todo.id = "12345678"
        cli_with_mocked_console.service.create_todo.return_value = mock_todo

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
        print_calls = cli_with_mocked_console.console.print.call_args_list
        success_call_found = any("created successfully" in str(call).lower() for call in print_calls)
        assert success_call_found


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
