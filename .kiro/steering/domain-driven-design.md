# Domain-Driven Design (DDD) Guidelines

## Core Principles

### Ubiquitous Language
- Use consistent terminology across code, documentation, and conversations
- Domain terms should match business language exactly
- Avoid technical jargon in domain models
- Create a glossary of domain terms and maintain it

### Bounded Contexts
- Identify clear boundaries between different business domains
- Each bounded context should have its own models and services
- Minimize dependencies between contexts
- Use well-defined interfaces for context communication

## Project Structure

### Layered Architecture
```
src/
├── domain/           # Core business logic
│   ├── models/       # Domain entities and value objects
│   ├── services/     # Domain services
│   └── repositories/ # Repository interfaces
├── application/      # Application services and use cases
│   ├── services/     # Application services
│   └── dto/          # Data transfer objects
├── infrastructure/   # External concerns
│   ├── persistence/  # Repository implementations
│   ├── external/     # External service integrations
│   └── config/       # Configuration
└── presentation/     # UI/API layer
    ├── api/          # REST/GraphQL endpoints
    └── cli/          # Command-line interface
```

## Domain Layer Guidelines

### Entities
- Represent core business objects with identity
- Encapsulate business rules and invariants
- Keep entities focused on business logic, not persistence
- Use rich domain models, not anemic data structures

```python
# Good: Rich domain model
class TodoItem:
    def __init__(self, title: str, description: str):
        self._validate_title(title)
        self.title = title
        self.description = description
        self.status = TodoStatus.PENDING
        self.created_at = datetime.now()

    def complete(self):
        if self.status == TodoStatus.COMPLETED:
            raise DomainError("Todo is already completed")
        self.status = TodoStatus.COMPLETED
        self.completed_at = datetime.now()

    def _validate_title(self, title: str):
        if not title or len(title.strip()) == 0:
            raise DomainError("Title cannot be empty")
```

### Value Objects
- Represent descriptive aspects without identity
- Immutable by design
- Implement equality based on value, not identity
- Use for complex attributes that have business meaning

```python
# Good: Value object for email
@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError("Invalid email format")

    def _is_valid_email(self, email: str) -> bool:
        return "@" in email and "." in email.split("@")[1]
```

### Domain Services
- Contain business logic that doesn't naturally fit in entities
- Stateless operations that work with multiple entities
- Keep focused on domain concerns, not infrastructure

### Repository Interfaces
- Define in domain layer, implement in infrastructure
- Use domain language, not persistence language
- Return domain objects, not data structures

```python
# Domain layer - repository interface
class TodoRepository(ABC):
    @abstractmethod
    def save(self, todo: TodoItem) -> None:
        pass

    @abstractmethod
    def find_by_id(self, todo_id: TodoId) -> Optional[TodoItem]:
        pass

    @abstractmethod
    def find_active_todos(self) -> List[TodoItem]:
        pass
```

## Application Layer Guidelines

### Application Services
- Orchestrate domain objects to fulfill use cases
- Handle transaction boundaries
- Convert between DTOs and domain objects
- Keep thin - delegate business logic to domain layer

```python
class TodoApplicationService:
    def __init__(self, todo_repo: TodoRepository):
        self.todo_repo = todo_repo

    def create_todo(self, request: CreateTodoRequest) -> TodoResponse:
        # Convert DTO to domain object
        todo = TodoItem(request.title, request.description)

        # Use domain service if needed
        self.todo_repo.save(todo)

        # Convert domain object to DTO
        return TodoResponse.from_domain(todo)
```

### Use Cases
- Represent specific business scenarios
- One use case per application service method
- Include validation and error handling
- Return DTOs, not domain objects

## Branch Naming for DDD

Align with existing branching strategy:

### Domain Changes
- `feat/domain-todo-entity` - New domain entities
- `feat/domain-user-value-objects` - Value object additions
- `refactor/domain-service-extraction` - Domain service refactoring

### Application Layer
- `feat/app-create-todo-usecase` - New use cases
- `feat/app-todo-dto-mapping` - DTO implementations

### Infrastructure
- `feat/infra-json-repository` - Repository implementations
- `feat/infra-external-api-integration` - External service integrations

## Commit Message Examples

```bash
feat(domain): add TodoItem entity with completion logic
feat(domain): implement Email value object with validation
feat(app): add CreateTodoUseCase with validation
feat(infra): implement JsonTodoRepository
refactor(domain): extract TodoValidationService
test(domain): add unit tests for TodoItem business rules
```

## Testing Strategy

### Domain Testing
- Focus on business rule validation
- Test entity behavior and invariants
- Mock external dependencies
- Use domain language in test names

### Integration Testing
- Test application services with real repositories
- Verify use case orchestration
- Test boundary interactions

## Common Anti-Patterns to Avoid

### Anemic Domain Model
- Entities with only getters/setters
- Business logic in application services
- Data structures instead of rich objects

### Leaky Abstractions
- Domain layer depending on infrastructure
- Persistence concerns in domain objects
- Framework-specific code in domain layer

### God Objects
- Entities with too many responsibilities
- Services that do everything
- Lack of proper bounded contexts

## Best Practices

### Code Organization
- Keep domain layer pure and framework-agnostic
- Use dependency injection for infrastructure concerns
- Implement proper error handling with domain exceptions
- Maintain clear separation between layers

### Documentation
- Document domain concepts and business rules
- Maintain architectural decision records (ADRs)
- Keep domain glossary up to date
- Use examples to illustrate complex domain logic

### Refactoring
- Continuously refine domain model based on learning
- Extract domain services when entities become complex
- Split bounded contexts when they grow too large
- Maintain backward compatibility in public interfaces
