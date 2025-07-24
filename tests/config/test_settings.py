"""Tests for Settings configuration management."""

import json
import tempfile
from pathlib import Path

import pytest

from src.config.settings import Settings


class TestSettings:
    """Test suite for Settings configuration management."""

    def test_should_create_settings_with_default_values(self):
        """Test Settings creation with default configuration values."""
        # Act
        settings = Settings()

        # Assert
        assert settings.storage_type == "json"
        assert settings.storage_file == "todos.json"

    def test_should_load_settings_from_json_file(self):
        """Test loading Settings from a JSON configuration file."""
        # Arrange
        config_data = {"storage_type": "xml", "storage_file": "custom_todos.xml"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            # Act
            settings = Settings.from_file(config_file)

            # Assert
            assert settings.storage_type == "xml"
            assert settings.storage_file == "custom_todos.xml"
        finally:
            Path(config_file).unlink()

    def test_should_validate_storage_type_enum(self):
        """Test that Settings validates storage_type against allowed values."""
        # Act & Assert
        with pytest.raises(ValueError, match="storage_type"):
            Settings(storage_type="invalid_type")

    def test_should_validate_storage_file_not_empty(self):
        """Test that Settings validates storage_file is not empty."""
        # Act & Assert
        with pytest.raises(ValueError, match="storage_file"):
            Settings(storage_file="")

    def test_should_handle_missing_config_file(self):
        """Test handling of missing configuration file."""
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            Settings.from_file("nonexistent_config.json")

    def test_should_handle_invalid_json_config_file(self):
        """Test handling of invalid JSON in configuration file."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            config_file = f.name

        try:
            # Act & Assert
            with pytest.raises(json.JSONDecodeError):
                Settings.from_file(config_file)
        finally:
            Path(config_file).unlink()

    def test_should_use_default_values_for_missing_fields(self):
        """Test that Settings uses defaults for missing configuration fields."""
        # Arrange
        config_data = {"storage_type": "xml"}  # Missing storage_file

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            # Act
            settings = Settings.from_file(config_file)

            # Assert
            assert settings.storage_type == "xml"
            assert settings.storage_file == "todos.json"  # Default value
        finally:
            Path(config_file).unlink()

    def test_should_convert_to_dict(self):
        """Test Settings conversion to dictionary."""
        # Arrange
        settings = Settings(storage_type="xml", storage_file="test.xml")

        # Act
        settings_dict = settings.to_dict()

        # Assert
        assert settings_dict == {"storage_type": "xml", "storage_file": "test.xml"}
