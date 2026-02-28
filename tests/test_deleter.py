"""Tests for Safe Deletion module."""

import tempfile
from pathlib import Path

import pytest

from mac_dedup.deleter import Deleter, DeletionResult
from mac_dedup.keep_strategy import Group


class TestDeletionResult:
    """Test DeletionResult dataclass."""

    def test_success_result(self) -> None:
        """Test successful deletion result."""
        result = DeletionResult(success=True, filepath="/path/to/file.txt")

        assert result.success is True
        assert result.filepath == "/path/to/file.txt"
        assert result.error is None

    def test_failure_result(self) -> None:
        """Test failed deletion result with error."""
        result = DeletionResult(
            success=False,
            filepath="/path/to/file.txt",
            error="Permission denied",
        )

        assert result.success is False
        assert result.filepath == "/path/to/file.txt"
        assert result.error == "Permission denied"


class TestDeleter:
    """Test Deleter class."""

    def test_init_without_send2trash(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test initialization fails without send2trash."""
        # Mock send2trash import to raise ImportError
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "send2trash":
                raise ImportError("No module named 'send2trash'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr("builtins.__import__", mock_import)

        with pytest.raises(ImportError, match="send2trash is required"):
            Deleter()

    def test_init_dry_run(self) -> None:
        """Test initialization with dry_run mode."""
        deleter = Deleter(dry_run=True)

        assert deleter.dry_run is True

    def test_delete_file_dry_run(self, tmp_path: Path) -> None:
        """Test deleting a file in dry-run mode."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        deleter = Deleter(dry_run=True)
        result = deleter.delete_file(str(test_file))

        assert result.success is True
        assert result.filepath == str(test_file)
        assert result.error is None

        # File should still exist in dry-run mode
        assert test_file.exists()

    def test_delete_nonexistent_file(self, tmp_path: Path) -> None:
        """Test deleting a non-existent file."""
        deleter = Deleter(dry_run=True)
        result = deleter.delete_file(str(tmp_path / "nonexistent.txt"))

        assert result.success is False
        assert "not found" in result.error

    def test_delete_directory_instead_of_file(self, tmp_path: Path) -> None:
        """Test deleting a directory instead of a file."""
        deleter = Deleter(dry_run=True)
        result = deleter.delete_file(str(tmp_path))

        assert result.success is False
        assert "not a file" in result.error

    def test_delete_files_multiple(self, tmp_path: Path) -> None:
        """Test deleting multiple files."""
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")

        deleter = Deleter(dry_run=True)
        results = deleter.delete_files([str(file1), str(file2)])

        assert len(results) == 2
        assert all(r.success for r in results)

    def test_delete_groups(self, tmp_path: Path) -> None:
        """Test deleting files from multiple groups."""
        # Create test files
        del1a = tmp_path / "file1a.txt"
        del1b = tmp_path / "file1b.txt"
        del2a = tmp_path / "file2a.txt"
        del1a.write_text("content1")
        del1b.write_text("content2")
        del2a.write_text("content3")

        group1 = Group(
            hash="abc123",
            keep_file="/keep/file1.txt",
            delete_files=[str(del1a), str(del1b)],
        )
        group2 = Group(
            hash="def456",
            keep_file="/keep/file2.txt",
            delete_files=[str(del2a)],
        )

        deleter = Deleter(dry_run=True)
        success, failure, results = deleter.delete_groups([group1, group2])

        assert success == 3  # All 3 delete files
        assert failure == 0
        assert len(results) == 3

    def test_get_preview(self) -> None:
        """Test getting preview of files to delete."""
        group1 = Group(
            hash="abc123",
            keep_file="/keep/file1.txt",
            delete_files=["/delete/file1a.txt", "/delete/file1b.txt"],
        )
        group2 = Group(
            hash="def456",
            keep_file="/keep/file2.txt",
            delete_files=["/delete/file2a.txt"],
        )

        deleter = Deleter(dry_run=True)
        preview = deleter.get_preview([group1, group2])

        assert len(preview) == 3
        assert "/delete/file1a.txt" in preview
        assert "/delete/file1b.txt" in preview
        assert "/delete/file2a.txt" in preview


@pytest.mark.skipif(
    "sys.platform == 'win32'",
    reason="send2trash trash behavior differs on Windows",
)
class TestDeleterIntegration:
    """Integration tests with real send2trash (dry-run only)."""

    def test_delete_file_to_trash_dry_run(self, tmp_path: Path) -> None:
        """Test dry-run mode preserves file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        deleter = Deleter(dry_run=True)
        result = deleter.delete_file(str(test_file))

        assert result.success is True
        assert test_file.exists()  # File should still exist
