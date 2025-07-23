"""
Test module for domain models.

Following TDD principles, these tests define the expected behavior
of domain models before implementation.
"""
import pytest
from datetime import datetime, timedelta
from uuid import UUID
from pydantic import ValidationError as PydanticValidationError

from src.domain.models import TodoItem
from src.domain.exceptions import ValidationError


class TestTodoItemCreation:
    """Test suite for TodoItem creation and initialization"""
    
    def test_should_create_todo_with_required_fields(self):
        """TodoItem should be created with only title provided"""
        title = "Buy groceries"
        todo = TodoItem(title=title)
        
        assert todo.title == title
        assert todo.description is None
        assert todo.due_date is None
        assert todo.completed is False
        assert isinstance(todo.id, UUID)
        assert isinstance(todo.created_at, datetime)
        assert isinstance(todo.updated_at, datetime)
    
    def test_should_create_todo_with_all_fields(self):
        """TodoItem should be created with all fields provided"""
        title = "Buy groceries"
        description = "Milk, eggs, bread"
        due_date = datetime.now() + timedelta(days=1)
        
        todo = TodoItem(
            title=title,
            description=description,
            due_date=due_date
        )
        
        assert todo.title == title
        assert todo.description == description
        assert todo.due_date == due_date
        assert todo.completed is False
        assert isinstance(todo.id, UUID)
    
    def test_should_generate_unique_ids(self):
        """Each TodoItem should have a unique ID"""
        todo1 = TodoItem(title="Task 1")
        todo2 = TodoItem(title="Task 2")
        
        assert todo1.id != todo2.id
        assert isinstance(todo1.id, UUID)
        assert isinstance(todo2.id, UUID)
    
    def test_should_set_timestamps_on_creation(self):
        """TodoItem should set created_at and updated_at on creation"""
        before_creation = datetime.now()
        todo = TodoItem(title="Test task")
        after_creation = datetime.now()
        
        assert before_creation <= todo.created_at <= after_creation
        assert before_creation <= todo.updated_at <= after_creation
        assert todo.created_at == todo.updated_at


class TestTodoItemValidation:
    """Test suite for TodoItem validation rules"""
    
    def test_should_reject_empty_title(self):
        """TodoItem should reject empty title"""
        with pytest.raises(PydanticValidationError) as exc_info:
            TodoItem(title="")
        
        errors = exc_info.value.errors()
        assert any("at least 1 character" in str(error) for error in errors)
    
    def test_should_reject_whitespace_only_title(self):
        """TodoItem should reject title with only whitespace"""
        with pytest.raises(PydanticValidationError) as exc_info:
            TodoItem(title="   ")
        
        errors = exc_info.value.errors()
        assert any("empty or whitespace" in str(error) for error in errors)
    
    def test_should_reject_title_too_long(self):
        """TodoItem should reject title longer than 200 characters"""
        long_title = "a" * 201
        
        with pytest.raises(PydanticValidationError) as exc_info:
            TodoItem(title=long_title)
        
        errors = exc_info.value.errors()
        assert any("at most 200 characters" in str(error) for error in errors)
    
    def test_should_accept_title_at_max_length(self):
        """TodoItem should accept title exactly at max length"""
        max_title = "a" * 200
        todo = TodoItem(title=max_title)
        
        assert todo.title == max_title
    
    def test_should_reject_description_too_long(self):
        """TodoItem should reject description longer than 1000 characters"""
        long_description = "a" * 1001
        
        with pytest.raises(PydanticValidationError) as exc_info:
            TodoItem(title="Valid title", description=long_description)
        
        errors = exc_info.value.errors()
        assert any("at most 1000 characters" in str(error) for error in errors)
    
    def test_should_accept_description_at_max_length(self):
        """TodoItem should accept description exactly at max length"""
        max_description = "a" * 1000
        todo = TodoItem(title="Valid title", description=max_description)
        
        assert todo.description == max_description
    
    def test_should_reject_past_due_date(self):
        """TodoItem should reject due date in the past"""
        past_date = datetime.now() - timedelta(days=1)
        
        with pytest.raises(PydanticValidationError) as exc_info:
            TodoItem(title="Valid title", due_date=past_date)
        
        errors = exc_info.value.errors()
        assert any("cannot be in the past" in str(error) for error in errors)
    
    def test_should_accept_future_due_date(self):
        """TodoItem should accept due date in the future"""
        future_date = datetime.now() + timedelta(days=1)
        todo = TodoItem(title="Valid title", due_date=future_date)
        
        assert todo.due_date == future_date
    
    def test_should_accept_current_time_as_due_date(self):
        """TodoItem should accept current time as due date"""
        # Add a small buffer to account for execution time
        current_time = datetime.now() + timedelta(milliseconds=10)
        todo = TodoItem(title="Valid title", due_date=current_time)
        
        assert todo.due_date == current_time


class TestTodoItemBusinessMethods:
    """Test suite for TodoItem business logic methods"""
    
    def test_should_mark_todo_as_completed(self):
        """mark_completed should set completed to True and update timestamp"""
        todo = TodoItem(title="Test task")
        original_updated_at = todo.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.001)
        
        todo.mark_completed()
        
        assert todo.completed is True
        assert todo.updated_at > original_updated_at
    
    def test_should_not_fail_when_marking_completed_todo_as_completed(self):
        """mark_completed should not fail when called on already completed todo"""
        todo = TodoItem(title="Test task")
        todo.mark_completed()
        
        # Should not raise exception
        todo.mark_completed()
        assert todo.completed is True
    
    def test_should_update_title_only(self):
        """update_details should update only title when provided"""
        todo = TodoItem(title="Original title", description="Original description")
        original_description = todo.description
        original_updated_at = todo.updated_at
        
        import time
        time.sleep(0.001)
        
        new_title = "Updated title"
        todo.update_details(title=new_title)
        
        assert todo.title == new_title
        assert todo.description == original_description
        assert todo.updated_at > original_updated_at
    
    def test_should_update_description_only(self):
        """update_details should update only description when provided"""
        todo = TodoItem(title="Original title", description="Original description")
        original_title = todo.title
        original_updated_at = todo.updated_at
        
        import time
        time.sleep(0.001)
        
        new_description = "Updated description"
        todo.update_details(description=new_description)
        
        assert todo.title == original_title
        assert todo.description == new_description
        assert todo.updated_at > original_updated_at
    
    def test_should_update_due_date_only(self):
        """update_details should update only due_date when provided"""
        original_due_date = datetime.now() + timedelta(days=1)
        todo = TodoItem(title="Test title", due_date=original_due_date)
        original_title = todo.title
        original_updated_at = todo.updated_at
        
        import time
        time.sleep(0.001)
        
        new_due_date = datetime.now() + timedelta(days=2)
        todo.update_details(due_date=new_due_date)
        
        assert todo.title == original_title
        assert todo.due_date == new_due_date
        assert todo.updated_at > original_updated_at
    
    def test_should_update_all_fields(self):
        """update_details should update all fields when provided"""
        todo = TodoItem(title="Original title")
        original_updated_at = todo.updated_at
        
        import time
        time.sleep(0.001)
        
        new_title = "Updated title"
        new_description = "Updated description"
        new_due_date = datetime.now() + timedelta(days=1)
        
        todo.update_details(
            title=new_title,
            description=new_description,
            due_date=new_due_date
        )
        
        assert todo.title == new_title
        assert todo.description == new_description
        assert todo.due_date == new_due_date
        assert todo.updated_at > original_updated_at
    
    def test_should_not_update_when_no_parameters_provided(self):
        """update_details should not change anything when no parameters provided"""
        todo = TodoItem(title="Original title", description="Original description")
        original_title = todo.title
        original_description = todo.description
        original_due_date = todo.due_date
        original_updated_at = todo.updated_at
        
        todo.update_details()
        
        assert todo.title == original_title
        assert todo.description == original_description
        assert todo.due_date == original_due_date
        # updated_at should still be updated even with no changes
        assert todo.updated_at >= original_updated_at
    
    def test_should_validate_updated_title(self):
        """update_details should validate title when updating"""
        todo = TodoItem(title="Original title")
        
        with pytest.raises(PydanticValidationError):
            todo.update_details(title="")
    
    def test_should_validate_updated_description(self):
        """update_details should validate description when updating"""
        todo = TodoItem(title="Original title")
        long_description = "a" * 1001
        
        with pytest.raises(PydanticValidationError):
            todo.update_details(description=long_description)
    
    def test_should_validate_updated_due_date(self):
        """update_details should validate due_date when updating"""
        todo = TodoItem(title="Original title")
        past_date = datetime.now() - timedelta(days=1)
        
        with pytest.raises(PydanticValidationError):
            todo.update_details(due_date=past_date)


class TestTodoItemEdgeCases:
    """Test suite for TodoItem edge cases and boundary conditions"""
    
    def test_should_handle_unicode_characters_in_title(self):
        """TodoItem should handle unicode characters in title"""
        unicode_title = "📝 Buy groceries 🛒"
        todo = TodoItem(title=unicode_title)
        
        assert todo.title == unicode_title
    
    def test_should_handle_unicode_characters_in_description(self):
        """TodoItem should handle unicode characters in description"""
        unicode_description = "🥛 Milk, 🥚 eggs, 🍞 bread"
        todo = TodoItem(title="Buy groceries", description=unicode_description)
        
        assert todo.description == unicode_description
    
    def test_should_handle_newlines_in_description(self):
        """TodoItem should handle newlines in description"""
        multiline_description = "Line 1\nLine 2\nLine 3"
        todo = TodoItem(title="Test task", description=multiline_description)
        
        assert todo.description == multiline_description
    
    def test_should_preserve_completion_status_during_updates(self):
        """Completion status should be preserved during field updates"""
        todo = TodoItem(title="Test task")
        todo.mark_completed()
        
        todo.update_details(title="Updated title")
        
        assert todo.completed is True
    
    def test_should_handle_none_values_in_update(self):
        """update_details should handle None values correctly"""
        todo = TodoItem(title="Test task", description="Test description")
        
        # Explicitly setting to None should clear the field
        todo.update_details(description=None)
        
        assert todo.description is None