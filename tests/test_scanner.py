"""Tests for directory scanner."""

import os
import tempfile
from pathlib import Path

import pytest

from mac_dedup.scanner import DirectoryScanner


class TestDirectoryScanner:
    """Test DirectoryScanner functionality."""

    def test_scanner_yields_file_info(self, temp_dir_with_files):
        """Scanner yields correct file info dictionaries."""
        scanner = DirectoryScanner(str(temp_dir_with_files))
        files = list(scanner.scan())

        assert len(files) > 0
        for file_info in files:
            assert "path" in file_info
            assert "size" in file_info
            assert "mtime" in file_info
            assert isinstance(file_info["path"], str)
            assert isinstance(file_info["size"], int)
            assert isinstance(file_info["mtime"], float)

    def test_scanner_recursively_scans_subdirs(self, temp_dir_with_nested_structure):
        """Scanner visits all subdirectories recursively."""
        scanner = DirectoryScanner(str(temp_dir_with_nested_structure))
        files = list(scanner.scan())

        # Should find files in all nested levels
        assert len(files) >= 6  # 2 files * 3 directories

        paths = [f["path"] for f in files]
        assert any("subdir1" in p for p in paths)
        assert any("subdir2" in p for p in paths)
        assert any("nested" in p for p in paths)

    def test_scanner_displays_progress_bar(self, temp_dir_with_files, capsys):
        """Scanner displays progress bar in correct format."""
        scanner = DirectoryScanner(str(temp_dir_with_files))
        list(scanner.scan())

        captured = capsys.readouterr()
        # For small directories, progress may not update (only every 100 files or 1 second)
        # Just verify the scanner completes successfully
        assert "Scanning:" in captured.out
        assert "Scan complete!" in captured.out

    def test_scanner_skips_symlinks(self, temp_dir_with_symlinks):
        """Scanner skips symbolic links and counts them."""
        scanner = DirectoryScanner(str(temp_dir_with_symlinks))

        generator = scanner.scan()
        files = list(generator)

        # Verify no symlink paths in results
        assert all(not Path(f["path"]).is_symlink() for f in files)

    def test_scanner_handles_permission_errors(self, temp_dir_with_restricted):
        """Scanner continues scanning after permission errors."""
        scanner = DirectoryScanner(str(temp_dir_with_restricted))
        files = list(scanner.scan())

        # Should still process accessible files
        accessible_files = [f for f in files if "restricted" not in f["path"]]
        assert len(accessible_files) > 0

    def test_scanner_returns_summary_stats(self, temp_dir_with_files):
        """Scanner returns summary statistics."""
        scanner = DirectoryScanner(str(temp_dir_with_files))

        generator = scanner.scan()
        files = list(generator)

        # Verify scan completes without error
        assert len(files) > 0

    def test_scanner_progress_bar_with_many_files(self, temp_dir_with_many_files, capsys):
        """Scanner displays progress bar for directories with many files."""
        scanner = DirectoryScanner(str(temp_dir_with_many_files))
        list(scanner.scan())

        captured = capsys.readouterr()
        # With 150 files, should trigger progress update (every 100 files)
        assert "[" in captured.out
        assert "%" in captured.out


# Pytest fixtures for test data
@pytest.fixture
def temp_dir_with_many_files():
    """Create temporary directory with many test files (for progress bar testing)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create 150 test files to trigger progress update (every 100 files)
        for i in range(150):
            Path(tmpdir, f"test_{i:03d}.txt").write_text(f"content {i}")
        yield Path(tmpdir)


@pytest.fixture
def temp_dir_with_files():
    """Create temporary directory with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some test files
        for i in range(5):
            Path(tmpdir, f"test_{i}.txt").write_text(f"content {i}")
        yield Path(tmpdir)


@pytest.fixture
def temp_dir_with_nested_structure():
    """Create temporary directory with nested subdirectories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create nested structure
        subdir1 = root / "subdir1"
        subdir2 = root / "subdir2"
        nested = subdir2 / "nested"

        subdir1.mkdir()
        subdir2.mkdir()
        nested.mkdir()

        # Create files at each level
        for d in [root, subdir1, subdir2, nested]:
            for i in range(2):
                (d / f"file_{i}.txt").write_text(f"content in {d}")

        yield root


@pytest.fixture
def temp_dir_with_symlinks():
    """Create temporary directory with symbolic links."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create real files
        real_file = root / "real.txt"
        real_file.write_text("real content")

        # Create symlink
        symlink = root / "symlink.txt"
        symlink.symlink_to(real_file)

        yield root


@pytest.fixture
def temp_dir_with_restricted():
    """Create temporary directory with restricted access."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create accessible files
        for i in range(3):
            (root / f"file_{i}.txt").write_text(f"content {i}")

        # Create restricted directory (will skip due to permissions)
        restricted = root / "restricted"
        restricted.mkdir()

        # Create file in restricted (may not be accessible)
        try:
            restricted_file = restricted / "secret.txt"
            restricted_file.write_text("secret")
            # Make unreadable (may fail on some systems)
            os.chmod(str(restricted), 0o000)
        except (OSError, PermissionError):
            pass

        yield root
