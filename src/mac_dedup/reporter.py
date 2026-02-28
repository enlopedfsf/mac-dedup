"""Reporting Module

Generates comprehensive duplicate file reports with statistics in multiple
formats: table, CSV, and JSON.
"""

import csv
import json
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional

from mac_dedup.keep_strategy import Group


@dataclass
class ScanStats:
    """Statistics for a duplicate scan operation.

    Attributes:
        total_files_scanned: Total number of files processed
        duplicate_groups_found: Number of duplicate groups found
        total_duplicate_files: Total number of duplicate files (all copies)
        files_to_delete: Number of files marked for deletion
        space_to_recover: Total bytes that can be recovered
    """

    total_files_scanned: int = 0
    duplicate_groups_found: int = 0
    total_duplicate_files: int = 0
    files_to_delete: int = 0
    space_to_recover: int = 0

    def get_space_human(self) -> str:
        """Get space to recover in human-readable format.

        Returns:
            Human-readable string (e.g., "1.23 GB")
        """
        bytes_size: float = float(self.space_to_recover)

        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"


class Reporter:
    """Generates duplicate file reports in multiple formats.

    Supports table, CSV, and JSON output formats.
    """

    def __init__(self) -> None:
        """Initialize reporter."""
        pass

    def calculate_stats(
        self,
        groups: List[Group],
        total_files_scanned: int,
    ) -> ScanStats:
        """Calculate statistics from duplicate groups.

        Args:
            groups: List of Group objects from KeepStrategy
            total_files_scanned: Total number of files scanned

        Returns:
            ScanStats with calculated statistics
        """
        if not groups:
            return ScanStats(total_files_scanned=total_files_scanned)

        total_dup_files = sum(len(g.delete_files) + 1 for g in groups)
        files_to_delete = sum(len(g.delete_files) for g in groups)

        # Calculate recoverable space
        space_to_recover = 0
        for group in groups:
            keep_file = Path(group.keep_file)
            if keep_file.exists():
                space_to_recover += keep_file.stat().st_size * len(group.delete_files)

        return ScanStats(
            total_files_scanned=total_files_scanned,
            duplicate_groups_found=len(groups),
            total_duplicate_files=total_dup_files,
            files_to_delete=files_to_delete,
            space_to_recover=space_to_recover,
        )

    def generate_table(
        self,
        groups: List[Group],
        stats: Optional[ScanStats] = None,
    ) -> str:
        """Generate a formatted table report.

        Args:
            groups: List of Group objects
            stats: Optional ScanStats (will calculate if None)

        Returns:
            Formatted table as string
        """
        if stats is None:
            stats = self.calculate_stats(groups, 0)

        output = StringIO()

        # Print statistics header
        output.write("=" * 80)
        output.write("\n")
        output.write(f"Total Files Scanned: {stats.total_files_scanned}\n")
        output.write(f"Duplicate Groups Found: {stats.duplicate_groups_found}\n")
        output.write(f"Total Duplicate Files: {stats.total_duplicate_files}\n")
        output.write(f"Files to Delete: {stats.files_to_delete}\n")
        output.write(f"Space to Recover: {stats.get_space_human()}\n")
        output.write("=" * 80)
        output.write("\n\n")

        # Print duplicate groups
        if not groups:
            output.write("No duplicates found.\n")
            return output.getvalue()

        for i, group in enumerate(groups, 1):
            output.write(f"[{i}] Hash: {group.hash[:16]}...\n")
            output.write(f"    KEEP: {group.keep_file}\n")

            for del_file in group.delete_files:
                output.write(f"    DELETE: {del_file}\n")

            output.write("\n")

        return output.getvalue()

    def generate_csv(self, groups: List[Group]) -> str:
        """Generate CSV report.

        Args:
            groups: List of Group objects

        Returns:
            CSV formatted string
        """
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Group", "Hash", "Action", "File Path"])

        # Write data
        for i, group in enumerate(groups, 1):
            # Keep file
            writer.writerow([i, group.hash, "KEEP", group.keep_file])

            # Delete files
            for del_file in group.delete_files:
                writer.writerow([i, group.hash, "DELETE", del_file])

        return output.getvalue()

    def generate_json(
        self,
        groups: List[Group],
        stats: Optional[ScanStats] = None,
        total_files_scanned: int = 0,
    ) -> str:
        """Generate JSON report.

        Args:
            groups: List of Group objects
            stats: Optional ScanStats (will calculate if None)
            total_files_scanned: Total files scanned for stats calculation

        Returns:
            JSON formatted string
        """
        if stats is None:
            stats = self.calculate_stats(groups, total_files_scanned)

        # Build groups data
        groups_data = []
        for group in groups:
            groups_data.append(
                {
                    "hash": group.hash,
                    "keep_file": group.keep_file,
                    "delete_files": group.delete_files,
                }
            )

        # Build report
        report = {
            "summary": {
                "total_files_scanned": stats.total_files_scanned,
                "duplicate_groups_found": stats.duplicate_groups_found,
                "total_duplicate_files": stats.total_duplicate_files,
                "files_to_delete": stats.files_to_delete,
                "space_to_recover_bytes": stats.space_to_recover,
                "space_to_recover_human": stats.get_space_human(),
            },
            "groups": groups_data,
        }

        return json.dumps(report, indent=2)

    def save_csv(self, groups: List[Group], filepath: str) -> None:
        """Save CSV report to file.

        Args:
            groups: List of Group objects
            filepath: Path where to save the CSV file
        """
        csv_content = self.generate_csv(groups)
        Path(filepath).write_text(csv_content, encoding="utf-8")

    def save_json(
        self,
        groups: List[Group],
        filepath: str,
        total_files_scanned: int = 0,
    ) -> None:
        """Save JSON report to file.

        Args:
            groups: List of Group objects
            filepath: Path where to save the JSON file
            total_files_scanned: Total files scanned for stats calculation
        """
        json_content = self.generate_json(groups, total_files_scanned=total_files_scanned)
        Path(filepath).write_text(json_content, encoding="utf-8")

    def print_summary(self, groups: List[Group], total_files_scanned: int) -> None:
        """Print a concise summary to stdout.

        Args:
            groups: List of Group objects
            total_files_scanned: Total files scanned
        """
        stats = self.calculate_stats(groups, total_files_scanned)

        print(f"\n{'=' * 50}")
        print(f"Scan Summary")
        print(f"{'=' * 50}")
        print(f"Files Scanned:    {stats.total_files_scanned:,}")
        print(f"Duplicate Groups:  {stats.duplicate_groups_found:,}")
        print(f"Duplicate Files:   {stats.total_duplicate_files:,}")
        print(f"Files to Delete:  {stats.files_to_delete:,}")
        print(f"Space to Recover:  {stats.get_space_human()}")
        print(f"{'=' * 50}\n")
