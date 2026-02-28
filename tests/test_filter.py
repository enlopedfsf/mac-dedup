"""Tests for Filter module."""

from pathlib import Path

import pytest

from mac_dedup.file_type import FileType, get_supported_extensions
from mac_dedup.filter import FileFilter


class TestFileFilter:
    """Test FileFilter class."""

    def test_init_no_filters(self, tmp_path: Path) -> None:
        """Test initialization without filters."""
        filter_obj = FileFilter()

        assert filter_obj.is_filtering_active() is False
        assert len(filter_obj._allowed_extensions) == 0
        assert len(filter_obj._exclude_patterns) == len(FileFilter.DEFAULT_EXCLUDE_DIRS)

    def test_init_with_file_types(self) -> None:
        """Test initialization with file types."""
        filter_obj = FileFilter(file_types=[FileType.TEXT, FileType.AUDIO])

        assert len(filter_obj._allowed_extensions) > 0
        assert ".txt" in filter_obj._allowed_extensions
        assert ".md" in filter_obj._allowed_extensions
        assert ".mp3" in filter_obj._allowed_extensions
        assert ".m4a" in filter_obj._allowed_extensions

    def test_init_with_exclude_dirs(self) -> None:
        """Test initialization with exclude directories."""
        filter_obj = FileFilter(exclude_dirs=[".custom", "build"])

        assert ".custom" in filter_obj._exclude_patterns
        assert "build" in filter_obj._exclude_patterns

    def test_should_include_file_no_filter(self, tmp_path: Path) -> None:
        """Test file inclusion with no filters."""
        filter_obj = FileFilter()
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        assert filter_obj.should_include_file(str(test_file)) is True

    def test_should_include_file_with_type_filter(self, tmp_path: Path) -> None:
        """Test file inclusion with extension filter."""
        filter_obj = FileFilter(file_types=[FileType.TEXT])

        txt_file = tmp_path / "test.txt"
        mp3_file = tmp_path / "test.mp3"
        txt_file.write_text("text")
        mp3_file.write_bytes(b"audio")

        assert filter_obj.should_include_file(str(txt_file)) is True
        assert filter_obj.should_include_file(str(mp3_file)) is False

    def test_should_include_file_with_dir_exclude(self, tmp_path: Path) -> None:
        """Test file exclusion by directory."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        git_file = git_dir / "test.txt"
        git_file.write_text("content")

        normal_dir = tmp_path / "src"
        normal_dir.mkdir()
        normal_file = normal_dir / "test.txt"
        normal_file.write_text("content")

        filter_obj = FileFilter(exclude_dirs=[".git"])

        assert filter_obj.should_include_file(str(git_file)) is False
        assert filter_obj.should_include_file(str(normal_file)) is True

    def test_should_include_file_wildcard_pattern(self, tmp_path: Path) -> None:
        """Test directory exclusion with wildcard pattern."""
        node_dir = tmp_path / "node_modules"
        node_dir.mkdir()
        nested_dir = node_dir / "react"
        nested_dir.mkdir()
        nested_file = nested_dir / "test.txt"
        nested_file.write_text("content")

        filter_obj = FileFilter(exclude_dirs=["node_modules"])

        assert filter_obj.should_include_file(str(nested_file)) is False

    def test_filter_files(self, tmp_path: Path) -> None:
        """Test filtering a list of files."""
        txt_file = tmp_path / "test.txt"
        mp3_file = tmp_path / "test.mp3"
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        git_file = git_dir / "test.txt"

        txt_file.write_text("text")
        mp3_file.write_bytes(b"audio")
        git_file.write_text("content")

        filter_obj = FileFilter(
            file_types=[FileType.TEXT],
            exclude_dirs=[".git"],
        )

        files = [
            str(txt_file),
            str(mp3_file),
            str(git_file),
        ]

        filtered = filter_obj.filter_files(files)

        assert len(filtered) == 1
        assert str(txt_file) in filtered
        assert str(mp3_file) not in filtered
        assert str(git_file) not in filtered

    def test_add_exclude_pattern(self) -> None:
        """Test adding exclude pattern dynamically."""
        filter_obj = FileFilter()
        initial_count = len(filter_obj._exclude_patterns)

        filter_obj.add_exclude_pattern(".custom")
        assert len(filter_obj._exclude_patterns) == initial_count + 1
        assert ".custom" in filter_obj._exclude_patterns

    def test_set_file_types(self) -> None:
        """Test setting file types dynamically."""
        filter_obj = FileFilter(file_types=[FileType.TEXT])

        assert ".txt" in filter_obj._allowed_extensions
        assert ".mp3" not in filter_obj._allowed_extensions

        filter_obj.set_file_types([FileType.AUDIO, FileType.VIDEO])

        assert ".txt" not in filter_obj._allowed_extensions
        assert ".mp3" in filter_obj._allowed_extensions
        assert ".mp4" in filter_obj._allowed_extensions

    def test_is_filtering_active(self) -> None:
        """Test filtering active status."""
        no_filter = FileFilter()
        type_filter = FileFilter(file_types=[FileType.TEXT])
        dir_filter = FileFilter(exclude_dirs=[".git"])
        both_filter = FileFilter(file_types=[FileType.TEXT], exclude_dirs=[".git"])

        assert no_filter.is_filtering_active() is False
        assert type_filter.is_filtering_active() is True
        assert dir_filter.is_filtering_active() is True
        assert both_filter.is_filtering_active() is True

    def test_default_exclude_dirs(self) -> None:
        """Test default exclude directories."""
        filter_obj = FileFilter()

        assert ".git" in filter_obj._exclude_patterns
        assert "node_modules" in filter_obj._exclude_patterns
        assert "__pycache__" in filter_obj._exclude_patterns
        assert ".pytest_cache" in filter_obj._exclude_patterns

    def test_all_file_types_coverage(self) -> None:
        """Test all file types are covered."""
        filter_obj = FileFilter(
            file_types=[FileType.TEXT, FileType.AUDIO, FileType.VIDEO, FileType.ARCHIVE]
        )

        # Sample extensions from each type
        assert ".txt" in filter_obj._allowed_extensions  # TEXT
        assert ".pdf" in filter_obj._allowed_extensions  # TEXT
        assert ".mp3" in filter_obj._allowed_extensions  # AUDIO
        assert ".mp4" in filter_obj._allowed_extensions  # VIDEO
        assert ".zip" in filter_obj._allowed_extensions  # ARCHIVE
        assert ".dmg" in filter_obj._allowed_extensions  # ARCHIVE


class TestDirectoryScannerWithFilter:
    """Test DirectoryScanner with filter integration."""

    def test_scanner_with_type_filter(self, tmp_path: Path) -> None:
        """Test scanner with file type filter."""
        txt_file = tmp_path / "test.txt"
        mp3_file = tmp_path / "test.mp3"
        txt_file.write_text("text")
        mp3_file.write_bytes(b"audio")

        from mac_dedup.scanner import DirectoryScanner

        scanner = DirectoryScanner(str(tmp_path), file_types=[FileType.TEXT])
        files = list(scanner.scan())

        assert len(files) == 1
        assert str(txt_file) in [f["path"] for f in files]
        assert str(mp3_file) not in [f["path"] for f in files]

    def test_scanner_with_dir_exclude(self, tmp_path: Path) -> None:
        """Test scanner with directory exclusion."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        git_file = git_dir / "test.txt"
        git_file.write_text("content")

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        src_file = src_dir / "test.txt"
        src_file.write_text("content")

        from mac_dedup.scanner import DirectoryScanner

        scanner = DirectoryScanner(str(tmp_path), exclude_dirs=[".git"])
        files = list(scanner.scan())

        assert len(files) == 1
        assert str(src_file) in [f["path"] for f in files]
        assert str(git_file) not in [f["path"] for f in files]

    def test_scanner_combined_filters(self, tmp_path: Path) -> None:
        """Test scanner with both filters combined."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        git_txt = git_dir / "test.txt"
        git_txt.write_text("content")

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        src_txt = src_dir / "test.txt"
        src_txt.write_text("text")

        src_mp3 = src_dir / "test.mp3"
        src_mp3.write_bytes(b"audio")

        from mac_dedup.scanner import DirectoryScanner

        scanner = DirectoryScanner(
            str(tmp_path),
            file_types=[FileType.TEXT],
            exclude_dirs=[".git"],
        )
        files = list(scanner.scan())

        # Only src/test.txt should pass both filters
        assert len(files) == 1
        assert str(src_txt) in [f["path"] for f in files]
        assert str(src_mp3) not in [f["path"] for f in files]
        assert str(git_txt) not in [f["path"] for f in files]

    def test_scanner_no_filters(self, tmp_path: Path) -> None:
        """Test scanner with no filters (default behavior)."""
        txt_file = tmp_path / "test.txt"
        mp3_file = tmp_path / "test.mp3"
        txt_file.write_text("text")
        mp3_file.write_bytes(b"audio")

        from mac_dedup.scanner import DirectoryScanner

        scanner = DirectoryScanner(str(tmp_path))
        files = list(scanner.scan())

        # All files should be included
        assert len(files) == 2
