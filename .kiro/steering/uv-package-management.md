# UV Package Management

## Project Setup
This project uses `uv` as the Python package manager instead of pip or poetry.

## Required Commands

### Running Python Commands
- Always use `uv run` prefix for Python commands
- Example: `uv run python -m pytest` instead of `python -m pytest`
- Example: `uv run python src/main.py` instead of `python src/main.py`

### Adding Dependencies
- Use `uv add` to add new dependencies
- Example: `uv add pytest` instead of `pip install pytest`
- Example: `uv add --dev black` for development dependencies

### Running Tests
- Use `uv run pytest` or `uv run python -m pytest`
- Example: `uv run pytest tests/`
- Example: `uv run pytest tests/domain/test_models.py -v`

### Running Linting and Formatting
- Use `uv run` for all development tools
- Example: `uv run ruff check src/`
- Example: `uv run mypy src/`

### Installing Dependencies
- Use `uv sync` to install dependencies from pyproject.toml
- Use `uv lock` to update the lock file

## Important Notes
- Never use `python`, `pip`, or `poetry` commands directly
- Always prefix with `uv run` for execution
- Always use `uv add` for adding new packages
- The project uses pyproject.toml for dependency management with uv
