"""Tests for CLI interface."""

from pathlib import Path

from click.testing import CliRunner

from mac_dedup.cli import main


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "mac-dedup" in result.output
    assert "scan" in result.output
    assert "clean" in result.output
    assert "report" in result.output


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_scan_command_help():
    """Test scan command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["scan", "--help"])
    assert result.exit_code == 0
    assert "DIRECTORY" in result.output
    assert "Scan directory for duplicate files" in result.output


def test_clean_command_help():
    """Test clean command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["clean", "--help"])
    assert result.exit_code == 0
    assert "DIRECTORY" in result.output
    assert "Remove duplicate files" in result.output
    assert "dry-run" in result.output


def test_report_command_help():
    """Test report command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["report", "--help"])
    assert result.exit_code == 0
    assert "DIRECTORY" in result.output
    assert "Generate report" in result.output


def test_scan_command_runs(temp_directory: Path):
    """Test scan command with existing directory."""
    runner = CliRunner()
    result = runner.invoke(main, ["scan", str(temp_directory)])
    assert result.exit_code == 0
    assert "Scanning" in result.output
