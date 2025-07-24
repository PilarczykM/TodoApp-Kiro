"""
Console helper utilities for the CLI interface.

This module provides utilities for console formatting, colors, and display
helpers using Rich library for enhanced terminal output.
"""

from rich.table import Table

from src.domain.models import TodoItem


class ConsoleColors:
    """
    Console color constants for Rich formatting.

    Provides consistent color scheme across the CLI interface
    using Rich markup syntax.
    """

    SUCCESS = "green"
    ERROR = "red"
    WARNING = "yellow"
    INFO = "blue"
    PENDING = "yellow"
    COMPLETED = "green"


def format_status(completed: bool) -> str:
    """
    Format todo status with appropriate color.

    Args:
        completed: Boolean indicating if todo is completed

    Returns:
        Formatted status string with Rich color markup
    """
    if completed:
        return f"[{ConsoleColors.COMPLETED}]COMPLETED[/{ConsoleColors.COMPLETED}]"
    else:
        return f"[{ConsoleColors.PENDING}]PENDING[/{ConsoleColors.PENDING}]"


def format_todo_table(todos: list[TodoItem]) -> Table:
    """
    Create a Rich table for displaying todo items.

    Args:
        todos: List of TodoItem instances to display

    Returns:
        Rich Table instance with formatted todo data
    """
    table = Table(title="Todo Items")

    # Add columns
    table.add_column("ID", style="dim", width=8)
    table.add_column("Title", style="bold")
    table.add_column("Description")
    table.add_column("Status", justify="center")
    table.add_column("Due Date", justify="center")
    table.add_column("Created", justify="center", style="dim")

    # Add rows for each todo
    for todo in todos:
        # Format ID (show first 8 characters)
        todo_id = str(todo.id)[:8]

        # Format description (handle None)
        description = todo.description if todo.description else "-"

        # Format due date (handle None)
        due_date = todo.due_date.strftime("%Y-%m-%d") if todo.due_date else "-"

        # Format created date
        created = todo.created_at.strftime("%Y-%m-%d %H:%M")

        # Format status with color
        status = format_status(todo.completed)

        table.add_row(todo_id, todo.title, description, status, due_date, created)

    return table
