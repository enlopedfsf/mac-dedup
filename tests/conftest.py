"""Pytest fixtures for mac-dedup tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_directory() -> Path:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_files(temp_directory: Path) -> Path:
    """Create sample files in temporary directory."""
    (temp_directory / "file1.txt").write_text("Hello, World!")
    (temp_directory / "file2.txt").write_text("Different content")
    (temp_directory / "file3.txt").write_text("Hello, World!")  # Duplicate of file1
    return temp_directory
