"""Tests for HashEngine module."""

import os
import tempfile
from pathlib import Path

import pytest

from mac_dedup.hash_engine import HashEngine


class TestHashEngine:
    """Test HashEngine class functionality."""

    def test_init(self) -> None:
        """Test HashEngine initialization."""
        engine = HashEngine()
        assert engine._hash_cache == {}
        assert engine.CHUNK_THRESHOLD == 10 * 1024 * 1024
        assert engine.CHUNK_SIZE == 4 * 1024 * 1024

    def test_calculate_hash_small_file(self, tmp_path: Path) -> None:
        """Test hash calculation for small files."""
        engine = HashEngine()

        # Create a small test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        hash_value = engine._calculate_hash(str(test_file))

        # SHA-256 of "Hello, World!" is known
        assert hash_value == "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"

    def test_calculate_hash_large_file(self, tmp_path: Path) -> None:
        """Test chunked hash calculation for large files."""
        engine = HashEngine()

        # Create a file > 10MB to trigger chunked reading
        large_file = tmp_path / "large.bin"
        chunk_size = 1024 * 1024  # 1MB
        chunk = b"X" * chunk_size

        with large_file.open("wb") as f:
            for _ in range(12):  # 12MB total
                f.write(chunk)

        hash_value = engine._calculate_hash(str(large_file))

        # Verify it's a valid SHA-256 hash (64 hex characters)
        assert len(hash_value) == 64
        assert all(c in "0123456789abcdef" for c in hash_value)

    def test_calculate_hash_binary_mode(self, tmp_path: Path) -> None:
        """Test that hash calculation uses binary mode for cross-platform consistency."""
        engine = HashEngine()

        # Create file with binary content
        test_file = tmp_path / "binary.bin"
        test_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe")

        hash_value1 = engine._calculate_hash(str(test_file))
        hash_value2 = engine._calculate_hash(str(test_file))

        # Should be deterministic
        assert hash_value1 == hash_value2

    def test_calculate_hash_file_not_found(self) -> None:
        """Test _calculate_hash raises FileNotFoundError for non-existent files."""
        engine = HashEngine()

        with pytest.raises(FileNotFoundError, match="File not found"):
            engine._calculate_hash("/nonexistent/file.txt")

    def test_calculate_hash_permission_error(self, tmp_path: Path) -> None:
        """Test _calculate_hash raises PermissionError for unreadable files."""
        engine = HashEngine()

        # Create a file and make it unreadable
        test_file = tmp_path / "unreadable.txt"
        test_file.write_text("test")

        # Make file unreadable (only on Unix)
        if os.name != "nt":
            os.chmod(test_file, 0o000)

            with pytest.raises(PermissionError):
                engine._calculate_hash(str(test_file))

            # Restore permissions for cleanup
            os.chmod(test_file, 0o644)

    def test_calculate_hash_path_not_file(self, tmp_path: Path) -> None:
        """Test _calculate_hash raises ValueError for non-file paths."""
        engine = HashEngine()

        with pytest.raises(ValueError, match="Path is not a file"):
            engine._calculate_hash(str(tmp_path))

    def test_find_duplicates_no_files(self) -> None:
        """Test find_duplicates returns empty dict for no files."""
        engine = HashEngine()
        duplicates = engine.find_duplicates([])
        assert duplicates == {}

    def test_find_duplicates_all_unique(self, tmp_path: Path) -> None:
        """Test find_duplicates returns empty dict for unique files."""
        engine = HashEngine()

        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")

        file_infos = [
            {"path": str(file1), "size": 8, "mtime": 1.0},
            {"path": str(file2), "size": 8, "mtime": 2.0},
        ]

        duplicates = engine.find_duplicates(file_infos)
        assert duplicates == {}

    def test_find_duplicates_with_duplicates(self, tmp_path: Path) -> None:
        """Test find_duplicates correctly identifies duplicate files."""
        engine = HashEngine()

        # Create duplicate files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file3 = tmp_path / "file3.txt"

        content = "duplicate content"
        file1.write_text(content)
        file2.write_text(content)  # Same as file1
        file3.write_text("unique content")

        file_infos = [
            {"path": str(file1), "size": len(content), "mtime": 1.0},
            {"path": str(file2), "size": len(content), "mtime": 2.0},
            {"path": str(file3), "size": len("unique content"), "mtime": 3.0},
        ]

        duplicates = engine.find_duplicates(file_infos)

        # Should find one duplicate group (file1 and file2)
        assert len(duplicates) == 1
        duplicate_hash = list(duplicates.keys())[0]
        assert len(duplicates[duplicate_hash]) == 2

    def test_find_duplicates_handles_missing_files(self, tmp_path: Path) -> None:
        """Test find_duplicates continues when file is missing."""
        engine = HashEngine()

        file1 = tmp_path / "file1.txt"
        file1.write_text("content1")

        file_infos = [
            {"path": str(file1), "size": 7, "mtime": 1.0},
            {"path": "/nonexistent/file.txt", "size": 0, "mtime": 2.0},
        ]

        # Should not raise, just skip the missing file
        duplicates = engine.find_duplicates(file_infos)
        assert duplicates == {}

    def test_find_duplicates_with_progress_callback(self, tmp_path: Path) -> None:
        """Test find_duplicates_with_progress calls progress callback."""
        engine = HashEngine()

        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")

        file_infos = [
            {"path": str(file1), "size": 7, "mtime": 1.0},
            {"path": str(file2), "size": 7, "mtime": 2.0},
        ]

        progress_values = []

        def callback(percentage: int) -> None:
            progress_values.append(percentage)

        duplicates = engine.find_duplicates_with_progress(file_infos, callback)

        assert duplicates == {}
        assert len(progress_values) == 2
        assert progress_values[0] == 50  # 1/2 files
        assert progress_values[1] == 100  # 2/2 files

    def test_clear_cache(self, tmp_path: Path) -> None:
        """Test clear_cache clears internal hash cache."""
        engine = HashEngine()

        file1 = tmp_path / "file1.txt"
        file1.write_text("content")

        # Calculate hash to populate cache
        engine._calculate_hash(str(file1))
        assert len(engine._hash_cache) == 1

        # Clear cache
        engine.clear_cache()
        assert len(engine._hash_cache) == 0

    def test_hash_cache_avoids_recalculation(self, tmp_path: Path) -> None:
        """Test that hash cache avoids recalculating hashes."""
        engine = HashEngine()

        file1 = tmp_path / "file1.txt"
        file1.write_text("content")

        # First calculation
        hash1 = engine._calculate_hash(str(file1))

        # Modify file (but cache should return original hash)
        file1.write_text("modified")

        # Second calculation should use cache
        hash2 = engine._calculate_hash(str(file1))

        assert hash1 == hash2
        assert len(engine._hash_cache) == 1

    def test_hash_cache_independence(self, tmp_path: Path) -> None:
        """Test that hash cache is independent for each file."""
        engine = HashEngine()

        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")

        hash1 = engine._calculate_hash(str(file1))
        hash2 = engine._calculate_hash(str(file2))

        assert hash1 != hash2
        assert len(engine._hash_cache) == 2
