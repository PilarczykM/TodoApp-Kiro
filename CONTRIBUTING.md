# Contributing to TodoApp-Kiro

Thank you for your interest in contributing to TodoApp-Kiro! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** package manager
- **Git** for version control

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/TodoApp-Kiro.git
   cd TodoApp-Kiro
   ```

2. **Install dependencies:**
   ```bash
   make install
   ```

3. **Verify setup by running tests:**
   ```bash
   make test
   ```

## 🏗️ Development Workflow

### Branch Strategy

Follow GitHub conventional branch naming with prefixes:

- `feat/` for new features (e.g., `feat/project-setup`, `feat/domain-layer`)
- `docs/` for documentation updates (e.g., `docs/readme-update`, `docs/api-documentation`)
- `test/` for test-related changes (e.g., `test/coverage-improvement`, `test/integration-tests`)
- `fix/` for bug fixes (e.g., `fix/validation-error`, `fix/persistence-issue`)
- `refactor/` for code refactoring (e.g., `refactor/repository-pattern`)
- `chore/` for maintenance tasks (e.g., `chore/dependency-update`, `chore/ci-setup`)

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes following the coding standards**

3. **Run quality checks:**
   ```bash
   make check     # Lint + type check
   make test      # Run all tests
   make coverage  # Verify 95%+ coverage
   ```

4. **Commit with conventional commit messages:**
   ```bash
   git commit -m "feat: add amazing feature"
   ```

5. **Push and create a Pull Request:**
   ```bash
   git push origin feat/your-feature-name
   ```

## 🛠️ Development Commands

The project uses a `Makefile` for development automation:

### Essential Commands

```bash
make install      # Install dependencies with uv
make test         # Run all tests
make coverage     # Run tests with 95% coverage requirement
make lint         # Ruff linting
make format       # Ruff code formatting
make type-check   # MyPy type checking (excludes tests/)
make check        # Run lint + type-check
make pre-commit   # Full pre-commit pipeline
make ci           # Complete CI: install + lint + type-check + test + coverage
make clean        # Clean build artifacts
make help         # Show all available commands
```

### Running Specific Tests

```bash
# Run specific test categories
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m property_based # Property-based tests

# Run single test file
uv run pytest tests/domain/test_models.py

# Run single test method
uv run pytest tests/domain/test_models.py::TestTodoItem::test_create_valid_todo

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage report
uv run pytest --cov=src --cov-report=html
```

## 🏛️ Architecture Guidelines

### Domain-Driven Design Structure

The project follows **Domain-Driven Design (DDD)** with clean architecture:

```
src/
├── domain/           # Core business logic (TodoItem, exceptions)
├── application/      # Use cases (TodoService, factories)
├── infrastructure/   # External concerns (JSON/XML repositories)
├── interface/        # User interfaces (CLI with Rich)
└── config/          # Configuration and dependency injection
```

### Key Patterns

- **Repository Pattern**: Abstract `TodoRepository` with JSON/XML implementations
- **Factory Pattern**: `TodoItemFactory` and repository factory for DI
- **Service Layer**: `TodoService` orchestrates domain operations
- **Immutable Timestamps**: `created_at` preserved, `updated_at` auto-managed

### Adding New Features

1. **Start with the domain layer** - Add business logic and entities
2. **Create application services** - Implement use cases
3. **Add infrastructure** - Implement external integrations
4. **Build interface layer** - Add CLI commands or API endpoints
5. **Write comprehensive tests** - Unit, integration, and property-based tests

## 📏 Code Standards

### Python Code Style

- **Line Length**: 120 characters (enforced by Ruff)
- **Python Version**: 3.12+ (strictly enforced)
- **Type Hints**: Required for all functions and methods
- **Docstrings**: Use Google-style docstrings for public APIs

### Ruff Configuration

The project uses Ruff for linting and formatting with these rules:

- **Enabled**: pycodestyle, pyflakes, isort, flake8-bugbear, pyupgrade, pep8-naming
- **Line Length**: 120 characters
- **Import Sorting**: isort with known first-party = ["src"]

### MyPy Configuration

- **Strict type checking** enabled
- **Tests directory excluded** by design
- **No untyped definitions** allowed in src/

### Test Organization

- **Move all possible mocks and fixtures** into `conftest.py` files
- **Test markers**: Use `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.property_based`
- **Coverage requirement**: 95% minimum (enforced)
- **Test structure**: Follow `tests/` directory structure matching `src/`

## 🧪 Testing Guidelines

### Test-Driven Development

Follow TDD principles:

1. **Write failing tests first**
2. **Implement minimal code to make tests pass**
3. **Refactor while keeping tests green**

### Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Property-Based Tests**: Use Hypothesis for edge case discovery
- **End-to-End Tests**: Test complete user workflows

### Coverage Requirements

- **Minimum 95% coverage** (enforced by CI)
- **Exclude patterns**: See `pyproject.toml` coverage configuration
- **Test all edge cases** and error conditions

### Example Test Structure

```python
import pytest
from src.domain.models import TodoItem

class TestTodoItem:
    """Test TodoItem domain model."""

    def test_create_valid_todo(self) -> None:
        """Test creating a valid todo item."""
        todo = TodoItem(
            title="Test todo",
            description="Test description"
        )
        assert todo.title == "Test todo"
        assert not todo.is_completed

    def test_title_validation_fails_for_empty_string(self) -> None:
        """Test that empty title raises validation error."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            TodoItem(title="", description="Test")
```

## 🔍 Code Review Process

### Pull Request Guidelines

1. **Descriptive title** following conventional commit format
2. **Detailed description** explaining changes and reasoning
3. **Link to related issues** if applicable
4. **Screenshots** for UI changes
5. **Test coverage** maintained at 95%+

### Review Checklist

- [ ] Code follows project architecture patterns
- [ ] All tests pass (`make test`)
- [ ] Code quality checks pass (`make check`)
- [ ] Coverage requirement met (`make coverage`)
- [ ] Documentation updated if needed
- [ ] No breaking changes or migrations needed

### Commit Message Format

Use conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or modifications
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

**Examples:**
```
feat(domain): add TodoItem validation for due dates
fix(repository): handle file not found errors in JSON storage
docs(readme): update installation instructions
test(integration): add end-to-end workflow tests
```

## 🚫 What NOT to Do

### Avoid These Patterns

- **Don't** commit without running tests
- **Don't** push directly to `main` branch
- **Don't** ignore type checking errors
- **Don't** add dependencies without discussion
- **Don't** lower test coverage below 95%
- **Don't** commit secrets or sensitive data
- **Don't** create large, monolithic commits

### Code Quality No-Nos

- **No print statements** in production code (use logging)
- **No hardcoded paths** or configuration
- **No TODO comments** in production code
- **No unused imports** or variables
- **No mutable defaults** in function arguments

## 🐛 Bug Reports

### Before Reporting

1. **Search existing issues** for duplicates
2. **Update to latest version** and test again
3. **Run tests** to ensure environment is working

### Bug Report Template

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- Python version:
- uv version:
- OS:

**Additional Context**
Any other relevant information
```

## 💡 Feature Requests

### Before Requesting

1. **Check existing issues** for similar requests
2. **Consider if it fits** the project's scope
3. **Think about implementation** approach

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this work?

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Any other relevant information
```

## 📚 Resources

### Project Documentation

- [README.md](README.md) - Project overview and usage
- [CLAUDE.md](CLAUDE.md) - AI assistant instructions
- [docs/](docs/) - Additional project documentation

### External Resources

- [Domain-Driven Design](https://martinfowler.com/tags/domain%20driven%20design.html)
- [Test-Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Rich Documentation](https://rich.readthedocs.io/)

### Development Tools

- [uv Documentation](https://docs.astral.sh/uv/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)

---

**Questions?** Feel free to ask in issues or discussions. We're here to help! 🚀
