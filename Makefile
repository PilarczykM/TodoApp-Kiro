# Todo App Development Makefile
# This Makefile provides automation for common development tasks

.PHONY: help install test lint format type-check clean coverage report all

# Default target
help: ## Display this help message
	@echo "Todo App Development Commands:"
	@echo "=============================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install project dependencies using uv
	@echo "Installing dependencies with uv..."
	uv sync
	@echo "Dependencies installed successfully!"

test: ## Run all tests with pytest
	@echo "Running tests..."
	uv run pytest tests/ -v
	@echo "Tests completed!"

test-watch: ## Run tests in watch mode for TDD
	@echo "Running tests in watch mode..."
	uv run pytest-watch tests/ -- -v

lint: ## Run linting with ruff
	@echo "Running linter..."
	uv run ruff check src/ tests/
	@echo "Linting completed!"

format: ## Format code with ruff
	@echo "Formatting code..."
	uv run ruff format src/ tests/
	@echo "Code formatting completed!"

type-check: ## Run type checking with mypy
	@echo "Running type checker..."
	uv run mypy src/
	@echo "Type checking completed!"

coverage: ## Run tests with coverage reporting
	@echo "Running tests with coverage..."
	uv run pytest tests/ --cov=src --cov-report=term-missing -v
	@echo "Coverage analysis completed!"

coverage-html: ## Generate HTML coverage report
	@echo "Generating HTML coverage report..."
	uv run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -v
	@echo "HTML coverage report generated in htmlcov/"

coverage-xml: ## Generate XML coverage report for CI
	@echo "Generating XML coverage report..."
	uv run pytest tests/ --cov=src --cov-report=xml --cov-report=term-missing -v
	@echo "XML coverage report generated as coverage.xml"

report: coverage-html ## Generate comprehensive coverage report
	@echo "Opening coverage report..."
	@if command -v open >/dev/null 2>&1; then \
		open htmlcov/index.html; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open htmlcov/index.html; \
	else \
		echo "Coverage report generated in htmlcov/index.html"; \
	fi

clean: ## Clean up generated files and caches
	@echo "Cleaning up..."
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf coverage.xml
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup completed!"

check: lint type-check ## Run all code quality checks
	@echo "All code quality checks completed!"

test-all: test coverage ## Run all tests with coverage
	@echo "All tests completed with coverage!"

ci: install lint type-check test coverage ## Run full CI pipeline locally
	@echo "Full CI pipeline completed successfully!"

dev-setup: install ## Set up development environment
	@echo "Development environment setup completed!"
	@echo "Run 'make help' to see available commands"

all: clean install lint format type-check test coverage ## Run complete development workflow
	@echo "Complete development workflow finished!"

# Development workflow targets
quick-check: lint type-check ## Quick code quality check without tests
	@echo "Quick quality checks completed!"

pre-commit: format lint type-check test ## Pre-commit checks
	@echo "Pre-commit checks completed!"

# Utility targets
show-deps: ## Show installed dependencies
	@echo "Installed dependencies:"
	uv pip list

update-deps: ## Update dependencies to latest versions
	@echo "Updating dependencies..."
	uv sync --upgrade
	@echo "Dependencies updated!"

# Project information
info: ## Show project information
	@echo "Todo App Development Environment"
	@echo "==============================="
	@echo "Python version: $$(python --version)"
	@echo "UV version: $$(uv --version)"
	@echo "Project structure:"
	@find src tests -type f -name "*.py" | head -10
	@echo "..."
