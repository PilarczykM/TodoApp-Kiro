# Test-Driven Development (TDD) Guidelines

## Core TDD Cycle

### Red-Green-Refactor
1. **Red**: Write a failing test that describes desired behavior
2. **Green**: Write minimal code to make the test pass
3. **Refactor**: Improve code quality while keeping tests green

### TDD Mantras
- "Test first, code second"
- "Write only enough code to make the test pass"
- "Refactor with confidence"
- "Let tests drive your design"

## Testing Strategy by Layer

### Domain Layer Testing
Focus on business logic and domain rules:

```python
# Test domain entity behavior
class TestTodoItem:
    def test_should_create_todo_with_pending_status(self):
        # Arrange & Act
        todo = TodoItem("Buy groceries", "Milk, eggs, bread")
        
        # Assert
        assert todo.title == "Buy groceries"
        assert todo.status == TodoStatus.PENDING
        assert todo.created_at is not None
    
    def test_should_complete_pending_todo(self):
        # Arrange
        todo = TodoItem("Task", "Description")
        
        # Act
        todo.complete()
        
        # Assert
        assert todo.status == TodoStatus.COMPLETED
        assert todo.completed_at is not None
    
    def test_should_raise_error_when_completing_already_completed_todo(self):
        # Arrange
        todo = TodoItem("Task", "Description")
        todo.complete()
        
        # Act & Assert
        with pytest.raises(DomainError, match="already completed"):
            todo.complete()
    
    def test_should_raise_error_for_empty_title(self):
        # Act & Assert
        with pytest.raises(DomainError, match="Title cannot be empty"):
            TodoItem("", "Description")
```

### Application Layer Testing
Test use case orchestration and business workflows:

```python
class TestTodoApplicationService:
    def setup_method(self):
        self.mock_repo = Mock(spec=TodoRepository)
        self.service = TodoApplicationService(self.mock_repo)
    
    def test_should_create_todo_successfully(self):
        # Arrange
        request = CreateTodoRequest("Buy milk", "From grocery store")
        
        # Act
        response = self.service.create_todo(request)
        
        # Assert
        assert response.title == "Buy milk"
        assert response.status == "PENDING"
        self.mock_repo.save.assert_called_once()
    
    def test_should_handle_domain_validation_errors(self):
        # Arrange
        request = CreateTodoRequest("", "Empty title")
        
        # Act & Assert
        with pytest.raises(ValidationError):
            self.service.create_todo(request)
        
        self.mock_repo.save.assert_not_called()
```

### Infrastructure Layer Testing
Test external integrations and persistence:

```python
class TestJsonTodoRepository:
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.repo = JsonTodoRepository(self.temp_file.name)
    
    def teardown_method(self):
        os.unlink(self.temp_file.name)
    
    def test_should_save_and_retrieve_todo(self):
        # Arrange
        todo = TodoItem("Test task", "Test description")
        
        # Act
        self.repo.save(todo)
        retrieved = self.repo.find_by_id(todo.id)
        
        # Assert
        assert retrieved is not None
        assert retrieved.title == "Test task"
        assert retrieved.status == TodoStatus.PENDING
```

## TDD Best Practices

### Test Structure
Use the AAA pattern consistently:
- **Arrange**: Set up test data and dependencies
- **Act**: Execute the behavior being tested
- **Assert**: Verify the expected outcome

### Test Naming
Use descriptive names that explain behavior:
```python
# Good: Describes behavior and expected outcome
def test_should_mark_todo_as_completed_when_complete_is_called(self):
    pass

def test_should_raise_validation_error_when_title_is_empty(self):
    pass

def test_should_return_only_active_todos_when_filtering_by_status(self):
    pass

# Avoid: Generic or unclear names
def test_complete(self):
    pass

def test_validation(self):
    pass
```

### Test Organization
```python
class TestTodoItem:
    """Test suite for TodoItem domain entity"""
    
    class TestCreation:
        """Tests for todo item creation"""
        
        def test_should_create_with_valid_data(self):
            pass
        
        def test_should_reject_empty_title(self):
            pass
    
    class TestCompletion:
        """Tests for todo completion behavior"""
        
        def test_should_complete_pending_todo(self):
            pass
        
        def test_should_reject_completing_completed_todo(self):
            pass
```

### Mock Usage Guidelines
- Mock external dependencies, not the system under test
- Use mocks for infrastructure concerns (databases, APIs, file systems)
- Avoid mocking domain objects - test them directly
- Verify mock interactions when behavior matters

```python
# Good: Mock infrastructure dependency
def test_should_save_todo_to_repository(self):
    mock_repo = Mock(spec=TodoRepository)
    service = TodoApplicationService(mock_repo)
    
    service.create_todo(CreateTodoRequest("Task", "Description"))
    
    mock_repo.save.assert_called_once()

# Avoid: Mocking domain objects
def test_should_complete_todo(self):
    mock_todo = Mock(spec=TodoItem)  # Don't do this
    mock_todo.complete()
    mock_todo.complete.assert_called_once()
```

## TDD Workflow Integration

### Branch Naming for TDD
Align with existing branching strategy:

```bash
# Test-first development
test/domain-todo-validation     # Domain layer tests
test/app-create-todo-usecase    # Application layer tests
test/infra-json-persistence     # Infrastructure tests
test/integration-todo-workflow  # Integration tests

# Bug fixes with tests
fix/todo-completion-validation  # Fix with accompanying tests
```

### Commit Strategy
Follow TDD cycle in commits:

```bash
# Red phase - failing test
git commit -m "test(domain): add failing test for todo completion validation"

# Green phase - minimal implementation
git commit -m "feat(domain): implement basic todo completion logic"

# Refactor phase - improve code quality
git commit -m "refactor(domain): extract validation logic to private method"
```

### Combined Workflow Example
```bash
# 1. Create feature branch
git checkout -b feat/domain-todo-completion

# 2. Write failing test (Red)
git add tests/domain/test_todo_item.py
git commit -m "test(domain): add failing test for todo completion"

# 3. Implement minimal code (Green)
git add src/domain/models/todo_item.py
git commit -m "feat(domain): add basic todo completion method"

# 4. Refactor and improve (Refactor)
git add src/domain/models/todo_item.py
git commit -m "refactor(domain): improve completion validation logic"

# 5. Add more test cases
git add tests/domain/test_todo_item.py
git commit -m "test(domain): add edge cases for todo completion"
```

## Testing Pyramid

### Unit Tests (70%)
- Fast execution (< 1ms per test)
- Test individual components in isolation
- Mock external dependencies
- Focus on domain logic and business rules

### Integration Tests (20%)
- Test component interactions
- Use real implementations where possible
- Test data flow between layers
- Verify use case orchestration

### End-to-End Tests (10%)
- Test complete user workflows
- Use real external systems or reliable test doubles
- Focus on critical business paths
- Keep minimal but comprehensive

## Test Quality Guidelines

### Characteristics of Good Tests
- **Fast**: Execute quickly to enable frequent running
- **Independent**: Don't depend on other tests or external state
- **Repeatable**: Produce same results in any environment
- **Self-validating**: Clear pass/fail result
- **Timely**: Written just before production code

### Test Maintenance
- Keep tests simple and focused
- Refactor tests when refactoring code
- Remove obsolete tests promptly
- Use test utilities for common setup
- Maintain test readability over DRY principles

## Common TDD Anti-Patterns

### Testing Implementation Details
```python
# Bad: Testing internal implementation
def test_should_call_validate_method(self):
    todo = TodoItem("Task", "Description")
    with patch.object(todo, '_validate_title') as mock_validate:
        todo.title = "New title"
        mock_validate.assert_called_once()

# Good: Testing behavior
def test_should_reject_empty_title_when_updating(self):
    todo = TodoItem("Task", "Description")
    with pytest.raises(DomainError):
        todo.title = ""
```

### Writing Tests After Code
- Leads to tests that confirm existing implementation
- Misses edge cases and error conditions
- Reduces design benefits of TDD

### Overly Complex Tests
- Tests that are hard to understand
- Tests with multiple assertions
- Tests that test multiple behaviors

## IDE and Tool Integration

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/domain/test_todo_item.py

# Run with coverage
pytest --cov=src tests/

# Run in watch mode for TDD
pytest-watch
```

### Test Configuration
```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--cov=src",
    "--cov-report=term-missing"
]
```

## Continuous Integration

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: Run tests
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

### CI Pipeline
```yaml
# GitHub Actions example
- name: Run tests
  run: |
    pytest --cov=src tests/
    pytest --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v1
```

Remember: TDD is not just about testing - it's a design methodology that uses tests to drive better software architecture and more maintainable code.