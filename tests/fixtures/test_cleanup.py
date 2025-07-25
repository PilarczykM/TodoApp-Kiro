"""Test cleanup utilities for TodoApp testing.

This module provides utilities for cleaning up test resources, ensuring test isolation,
and managing temporary files and directories created during testing.
"""

import os
import shutil
import tempfile
from collections.abc import Generator
from contextlib import contextmanager, suppress
from pathlib import Path

import pytest


class TestCleanupManager:
    """Manages cleanup of test resources and ensures test isolation."""

    def __init__(self):
        self._temp_files: set[Path] = set()
        self._temp_directories: set[Path] = set()
        self._created_files: set[Path] = set()

    def register_temp_file(self, file_path: Path) -> None:
        """Register a temporary file for cleanup."""
        self._temp_files.add(file_path)

    def register_temp_directory(self, dir_path: Path) -> None:
        """Register a temporary directory for cleanup."""
        self._temp_directories.add(dir_path)

    def register_created_file(self, file_path: Path) -> None:
        """Register a created file for cleanup."""
        self._created_files.add(file_path)

    def cleanup_temp_files(self) -> None:
        """Clean up all registered temporary files."""
        for file_path in self._temp_files.copy():
            try:
                if file_path.exists():
                    file_path.unlink()
                self._temp_files.remove(file_path)
            except (OSError, PermissionError) as e:
                # Log warning but continue cleanup
                print(f"Warning: Could not remove temp file {file_path}: {e}")

    def cleanup_temp_directories(self) -> None:
        """Clean up all registered temporary directories."""
        for dir_path in self._temp_directories.copy():
            try:
                if dir_path.exists() and dir_path.is_dir():
                    shutil.rmtree(dir_path)
                self._temp_directories.remove(dir_path)
            except (OSError, PermissionError) as e:
                print(f"Warning: Could not remove temp directory {dir_path}: {e}")

    def cleanup_created_files(self) -> None:
        """Clean up all files created during tests."""
        for file_path in self._created_files.copy():
            try:
                if file_path.exists():
                    file_path.unlink()
                self._created_files.remove(file_path)
            except (OSError, PermissionError) as e:
                print(f"Warning: Could not remove created file {file_path}: {e}")

    def cleanup_all(self) -> None:
        """Clean up all registered resources."""
        self.cleanup_temp_files()
        self.cleanup_created_files()
        self.cleanup_temp_directories()


@pytest.fixture(scope="function")
def cleanup_manager() -> Generator[TestCleanupManager, None, None]:
    """Provide a cleanup manager for individual tests."""
    manager = TestCleanupManager()
    try:
        yield manager
    finally:
        manager.cleanup_all()


@pytest.fixture(scope="session")
def session_cleanup_manager() -> Generator[TestCleanupManager, None, None]:
    """Provide a cleanup manager for the entire test session."""
    manager = TestCleanupManager()
    try:
        yield manager
    finally:
        manager.cleanup_all()


@contextmanager
def temporary_file(suffix: str = "", prefix: str = "test_", content: str | None = None):
    """Context manager for creating and cleaning up temporary files."""
    temp_file = None
    try:
        fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        temp_file = Path(temp_path)

        if content is not None:
            with os.fdopen(fd, "w") as f:
                f.write(content)
        else:
            os.close(fd)

        yield temp_file
    finally:
        if temp_file and temp_file.exists():
            with suppress(OSError, PermissionError):
                temp_file.unlink()


@contextmanager
def temporary_directory(prefix: str = "test_"):
    """Context manager for creating and cleaning up temporary directories."""
    temp_dir = None
    try:
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
        yield temp_dir
    finally:
        if temp_dir and temp_dir.exists():
            with suppress(OSError, PermissionError):
                shutil.rmtree(temp_dir)


class FileSystemTestHelper:
    """Helper class for file system operations in tests."""

    @staticmethod
    def create_test_file(file_path: Path, content: str = "", cleanup_manager: TestCleanupManager = None) -> Path:
        """Create a test file with specified content."""
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as f:
            f.write(content)

        if cleanup_manager:
            cleanup_manager.register_created_file(file_path)

        return file_path

    @staticmethod
    def create_test_directory(dir_path: Path, cleanup_manager: TestCleanupManager = None) -> Path:
        """Create a test directory."""
        dir_path.mkdir(parents=True, exist_ok=True)

        if cleanup_manager:
            cleanup_manager.register_temp_directory(dir_path)

        return dir_path

    @staticmethod
    def corrupt_file(file_path: Path, corruption_type: str = "truncate") -> None:
        """Corrupt a file for error handling tests."""
        if not file_path.exists():
            return

        if corruption_type == "truncate":
            # Truncate file to invalid state
            with open(file_path, "w") as f:
                f.write('{"invalid": json')
        elif corruption_type == "empty":
            # Make file empty
            with open(file_path, "w") as f:
                f.write("")
        elif corruption_type == "binary":
            # Write binary data
            with open(file_path, "wb") as f:
                f.write(b"\x00\x01\x02\x03\xff\xfe\xfd")
        elif corruption_type == "permission":
            # Change permissions (Unix-like systems only)
            with suppress(OSError, AttributeError):
                file_path.chmod(0o000)  # No permissions

    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """Get file size in bytes."""
        if file_path.exists():
            return file_path.stat().st_size
        return 0

    @staticmethod
    def compare_files(file1: Path, file2: Path) -> bool:
        """Compare two files for equality."""
        if not (file1.exists() and file2.exists()):
            return False

        if file1.stat().st_size != file2.stat().st_size:
            return False

        with open(file1, "rb") as f1, open(file2, "rb") as f2:
            return f1.read() == f2.read()


@pytest.fixture
def fs_helper() -> FileSystemTestHelper:
    """Provide FileSystemTestHelper for tests."""
    return FileSystemTestHelper()


class RepositoryTestCleaner:
    """Specialized cleaner for repository-related test resources."""

    def __init__(self, base_directory: Path):
        self.base_directory = base_directory
        self.json_files: list[Path] = []
        self.xml_files: list[Path] = []

    def register_json_file(self, file_path: Path) -> None:
        """Register a JSON storage file for cleanup."""
        self.json_files.append(file_path)

    def register_xml_file(self, file_path: Path) -> None:
        """Register an XML storage file for cleanup."""
        self.xml_files.append(file_path)

    def cleanup_repository_files(self) -> None:
        """Clean up all repository files."""
        for json_file in self.json_files:
            if json_file.exists():
                with suppress(OSError, PermissionError):
                    json_file.unlink()

        for xml_file in self.xml_files:
            if xml_file.exists():
                with suppress(OSError, PermissionError):
                    xml_file.unlink()

        self.json_files.clear()
        self.xml_files.clear()

    def verify_cleanup(self) -> bool:
        """Verify that all registered files have been cleaned up."""
        remaining_files = []

        for json_file in self.json_files:
            if json_file.exists():
                remaining_files.append(json_file)

        for xml_file in self.xml_files:
            if xml_file.exists():
                remaining_files.append(xml_file)

        return len(remaining_files) == 0


@pytest.fixture
def repo_cleaner(temp_storage_directory: Path) -> Generator[RepositoryTestCleaner, None, None]:
    """Provide a repository-specific cleaner."""
    cleaner = RepositoryTestCleaner(temp_storage_directory)
    try:
        yield cleaner
    finally:
        cleaner.cleanup_repository_files()


class TestIsolationValidator:
    """Validates that tests are properly isolated."""

    def __init__(self):
        self.initial_state = {}
        self.final_state = {}

    def capture_initial_state(self, base_directory: Path) -> None:
        """Capture initial state before test execution."""
        self.initial_state = self._capture_directory_state(base_directory)

    def capture_final_state(self, base_directory: Path) -> None:
        """Capture final state after test execution."""
        self.final_state = self._capture_directory_state(base_directory)

    def validate_isolation(self) -> bool:
        """Validate that no permanent changes were made."""
        return self.initial_state == self.final_state

    def get_state_differences(self) -> dict:
        """Get differences between initial and final states."""
        differences = {"added_files": [], "removed_files": [], "modified_files": []}

        initial_files = set(self.initial_state.keys())
        final_files = set(self.final_state.keys())

        differences["added_files"] = list(final_files - initial_files)
        differences["removed_files"] = list(initial_files - final_files)

        for file_path in initial_files & final_files:
            if self.initial_state[file_path] != self.final_state[file_path]:
                differences["modified_files"].append(file_path)

        return differences

    def _capture_directory_state(self, directory: Path) -> dict:
        """Capture the state of a directory and its contents."""
        state = {}

        if not directory.exists():
            return state

        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    state[str(file_path)] = {"size": file_path.stat().st_size, "mtime": file_path.stat().st_mtime}
                except (OSError, PermissionError):
                    state[str(file_path)] = {"error": "access_denied"}

        return state


@pytest.fixture
def isolation_validator() -> TestIsolationValidator:
    """Provide test isolation validator."""
    return TestIsolationValidator()


# Auto-cleanup fixture that runs after every test
@pytest.fixture(autouse=True)
def auto_cleanup(temp_test_directory: Path):
    """Automatically clean up test artifacts after each test."""
    # Before test - capture initial state if needed
    yield

    # After test - perform cleanup
    # Clean up any leftover test files in the temp directory
    if temp_test_directory.exists():
        for item in temp_test_directory.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except (OSError, PermissionError):
                # Log but continue
                pass
