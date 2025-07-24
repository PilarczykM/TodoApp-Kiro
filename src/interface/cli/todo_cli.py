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
        self._menu_options = {
            "1": ("Add Todo", self.add_todo),
            "2": ("List Todos", self.list_todos),
            "3": ("Update Todo", self.update_todo),
            "4": ("Complete Todo", self.complete_todo),
            "5": ("Delete Todo", self.delete_todo),
            "6": ("Exit", self._exit_application),
        }

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

                if not self._handle_menu_choice(choice):
                    break

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
        menu_options = []
        for option_key, (description, _) in self._menu_options.items():
            menu_options.append(f"[cyan]{option_key}.[/cyan] {description}")

        menu_text = f"""
[bold]Choose an option:[/bold]

{chr(10).join(menu_options)}
        """

        menu_panel = Panel(menu_text.strip(), title="Menu", border_style="cyan")
        self.console.print(menu_panel)

    def add_todo(self) -> bool:
        """Handle add todo workflow - placeholder for now."""
        self.console.print(f"[{ConsoleColors.INFO}]Add Todo functionality coming soon![/{ConsoleColors.INFO}]")
        return True

    def list_todos(self) -> bool:
        """Handle list todos workflow - placeholder for now."""
        self.console.print(f"[{ConsoleColors.INFO}]List Todos functionality coming soon![/{ConsoleColors.INFO}]")
        return True

    def update_todo(self) -> bool:
        """Handle update todo workflow - placeholder for now."""
        self.console.print(f"[{ConsoleColors.INFO}]Update Todo functionality coming soon![/{ConsoleColors.INFO}]")
        return True

    def complete_todo(self) -> bool:
        """Handle complete todo workflow - placeholder for now."""
        self.console.print(f"[{ConsoleColors.INFO}]Complete Todo functionality coming soon![/{ConsoleColors.INFO}]")
        return True

    def delete_todo(self) -> bool:
        """Handle delete todo workflow - placeholder for now."""
        self.console.print(f"[{ConsoleColors.INFO}]Delete Todo functionality coming soon![/{ConsoleColors.INFO}]")
        return True

    def _exit_application(self) -> bool:
        """Handle application exit."""
        self._show_goodbye_message()
        return False

    def _get_menu_choice(self) -> str:
        """
        Get user's menu choice with input validation.

        Returns:
            User's choice as string
        """
        valid_choices = list(self._menu_options.keys())
        return Prompt.ask("\n[bold]Enter your choice[/bold]", choices=valid_choices, default="6")

    def _handle_menu_choice(self, choice: str) -> bool:
        """
        Handle user's menu choice using command dispatch pattern.

        Args:
            choice: User's menu choice as string

        Returns:
            True to continue the main loop, False to exit
        """
        if choice in self._menu_options:
            _, handler = self._menu_options[choice]
            return handler()
        else:
            self._show_invalid_choice_message()
            return True

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
