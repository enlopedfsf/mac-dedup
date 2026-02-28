"""Tests for Reporting module."""

from io import StringIO
from pathlib import Path

import pytest

from mac_dedup.keep_strategy import Group
from mac_dedup.reporter import Reporter, ScanStats


class TestScanStats:
    """Test ScanStats dataclass."""

    def test_default_stats(self) -> None:
        """Test default stats initialization."""
        stats = ScanStats()

        assert stats.total_files_scanned == 0
        assert stats.duplicate_groups_found == 0
        assert stats.total_duplicate_files == 0
        assert stats.files_to_delete == 0
        assert stats.space_to_recover == 0

    def test_get_space_human_bytes(self) -> None:
        """Test human-readable format for bytes."""
        stats = ScanStats(space_to_recover=512)
        assert stats.get_space_human() == "512.00 B"

    def test_get_space_human_kb(self) -> None:
        """Test human-readable format for kilobytes."""
        stats = ScanStats(space_to_recover=2 * 1024)
        assert stats.get_space_human() == "2.00 KB"

    def test_get_space_human_mb(self) -> None:
        """Test human-readable format for megabytes."""
        stats = ScanStats(space_to_recover=5 * 1024 * 1024)
        assert stats.get_space_human() == "5.00 MB"

    def test_get_space_human_gb(self) -> None:
        """Test human-readable format for gigabytes."""
        stats = ScanStats(space_to_recover=1.5 * 1024 * 1024 * 1024)
        assert stats.get_space_human() == "1.50 GB"

    def test_get_space_human_tb(self) -> None:
        """Test human-readable format for terabytes."""
        stats = ScanStats(space_to_recover=2 * 1024 * 1024 * 1024 * 1024)
        assert stats.get_space_human() == "2.00 TB"


class TestReporter:
    """Test Reporter class."""

    def test_init(self) -> None:
        """Test reporter initialization."""
        reporter = Reporter()
        assert reporter is not None

    def test_calculate_stats_empty(self) -> None:
        """Test calculating stats with no groups."""
        reporter = Reporter()
        stats = reporter.calculate_stats([], total_files_scanned=100)

        assert stats.total_files_scanned == 100
        assert stats.duplicate_groups_found == 0
        assert stats.total_duplicate_files == 0
        assert stats.files_to_delete == 0
        assert stats.space_to_recover == 0

    def test_calculate_stats_with_groups(self, tmp_path: Path) -> None:
        """Test calculating stats with duplicate groups."""
        # Create a test file for size calculation
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        groups = [
            Group(
                hash="abc123",
                keep_file=str(test_file),
                delete_files=["/delete1.txt", "/delete2.txt"],
            ),
            Group(
                hash="def456",
                keep_file="/keep2.txt",
                delete_files=["/delete3.txt"],
            ),
        ]

        reporter = Reporter()
        stats = reporter.calculate_stats(groups, total_files_scanned=10)

        assert stats.total_files_scanned == 10
        assert stats.duplicate_groups_found == 2
        # total_dup_files = (1 keep + 2 delete) + (1 keep + 1 delete) = 5
        assert stats.total_duplicate_files == 5
        assert stats.files_to_delete == 3  # 2 + 1 files to delete
        # Space = size of keep_file * number of deletes
        # First group: 12 bytes * 2 deletes = 24 bytes
        # Second group: keep file doesn't exist = 0 bytes
        assert stats.space_to_recover == test_file.stat().st_size * 2

    def test_generate_table_empty(self) -> None:
        """Test generating table with no groups."""
        reporter = Reporter()
        table = reporter.generate_table([])

        assert "No duplicates found" in table
        assert "Total Files Scanned: 0" in table

    def test_generate_table_with_groups(self, tmp_path: Path) -> None:
        """Test generating table with duplicate groups."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        groups = [
            Group(
                hash="abc123",
                keep_file=str(test_file),
                delete_files=["/delete1.txt"],
            ),
        ]

        reporter = Reporter()
        table = reporter.generate_table(groups)

        assert "Duplicate Groups Found: 1" in table
        assert "abc123" in table
        assert "KEEP:" in table
        assert "DELETE:" in table
        assert str(test_file) in table

    def test_generate_csv_empty(self) -> None:
        """Test generating CSV with no groups."""
        reporter = Reporter()
        csv = reporter.generate_csv([])

        assert "Group,Hash,Action,File Path" in csv

    def test_generate_csv_with_groups(self) -> None:
        """Test generating CSV with duplicate groups."""
        groups = [
            Group(
                hash="abc123",
                keep_file="/keep/file.txt",
                delete_files=["/delete/file1.txt", "/delete/file2.txt"],
            ),
        ]

        reporter = Reporter()
        csv_output = reporter.generate_csv(groups)

        lines = csv_output.strip().split("\n")
        assert len(lines) == 4  # Header + 3 data rows
        assert "1,abc123,KEEP,/keep/file.txt" in lines[1]
        assert "1,abc123,DELETE,/delete/file1.txt" in lines[2]
        assert "1,abc123,DELETE,/delete/file2.txt" in lines[3]

    def test_generate_json_empty(self) -> None:
        """Test generating JSON with no groups."""
        reporter = Reporter()
        json_str = reporter.generate_json([])

        import json

        data = json.loads(json_str)
        assert "summary" in data
        assert data["summary"]["duplicate_groups_found"] == 0
        assert data["groups"] == []

    def test_generate_json_with_groups(self) -> None:
        """Test generating JSON with duplicate groups."""
        groups = [
            Group(
                hash="abc123",
                keep_file="/keep/file.txt",
                delete_files=["/delete/file.txt"],
            ),
        ]

        reporter = Reporter()
        json_str = reporter.generate_json(groups, total_files_scanned=100)

        import json

        data = json.loads(json_str)
        assert data["summary"]["total_files_scanned"] == 100
        assert data["summary"]["duplicate_groups_found"] == 1
        assert len(data["groups"]) == 1
        assert data["groups"][0]["hash"] == "abc123"
        assert data["groups"][0]["keep_file"] == "/keep/file.txt"
        assert data["groups"][0]["delete_files"] == ["/delete/file.txt"]

    def test_save_csv(self, tmp_path: Path) -> None:
        """Test saving CSV to file."""
        groups = [
            Group(
                hash="abc123",
                keep_file="/keep/file.txt",
                delete_files=["/delete/file.txt"],
            ),
        ]

        reporter = Reporter()
        output_file = tmp_path / "report.csv"
        reporter.save_csv(groups, str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert "Group,Hash,Action,File Path" in content

    def test_save_json(self, tmp_path: Path) -> None:
        """Test saving JSON to file."""
        groups = [
            Group(
                hash="abc123",
                keep_file="/keep/file.txt",
                delete_files=["/delete/file.txt"],
            ),
        ]

        reporter = Reporter()
        output_file = tmp_path / "report.json"
        reporter.save_json(groups, str(output_file), total_files_scanned=50)

        assert output_file.exists()

        import json

        data = json.loads(output_file.read_text())
        assert data["summary"]["total_files_scanned"] == 50

    def test_print_summary(self, capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
        """Test printing summary to stdout."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        groups = [
            Group(
                hash="abc123",
                keep_file=str(test_file),
                delete_files=["/delete/file.txt"],
            ),
        ]

        reporter = Reporter()
        reporter.print_summary(groups, total_files_scanned=100)

        captured = capsys.readouterr()
        assert "Scan Summary" in captured.out
        assert "Files Scanned:    100" in captured.out
        assert "Duplicate Groups:  1" in captured.out
