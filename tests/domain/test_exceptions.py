"""
Test module for domain exceptions.

Following TDD principles, these tests define the expected behavior
of domain exceptions before implementation.
"""
import pytest
from src.domain.exceptions import TodoDomainError, TodoNotFoundError, ValidationError


class TestTodoDomainError:
    """Test suite for base TodoDomainError exception"""
    
    def test_should_be_instance_of_exception(self):
        """TodoDomainError should inherit from Exception"""
        error = TodoDomainError("Test error")
        assert isinstance(error, Exception)
    
    def test_should_store_error_message(self):
        """TodoDomainError should store and return error message"""
        message = "Test domain error message"
        error = TodoDomainError(message)
        assert str(error) == message
    
    def test_should_allow_empty_message(self):
        """TodoDomainError should allow creation with empty message"""
        error = TodoDomainError()
        assert str(error) == ""


class TestTodoNotFoundError:
    """Test suite for TodoNotFoundError exception"""
    
    def test_should_inherit_from_todo_domain_error(self):
        """TodoNotFoundError should inherit from TodoDomainError"""
        error = TodoNotFoundError("Todo not found")
        assert isinstance(error, TodoDomainError)
        assert isinstance(error, Exception)
    
    def test_should_store_error_message(self):
        """TodoNotFoundError should store and return error message"""
        message = "Todo with ID 123 not found"
        error = TodoNotFoundError(message)
        assert str(error) == message
    
    def test_should_allow_empty_message(self):
        """TodoNotFoundError should allow creation with empty message"""
        error = TodoNotFoundError()
        assert str(error) == ""


class TestValidationError:
    """Test suite for ValidationError exception"""
    
    def test_should_inherit_from_todo_domain_error(self):
        """ValidationError should inherit from TodoDomainError"""
        error = ValidationError("Validation failed")
        assert isinstance(error, TodoDomainError)
        assert isinstance(error, Exception)
    
    def test_should_store_error_message(self):
        """ValidationError should store and return error message"""
        message = "Title cannot be empty"
        error = ValidationError(message)
        assert str(error) == message
    
    def test_should_allow_empty_message(self):
        """ValidationError should allow creation with empty message"""
        error = ValidationError()
        assert str(error) == ""
    
    def test_should_support_multiple_validation_errors(self):
        """ValidationError should support multiple error messages"""
        errors = ["Title cannot be empty", "Due date cannot be in the past"]
        message = "; ".join(errors)
        error = ValidationError(message)
        assert str(error) == message