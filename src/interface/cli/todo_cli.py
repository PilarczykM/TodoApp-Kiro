"""
TodoCLI main interface class for console interaction.

This module provides the main CLI interface for the Todo application,
including menu system, user input handling, and navigation.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from src.application.services.todo_service import TodoService
from src.domain.exceptions import TodoDomainError, ValidationError
from src.interface.cli.console_helpers import ConsoleColors

if TYPE_CHECKING:
    from src.domain.models import TodoItem


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
        """
        Handle add todo workflow with Rich prompts and error handling.

        Prompts user for title, description, and due date, then creates
        a new todo item through the service layer. Handles validation
        errors gracefully and allows retry.

        Returns:
            True to continue the main menu loop
        """
        self.console.print()
        self.console.print(Panel("[bold cyan]Add New Todo[/bold cyan]", border_style="cyan"))

        while True:
            try:
                # Collect user input
                title = self._prompt_for_title()
                description = self._prompt_for_description()
                due_date = self._prompt_for_due_date()

                # Create the todo through service
                created_todo = self.service.create_todo(
                    title=title, description=description if description else None, due_date=due_date
                )

                # Display success message
                self._display_todo_created_success(created_todo)
                return True

            except ValidationError as e:
                self._display_validation_error(e)
                # Continue loop to retry
                continue

            except TodoDomainError as e:
                self._display_domain_error(e)
                return True

            except Exception as e:
                self._display_unexpected_error(e)
                return True

    def list_todos(self) -> bool:
        """
        Handle list todos workflow with Rich table display.

        Retrieves all todos from the service and displays them in a formatted
        table with color coding for status and proper sorting by due date.
        Handles empty list and error cases gracefully.

        Returns:
            True to continue the main menu loop
        """
        self.console.print()
        self.console.print(Panel("[bold cyan]Todo List[/bold cyan]", border_style="cyan"))

        try:
            # Get all todos from service
            todos = self.service.get_all_todos()

            # Handle empty list case
            if not todos:
                self._display_empty_todos_message()
                return True

            # Sort todos by due date (overdue first, then by date, then no date)
            sorted_todos = self._sort_todos_by_due_date(todos)

            # Display todos in formatted table
            self._display_todos_table(sorted_todos)
            return True

        except TodoDomainError as e:
            self._display_domain_error(e)
            return True

        except Exception as e:
            self._display_unexpected_error(e)
            return True

    def update_todo(self) -> bool:
        """
        Handle update todo workflow with ID prompting and field editing.

        Prompts user for todo ID, displays current values, allows editing
        of title, description, and due date fields. Handles validation
        errors gracefully and displays success/error messages.

        Returns:
            True to continue the main menu loop
        """
        self.console.print()
        self.console.print(Panel("[bold cyan]Update Todo[/bold cyan]", border_style="cyan"))

        try:
            # Get todo ID from user
            todo_id = self._prompt_for_todo_id()
            if todo_id is None:
                return True

            # Find existing todo
            existing_todo = self.service.repository.find_by_id(todo_id)
            if existing_todo is None:
                self._display_todo_not_found_error()
                return True

            # Display current values
            self._display_current_todo_values(existing_todo)

            # Prompt for updates
            title = self._prompt_for_updated_title(existing_todo.title)
            description = self._prompt_for_updated_description(existing_todo.description)
            due_date = self._prompt_for_updated_due_date(existing_todo.due_date)

            # Update todo through service
            updated_todo = self.service.update_todo(
                todo_id=todo_id,
                title=title if title != existing_todo.title else None,
                description=description if description != existing_todo.description else None,
                due_date=due_date if due_date != existing_todo.due_date else None,
            )

            # Display success message
            self._display_todo_updated_success(updated_todo)
            return True

        except ValidationError as e:
            self._display_validation_error(e)
            return True

        except TodoDomainError as e:
            self._display_domain_error(e)
            return True

        except Exception as e:
            self._display_unexpected_error(e)
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

    def _display_empty_todos_message(self) -> None:
        """Display message when no todos exist."""
        empty_message = f"[{ConsoleColors.INFO}]No todos found. Start by adding your first todo![/{ConsoleColors.INFO}]"
        self.console.print(Panel(empty_message, title="Empty List", border_style="yellow"))

    def _sort_todos_by_due_date(self, todos: list["TodoItem"]) -> list["TodoItem"]:
        """
        Sort todos by due date with specific ordering.

        Order: Overdue items first, then future items by due date, then items without due date.

        Args:
            todos: List of TodoItem instances to sort

        Returns:
            Sorted list of TodoItem instances
        """
        from datetime import datetime

        def sort_key(todo: "TodoItem") -> tuple:
            # Items without due date go to the end
            if todo.due_date is None:
                return (2, datetime.max)

            now = datetime.now()
            # Overdue items (past due date) go first
            if todo.due_date < now:
                return (0, todo.due_date)

            # Future items go in the middle, sorted by due date
            return (1, todo.due_date)

        return sorted(todos, key=sort_key)

    def _display_todos_table(self, todos: list["TodoItem"]) -> None:
        """Display todos in a formatted Rich table."""
        from src.interface.cli.console_helpers import format_todo_table

        table = format_todo_table(todos)
        self.console.print(table)

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

    def _prompt_for_title(self) -> str:
        """Prompt user for todo title."""
        return Prompt.ask("[bold]Enter todo title[/bold]", default="")

    def _prompt_for_description(self) -> str:
        """Prompt user for todo description (optional)."""
        return Prompt.ask("[bold]Enter description[/bold] [dim](optional)[/dim]", default="")

    def _prompt_for_due_date(self) -> datetime | None:
        """Prompt user for due date and parse it."""
        date_input = Prompt.ask("[bold]Enter due date[/bold] [dim](YYYY-MM-DD format, optional)[/dim]", default="")

        if not date_input.strip():
            return None

        try:
            # Parse date in YYYY-MM-DD format
            return datetime.strptime(date_input.strip(), "%Y-%m-%d")
        except ValueError:
            self.console.print(
                f"[{ConsoleColors.WARNING}]Invalid date format. Please use YYYY-MM-DD format.[/{ConsoleColors.WARNING}]"
            )
            # Retry date input
            return self._prompt_for_due_date()

    def _display_todo_created_success(self, todo: "TodoItem") -> None:
        """Display success message with created todo details."""
        success_message = f"[{ConsoleColors.SUCCESS}]✅ Todo created successfully![/{ConsoleColors.SUCCESS}]"

        details = f"""
[bold]Title:[/bold] {todo.title}
[bold]ID:[/bold] {str(todo.id)[:8]}...
[bold]Description:[/bold] {todo.description or "No description"}
[bold]Due Date:[/bold] {todo.due_date.strftime("%Y-%m-%d") if todo.due_date else "No due date"}
        """

        self.console.print(success_message)
        self.console.print(Panel(details.strip(), title="Todo Details", border_style="green"))

    def _display_validation_error(self, error: ValidationError) -> None:
        """Display validation error message with retry option."""
        error_message = f"[{ConsoleColors.ERROR}]❌ Validation Error:[/{ConsoleColors.ERROR}] {error!s}"
        self.console.print(error_message)
        self.console.print(f"[{ConsoleColors.INFO}]Please try again with valid input.[/{ConsoleColors.INFO}]")
        self.console.print()

    def _display_domain_error(self, error: TodoDomainError) -> None:
        """Display domain error message."""
        error_message = f"[{ConsoleColors.ERROR}]❌ Error:[/{ConsoleColors.ERROR}] {error!s}"
        self.console.print(error_message)

    def _display_unexpected_error(self, error: Exception) -> None:
        """Display unexpected error message."""
        error_message = f"[{ConsoleColors.ERROR}]❌ Unexpected error:[/{ConsoleColors.ERROR}] {error!s}"
        self.console.print(error_message)
        self.console.print(
            f"[{ConsoleColors.INFO}]Please try again or contact support if the problem persists.[/{ConsoleColors.INFO}]"
        )

    def _show_goodbye_message(self) -> None:
        """Display goodbye message when exiting."""
        goodbye_panel = Panel(
            "[bold green]Thank you for using Todo Manager![/bold green]\nHave a productive day! 🚀",
            title="Goodbye",
            border_style="green",
        )
        self.console.print(goodbye_panel)

    def _prompt_for_todo_id(self) -> "UUID | None":
        """
        Prompt user for todo ID and parse to UUID.

        Returns:
            UUID if valid, None if invalid format
        """
        id_input = Prompt.ask("[bold]Enter todo ID[/bold]", default="")

        if not id_input.strip():
            self.console.print(f"[{ConsoleColors.ERROR}]Todo ID is required.[/{ConsoleColors.ERROR}]")
            return None

        try:
            return UUID(id_input.strip())
        except ValueError:
            self.console.print(
                f"[{ConsoleColors.ERROR}]Invalid ID format. Please enter a valid UUID.[/{ConsoleColors.ERROR}]"
            )
            return None

    def _display_current_todo_values(self, todo: "TodoItem") -> None:
        """Display current todo values in a formatted panel."""
        due_date_str = todo.due_date.strftime("%Y-%m-%d") if todo.due_date else "No due date"

        current_values = f"""
[bold]Current Values:[/bold]

[bold]Title:[/bold] {todo.title}
[bold]Description:[/bold] {todo.description or "No description"}
[bold]Due Date:[/bold] {due_date_str}
[bold]Status:[/bold] {"Completed" if todo.completed else "Pending"}

[dim]Leave fields empty to keep current values[/dim]
        """

        self.console.print(Panel(current_values.strip(), title="Todo Details", border_style="blue"))

    def _prompt_for_updated_title(self, current_title: str) -> str:
        """Prompt for updated title with current value as default."""
        new_title = Prompt.ask("[bold]Enter new title[/bold] [dim](or press Enter to keep current)[/dim]", default="")
        return new_title.strip() if new_title.strip() else current_title

    def _prompt_for_updated_description(self, current_description: str | None) -> str | None:
        """Prompt for updated description with current value handling."""
        current_desc_display = current_description or "No description"
        new_description = Prompt.ask(
            f"[bold]Enter new description[/bold] [dim](current: {current_desc_display})[/dim]", default=""
        )
        if not new_description.strip():
            return current_description
        return new_description.strip()

    def _prompt_for_updated_due_date(self, current_due_date: datetime | None) -> datetime | None:
        """Prompt for updated due date with current value handling."""
        current_date_display = current_due_date.strftime("%Y-%m-%d") if current_due_date else "No due date"

        date_input = Prompt.ask(
            f"[bold]Enter new due date[/bold] [dim](YYYY-MM-DD, current: {current_date_display})[/dim]", default=""
        )

        if not date_input.strip():
            return current_due_date

        try:
            return datetime.strptime(date_input.strip(), "%Y-%m-%d")
        except ValueError:
            self.console.print(
                f"[{ConsoleColors.WARNING}]Invalid date format. Please use YYYY-MM-DD format.[/{ConsoleColors.WARNING}]"
            )
            return self._prompt_for_updated_due_date(current_due_date)

    def _display_todo_not_found_error(self) -> None:
        """Display error message when todo is not found."""
        error_message = (
            f"[{ConsoleColors.ERROR}]❌ Todo not found.[/{ConsoleColors.ERROR}] Please check the ID and try again."
        )
        self.console.print(error_message)

    def _display_todo_updated_success(self, todo: "TodoItem") -> None:
        """Display success message with updated todo details."""
        success_message = f"[{ConsoleColors.SUCCESS}]✅ Todo updated successfully![/{ConsoleColors.SUCCESS}]"

        details = f"""
[bold]Updated Todo:[/bold]

[bold]Title:[/bold] {todo.title}
[bold]ID:[/bold] {str(todo.id)[:8]}...
[bold]Description:[/bold] {todo.description or "No description"}
[bold]Due Date:[/bold] {todo.due_date.strftime("%Y-%m-%d") if todo.due_date else "No due date"}
[bold]Status:[/bold] {"Completed" if todo.completed else "Pending"}
        """

        self.console.print(success_message)
        self.console.print(Panel(details.strip(), title="Updated Details", border_style="green"))
