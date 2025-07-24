# Task 8: Main Application Entry Point - Comprehensive Implementation Plan

## Current State Analysis
- ✅ All supporting infrastructure completed (Tasks 1-7)
- ✅ pyproject.toml configured with entry point: `todo = "src.main:main"`
- ❌ `src/main.py` does not exist (needs creation)
- ⚠️ Config.json field mismatch: uses `data_file_path` but Settings expects `storage_file`

## Validation Results from Multiple Agents

### 1. DDD Pattern Validation
**Key Findings:**
- Current codebase maintains proper layer separation: Domain ← Application ← Interface
- Repository pattern correctly implemented with factory abstraction
- Service layer properly orchestrates domain operations
- CLI layer coordinates through application services only

**Recommendations for main.py:**
- Serve as Composition Root for dependency injection
- Follow existing Settings.from_file() pattern for configuration
- Use create_repository() factory for storage strategy
- Wire dependencies: CLI → Service → Repository
- Maintain clean architecture boundaries

### 2. PyTest Pattern Validation
**Current Test Structure:**
- Class-based organization with descriptive test names
- Centralized fixtures in conftest.py files
- Mock specifications for type safety
- 95% coverage requirement with proper exclusions
- Systematic error testing with pytest.raises

**Recommended Test Classes for tests/test_main.py:**
- TestMainFunctionInitialization
- TestSettingsLoading
- TestDependencyInjection
- TestApplicationLifecycle
- TestErrorHandling
- TestConfigurationIntegration
- TestMainIntegration

### 3. Error Handling Validation
**Established Patterns:**
- Domain exceptions bubble up through layers
- Rich console formatting for user-friendly messages
- Service-level error handling with graceful recovery
- CLI error display methods with color coding

**Required Error Scenarios:**
- Configuration loading failures
- Repository creation errors
- Service initialization issues
- System-level errors (permissions, disk space)
- Graceful KeyboardInterrupt handling

## Implementation Plan

### Phase 1: Fix Configuration Compatibility
1. **Update config.json** to use correct field name `storage_file` instead of `data_file_path`
2. **Remove unused fields** (`log_level`) to match Settings model expectations

### Phase 2: Subtask 8.1 - Main Function with Dependency Wiring

#### 2.1 Create Failing Tests (TDD Approach)
Create `tests/test_main.py` with comprehensive test coverage:

```python
# Key test classes structure:
class TestMainFunctionInitialization:
    # Test basic main function exists and initializes correctly

class TestSettingsLoading:
    # Test config.json loading with various scenarios
    # Test fallback to defaults when config missing
    # Test validation error handling

class TestDependencyInjection:
    # Test repository factory integration
    # Test TodoService creation with repository
    # Test TodoCLI creation with service

class TestApplicationLifecycle:
    # Test complete startup sequence
    # Test CLI.run() invocation
    # Test normal shutdown

class TestErrorHandling:
    # Test configuration errors
    # Test repository creation failures
    # Test service initialization errors
    # Test KeyboardInterrupt handling
```

#### 2.2 Implement `src/main.py`
Following DDD and established patterns:

```python
def main() -> None:
    """
    Main application entry point with dependency injection.

    Loads configuration, creates repository via factory pattern,
    initializes service and CLI components, then starts the application.
    """
    # 1. Initialize Rich console for error display
    # 2. Load settings from config.json with fallback
    # 3. Create repository using factory pattern
    # 4. Initialize TodoService with repository dependency
    # 5. Create TodoCLI with service dependency
    # 6. Start CLI application loop
    # 7. Handle errors at composition root level
```

### Phase 3: Subtask 8.2 - Error Handling & Graceful Shutdown

#### 3.1 Add Comprehensive Error Handling Tests
- Missing/invalid config.json scenarios
- Repository creation failures for both JSON/XML
- Service initialization edge cases
- KeyboardInterrupt and SIGTERM handling
- Application recovery scenarios
- Exit code validation

#### 3.2 Implement Robust Error Handling
Following established Rich formatting patterns:

```python
# Error handling strategy:
try:
    # Application initialization
except FileNotFoundError:
    # Config file missing - use defaults
except json.JSONDecodeError:
    # Invalid config format
except ValidationError:
    # Config validation failure
except ValueError:
    # Repository creation failure
except KeyboardInterrupt:
    # Graceful shutdown
except Exception:
    # Unexpected errors with user-friendly messages
```

**Exit Codes:**
- 0: Normal exit
- 1: Configuration/initialization errors
- 2: Repository creation errors
- 3: Critical system errors

### Phase 4: Integration Testing & Validation

#### 4.1 Test Coverage Validation
- Run `make test` to ensure all tests pass
- Run `make coverage` to maintain 95% coverage requirement
- Verify both JSON and XML storage backends work
- Test edge cases and error scenarios

#### 4.2 End-to-End Testing
- Test `uv run todo` command functionality
- Verify complete application workflow
- Test configuration switching between storage types
- Validate user experience for error scenarios

## Key Design Decisions

### 1. Configuration Management
- Use existing Settings.from_file() pattern
- Provide fallback to default settings for missing config
- Handle validation errors gracefully
- Support both JSON and XML storage switching

### 2. Dependency Injection
- Follow established factory pattern for repository creation
- Maintain clean layer boundaries per DDD principles
- Use composition root pattern in main()
- Ensure testable dependency wiring

### 3. Error Handling Philosophy
- Fail fast for critical errors (invalid config format)
- Graceful degradation where possible (missing config → defaults)
- User-friendly error messages with actionable guidance
- Proper exit codes for automation/scripting

### 4. Testing Strategy
- TDD approach with failing tests first
- Comprehensive mock usage following existing patterns
- Integration tests for end-to-end workflows
- Error scenario coverage for robustness

## Expected Deliverables

1. **`src/main.py`** - Complete main application entry point with:
   - Proper dependency injection following DDD patterns
   - Robust error handling with user-friendly messages
   - Configuration loading with fallback support
   - Graceful shutdown handling

2. **`tests/test_main.py`** - Comprehensive test suite with:
   - TDD-driven test implementation
   - Mock usage following established patterns
   - Complete error scenario coverage
   - Integration test coverage

3. **Updated `config.json`** - Fixed configuration file with:
   - Correct field names matching Settings model
   - Removal of unused fields
   - Proper JSON structure

4. **Maintained Standards** - Ensuring:
   - 95% test coverage requirement met
   - Clean architecture principles preserved
   - Consistent code style and patterns
   - Full integration with existing codebase

This implementation plan ensures Task 8 follows all established coding patterns, DDD principles, and pytest standards while maintaining the high-quality standards of the existing codebase.
