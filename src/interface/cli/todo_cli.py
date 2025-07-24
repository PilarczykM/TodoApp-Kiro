"""
TodoCLI main interface class for console interaction.

This module provides the main CLI interface for the Todo application,
including menu system, user input handling, and navigation.
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from src.application.services.todo_service import TodoService
from src.interface.cli.console_helpers import ConsoleColors


class TodoCLI:
    """
    Main CLI interface for the Todo application.

    Provides menu system, user interaction, and navigation
    for all todo management operations.
    """

    def __init__(self, service: TodoService) -> None:
        """
        Initialize TodoCLI with service dependency.

        Args:
            service: TodoService instance for business operations
        """
        self.service = service
        self.console = Console()

    def run(self) -> None:
        """
        Start the CLI application main loop.

        Displays the main menu and handles user navigation
        until the user chooses to exit.
        """
        try:
            while True:
                self.show_main_menu()
                choice = self._get_menu_choice()

                if choice == "1":
                    self.add_todo()
                elif choice == "2":
                    self.list_todos()
                elif choice == "3":
                    self.update_todo()
                elif choice == "4":
                    self.complete_todo()
                elif choice == "5":
                    self.delete_todo()
                elif choice == "6":
                    self._show_goodbye_message()
                    break
                else:
                    self._show_invalid_choice_message()

        except KeyboardInterrupt:
            self._show_goodbye_message()

    def show_main_menu(self) -> None:
        """Display the main menu with all available options."""
        self.console.print()

        # Display welcome header
        welcome_panel = Panel(
            "[bold blue]Todo Manager[/bold blue]\nManage your tasks efficiently", title="Welcome", border_style="blue"
        )
        self.console.print(welcome_panel)

        # Display menu options
        menu_text = """
[bold]Choose an option:[/bold]

[cyan]1.[/cyan] Add Todo
[cyan]2.[/cyan] List Todos
[cyan]3.[/cyan] Update Todo
[cyan]4.[/cyan] Complete Todo
[cyan]5.[/cyan] Delete Todo
[cyan]6.[/cyan] Exit
        """

        menu_panel = Panel(menu_text.strip(), title="Menu", border_style="cyan")
        self.console.print(menu_panel)

    def add_todo(self) -> None:
        """Handle add todo workflow - placeholder for now."""
        self.console.print(f"[{ConsoleColors.INFO}]Add Todo functionality coming soon![/{ConsoleColors.INFO}]")

    def list_todos(self) -> None:
        """Handle list todos workflow - placeholder for now."""
        self.console.print(f"[{ConsoleColors.INFO}]List Todos functionality coming soon![/{ConsoleColors.INFO}]")

    def update_todo(self) -> None:
        """Handle update todo workflow - placeholder for now."""
        self.console.print(f"[{ConsoleColors.INFO}]Update Todo functionality coming soon![/{ConsoleColors.INFO}]")

    def complete_todo(self) -> None:
        """Handle complete todo workflow - placeholder for now."""
        self.console.print(f"[{ConsoleColors.INFO}]Complete Todo functionality coming soon![/{ConsoleColors.INFO}]")

    def delete_todo(self) -> None:
        """Handle delete todo workflow - placeholder for now."""
        self.console.print(f"[{ConsoleColors.INFO}]Delete Todo functionality coming soon![/{ConsoleColors.INFO}]")

    def _get_menu_choice(self) -> str:
        """
        Get user's menu choice with input validation.

        Returns:
            User's choice as string
        """
        return Prompt.ask("\n[bold]Enter your choice[/bold]", choices=["1", "2", "3", "4", "5", "6"], default="6")

    def _show_invalid_choice_message(self) -> None:
        """Display invalid choice error message."""
        self.console.print(
            f"[{ConsoleColors.ERROR}]Invalid choice! Please select a valid option.[/{ConsoleColors.ERROR}]"
        )

    def _show_goodbye_message(self) -> None:
        """Display goodbye message when exiting."""
        goodbye_panel = Panel(
            "[bold green]Thank you for using Todo Manager![/bold green]\nHave a productive day! 🚀",
            title="Goodbye",
            border_style="green",
        )
        self.console.print(goodbye_panel)
