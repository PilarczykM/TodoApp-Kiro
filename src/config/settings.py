"""Settings configuration management with Pydantic validation."""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, validator


class Settings(BaseModel):
    """Application settings with validation and JSON config loading."""

    storage_type: Literal["json", "xml"] = Field(default="json", description="Type of storage backend to use")
    storage_file: str = Field(default="todos.json", description="File path for data storage")

    @validator("storage_file")
    def validate_storage_file(cls, v: str) -> str:
        """Validate that storage_file is not empty."""
        if not v or not v.strip():
            raise ValueError("storage_file cannot be empty")
        return v

    @classmethod
    def from_file(cls, config_path: str) -> "Settings":
        """Load settings from a JSON configuration file.

        Args:
            config_path: Path to the JSON configuration file

        Returns:
            Settings instance with loaded configuration

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file contains invalid JSON
        """
        config_file = Path(config_path)

        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_file) as f:
            config_data = json.load(f)

        return cls(**config_data)

    def to_dict(self) -> dict:
        """Convert settings to dictionary.

        Returns:
            Dictionary representation of settings
        """
        return self.dict()
