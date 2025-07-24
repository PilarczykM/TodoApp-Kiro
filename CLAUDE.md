# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

**Development Setup:**
```bash
make install          # Install dependencies with uv
```

**Testing:**
```bash
make test            # Run all tests
make coverage        # Run tests with 95% coverage requirement
uv run pytest tests/path/to/test_file.py::TestClass::test_method  # Run single test
```

**Code Quality:**
```bash
make lint            # Ruff linting
make format          # Ruff code formatting
make type-check      # MyPy type checking (excludes tests/)
make check           # Run lint + type-check
make pre-commit      # Full pre-commit pipeline
```

**CI Pipeline:**
```bash
make ci              # Complete CI: install + lint + type-check + test + coverage
```

## Architecture Overview

This TodoApp follows **Domain-Driven Design (DDD)** with clean architecture:

```
src/
├── domain/           # Core business logic (TodoItem, exceptions)
├── application/      # Use cases (TodoService, factories)
├── infrastructure/   # External concerns (JSON/XML repositories)
├── interface/        # User interfaces (CLI with Rich)
└── config/          # Configuration and dependency injection
```

**Key Patterns:**
- **Repository Pattern**: Abstract `TodoRepository` with JSON/XML implementations
- **Factory Pattern**: `TodoItemFactory` and repository factory for DI
- **Service Layer**: `TodoService` orchestrates domain operations
- **Immutable Timestamps**: `created_at` preserved, `updated_at` auto-managed

## Technology Stack

- **Python**: 3.12+ (strictly enforced)
- **Package Manager**: `uv` (modern Python dependency management)
- **CLI Framework**: `rich` for beautiful console interfaces
- **Validation**: `pydantic` >= 2.0 for data models
- **Storage**: Configurable JSON/XML backends via `lxml`
- **Testing**: `pytest` with 95% coverage requirement
- **Quality Tools**: `ruff` (lint/format), `mypy` (type checking)

## Configuration Management

- **Settings**: Pydantic-based with `config.json` file loading
- **Storage Strategy**: Configurable via `create_repository()` factory
- **Repository Types**: `JSONTodoRepository`, `XMLTodoRepository`

## Development Standards

- **Coverage**: 95% minimum requirement (enforced)
- **Type Safety**: Strict MyPy configuration (tests excluded by design)
- **Code Style**: Ruff with 120 character line length
- **Testing**: Comprehensive unit/integration tests with pytest markers
- **Test Organization**: Move all possible mocks and fixtures into conftest.py files
- **Error Handling**: Custom domain exceptions with Pydantic validation

## CLI Interface (In Development)

The CLI uses Rich library for enhanced console output:
- Menu-driven navigation system
- Colored output with consistent styling
- Currently has placeholder methods being implemented

Entry point: `uv run todo` (via pyproject.toml script)

## Git Commit Guidelines

When creating git commits, follow these specific guidelines:

- **DO NOT** add co-author information or mention who created the changes
- **DO NOT** include lines like "Generated with [Claude Code]" or "Co-Authored-By: Claude"
- Keep commit messages focused on the technical changes and their purpose
- Use conventional commit format: `type(scope): description`
- Include detailed explanations of features, requirements satisfied, and testing done
