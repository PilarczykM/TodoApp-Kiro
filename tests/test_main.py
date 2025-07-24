"""Tests for main application entry point."""

import json
from unittest.mock import Mock, mock_open, patch

import pytest
from pydantic import ValidationError

from src.main import main


class TestMainFunctionInitialization:
    """Test basic main function exists and initializes correctly."""

    def test_main_function_exists(self):
        """Test that main function is defined and callable."""
        assert callable(main)

    @patch("src.main.console")
    @patch("src.main.Settings.from_file")
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    @patch("src.main.TodoCLI")
    def test_main_function_initialization_flow(
        self, mock_cli_class, mock_service_class, mock_create_repo, mock_settings, mock_console
    ):
        """Test main function follows proper initialization flow."""
        # Arrange
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance
        mock_repo = Mock()
        mock_create_repo.return_value = mock_repo
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli

        # Act
        main()

        # Assert
        mock_settings.assert_called_once_with("config.json")
        mock_create_repo.assert_called_once_with(mock_settings_instance)
        mock_service_class.assert_called_once_with(mock_repo)
        mock_cli_class.assert_called_once_with(mock_service)
        mock_cli.run.assert_called_once()


class TestSettingsLoading:
    """Test config.json loading with various scenarios."""

    @patch("src.main.Settings.from_file")
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    @patch("src.main.TodoCLI")
    def test_settings_loaded_from_config_file(
        self, mock_cli_class, mock_service_class, mock_create_repo, mock_settings
    ):
        """Test settings are loaded from config.json file."""
        # Arrange
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance

        # Act
        main()

        # Assert
        mock_settings.assert_called_once_with("config.json")

    @patch("src.main.console")
    @patch("src.main.Settings.from_file")
    @patch("src.main.Settings")
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    @patch("src.main.TodoCLI")
    def test_fallback_to_defaults_when_config_missing(
        self,
        mock_cli_class,
        mock_service_class,
        mock_create_repo,
        mock_settings_class,
        mock_settings_from_file,
        mock_console,
    ):
        """Test fallback to default settings when config file is missing."""
        # Arrange
        mock_settings_from_file.side_effect = FileNotFoundError("Config file not found")
        mock_default_settings = Mock()
        mock_settings_class.return_value = mock_default_settings

        # Act
        main()

        # Assert
        mock_settings_from_file.assert_called_once_with("config.json")
        mock_settings_class.assert_called_once()
        mock_create_repo.assert_called_once_with(mock_default_settings)

    @patch("src.main.console")
    @patch("src.main.Settings.from_file")
    def test_validation_error_handling(self, mock_settings, mock_console):
        """Test handling of settings validation errors."""
        # Arrange
        try:
            from src.config.settings import Settings

            Settings(storage_type="invalid")
        except ValidationError as e:
            mock_settings.side_effect = e

        # Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


class TestDependencyInjection:
    """Test repository factory integration and dependency wiring."""

    @patch("src.main.Settings.from_file")
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    @patch("src.main.TodoCLI")
    def test_repository_factory_integration(self, mock_cli_class, mock_service_class, mock_create_repo, mock_settings):
        """Test repository factory is called with settings."""
        # Arrange
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance
        mock_repo = Mock()
        mock_create_repo.return_value = mock_repo

        # Act
        main()

        # Assert
        mock_create_repo.assert_called_once_with(mock_settings_instance)

    @patch("src.main.Settings.from_file")
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    @patch("src.main.TodoCLI")
    def test_todo_service_creation_with_repository(
        self, mock_cli_class, mock_service_class, mock_create_repo, mock_settings
    ):
        """Test TodoService is created with repository dependency."""
        # Arrange
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance
        mock_repo = Mock()
        mock_create_repo.return_value = mock_repo

        # Act
        main()

        # Assert
        mock_service_class.assert_called_once_with(mock_repo)

    @patch("src.main.Settings.from_file")
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    @patch("src.main.TodoCLI")
    def test_todo_cli_creation_with_service(self, mock_cli_class, mock_service_class, mock_create_repo, mock_settings):
        """Test TodoCLI is created with service dependency."""
        # Arrange
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance
        mock_repo = Mock()
        mock_create_repo.return_value = mock_repo
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        # Act
        main()

        # Assert
        mock_cli_class.assert_called_once_with(mock_service)


class TestApplicationLifecycle:
    """Test complete startup sequence and CLI execution."""

    @patch("src.main.Settings.from_file")
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    @patch("src.main.TodoCLI")
    def test_complete_startup_sequence(self, mock_cli_class, mock_service_class, mock_create_repo, mock_settings):
        """Test complete application startup sequence."""
        # Arrange
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance
        mock_repo = Mock()
        mock_create_repo.return_value = mock_repo
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli

        # Act
        main()

        # Assert - verify call order
        mock_settings.assert_called_once()
        mock_create_repo.assert_called_once()
        mock_service_class.assert_called_once()
        mock_cli_class.assert_called_once()
        mock_cli.run.assert_called_once()

    @patch("src.main.Settings.from_file")
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    @patch("src.main.TodoCLI")
    def test_cli_run_invocation(self, mock_cli_class, mock_service_class, mock_create_repo, mock_settings):
        """Test CLI.run() is invoked."""
        # Arrange
        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli

        # Act
        main()

        # Assert
        mock_cli.run.assert_called_once()

    @patch("src.main.Settings.from_file")
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    @patch("src.main.TodoCLI")
    def test_normal_shutdown(self, mock_cli_class, mock_service_class, mock_create_repo, mock_settings):
        """Test normal application shutdown."""
        # Arrange
        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli

        # Act
        result = main()

        # Assert
        assert result is None  # Normal exit


class TestErrorHandling:
    """Test configuration errors, repository failures, and system errors."""

    @patch("src.main.console")
    @patch("src.main.Settings.from_file")
    def test_configuration_errors(self, mock_settings, mock_console):
        """Test handling of configuration loading errors."""
        # Test JSON decode error
        mock_settings.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    @patch("src.main.console")
    @patch("src.main.Settings.from_file")
    @patch("src.main.create_repository")
    def test_repository_creation_failures(self, mock_create_repo, mock_settings, mock_console):
        """Test handling of repository creation failures."""
        # Arrange
        mock_settings.return_value = Mock()
        mock_create_repo.side_effect = ValueError("Invalid repository type")

        # Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 2

    @patch("src.main.console")
    @patch("src.main.Settings.from_file")
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    def test_service_initialization_errors(self, mock_service_class, mock_create_repo, mock_settings, mock_console):
        """Test handling of service initialization errors."""
        # Arrange
        mock_settings.return_value = Mock()
        mock_create_repo.return_value = Mock()
        mock_service_class.side_effect = Exception("Service initialization failed")

        # Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 3

    @patch("src.main.console")
    @patch("src.main.Settings.from_file")
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    @patch("src.main.TodoCLI")
    def test_keyboard_interrupt_handling(
        self, mock_cli_class, mock_service_class, mock_create_repo, mock_settings, mock_console
    ):
        """Test graceful KeyboardInterrupt handling."""
        # Arrange
        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli
        mock_cli.run.side_effect = KeyboardInterrupt()

        # Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0  # Graceful exit

    @patch("src.main.console")
    @patch("src.main.Settings.from_file")
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    @patch("src.main.TodoCLI")
    def test_system_level_errors(
        self, mock_cli_class, mock_service_class, mock_create_repo, mock_settings, mock_console
    ):
        """Test handling of system-level errors."""
        # Arrange
        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli
        mock_cli.run.side_effect = PermissionError("Permission denied")

        # Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 3


class TestConfigurationIntegration:
    """Test config.json integration with Settings model."""

    @patch("builtins.open", new_callable=mock_open, read_data='{"storage_type": "json", "storage_file": "test.json"}')
    @patch("pathlib.Path.exists", return_value=True)
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    @patch("src.main.TodoCLI")
    def test_valid_config_loading(self, mock_cli_class, mock_service_class, mock_create_repo, mock_exists, mock_file):
        """Test loading valid configuration from config.json."""
        # Act
        main()

        # Assert
        mock_file.assert_called()
        mock_create_repo.assert_called_once()

    @patch("src.main.console")
    @patch("builtins.open", new_callable=mock_open, read_data='{"storage_type": "invalid"}')
    @patch("pathlib.Path.exists", return_value=True)
    def test_invalid_config_validation(self, mock_exists, mock_file, mock_console):
        """Test handling of invalid configuration values."""
        # Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


class TestMainIntegration:
    """Test main function integration scenarios."""

    @patch("src.main.console")
    @patch("src.main.Settings.from_file")
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    @patch("src.main.TodoCLI")
    def test_end_to_end_success_flow(
        self, mock_cli_class, mock_service_class, mock_create_repo, mock_settings, mock_console
    ):
        """Test successful end-to-end application flow."""
        # Arrange
        mock_settings_instance = Mock()
        mock_settings_instance.storage_type = "json"
        mock_settings_instance.storage_file = "todos.json"
        mock_settings.return_value = mock_settings_instance

        mock_repo = Mock()
        mock_create_repo.return_value = mock_repo

        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli

        # Act
        main()

        # Assert - verify complete flow
        mock_settings.assert_called_once_with("config.json")
        mock_create_repo.assert_called_once_with(mock_settings_instance)
        mock_service_class.assert_called_once_with(mock_repo)
        mock_cli_class.assert_called_once_with(mock_service)
        mock_cli.run.assert_called_once()

    @patch("src.main.console")
    @patch("src.main.Settings.from_file")
    @patch("src.main.Settings")
    @patch("src.main.create_repository")
    @patch("src.main.TodoService")
    @patch("src.main.TodoCLI")
    def test_fallback_configuration_flow(
        self,
        mock_cli_class,
        mock_service_class,
        mock_create_repo,
        mock_settings_class,
        mock_settings_from_file,
        mock_console,
    ):
        """Test application flow with fallback configuration."""
        # Arrange
        mock_settings_from_file.side_effect = FileNotFoundError("Config not found")
        mock_default_settings = Mock()
        mock_settings_class.return_value = mock_default_settings

        # Act
        main()

        # Assert
        mock_settings_from_file.assert_called_once_with("config.json")
        mock_settings_class.assert_called_once()
        mock_create_repo.assert_called_once_with(mock_default_settings)
