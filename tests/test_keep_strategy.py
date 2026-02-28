"""Tests for Keep Strategy module."""

import pytest
from mac_dedup.keep_strategy import Group, KeepStrategy


class TestGroup:
    """Test Group dataclass and methods."""

    def test_group_creation(self):
        """Test Group can be created with correct attributes."""
        group = Group(
            hash="abc123",
            keep_file="/keep/file.txt",
            delete_files=["/delete/file1.txt", "/delete/file2.txt"],
        )
        assert group.hash == "abc123"
        assert group.keep_file == "/keep/file.txt"
        assert group.delete_files == ["/delete/file1.txt", "/delete/file2.txt"]

    def test_group_get_keep_file(self):
        """Test get_keep_file() returns the keep_file attribute."""
        group = Group(hash="abc123", keep_file="/keep/file.txt", delete_files=["/delete/file1.txt"])
        assert group.get_keep_file() == "/keep/file.txt"

    def test_group_get_delete_files(self):
        """Test get_delete_files() returns the delete_files list."""
        group = Group(
            hash="abc123",
            keep_file="/keep/file.txt",
            delete_files=["/delete/file1.txt", "/delete/file2.txt"],
        )
        assert group.get_delete_files() == ["/delete/file1.txt", "/delete/file2.txt"]


class TestKeepStrategy:
    """Test KeepStrategy class."""

    def test_keep_newest_mtime(self):
        """Test newest mtime file is kept."""
        strategy = KeepStrategy()
        duplicates = {
            "hash1": [
                ("/old/file.txt", 1000.0),
                ("/new/file.txt", 2000.0),
                ("/mid/file.txt", 1500.0),
            ]
        }

        groups = strategy.analyze_groups(duplicates)

        assert len(groups) == 1
        assert groups[0].hash == "hash1"
        assert groups[0].keep_file == "/new/file.txt"
        assert "/old/file.txt" in groups[0].delete_files
        assert "/mid/file.txt" in groups[0].delete_files

    def test_tiebreaker_shorter_path(self):
        """Test shorter path is kept when mtime is equal."""
        strategy = KeepStrategy()
        duplicates = {
            "hash1": [("/a/very/long/path/to/file.txt", 1000.0), ("/short/file.txt", 1000.0)]
        }

        groups = strategy.analyze_groups(duplicates)

        assert len(groups) == 1
        assert groups[0].keep_file == "/short/file.txt"
        assert "/a/very/long/path/to/file.txt" in groups[0].delete_files

    def test_single_duplicate_pair(self):
        """Test correct identification with two duplicate files."""
        strategy = KeepStrategy()
        duplicates = {"hash1": [("/file1.txt", 1000.0), ("/file2.txt", 2000.0)]}

        groups = strategy.analyze_groups(duplicates)

        assert len(groups) == 1
        assert groups[0].keep_file == "/file2.txt"
        assert ["/file1.txt"] == groups[0].delete_files

    def test_multiple_duplicates(self):
        """Test multiple duplicate groups are processed correctly."""
        strategy = KeepStrategy()
        duplicates = {
            "hash1": [("/file1.txt", 1000.0), ("/file2.txt", 2000.0)],
            "hash2": [("/file3.txt", 3000.0), ("/file4.txt", 2500.0)],
        }

        groups = strategy.analyze_groups(duplicates)

        assert len(groups) == 2
        # First group: newest is /file2.txt
        hash1_group = next(g for g in groups if g.hash == "hash1")
        assert hash1_group.keep_file == "/file2.txt"
        # Second group: newest is /file3.txt
        hash2_group = next(g for g in groups if g.hash == "hash2")
        assert hash2_group.keep_file == "/file3.txt"

    def test_empty_input(self):
        """Test empty input returns empty list."""
        strategy = KeepStrategy()
        groups = strategy.analyze_groups({})
        assert groups == []

    def test_mtime_float_precision(self):
        """Test mtime comparison uses float precision."""
        strategy = KeepStrategy()
        duplicates = {
            "hash1": [("/file1.txt", 1700000000.123456), ("/file2.txt", 1700000000.123457)]
        }

        groups = strategy.analyze_groups(duplicates)

        assert len(groups) == 1
        assert groups[0].keep_file == "/file2.txt"
        assert "/file1.txt" in groups[0].delete_files

    def test_case_sensitive_paths(self):
        """Test path comparison is case-sensitive."""
        strategy = KeepStrategy()
        duplicates = {"hash1": [("/File.txt", 1000.0), ("/file.txt", 1000.0)]}

        groups = strategy.analyze_groups(duplicates)

        assert len(groups) == 1
        # Both have same length (9 chars), first wins due to sort stability
        assert groups[0].keep_file == "/File.txt"

    def test_single_file_in_group(self):
        """Test group with only one file (edge case)."""
        strategy = KeepStrategy()
        duplicates = {"hash1": [("/file.txt", 1000.0)]}

        groups = strategy.analyze_groups(duplicates)

        # Single file should still create a group
        assert len(groups) == 1
        assert groups[0].keep_file == "/file.txt"
        assert groups[0].delete_files == []
