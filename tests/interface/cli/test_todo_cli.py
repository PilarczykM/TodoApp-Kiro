"""
Tests for TodoCLI main interface class.

This module contains tests for the main CLI interface, menu system,
and user interaction workflows.
"""

from unittest.mock import Mock, patch

from src.interface.cli.todo_cli import TodoCLI


class TestTodoCLI:
    """Test suite for TodoCLI main interface class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_service = Mock()
        self.cli = TodoCLI(self.mock_service)

    def test_should_initialize_with_service_dependency(self):
        """Test that TodoCLI initializes with service dependency."""
        # Assert
        assert self.cli.service == self.mock_service

    def test_should_have_main_menu_method(self):
        """Test that TodoCLI has a main menu method."""
        # Assert
        assert hasattr(self.cli, "show_main_menu")
        assert callable(self.cli.show_main_menu)

    def test_should_have_run_method(self):
        """Test that TodoCLI has a run method for starting the application."""
        # Assert
        assert hasattr(self.cli, "run")
        assert callable(self.cli.run)

    def test_should_display_menu_options(self):
        """Test that main menu displays all expected options."""
        # Arrange
        with patch("rich.prompt.Prompt.ask", return_value="6"), patch.object(self.cli, "console") as mock_console:
            # Act
            self.cli.run()

            # Assert - verify console.print was called with menu options
            mock_console.print.assert_called()

            # Check that menu options were displayed
            print_calls = mock_console.print.call_args_list

            # Check if Panel objects contain the expected text
            menu_displayed = any(
                hasattr(call[0][0], "renderable") and "Add Todo" in str(call[0][0].renderable)
                for call in print_calls
                if call[0] and hasattr(call[0][0], "renderable")
            )

            assert mock_console.print.call_count >= 3  # Should have printed welcome, menu, and goodbye panels
            assert menu_displayed

    def test_should_handle_add_todo_choice(self):
        """Test that choosing option 1 calls add todo method."""
        # Arrange
        with (
            patch("rich.prompt.Prompt.ask", side_effect=["1", "6"]),
            patch.object(self.cli, "add_todo") as mock_add_todo,
        ):
            # Act
            self.cli.run()

            # Assert
            mock_add_todo.assert_called_once()

    def test_should_handle_list_todos_choice(self):
        """Test that choosing option 2 calls list todos method."""
        # Arrange
        with (
            patch("rich.prompt.Prompt.ask", side_effect=["2", "6"]),
            patch.object(self.cli, "list_todos") as mock_list_todos,
        ):
            # Act
            self.cli.run()

            # Assert
            mock_list_todos.assert_called_once()

    def test_should_handle_invalid_menu_choice(self):
        """Test that invalid menu choices are handled gracefully."""
        # Arrange - Mock Prompt.ask to first return invalid choice, then valid exit choice
        with (
            patch("rich.prompt.Prompt.ask", side_effect=["7", "6"]) as mock_prompt,
            patch.object(self.cli, "console") as mock_console,
        ):
            # Act
            self.cli.run()

            # Assert - Prompt should have been called twice (invalid then valid)
            assert mock_prompt.call_count == 2

            # Verify error message was displayed
            print_calls = mock_console.print.call_args_list
            error_displayed = any("Invalid choice" in str(call) for call in print_calls)
            assert error_displayed

    def test_should_exit_gracefully(self):
        """Test that choosing exit option terminates the application."""
        # Arrange
        with patch("rich.prompt.Prompt.ask", return_value="6"):
            # Act
            self.cli.run()

            # Assert - should complete without raising exceptions
            assert True  # If we reach here, exit was handled gracefully


class TestTodoCLIMenuDisplay:
    """Test suite for menu display functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_service = Mock()
        self.cli = TodoCLI(self.mock_service)

    def test_should_display_welcome_message(self):
        """Test that welcome message is displayed."""
        # Arrange
        with patch.object(self.cli, "console") as mock_console:
            # Act
            self.cli.show_main_menu()

            # Assert
            print_calls = mock_console.print.call_args_list
            welcome_displayed = any(
                hasattr(call[0][0], "renderable") and "Todo Manager" in str(call[0][0].renderable)
                for call in print_calls
                if call[0] and hasattr(call[0][0], "renderable")
            )
            assert welcome_displayed

    def test_should_display_all_menu_options(self):
        """Test that all menu options are displayed."""
        # Arrange
        with patch.object(self.cli, "console") as mock_console:
            # Act
            self.cli.show_main_menu()

            # Assert
            print_calls = mock_console.print.call_args_list

            # Check if Panel objects contain the expected menu options
            menu_options_displayed = any(
                hasattr(call[0][0], "renderable")
                and all(option in str(call[0][0].renderable) for option in ["1.", "2.", "Exit"])
                for call in print_calls
                if call[0] and hasattr(call[0][0], "renderable")
            )

            assert menu_options_displayed
