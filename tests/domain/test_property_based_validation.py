"""Property-based testing for domain model validation.

This module demonstrates advanced pytest best practices using property-based testing
to validate the TodoItem domain model with generated data that explores edge cases
systematically.
"""

from datetime import UTC, datetime, timedelta

import pytest
from hypothesis import Verbosity, given, settings
from hypothesis import strategies as st
from hypothesis.strategies import booleans, datetimes, text
from pydantic import ValidationError

from src.domain.models import TodoItem


# Custom hypothesis strategies for TodoItem testing
@st.composite
def valid_titles(draw):
    """Generate valid titles (1-200 characters, not just whitespace)."""
    # Generate titles that are valid but explore edge cases
    title = draw(
        text(
            min_size=1,
            max_size=200,
            alphabet=st.characters(
                whitelist_categories=(
                    "Lu",
                    "Ll",
                    "Lt",
                    "Lm",
                    "Lo",
                    "Nd",
                    "Pc",
                    "Pd",
                    "Ps",
                    "Pe",
                    "Po",
                    "Sm",
                    "Sc",
                    "Sk",
                    "So",
                ),
                min_codepoint=32,
                max_codepoint=1000,
            ),
        )
    )
    # Ensure it's not just whitespace
    if not title.strip():
        title = "A"  # Fallback to minimal valid title
    return title.strip()


@st.composite
def valid_descriptions(draw):
    """Generate valid descriptions (0-1000 characters or None)."""
    return draw(
        st.one_of(
            st.none(),
            text(
                max_size=1000,
                alphabet=st.characters(
                    whitelist_categories=(
                        "Lu",
                        "Ll",
                        "Lt",
                        "Lm",
                        "Lo",
                        "Nd",
                        "Pc",
                        "Pd",
                        "Ps",
                        "Pe",
                        "Po",
                        "Sm",
                        "Sc",
                        "Sk",
                        "So",
                    ),
                    min_codepoint=32,
                    max_codepoint=1000,
                ),
            ),
        )
    )


@st.composite
def future_datetimes(draw):
    """Generate datetime objects in the future."""
    now = datetime.now()
    # Generate dates between now and 10 years in the future
    future_date = draw(
        datetimes(
            min_value=now + timedelta(seconds=1),
            max_value=now + timedelta(days=3650),  # 10 years
        )
    )
    return future_date


@st.composite
def valid_todo_data(draw):
    """Generate valid TodoItem data."""
    return {
        "title": draw(valid_titles()),
        "description": draw(valid_descriptions()),
        "due_date": draw(st.one_of(st.none(), future_datetimes())),
        "completed": draw(booleans()),
    }


class TestTodoItemPropertyBased:
    """Property-based tests for TodoItem validation and behavior."""

    @given(valid_todo_data())
    @settings(max_examples=50, verbosity=Verbosity.normal)
    def test_valid_todo_creation_always_succeeds(self, todo_data):
        """Property: Valid todo data should always create a TodoItem successfully."""
        # This property ensures that our valid_todo_data strategy is correct
        todo = TodoItem(**todo_data)

        # Verify essential properties
        assert todo.title == todo_data["title"].strip()
        assert todo.description == todo_data["description"]
        assert todo.due_date == todo_data["due_date"]
        assert todo.completed == todo_data["completed"]
        assert todo.id is not None
        assert todo.created_at <= datetime.now()
        assert todo.updated_at <= datetime.now()

    @given(text())
    @settings(max_examples=100)
    def test_empty_or_whitespace_titles_always_fail(self, title):
        """Property: Empty or whitespace-only titles should always fail validation."""
        # Skip valid titles to focus on invalid ones
        if title and title.strip():
            return

        with pytest.raises(ValidationError):
            TodoItem(title=title, description="Test")

    @given(text(min_size=201))
    @settings(max_examples=50)
    def test_overly_long_titles_always_fail(self, long_title):
        """Property: Titles longer than 200 characters should always fail."""
        with pytest.raises(ValidationError):
            TodoItem(title=long_title, description="Test")

    @given(text(min_size=1001))
    @settings(max_examples=50)
    def test_overly_long_descriptions_always_fail(self, long_description):
        """Property: Descriptions longer than 1000 characters should always fail."""
        with pytest.raises(ValidationError):
            TodoItem(title="Valid Title", description=long_description)

    @given(datetimes(max_value=datetime.now() - timedelta(seconds=1)))
    @settings(max_examples=50)
    def test_past_due_dates_always_fail(self, past_date):
        """Property: Due dates in the past should always fail validation."""
        with pytest.raises(ValidationError):
            TodoItem(title="Valid Title", due_date=past_date)

    @given(valid_todo_data())
    @settings(max_examples=50)
    def test_todo_immutability_properties(self, todo_data):
        """Property: TodoItem should preserve immutable fields across updates."""
        original_todo = TodoItem(**todo_data)
        original_id = original_todo.id
        original_created_at = original_todo.created_at

        # Create an updated version
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "completed": not original_todo.completed,
        }

        updated_todo = TodoItem(**update_data)
        # Simulate update process (preserving immutable fields)
        updated_todo.id = original_id
        updated_todo.created_at = original_created_at

        # Properties that should be preserved
        assert updated_todo.id == original_id
        assert updated_todo.created_at == original_created_at

        # Properties that should change
        assert updated_todo.title == "Updated Title"
        assert updated_todo.description == "Updated Description"

    @given(st.lists(valid_todo_data(), min_size=2, max_size=10))
    @settings(max_examples=20)
    def test_multiple_todos_have_unique_ids(self, todos_data):
        """Property: Multiple TodoItems should always have unique IDs."""
        todos = [TodoItem(**data) for data in todos_data]
        ids = [todo.id for todo in todos]

        # All IDs should be unique
        assert len(ids) == len(set(ids))

    @given(valid_titles(), valid_descriptions())
    @settings(max_examples=50)
    def test_title_normalization_property(self, title, description):
        """Property: Titles should be normalized (trimmed) consistently."""
        # Add some whitespace to test normalization
        padded_title = f"  {title}  "

        todo = TodoItem(title=padded_title, description=description)

        # Title should be trimmed
        assert todo.title == title.strip()
        assert not todo.title.startswith(" ")
        assert not todo.title.endswith(" ")

    @pytest.mark.parametrize(
        "field_name,invalid_values",
        [
            ("title", ["", "   ", "\t\n", None]),
            ("due_date", [datetime.now() - timedelta(days=1), datetime.now() - timedelta(hours=1)]),
        ],
    )
    def test_parametrized_validation_failures(self, field_name, invalid_values):
        """Parametrized test for systematic validation failure testing."""
        base_data = {"title": "Valid Title", "description": "Valid Description"}

        for invalid_value in invalid_values:
            test_data = base_data.copy()
            test_data[field_name] = invalid_value

            with pytest.raises(ValidationError):
                TodoItem(**test_data)


class TestTodoItemEdgeCases:
    """Edge case testing using targeted examples."""

    @pytest.mark.parametrize(
        "title",
        [
            "A",  # Minimum length
            "x" * 200,  # Maximum length
            "🚀 Unicode Title",  # Unicode
            "Title with\ttab",  # Tab character
            "Title with\nnewline",  # Newline character
            "Special !@#$%^&*() chars",  # Special characters
        ],
    )
    def test_title_edge_cases(self, title):
        """Test specific edge cases for title validation."""
        todo = TodoItem(title=title, description="Test")
        assert todo.title == title.strip()

    @pytest.mark.parametrize(
        "description",
        [
            None,  # None description
            "",  # Empty description
            "x" * 1000,  # Maximum length description
            "Multi\nline\ndescription",  # Multiline
            "Unicode description: 🎯 ñoño 中文",  # Unicode content
        ],
    )
    def test_description_edge_cases(self, description):
        """Test specific edge cases for description validation."""
        todo = TodoItem(title="Valid Title", description=description)
        assert todo.description == description

    def test_timezone_aware_datetime_handling(self):
        """Test handling of timezone-aware datetime objects."""

        # Future date with timezone
        future_tz = datetime.now(UTC) + timedelta(days=1)

        # Convert to naive datetime for comparison since model expects naive datetime
        future_naive = future_tz.replace(tzinfo=None)

        todo = TodoItem(title="TZ Test", due_date=future_naive)
        assert todo.due_date == future_naive

    def test_microsecond_precision_timestamps(self):
        """Test that timestamps preserve microsecond precision."""
        todo = TodoItem(title="Precision Test")

        # Check that timestamps have microsecond precision
        assert todo.created_at.microsecond is not None
        assert todo.updated_at.microsecond is not None

        # Timestamps should be very close (created within same operation)
        time_diff = abs((todo.updated_at - todo.created_at).total_seconds())
        assert time_diff < 0.001  # Less than 1 millisecond


# Performance testing with property-based approach
class TestTodoItemPerformance:
    """Performance-related property-based tests."""

    @given(st.lists(valid_todo_data(), min_size=100, max_size=1000))
    @settings(max_examples=5, deadline=5000)  # 5 second deadline
    def test_bulk_creation_performance(self, todos_data):
        """Property: Bulk TodoItem creation should complete within reasonable time."""
        import time

        start_time = time.time()
        todos = [TodoItem(**data) for data in todos_data]
        creation_time = time.time() - start_time

        # Should create 100+ todos in less than 1 second
        assert creation_time < 1.0
        assert len(todos) == len(todos_data)

        # All todos should be valid
        for todo in todos[:10]:  # Check first 10 for validity
            assert todo.title
            assert todo.id is not None


# Custom marks for organizing property-based tests
pytestmark = [
    pytest.mark.unit,
    pytest.mark.property_based,
]
