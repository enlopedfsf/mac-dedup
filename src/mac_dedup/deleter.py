"""Safe Deletion Module

Implements secure file deletion to macOS trash (~/.Trash) with
dry-run mode for previewing operations before execution.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from send2trash import send2trash  # noqa: F401
except ImportError:
    # Will be handled in __init__ with better error message
    pass


@dataclass
class DeletionResult:
    """Result of a deletion operation.

    Attributes:
        success: Whether the deletion was successful
        filepath: Absolute path to the file
        error: Error message if deletion failed (None if successful)
    """

    success: bool
    filepath: str
    error: Optional[str] = None


class Deleter:
    """Handles safe deletion of duplicate files to macOS trash.

    Supports dry-run mode for previewing operations without execution.
    """

    def __init__(self, dry_run: bool = False) -> None:
        """Initialize deleter.

        Args:
            dry_run: If True, preview deletions without executing

        Raises:
            ImportError: If send2trash is not installed
        """
        self.dry_run = dry_run

        # Verify send2trash is available
        try:
            from send2trash import send2trash  # noqa: F401, F811

            self._send2trash = send2trash
        except ImportError as e:
            raise ImportError("send2trash is required. Install with: pip install send2trash") from e

    def delete_file(self, filepath: str) -> DeletionResult:
        """Delete a single file to trash.

        Args:
            filepath: Absolute path to file to delete

        Returns:
            DeletionResult with success status and optional error message
        """
        path = Path(filepath)

        if not path.exists():
            return DeletionResult(
                success=False,
                filepath=filepath,
                error=f"File not found: {filepath}",
            )

        if not path.is_file():
            return DeletionResult(
                success=False,
                filepath=filepath,
                error=f"Path is not a file: {filepath}",
            )

        if self.dry_run:
            return DeletionResult(success=True, filepath=filepath)

        try:
            self._send2trash(str(path))
            return DeletionResult(success=True, filepath=filepath)
        except PermissionError as e:
            return DeletionResult(
                success=False,
                filepath=filepath,
                error=f"Permission denied: {e}",
            )
        except OSError as e:
            return DeletionResult(
                success=False,
                filepath=filepath,
                error=f"Failed to move to trash: {e}",
            )

    def delete_files(self, filepaths: List[str]) -> List[DeletionResult]:
        """Delete multiple files to trash.

        Args:
            filepaths: List of absolute paths to files to delete

        Returns:
            List of DeletionResult objects, one per file
        """
        return [self.delete_file(fp) for fp in filepaths]

    def delete_groups(self, groups: List["Group"]) -> Tuple[int, int, List[DeletionResult]]:
        """Delete all files marked for deletion in groups.

        Args:
            groups: List of Group objects from KeepStrategy

        Returns:
            Tuple of (success_count, failure_count, list_of_results)
        """
        all_delete_files: List[str] = []

        for group in groups:
            all_delete_files.extend(group.get_delete_files())

        results = self.delete_files(all_delete_files)

        success_count = sum(1 for r in results if r.success)
        failure_count = len(results) - success_count

        return success_count, failure_count, results

    def get_preview(self, groups: List["Group"]) -> List[str]:
        """Get preview of files that would be deleted.

        Args:
            groups: List of Group objects from KeepStrategy

        Returns:
            List of file paths that would be deleted
        """
        delete_files: List[str] = []

        for group in groups:
            delete_files.extend(group.get_delete_files())

        return delete_files


# Import Group here to avoid circular dependency
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mac_dedup.keep_strategy import Group
else:
    # Runtime import to avoid circular dependency
    class Group:  # type: ignore
        """Placeholder type hint for Group."""

        def get_delete_files(self) -> List[str]:
            """Get files to delete."""
            return []
