"""Main application entry point with dependency injection."""

import json
import sys
from typing import NoReturn

from pydantic import ValidationError
from rich.console import Console

from src.application.services.todo_service import TodoService
from src.config.repository_factory import create_repository
from src.config.settings import Settings
from src.interface.cli.todo_cli import TodoCLI

console = Console()


def main() -> None:
    """
    Main application entry point with dependency injection.

    Loads configuration, creates repository via factory pattern,
    initializes service and CLI components, then starts the application.

    Exit codes:
        0: Normal exit or graceful shutdown
        1: Configuration/initialization errors
        2: Repository creation errors
        3: Critical system errors
    """
    try:
        # Load settings from config.json with fallback to defaults
        try:
            settings = Settings.from_file("config.json")
        except FileNotFoundError:
            console.print("[yellow]Configuration file not found, using defaults[/yellow]")
            settings = Settings()
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON in config file: {e}[/red]")
            _exit_with_error(1)
        except ValidationError as e:
            console.print(f"[red]Configuration validation error: {e}[/red]")
            _exit_with_error(1)

        # Create repository using factory pattern
        try:
            repository = create_repository(settings)
        except ValueError as e:
            console.print(f"[red]Repository creation failed: {e}[/red]")
            _exit_with_error(2)

        # Initialize TodoService with repository dependency
        try:
            service = TodoService(repository)
        except Exception as e:
            console.print(f"[red]Service initialization failed: {e}[/red]")
            _exit_with_error(3)

        # Create TodoCLI with service dependency
        try:
            cli = TodoCLI(service)
        except Exception as e:
            console.print(f"[red]CLI initialization failed: {e}[/red]")
            _exit_with_error(3)

        # Start CLI application loop
        cli.run()

    except KeyboardInterrupt:
        console.print("\n[yellow]Application interrupted by user[/yellow]")
        _exit_with_error(0)  # Graceful shutdown
    except PermissionError as e:
        console.print(f"[red]Permission error: {e}[/red]")
        _exit_with_error(3)
    except OSError as e:
        console.print(f"[red]System error: {e}[/red]")
        _exit_with_error(3)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        _exit_with_error(3)


def _exit_with_error(code: int) -> NoReturn:
    """Exit the application with the specified error code.

    Args:
        code: Exit code to use
    """
    sys.exit(code)


if __name__ == "__main__":
    main()
