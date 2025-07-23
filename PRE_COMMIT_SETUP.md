# Pre-commit Setup

This project uses pre-commit hooks to ensure code quality and consistency. The hooks run automatically before each commit and include all the checks from `make pre-commit`.

## What's Included

The pre-commit configuration runs the following checks:

### Code Quality
- **Ruff Lint**: Linting with automatic fixes
- **Ruff Format**: Code formatting
- **MyPy**: Static type checking (src/ only)
- **Pytest**: Full test suite with 100% coverage requirement

### File Quality
- Trailing whitespace removal
- End-of-file newline fixes
- YAML, TOML, and JSON syntax validation
- Merge conflict detection
- Large file detection (>1MB)
- Python AST validation
- Debug statement detection
- Test naming validation

## Installation

Pre-commit is already installed as a dev dependency. To set up the hooks:

```bash
# Install the git hooks
uv run pre-commit install

# Run hooks on all files (optional)
uv run pre-commit run --all-files
```

## Usage

Once installed, the hooks run automatically on `git commit`. If any hook fails:

1. Fix the issues (many are auto-fixed)
2. Stage the changes: `git add .`
3. Commit again: `git commit`

## Manual Execution

You can run the hooks manually:

```bash
# Run on all files
uv run pre-commit run --all-files

# Run on staged files only
uv run pre-commit run

# Update hook versions
uv run pre-commit autoupdate
```

## Integration with Make

The existing `make pre-commit` command still works and runs the same checks. The pre-commit hooks provide automatic validation, while the make target is useful for manual testing.

## CI Integration

The configuration includes settings for pre-commit.ci, which can automatically:
- Run hooks on pull requests
- Auto-fix issues when possible
- Keep hook versions updated

This ensures consistent code quality across all contributions.
