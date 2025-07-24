# Design Document

## Overview

This design document outlines the architecture and implementation approach for a console-based Todo application in Python that follows Domain-Driven Design (DDD) principles, Test-Driven Development (TDD) practices, and supports switchable persistence backends. The application will be built using a layered architecture with clear separation of concerns, comprehensive validation, and a rich console interface.

## Required Libraries

### Core Dependencies
- **pydantic>=2.0**: Data validation and settings management using Pydantic v2
- **rich**: Enhanced console interface with colors, tables, and formatting
- **lxml**: XML parsing and generation for XML persistence backend

### Development Dependencies
- **pytest**: Testing framework for unit and integration tests
- **pytest-cov**: Code coverage reporting for pytest
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checker for Python
- **uv**: Package manager for dependency management

### Standard Library Usage
- **json**: JSON serialization for JSON persistence backend
- **pathlib**: Modern path handling for file operations
- **uuid**: UUID generation for todo item identifiers
- **datetime**: Date and time handling for due dates and timestamps
- **abc**: Abstract base classes for repository interfaces
- **enum**: Enumeration support for configuration options
- **typing**: Type hints and annotations

### Library Installation with uv
```bash
# Core dependencies
uv add "pydantic>=2.0"
uv add rich
uv add lxml

# Development dependencies
uv add --dev pytest
uv add --dev pytest-cov
uv add --dev ruff
uv add --dev mypy
```

### pyproject.toml Dependencies Section
```toml
[project]
dependencies = [
    "pydantic>=2.0",
    "rich",
    "lxml",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov",
    "ruff",
    "mypy",
]
```

## Coding Standards and Best Practices

### Clean Code Principles
- **Single Responsibility Principle (SRP)**: Each class and function has one reason to change
- **Open/Closed Principle**: Open for extension, closed for modification
- **Dependency Inversion**: Depend on abstractions, not concretions
- **KISS (Keep It Simple, Stupid)**: Prefer simple solutions over complex ones
- **YAGNI (You Aren't Gonna Need It)**: Don't implement features until they're needed
- **DRY (Don't Repeat Yourself)**: Avoid code duplication through abstraction

### Import Conventions
All imports use absolute imports from the project root:
```python
# Correct absolute imports
from domain.models import TodoItem
from application.todo_service import TodoService
from infrastructure.interfaces import TodoRepository
from infrastructure.json_repository import JSONTodoRepository
from config.settings import Settings

# Avoid relative imports like:
# from ..domain.models import TodoItem  # Don't do this
```

### Code Organization Standards
- **Function Length**: Maximum 20 lines per function
- **Class Length**: Maximum 200 lines per class
- **Parameter Count**: Maximum 5 parameters per function
- **Cyclomatic Complexity**: Maximum complexity of 10
- **Naming Conventions**:
  - Classes: PascalCase (e.g., `TodoService`)
  - Functions/Variables: snake_case (e.g., `create_todo`)
  - Constants: UPPER_SNAKE_CASE (e.g., `MAX_TITLE_LENGTH`)

### Helper Functions and Utilities
```python
# interface/console_helpers.py
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import List
from domain.models import TodoItem

class ConsoleColors:
    SUCCESS = "[green]"
    ERROR = "[red]"
    WARNING = "[yellow]"
    INFO = "[blue]"
    END = "[/]"

def display_success_message(console: Console, message: str) -> None:
    """Display success message with green color"""
    console.print(f"{ConsoleColors.SUCCESS}{message}{ConsoleColors.END}")

def display_error_message(console: Console, message: str) -> None:
    """Display error message with red color"""
    console.print(f"{ConsoleColors.ERROR}{message}{ConsoleColors.END}")

def create_todo_table(todos: List[TodoItem]) -> Table:
    """Create a formatted table for displaying todos"""
    table = Table(title="Todo Items")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Description", style="white")
    table.add_column("Due Date", style="yellow")
    table.add_column("Status", style="green")

    for todo in todos:
        status = "✅ Complete" if todo.completed else "⏳ Pending"
        due_date = todo.due_date.strftime("%Y-%m-%d") if todo.due_date else "No due date"
        table.add_row(
            str(todo.id)[:8],
            todo.title,
            todo.description or "No description",
            due_date,
            status
        )

    return table
```

## Architecture

The application follows a clean architecture pattern with four distinct layers:

### 1. Domain Layer
- **Purpose**: Contains business logic and domain models
- **Components**:
  - `TodoItem` model with Pydantic v2 validation
  - Domain services for business rules
  - Value objects and domain exceptions
- **Dependencies**: None (pure domain logic)

### 2. Application Layer
- **Purpose**: Orchestrates use cases and coordinates between layers
- **Components**:
  - `TodoService` for application logic
  - Use case implementations (CRUD operations)
  - Application-specific exceptions
- **Dependencies**: Domain layer only

### 3. Infrastructure Layer
- **Purpose**: Handles external concerns like persistence and I/O
- **Components**:
  - Repository implementations (`JSONTodoRepository`, `XMLTodoRepository`)
  - Repository interfaces (`TodoRepository`)
  - File system operations
  - Data serialization/deserialization
- **Dependencies**: Domain layer for models

### 4. Interface Layer
- **Purpose**: Handles user interaction and presentation
- **Components**:
  - CLI interface using Rich library
  - Menu system and user input handling
  - Display formatting and styling
- **Dependencies**: Application layer

## Components and Interfaces

### Domain Models

```python
# domain/models.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

class TodoItem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    due_date: Optional[datetime] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @validator('due_date')
    def validate_due_date(cls, v):
        if v and v < datetime.now():
            raise ValueError('Due date cannot be in the past')
        return v

    def mark_completed(self) -> None:
        self.completed = True
        self.updated_at = datetime.now()

    def update_details(self, title: str = None, description: str = None, due_date: datetime = None) -> None:
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if due_date is not None:
            self.due_date = due_date
        self.updated_at = datetime.now()
```

### Repository Pattern

```python
# infrastructure/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.models import TodoItem

class TodoRepository(ABC):
    @abstractmethod
    def save(self, todo: TodoItem) -> None:
        pass

    @abstractmethod
    def find_by_id(self, todo_id: UUID) -> Optional[TodoItem]:
        pass

    @abstractmethod
    def find_all(self) -> List[TodoItem]:
        pass

    @abstractmethod
    def update(self, todo: TodoItem) -> None:
        pass

    @abstractmethod
    def delete(self, todo_id: UUID) -> bool:
        pass
```

### Application Service

```python
# application/todo_service.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from domain.models import TodoItem
from infrastructure.interfaces import TodoRepository

class TodoService:
    def __init__(self, repository: TodoRepository):
        self._repository = repository

    def create_todo(self, title: str, description: str = None, due_date: datetime = None) -> TodoItem:
        todo = TodoItem(title=title, description=description, due_date=due_date)
        self._repository.save(todo)
        return todo

    def get_all_todos(self) -> List[TodoItem]:
        return self._repository.find_all()

    def get_todo_by_id(self, todo_id: UUID) -> Optional[TodoItem]:
        return self._repository.find_by_id(todo_id)

    def update_todo(self, todo_id: UUID, title: str = None, description: str = None, due_date: datetime = None) -> Optional[TodoItem]:
        todo = self._repository.find_by_id(todo_id)
        if todo:
            todo.update_details(title, description, due_date)
            self._repository.update(todo)
        return todo

    def complete_todo(self, todo_id: UUID) -> Optional[TodoItem]:
        todo = self._repository.find_by_id(todo_id)
        if todo:
            todo.mark_completed()
            self._repository.update(todo)
        return todo

    def delete_todo(self, todo_id: UUID) -> bool:
        return self._repository.delete(todo_id)
```

### Persistence Strategy

The application uses the Strategy pattern to support switchable persistence backends:

#### JSON Repository
```python
# infrastructure/json_repository.py
import json
from pathlib import Path
from typing import List, Optional
from uuid import UUID
from domain.models import TodoItem
from infrastructure.interfaces import TodoRepository

class JSONTodoRepository(TodoRepository):
    def __init__(self, file_path: str = "todos.json"):
        self.file_path = Path(file_path)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not self.file_path.exists():
            self.file_path.write_text("[]")

    def _load_todos(self) -> List[dict]:
        return json.loads(self.file_path.read_text())

    def _save_todos(self, todos: List[dict]):
        self.file_path.write_text(json.dumps(todos, indent=2, default=str))
```

#### XML Repository
```python
# infrastructure/xml_repository.py
from lxml import etree
from pathlib import Path
from typing import List, Optional
from uuid import UUID
from domain.models import TodoItem
from infrastructure.interfaces import TodoRepository

class XMLTodoRepository(TodoRepository):
    def __init__(self, file_path: str = "todos.xml"):
        self.file_path = Path(file_path)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not self.file_path.exists():
            root = etree.Element("todos")
            tree = etree.ElementTree(root)
            tree.write(str(self.file_path), pretty_print=True, xml_declaration=True, encoding="utf-8")
```

### CLI Interface Design

The CLI will use Rich library for enhanced console experience and focus on todo management operations:

```python
# interface/cli.py
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from application.todo_service import TodoService
from interface.console_helpers import (
    display_success_message,
    display_error_message,
    create_todo_table
)
from domain.exceptions import TodoNotFoundError, ValidationError

class TodoCLI:
    def __init__(self, todo_service: TodoService):
        self.console = Console()
        self.todo_service = todo_service

    def run(self) -> None:
        """Main application loop"""
        self._display_welcome()
        while True:
            self._display_menu()
            choice = self._get_user_choice()
            if not self._handle_choice(choice):
                break

    def _display_welcome(self) -> None:
        """Display welcome message"""
        welcome = Panel.fit(
            "Welcome to Todo App\nStorage format configured via config file",
            title="Todo Application"
        )
        self.console.print(welcome)

    def _display_menu(self) -> None:
        """Display main menu options"""
        menu = Panel.fit(
            "[1] Add Todo\n[2] List Todos\n[3] Update Todo\n[4] Complete Todo\n[5] Delete Todo\n[6] Exit",
            title="Todo App Menu"
        )
        self.console.print(menu)

    def _list_todos(self) -> None:
        """Display all todos in a formatted table"""
        try:
            todos = self.todo_service.get_all_todos()
            if not todos:
                display_error_message(self.console, "No todos found")
                return

            table = create_todo_table(todos)
            self.console.print(table)
        except Exception as e:
            display_error_message(self.console, f"Error listing todos: {e}")
```

## Data Models

### TodoItem Schema
- **id**: UUID (auto-generated, primary key)
- **title**: String (1-200 characters, required)
- **description**: String (optional, max 1000 characters)
- **due_date**: DateTime (optional, must be future date)
- **completed**: Boolean (default: false)
- **created_at**: DateTime (auto-generated)
- **updated_at**: DateTime (auto-updated)

### Validation Rules
- Title must be non-empty and under 200 characters
- Description is optional but limited to 1000 characters
- Due date, if provided, must be in the future
- All datetime fields use ISO format for serialization
- UUID fields use string representation for persistence

### Data Flow
1. **Input**: User provides data through CLI
2. **Validation**: Pydantic validates data at domain level
3. **Processing**: Application service coordinates business logic
4. **Persistence**: Repository saves to chosen backend (JSON/XML)
5. **Output**: Rich CLI displays formatted results

## Error Handling

### Domain-Level Errors
- **ValidationError**: Pydantic validation failures
- **BusinessRuleError**: Domain logic violations
- **TodoNotFoundError**: Entity not found exceptions

### Application-Level Errors
- **ServiceError**: Application service failures
- **RepositoryError**: Persistence operation failures

### Infrastructure-Level Errors
- **FileSystemError**: File I/O failures
- **SerializationError**: Data format conversion failures

### Error Handling Strategy
```python
# domain/exceptions.py
class TodoDomainError(Exception):
    """Base exception for domain errors"""
    pass

class TodoNotFoundError(TodoDomainError):
    """Raised when a todo item is not found"""
    pass

class ValidationError(TodoDomainError):
    """Raised when validation fails"""
    pass

# Error handling in CLI
try:
    result = self.todo_service.create_todo(title, description, due_date)
    self.console.print(f"[green]Todo created successfully: {result.title}[/green]")
except ValidationError as e:
    self.console.print(f"[red]Validation Error: {e}[/red]")
except Exception as e:
    self.console.print(f"[red]Unexpected error: {e}[/red]")
```

## Testing Strategy

### Test Structure
The test structure mirrors the source code structure for easy navigation and maintenance:

```
tests/
├── domain/
│   ├── __init__.py
│   └── test_models.py
├── application/
│   ├── __init__.py
│   └── test_todo_service.py
├── infrastructure/
│   ├── __init__.py
│   ├── test_json_repository.py
│   └── test_xml_repository.py
├── interface/
│   ├── __init__.py
│   └── test_cli.py
├── config/
│   ├── __init__.py
│   └── test_settings.py
├── integration/
│   ├── __init__.py
│   └── test_end_to_end.py
└── fixtures/
    ├── __init__.py
    └── sample_data.py
```

### TDD Approach
1. **Red**: Write failing test first
2. **Green**: Write minimal code to pass test
3. **Refactor**: Improve code while keeping tests green

### Test Coverage Requirements
- **Domain Models**: 100% coverage including validation rules
- **Application Services**: 100% coverage including error paths
- **Repository Implementations**: 100% coverage for both JSON and XML
- **CLI Interface**: Integration tests for user workflows

### Testing Tools Configuration
```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=95"
]

[tool.coverage.run]
source = ["src"]
omit = ["tests/*"]
```

### Mock Strategy
- Mock file system operations in repository tests
- Mock repository in service tests
- Use dependency injection for testability
- Create test fixtures for consistent data

## Architecture Diagrams

### Layer Dependencies
```
┌─────────────────┐
│  Interface      │ ← User Interaction (Rich CLI)
│  (CLI)          │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Application    │ ← Use Cases & Coordination
│  (Services)     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Domain         │ ← Business Logic & Models
│  (Models)       │
└─────────────────┘
         ▲
         │
┌─────────────────┐
│  Infrastructure │ ← Persistence & External
│  (Repositories) │
└─────────────────┘
```

### Data Flow Architecture
```
User Input → CLI → Service → Domain Model → Repository → Storage
    ↑                                                        │
    └── Rich Display ← Service ← Domain Model ← Repository ←─┘
```

### Repository Strategy Pattern
```
TodoService
     │
     ▼
TodoRepository (Interface)
     │
     ├── JSONTodoRepository
     └── XMLTodoRepository
```

## Configuration Management

### Environment Configuration
```python
# config/settings.py
from pydantic import BaseModel
from enum import Enum
from pathlib import Path
import json

class StorageType(str, Enum):
    JSON = "json"
    XML = "xml"

class Settings(BaseModel):
    storage_type: StorageType = StorageType.JSON
    data_file_path: str = "todos"
    log_level: str = "INFO"

    @classmethod
    def load_from_config_file(cls, config_path: str = "config.json"):
        """Load settings from configuration file"""
        config_file = Path(config_path)
        if config_file.exists():
            config_data = json.loads(config_file.read_text())
            return cls(**config_data)
        return cls()
```

### Configuration File Format
```json
# config.json
{
    "storage_type": "json",
    "data_file_path": "todos",
    "log_level": "INFO"
}
```

The application will read the storage format from this configuration file at startup, allowing users to switch between JSON and XML persistence without modifying code or using console options.

### Dependency Injection
```python
# main.py
from config.settings import Settings, StorageType
from infrastructure.json_repository import JSONTodoRepository
from infrastructure.xml_repository import XMLTodoRepository
from application.todo_service import TodoService
from interface.cli import TodoCLI

def create_repository(settings: Settings):
    """Factory function to create repository based on configuration"""
    if settings.storage_type == StorageType.JSON:
        return JSONTodoRepository(f"{settings.data_file_path}.json")
    else:
        return XMLTodoRepository(f"{settings.data_file_path}.xml")

def main():
    # Load settings from configuration file
    settings = Settings.load_from_config_file("config.json")

    # Create repository based on configured storage type
    repository = create_repository(settings)

    # Wire up dependencies
    service = TodoService(repository)
    cli = TodoCLI(service)

    # Start application
    cli.run()

if __name__ == "__main__":
    main()
```

## Performance Considerations

### File I/O Optimization
- Load data only when needed
- Batch operations for multiple updates
- Use file locking for concurrent access prevention
- Implement caching for frequently accessed data

### Memory Management
- Stream large datasets instead of loading everything
- Use generators for large collections
- Implement pagination for display

### Scalability Notes
- Current design supports file-based storage
- Repository pattern allows easy migration to database
- Service layer can be extended for caching
- CLI can be replaced with web interface without changing core logic

## Security Considerations

### Input Validation
- All user input validated through Pydantic models
- SQL injection not applicable (file-based storage)
- Path traversal protection in file operations

### Data Protection
- No sensitive data stored (todos are not confidential)
- File permissions set appropriately
- No network communication (local application)

### Error Information Disclosure
- Generic error messages to users
- Detailed logging for developers
- No stack traces exposed to end users
