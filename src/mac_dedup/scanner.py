"""Recursive directory scanner with progress display."""

import os
import time
from pathlib import Path
from typing import Dict, Generator, List, Optional

from mac_dedup.filter import FileFilter


class DirectoryScanner:
    """Recursively scan directories with real-time progress display."""

    def __init__(
        self,
        root_dir: str,
        file_types: Optional[List] = None,
        exclude_dirs: Optional[List[str]] = None,
        use_default_excludes: bool = True,
    ) -> None:
        """Initialize scanner with root directory and optional filters.

        Args:
            root_dir: Absolute path to directory to scan
            file_types: List of file types to include (None = all)
            exclude_dirs: List of directory patterns to exclude
            use_default_excludes: Whether to use default exclude patterns

        Raises:
            ValueError: If root_dir doesn't exist or isn't a directory
        """
        self.root_dir = Path(root_dir).resolve()
        if not self.root_dir.exists():
            raise ValueError(f"Directory does not exist: {root_dir}")
        if not self.root_dir.is_dir():
            raise ValueError(f"Path is not a directory: {root_dir}")

        self._total_files = 0
        self._processed_files = 0
        self._skipped_symlinks = 0
        self._errors = 0
        self._current_dir = ""

        # Initialize file filter
        self._filter = FileFilter(
            file_types=file_types,
            exclude_dirs=exclude_dirs,
            use_default_excludes=use_default_excludes,
        )

    def _estimate_total(self) -> int:
        """Estimate total files for progress calculation.

        Returns:
            Estimated number of regular files
        """
        count = 0
        for root, dirs, files in os.walk(self.root_dir):
            count += len(files)
        return count

    def _get_progress_bar(self, percentage: int) -> str:
        """Generate progress bar string.

        Args:
            percentage: Progress percentage (0-100)

        Returns:
            Progress bar string in format [███░░] 45%
        """
        filled = percentage // 10  # 10 blocks total
        empty = 10 - filled
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {percentage}%"

    def _update_progress(self, start_time: float) -> None:
        """Update and display progress.

        Args:
            start_time: Time when scan started (for 1-second updates)
        """
        # Update every 100 files or every second
        self._processed_files += 1

        should_update = self._processed_files % 100 == 0 or time.time() - start_time >= 1.0

        if should_update and self._total_files > 0:
            percentage = int((self._processed_files / self._total_files) * 100)
            print(
                f"\r{self._get_progress_bar(percentage)} "
                f"Files: {self._processed_files}/{self._total_files} "
                f"Dir: {self._current_dir}",
                end="",
                flush=True,
            )

    def scan(self) -> Generator[Dict[str, object], None, Dict[str, int]]:
        """Scan directory tree and yield file information.

        Yields:
            Dict with keys:
                - path: str (absolute file path)
                - size: int (file size in bytes)
                - mtime: float (modification timestamp)

        Returns:
            Summary dict with keys:
                - total_files: int
                - errors: int
                - skipped_symlinks: int

        Raises:
            OSError: If root directory cannot be accessed
        """
        self._total_files = self._estimate_total()
        start_time = time.time()

        print(f"\nScanning: {self.root_dir}")
        print(f"Estimated files: {self._total_files}\n")

        try:
            for root, dirs, files in os.walk(self.root_dir):
                self._current_dir = str(Path(root).relative_to(self.root_dir))

                for filename in files:
                    filepath = Path(root) / filename

                    # Skip symbolic links
                    if filepath.is_symlink():
                        self._skipped_symlinks += 1
                        continue

                    # Apply file filter
                    if self._filter.is_filtering_active():
                        if not self._filter.should_include_file(str(filepath)):
                            continue

                    try:
                        stat = filepath.stat()
                        yield {
                            "path": str(filepath),
                            "size": stat.st_size,
                            "mtime": stat.st_mtime,
                        }
                        self._update_progress(start_time)

                    except (PermissionError, OSError) as e:
                        self._errors += 1
                        # Continue scanning other files
                        continue

        except (PermissionError, OSError) as e:
            raise OSError(f"Cannot scan directory {self.root_dir}: {e}")

        # Final progress update
        print()  # New line after progress bar
        print(f"\nScan complete!")
        print(f"Files processed: {self._processed_files}")
        print(f"Skipped symlinks: {self._skipped_symlinks}")
        print(f"Errors: {self._errors}")

        return {
            "total_files": self._processed_files,
            "errors": self._errors,
            "skipped_symlinks": self._skipped_symlinks,
        }
