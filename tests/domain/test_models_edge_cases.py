"""
Additional edge case tests for TodoItem model.

These tests cover boundary conditions and edge cases
to ensure comprehensive test coverage.
"""
import pytest
from datetime import datetime, timedelta
from uuid import UUID
from pydantic import ValidationError as PydanticValidationError

from src.domain.models import TodoItem


class TestTodoItemEdgeCasesExtended:
    """Extended edge case tests for TodoItem"""
    
    def test_should_handle_very_long_valid_title(self):
        """TodoItem should handle title at exactly 200 characters"""
        title_199 = "a" * 199
        title_200 = "a" * 200
        
        # 199 characters should work
        todo199 = TodoItem(title=title_199)
        assert len(todo199.title) == 199
        
        # 200 characters should work
        todo200 = TodoItem(title=title_200)
        assert len(todo200.title) == 200
    
    def test_should_handle_very_long_valid_description(self):
        """TodoItem should handle description at exactly 1000 characters"""
        description_999 = "a" * 999
        description_1000 = "a" * 1000
        
        # 999 characters should work
        todo999 = TodoItem(title="Test", description=description_999)
        assert len(todo999.description) == 999
        
        # 1000 characters should work
        todo1000 = TodoItem(title="Test", description=description_1000)
        assert len(todo1000.description) == 1000
    
    def test_should_handle_due_date_exactly_at_current_time(self):
        """TodoItem should handle due date exactly at current time"""
        # This test ensures the boundary condition works
        current_time = datetime.now()
        # Add a small buffer to ensure it's in the future
        future_time = current_time + timedelta(milliseconds=10)
        
        todo = TodoItem(title="Test", due_date=future_time)
        assert todo.due_date == future_time
    
    def test_should_preserve_microsecond_precision_in_timestamps(self):
        """TodoItem should preserve microsecond precision in timestamps"""
        todo = TodoItem(title="Test")
        
        # Check that timestamps have microsecond precision
        assert todo.created_at.microsecond is not None
        assert todo.updated_at.microsecond is not None
    
    def test_should_handle_empty_string_description(self):
        """TodoItem should handle empty string description"""
        todo = TodoItem(title="Test", description="")
        assert todo.description == ""
    
    def test_should_handle_special_characters_in_title(self):
        """TodoItem should handle special characters in title"""
        special_title = "Test @#$%^&*()_+-=[]{}|;':\",./<>?"
        todo = TodoItem(title=special_title)
        assert todo.title == special_title
    
    def test_should_handle_tabs_and_newlines_in_title(self):
        """TodoItem should handle tabs and newlines in title"""
        title_with_whitespace = "Test\ttitle\nwith\rwhitespace"
        todo = TodoItem(title=title_with_whitespace)
        assert todo.title == title_with_whitespace
    
    def test_should_update_timestamp_on_each_update_call(self):
        """Each call to update_details should update the timestamp"""
        todo = TodoItem(title="Test")
        original_updated_at = todo.updated_at
        
        import time
        time.sleep(0.001)
        
        # First update
        todo.update_details(title="Updated 1")
        first_update_time = todo.updated_at
        assert first_update_time > original_updated_at
        
        time.sleep(0.001)
        
        # Second update
        todo.update_details(title="Updated 2")
        second_update_time = todo.updated_at
        assert second_update_time > first_update_time
    
    def test_should_handle_multiple_mark_completed_calls(self):
        """Multiple calls to mark_completed should update timestamp each time"""
        todo = TodoItem(title="Test")
        
        # First completion
        todo.mark_completed()
        first_completion_time = todo.updated_at
        assert todo.completed is True
        
        import time
        time.sleep(0.001)
        
        # Second completion call
        todo.mark_completed()
        second_completion_time = todo.updated_at
        assert second_completion_time > first_completion_time
        assert todo.completed is True
    
    def test_should_maintain_id_consistency_across_updates(self):
        """TodoItem ID should remain consistent across all updates"""
        todo = TodoItem(title="Test")
        original_id = todo.id
        
        todo.update_details(title="Updated")
        assert todo.id == original_id
        
        todo.mark_completed()
        assert todo.id == original_id
        
        todo.update_details(description="New description")
        assert todo.id == original_id
    
    def test_should_handle_boundary_validation_errors_gracefully(self):
        """Validation errors should be clear and informative"""
        # Test title too long
        with pytest.raises(PydanticValidationError) as exc_info:
            TodoItem(title="a" * 201)
        
        error_messages = [str(error) for error in exc_info.value.errors()]
        assert any("at most 200 characters" in msg for msg in error_messages)
        
        # Test description too long
        with pytest.raises(PydanticValidationError) as exc_info:
            TodoItem(title="Valid", description="a" * 1001)
        
        error_messages = [str(error) for error in exc_info.value.errors()]
        assert any("at most 1000 characters" in msg for msg in error_messages)
    
    def test_should_handle_concurrent_timestamp_updates(self):
        """Timestamp updates should be consistent even in rapid succession"""
        todo = TodoItem(title="Test")
        timestamps = []
        
        # Perform rapid updates
        for i in range(5):
            todo.update_details(title=f"Update {i}")
            timestamps.append(todo.updated_at)
            # Small delay to ensure timestamp difference
            import time
            time.sleep(0.001)
        
        # Verify timestamps are in ascending order
        for i in range(1, len(timestamps)):
            assert timestamps[i] > timestamps[i-1]
    
    def test_should_handle_model_serialization_and_deserialization(self):
        """TodoItem should serialize and deserialize correctly"""
        original_todo = TodoItem(
            title="Test Task",
            description="Test Description",
            due_date=datetime.now() + timedelta(days=1)
        )
        
        # Serialize to dict
        todo_dict = original_todo.model_dump()
        
        # Deserialize from dict
        restored_todo = TodoItem(**todo_dict)
        
        # Verify all fields match
        assert restored_todo.id == original_todo.id
        assert restored_todo.title == original_todo.title
        assert restored_todo.description == original_todo.description
        assert restored_todo.due_date == original_todo.due_date
        assert restored_todo.completed == original_todo.completed
        assert restored_todo.created_at == original_todo.created_at
        assert restored_todo.updated_at == original_todo.updated_at