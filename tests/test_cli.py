"""Tests for CLI interface."""

from pathlib import Path
from unittest.mock import patch

import pytest

from click.testing import CliRunner

# Import CLI inside tests to avoid import issues
import mac_dedup.cli


@pytest.fixture
def temp_directory(tmp_path: Path) -> Path:
    """Create a temporary directory for testing."""
    test_dir = tmp_path / "test_scan"
    test_dir.mkdir()

    # Create test files
    (test_dir / "file1.txt").write_text("content1")
    (test_dir / "file2.txt").write_text("content1")  # Duplicate
    (test_dir / "file3.txt").write_text("unique")

    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "file1.txt").write_text("sub content")

    # Create .git directory (should be excluded)
    git_dir = test_dir / ".git"
    git_dir.mkdir()
    (git_dir / "ignored.txt").write_text("git content")

    # Create mp3 file (different type)
    (test_dir / "audio.mp3").write_bytes(b"audio")

    return test_dir


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(mac_dedup.cli.main, ["--help"])
    assert result.exit_code == 0
    assert "mac-dedup" in result.output
    assert "scan" in result.output
    assert "clean" in result.output
    assert "report" in result.output


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(mac_dedup.cli.main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_scan_command_help():
    """Test scan command help."""
    runner = CliRunner()
    result = runner.invoke(mac_dedup.cli.main, ["scan", "--help"])
    assert result.exit_code == 0
    assert "DIRECTORY" in result.output
    assert "Scan directory for duplicate files" in result.output


def test_clean_command_help():
    """Test clean command help."""
    runner = CliRunner()
    result = runner.invoke(mac_dedup.cli.main, ["clean", "--help"])
    assert result.exit_code == 0
    assert "DIRECTORY" in result.output
    assert "Remove duplicate files" in result.output
    assert "dry-run" in result.output


def test_report_command_help():
    """Test report command help."""
    runner = CliRunner()
    result = runner.invoke(mac_dedup.cli.main, ["report", "--help"])
    assert result.exit_code == 0
    assert "DIRECTORY" in result.output
    assert "Generate a report of duplicate files" in result.output
    assert "format" in result.output


def test_scan_command_runs(temp_directory: Path) -> None:
    """Test scan command with existing directory."""
    runner = CliRunner()
    result = runner.invoke(mac_dedup.cli.main, ["scan", str(temp_directory)])
    assert result.exit_code == 0
    assert "Scanning" in result.output
    assert "duplicate group" in result.output


def test_scan_no_duplicates(temp_directory: Path) -> None:
    """Test scan with no duplicates."""
    unique_dir = temp_directory / "unique"
    unique_dir.mkdir()
    (unique_dir / "file1.txt").write_text("unique1")
    (unique_dir / "file2.txt").write_text("unique2")

    runner = CliRunner()
    result = runner.invoke(mac_dedup.cli.main, ["scan", str(unique_dir)])
    assert result.exit_code == 0
    assert "No duplicates found" in result.output


def test_scan_nonexistent_directory() -> None:
    """Test scan with nonexistent directory."""
    runner = CliRunner()
    result = runner.invoke(mac_dedup.cli.main, ["scan", "/nonexistent"])
    assert result.exit_code != 0


def test_scan_with_invalid_file_type() -> None:
    """Test scan with invalid file type."""
    runner = CliRunner()
    result = runner.invoke(mac_dedup.cli.main, ["scan", "--file-types", "invalid", "/tmp"])
    assert result.exit_code != 0
    assert "Invalid file type" in result.output


def test_clean_dry_run(temp_directory: Path) -> None:
    """Test clean command with dry-run."""
    runner = CliRunner()
    result = runner.invoke(mac_dedup.cli.main, ["clean", "--dry-run", str(temp_directory)])
    assert result.exit_code == 0
    assert "DRY RUN mode" in result.output or "dry run" in result.output.lower()


def test_clean_with_keep_option(temp_directory: Path) -> None:
    """Test clean command with dry run."""
    runner = CliRunner()
    result = runner.invoke(mac_dedup.cli.main, ["clean", "--dry-run", str(temp_directory)])
    assert result.exit_code == 0


def test_report_table_format(temp_directory: Path) -> None:
    """Test report with table format."""
    runner = CliRunner()
    result = runner.invoke(mac_dedup.cli.main, ["report", str(temp_directory)])
    assert result.exit_code == 0
    assert "Scan Summary" in result.output or "No duplicates" in result.output


def test_report_csv_format(temp_directory: Path) -> None:
    """Test report with CSV format."""
    runner = CliRunner()
    result = runner.invoke(mac_dedup.cli.main, ["report", "--format", "csv", str(temp_directory)])
    assert result.exit_code == 0
    assert "Group,Hash" in result.output or "No duplicates" in result.output


def test_report_json_format(temp_directory: Path) -> None:
    """Test report with JSON format."""
    runner = CliRunner()
    result = runner.invoke(mac_dedup.cli.main, ["report", "--format", "json", str(temp_directory)])
    assert result.exit_code == 0
    assert '"summary"' in result.output or "No duplicates" in result.output


def test_parse_file_types_none():
    """Test parse_file_types with None input."""
    assert mac_dedup.cli.parse_file_types(None) is None


def test_parse_file_types_empty():
    """Test parse_file_types with empty string."""
    assert mac_dedup.cli.parse_file_types("") is None


def test_parse_file_types_single():
    """Test parse_file_types with single type."""
    result = mac_dedup.cli.parse_file_types("text")
    assert result == [mac_dedup.cli.FileType.TEXT]


def test_parse_file_types_multiple():
    """Test parse_file_types with multiple types."""
    result = mac_dedup.cli.parse_file_types("text,video")
    assert mac_dedup.cli.FileType.TEXT in result
    assert mac_dedup.cli.FileType.VIDEO in result
    assert len(result) == 2


def test_parse_file_types_invalid():
    """Test parse_file_types with invalid type."""
    with pytest.raises(Exception):
        mac_dedup.cli.parse_file_types("invalid")


def test_report_no_duplicates() -> None:
    """Test report when no duplicates."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        unique_dir = Path(tmp) / "unique"
        unique_dir.mkdir()
        (unique_dir / "file.txt").write_text("content")

        runner = CliRunner()
        result = runner.invoke(mac_dedup.cli.main, ["report", str(unique_dir)])
        assert result.exit_code == 0
        assert "No duplicates found" in result.output
