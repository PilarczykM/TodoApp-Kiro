# TodoApp-Kiro

[![CI](https://github.com/PilarczykM/TodoApp-Kiro/actions/workflows/ci.yml/badge.svg)](https://github.com/PilarczykM/TodoApp-Kiro/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-95%25+-green.svg)](htmlcov/index.html)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A modern, console-based Todo application built with **Domain-Driven Design (DDD)** principles and **Test-Driven Development (TDD)**. Features a rich CLI interface, configurable storage backends (JSON/XML), and comprehensive test coverage.

## ✨ Features

- **Rich Console Interface**: Beautiful, color-coded CLI using Rich library
- **Flexible Storage**: Support for both JSON and XML storage backends
- **Domain-Driven Design**: Clean architecture with clear separation of concerns
- **Comprehensive Testing**: 95%+ test coverage with unit, integration, and property-based tests
- **Type Safety**: Full type checking with MyPy
- **Modern Python**: Built for Python 3.12+ with uv package management

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/PilarczykM/TodoApp-Kiro.git
cd TodoApp-Kiro

# Install dependencies using uv
make install

# Run the application
uv run todo
```

### Basic Usage

The application provides an interactive menu-driven interface:

```
┌─ Todo Application ─┐
│ 1. Add Todo        │
│ 2. List Todos      │
│ 3. Update Todo     │
│ 4. Complete Todo   │
│ 5. Delete Todo     │
│ 6. Exit            │
└────────────────────┘
```

## 📋 Core Operations

### Adding a Todo

```bash
# Interactive prompts will guide you
Enter title: Complete project documentation
Enter description: Write comprehensive README and setup docs
Enter due date (YYYY-MM-DD) or press Enter to skip: 2024-12-31
```

### Listing Todos

The application displays todos in a formatted table with:
- ✅ **Completed** todos in green
- ⏳ **Pending** todos in yellow
- 🔴 **Overdue** todos in red

### Managing Todos

- **Update**: Modify any field of an existing todo
- **Complete**: Mark todos as finished
- **Delete**: Remove todos with confirmation

## ⚙️ Configuration

### Storage Configuration

Configure storage backend via `config.json`:

```json
{
    "storage_type": "json",
    "storage_file": "todos.json"
}
```

**Supported storage types:**
- `"json"`: JSON file storage (default)
- `"xml"`: XML file storage with lxml

### Custom Configuration

Create a custom config file and reference it in your environment:

```bash
# Create custom config
cp config.json my_config.json

# Edit storage settings
{
    "storage_type": "xml",
    "storage_file": "my_todos.xml"
}
```

## 🏗️ Architecture

### Domain-Driven Design Structure

```
src/
├── domain/           # Core business logic
│   ├── models.py     # TodoItem entity
│   └── exceptions.py # Domain exceptions
├── application/      # Use cases and orchestration
│   ├── services/     # TodoService with business operations
│   └── factories/    # TodoItem factory with validation
├── infrastructure/   # External concerns
│   └── persistence/  # Repository implementations (JSON/XML)
├── interface/        # User interfaces
│   └── cli/          # Rich-based console interface
└── config/           # Configuration and dependency injection
```

### Key Design Patterns

- **Repository Pattern**: Abstract storage with pluggable backends
- **Factory Pattern**: Centralized TodoItem creation with validation
- **Service Layer**: Business logic orchestration
- **Dependency Injection**: Configurable component wiring

## 🧪 Development

### Prerequisites

- **Python 3.12+**
- **uv** package manager

### Development Setup

```bash
# Install dependencies
make install

# Run linting and formatting
make lint
make format

# Type checking
make type-check

# Run tests
make test

# Coverage report
make coverage

# Complete quality checks
make check
```

### Testing

The project maintains **95%+ test coverage** with comprehensive test suites:

```bash
# Run all tests
make test

# Run specific test categories
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m property_based # Property-based tests

# Run single test
uv run pytest tests/domain/test_models.py::TestTodoItem::test_create_valid_todo
```

### Development Commands

The `Makefile` provides convenient development commands:

```bash
make install      # Install dependencies with uv
make test         # Run all tests
make coverage     # Run tests with coverage report
make lint         # Ruff linting
make format       # Ruff code formatting
make type-check   # MyPy type checking
make check        # Run lint + type-check
make pre-commit   # Full pre-commit pipeline
make ci           # Complete CI: install + lint + type-check + test + coverage
make clean        # Clean build artifacts
make help         # Show all available commands
```

## 📝 Examples

### Data Models

```python
from datetime import date
from src.domain.models import TodoItem

# Create a todo item
todo = TodoItem(
    title="Complete project",
    description="Finish the todo application",
    due_date=date(2024, 12, 31)
)

# Business logic methods
todo.is_overdue()    # Check if past due date
todo.complete()      # Mark as completed
```

### Service Layer Usage

```python
from src.application.services.todo_service import TodoService
from src.config.repository_factory import create_repository

# Initialize service with repository
repository = create_repository()
service = TodoService(repository)

# Perform operations
todo_id = service.create_todo("New task", "Task description")
todos = service.get_all_todos()
service.complete_todo(todo_id)
```

## 🔧 Customization

### Adding New Storage Backends

1. Implement the `TodoRepository` interface:

```python
from src.infrastructure.persistence.repository import TodoRepository

class MyCustomRepository(TodoRepository):
    def create(self, todo: TodoItem) -> str:
        # Implementation
        pass

    # ... implement other methods
```

2. Register in the factory:

```python
# In repository_factory.py
def create_repository(storage_type: str = None) -> TodoRepository:
    if storage_type == "custom":
        return MyCustomRepository()
    # ... existing logic
```

### Extending the CLI

Add new commands by extending the `TodoCLI` class:

```python
def my_custom_command(self) -> None:
    """Custom CLI command"""
    # Implementation using Rich for formatting
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feat/amazing-feature`
3. **Run** tests: `make test`
4. **Commit** changes: `git commit -m 'feat: add amazing feature'`
5. **Push** to branch: `git push origin feat/amazing-feature`
6. **Open** a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

## 📊 Project Status

- ✅ **Domain Layer**: Complete with comprehensive validation
- ✅ **Application Layer**: Full CRUD operations with service orchestration
- ✅ **Infrastructure Layer**: JSON and XML repository implementations
- ✅ **Interface Layer**: Rich CLI with interactive menus
- ✅ **Testing**: 95%+ coverage with unit, integration, and property-based tests
- ✅ **CI/CD**: GitHub Actions with automated quality checks

## 🛠️ Built With

- **[Rich](https://rich.readthedocs.io/)** - Beautiful terminal formatting
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Data validation and settings
- **[lxml](https://lxml.de/)** - XML processing
- **[pytest](https://pytest.org/)** - Testing framework
- **[Hypothesis](https://hypothesis.readthedocs.io/)** - Property-based testing
- **[Ruff](https://docs.astral.sh/ruff/)** - Fast Python linter and formatter
- **[MyPy](https://mypy.readthedocs.io/)** - Static type checking
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package manager

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built following **Domain-Driven Design** principles by Eric Evans
- **Test-Driven Development** methodology for robust code quality
- **Clean Architecture** concepts for maintainable software design
