"""
Domain exceptions for the Todo application.

This module defines custom exceptions that represent domain-specific
error conditions following Domain-Driven Design principles.
"""


class TodoDomainError(Exception):
    """
    Base exception for all domain-related errors.
    
    This serves as the root exception for all domain-specific errors,
    allowing for consistent error handling across the domain layer.
    """
    
    def __init__(self, message: str = "") -> None:
        """
        Initialize the domain error with an optional message.
        
        Args:
            message: Error message describing the domain error
        """
        super().__init__(message)


class TodoNotFoundError(TodoDomainError):
    """
    Exception raised when a requested todo item cannot be found.
    
    This exception is raised when attempting to access, update, or delete
    a todo item that doesn't exist in the system.
    """
    
    def __init__(self, message: str = "") -> None:
        """
        Initialize the todo not found error.
        
        Args:
            message: Error message describing which todo was not found
        """
        super().__init__(message)


class ValidationError(TodoDomainError):
    """
    Exception raised when domain validation rules are violated.
    
    This exception is raised when data doesn't meet the business rules
    and validation constraints defined in the domain layer.
    """
    
    def __init__(self, message: str = "") -> None:
        """
        Initialize the validation error.
        
        Args:
            message: Error message describing the validation failure
        """
        super().__init__(message)