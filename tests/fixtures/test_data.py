"""Test data fixtures and sample datasets for TodoApp testing.

This module provides structured test data, sample datasets, and data generators
for comprehensive testing scenarios including edge cases and performance testing.
"""

import typing
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4


class TodoTestData:
    """Centralized test data provider with various todo scenarios."""

    # Basic test data sets
    VALID_TODOS: typing.ClassVar = [
        {
            "title": "Complete project documentation",
            "description": "Write comprehensive documentation for the TodoApp project",
            "due_date": "2026-06-30T17:00:00",
        },
        {
            "title": "Review code changes",
            "description": "Review the latest pull request changes",
            "due_date": "2026-06-15T09:00:00",
        },
        {
            "title": "Update dependencies",
            "description": "Update all project dependencies to latest versions",
            "due_date": None,
        },
        {"title": "Fix integration tests", "description": None, "due_date": "2026-06-20T14:30:00"},
        {
            "title": "Prepare demo presentation",
            "description": "Create slides and demo for client presentation",
            "due_date": "2026-07-01T10:00:00",
        },
    ]

    INVALID_TODOS: typing.ClassVar = [
        # Empty title
        {
            "title": "",
            "description": "This should fail due to empty title",
            "due_date": None,
            "expected_error": "at least 1 character",
        },
        # Whitespace-only title
        {
            "title": "   ",
            "description": "This should fail due to whitespace-only title",
            "due_date": None,
            "expected_error": "empty or whitespace",
        },
        # Title too long
        {
            "title": "a" * 201,
            "description": "This should fail due to title being too long",
            "due_date": None,
            "expected_error": "at most 200 characters",
        },
        # Description too long
        {
            "title": "Valid title",
            "description": "x" * 1001,
            "due_date": None,
            "expected_error": "at most 1000 characters",
        },
        # Invalid due date format
        {
            "title": "Valid title",
            "description": "Valid description",
            "due_date": "invalid-date-format",
            "expected_error": "datetime",
        },
    ]

    EDGE_CASE_TODOS: typing.ClassVar = [
        # Minimal valid data
        {"title": "A", "description": None, "due_date": None},
        # Maximum length title
        {"title": "x" * 200, "description": "Testing maximum title length", "due_date": None},
        # Maximum length description
        {"title": "Max description test", "description": "x" * 1000, "due_date": None},
        # Unicode and special characters
        {
            "title": "Unicode Test 🚀 émojis",
            "description": "Testing Unicode: 中文, العربية, 🎉, ñoño",
            "due_date": None,
        },
        # Special characters in title
        {
            "title": "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "description": "Testing special character handling",
            "due_date": None,
        },
        # Date edge cases
        {"title": "Y2K boundary test", "description": "Testing year 2000 boundary", "due_date": "2000-01-01T00:00:00"},
        {"title": "Far future date", "description": "Testing distant future date", "due_date": "2099-12-31T23:59:59"},
        {"title": "Leap year test", "description": "Testing leap year date", "due_date": "2026-02-29T12:00:00"},
    ]

    @classmethod
    def get_valid_todos(cls, count: int | None = None) -> list[dict[str, Any]]:
        """Get valid todo data, optionally limited to count."""
        if count is None:
            return cls.VALID_TODOS.copy()
        return cls.VALID_TODOS[:count].copy()

    @classmethod
    def get_invalid_todos(cls) -> list[dict[str, Any]]:
        """Get invalid todo data for validation testing."""
        return cls.INVALID_TODOS.copy()

    @classmethod
    def get_edge_case_todos(cls) -> list[dict[str, Any]]:
        """Get edge case todo data for boundary testing."""
        return cls.EDGE_CASE_TODOS.copy()

    @classmethod
    def generate_performance_dataset(cls, size: int = 100) -> list[dict[str, Any]]:
        """Generate large dataset for performance testing."""
        dataset = []
        base_date = datetime.now()

        for i in range(size):
            # Vary the data to simulate realistic usage
            has_description = i % 3 != 0  # 2/3 have descriptions
            has_due_date = i % 4 != 0  # 3/4 have due dates

            todo = {
                "title": f"Performance Test Todo {i + 1}",
                "description": f"Description for performance test todo number {i + 1}" if has_description else None,
            }

            if has_due_date:
                # Spread due dates over next 90 days
                days_ahead = (i % 90) + 1
                due_date = base_date + timedelta(days=days_ahead)
                todo["due_date"] = due_date.isoformat()
            else:
                todo["due_date"] = None

            dataset.append(todo)

        return dataset

    @classmethod
    def generate_mixed_scenario_dataset(cls) -> list[dict[str, Any]]:
        """Generate mixed scenario dataset with various todo types."""
        dataset = []

        # Add basic valid todos
        dataset.extend(cls.get_valid_todos())

        # Add edge cases (excluding invalid ones)
        dataset.extend(cls.get_edge_case_todos())

        # Add some generated todos with specific patterns
        current_time = datetime.now()

        # Overdue todos
        for i in range(3):
            overdue_date = current_time - timedelta(days=i + 1)
            dataset.append(
                {
                    "title": f"Overdue Todo {i + 1}",
                    "description": f"This todo is {i + 1} days overdue",
                    "due_date": overdue_date.isoformat(),
                }
            )

        # Future todos with various due dates
        for days in [1, 7, 30, 90]:
            future_date = current_time + timedelta(days=days)
            dataset.append(
                {
                    "title": f"Due in {days} days",
                    "description": f"Todo due in {days} days",
                    "due_date": future_date.isoformat(),
                }
            )

        return dataset


class RepositoryTestData:
    """Test data specifically for repository layer testing."""

    @staticmethod
    def get_json_storage_data() -> list[dict[str, Any]]:
        """Get test data formatted for JSON storage testing."""
        return [
            {
                "id": str(uuid4()),
                "title": "JSON Storage Test 1",
                "description": "Testing JSON serialization and deserialization",
                "due_date": "2026-06-30T17:00:00",
                "completed": False,
                "created_at": "2026-01-15T10:00:00",
                "updated_at": "2026-01-15T10:00:00",
            },
            {
                "id": str(uuid4()),
                "title": "JSON Storage Test 2",
                "description": None,
                "due_date": None,
                "completed": True,
                "created_at": "2026-01-16T11:30:00",
                "updated_at": "2026-01-16T14:20:00",
            },
        ]

    @staticmethod
    def get_xml_storage_structure() -> str:
        """Get test XML structure for XML repository testing."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<todos>
    <todo>
        <id>{uuid4()!s}</id>
        <title>XML Storage Test 1</title>
        <description>Testing XML serialization and deserialization</description>
        <due_date>2026-06-30T17:00:00</due_date>
        <completed>false</completed>
        <created_at>2026-01-15T10:00:00</created_at>
        <updated_at>2026-01-15T10:00:00</updated_at>
    </todo>
    <todo>
        <id>{uuid4()!s}</id>
        <title>XML Storage Test 2</title>
        <description></description>
        <due_date></due_date>
        <completed>true</completed>
        <created_at>2026-01-16T11:30:00</created_at>
        <updated_at>2026-01-16T14:20:00</updated_at>
    </todo>
</todos>"""

    @staticmethod
    def get_corrupted_json_samples() -> list[str]:
        """Get samples of corrupted JSON for error handling tests."""
        return [
            '{"invalid": json syntax',  # Missing closing brace
            '[{"title": "test", "description": }]',  # Invalid JSON structure
            '{"title": "test", "duplicate_key": 1, "duplicate_key": 2}',  # Duplicate keys
            "",  # Empty file
            "not json at all",  # Non-JSON content
            '{"title": "test", "date": "invalid-date-format"}',  # Invalid date
        ]

    @staticmethod
    def get_corrupted_xml_samples() -> list[str]:
        """Get samples of corrupted XML for error handling tests."""
        return [
            "<todos><todo><title>Unclosed tag</todos>",  # Unclosed tag
            '<?xml version="1.0"?><todos><todo><title></todo>',  # Missing closing tag
            "<todos><todo>Invalid XML structure</todos>",  # Invalid nesting
            "",  # Empty file
            "Not XML content at all",  # Non-XML content
            '<?xml version="1.0"?><todos><todo><title>Test</title></todo>',  # Missing root close
        ]


class CLITestData:
    """Test data specifically for CLI interface testing."""

    MENU_INPUTS: typing.ClassVar = {
        "add_todo": ["1"],
        "list_todos": ["2"],
        "update_todo": ["3"],
        "complete_todo": ["4"],
        "delete_todo": ["5"],
        "quit": ["6"],
    }

    ADD_TODO_INPUTS: typing.ClassVar = [
        # Valid inputs
        ["Valid Todo", "Valid description", "", "n"],  # No due date
        ["Todo with date", "Has due date", "2026-12-31T23:59:59", "n"],  # With due date
        ["Minimal todo", "", "", "n"],  # Minimal input
        # Edge case inputs
        ["A", "", "", "n"],  # Single character title
        ["x" * 200, "Max length title", "", "n"],  # Maximum title length
    ]

    UPDATE_TODO_INPUTS: typing.ClassVar = [
        # Valid update scenarios
        ["valid-uuid", "Updated Title", "Updated description", "", "n"],
        ["valid-uuid", "", "Only description update", "2026-12-31T12:00:00", "n"],
        # Error scenarios
        ["invalid-uuid", "", "", "", "n"],  # Invalid UUID
        ["", "", "", "", "n"],  # Empty UUID
    ]

    DELETE_TODO_INPUTS: typing.ClassVar = [
        # Confirmation scenarios
        ["valid-uuid", "y", "n"],  # Confirm deletion
        ["valid-uuid", "n", "n"],  # Cancel deletion
        ["valid-uuid", "yes", "n"],  # Alternative confirmation
        # Error scenarios
        ["invalid-uuid", "y", "n"],  # Invalid UUID
    ]

    @classmethod
    def get_menu_input_sequence(cls, actions: list[str]) -> list[str]:
        """Get menu input sequence for multiple actions."""
        inputs = []
        for action in actions:
            inputs.extend(cls.MENU_INPUTS.get(action, []))
        inputs.extend(cls.MENU_INPUTS["quit"])  # Always end with quit
        return inputs

    @classmethod
    def get_add_todo_sequence(cls, scenario_index: int = 0) -> list[str]:
        """Get add todo input sequence for specific scenario."""
        if scenario_index < len(cls.ADD_TODO_INPUTS):
            return cls.ADD_TODO_INPUTS[scenario_index]
        return cls.ADD_TODO_INPUTS[0]  # Default to first scenario


class IntegrationTestData:
    """Test data for integration testing scenarios."""

    @classmethod
    def get_complete_workflow_data(cls) -> dict[str, Any]:
        """Get data for complete workflow testing."""
        return {
            "initial_todos": [
                {
                    "title": "Workflow Test 1",
                    "description": "First todo in workflow test",
                    "due_date": "2026-07-01T10:00:00",
                },
                {"title": "Workflow Test 2", "description": "Second todo in workflow test", "due_date": None},
            ],
            "updates": [
                {
                    "index": 0,  # Update first todo
                    "title": "Updated Workflow Test 1",
                    "description": "Updated description",
                }
            ],
            "completions": [1],  # Complete second todo
            "deletions": [0],  # Delete first todo
        }

    @classmethod
    def get_migration_test_data(cls) -> dict[str, list[dict[str, Any]]]:
        """Get data for testing migration between storage formats."""
        return {
            "source_data": [
                {
                    "title": "Migration Test 1",
                    "description": "Testing data migration between formats",
                    "due_date": "2026-08-15T14:30:00",
                },
                {"title": "Migration Test 2", "description": None, "due_date": None},
                {
                    "title": "Unicode Migration Test 🌟",
                    "description": "Testing Unicode handling in migration",
                    "due_date": "2026-09-01T09:00:00",
                },
            ]
        }

    @classmethod
    def get_concurrent_access_data(cls) -> list[dict[str, Any]]:
        """Get data for concurrent access testing."""
        return [
            {
                "session": 1,
                "todos": [
                    {"title": "Session 1 Todo 1", "description": "From first session"},
                    {"title": "Session 1 Todo 2", "description": "Also from first session"},
                ],
            },
            {
                "session": 2,
                "todos": [
                    {"title": "Session 2 Todo 1", "description": "From second session"},
                    {"title": "Session 2 Todo 2", "description": "Also from second session"},
                ],
            },
        ]


# Export main data classes for easy importing
__all__ = ["CLITestData", "IntegrationTestData", "RepositoryTestData", "TodoTestData"]
