"""Keep Strategy Module

Implements decision logic for which duplicate file to keep based on
modification time and path length. Provides clear keep/delete identification.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict


@dataclass
class Group:
    """Represents a group of duplicate files with keep/delete decision.

    Attributes:
        hash: SHA-256 hash value for the group
        keep_file: Absolute path to file that should be kept
        delete_files: List of absolute paths to files that should be deleted
    """

    hash: str
    keep_file: str
    delete_files: List[str]

    def get_keep_file(self) -> str:
        """Get the file path to keep.

        Returns:
            Absolute path to file marked for preservation
        """
        return self.keep_file

    def get_delete_files(self) -> List[str]:
        """Get the file paths to delete.

        Returns:
            List of absolute paths to files marked for deletion
        """
        return self.delete_files


class KeepStrategy:
    """Implements keep/delete logic for duplicate files.

    Decisions based on:
    1. Modification time (newest first)
    2. Path length tiebreaker (shorter preferred)
    """

    def __init__(self) -> None:
        """Initialize keep strategy."""
        pass

    def analyze_groups(self, duplicates: Dict[str, List[Tuple[str, float]]]) -> List[Group]:
        """Analyze duplicate files and determine keep/delete assignments.

        Args:
            duplicates: Dict mapping hash to list of (filepath, mtime) tuples.
                      Typically from HashEngine.find_duplicates()

        Returns:
            List of Group objects with keep_file and delete_files assigned

        Sorting logic:
            - Primary: Modification time (newest first)
            - Secondary: Path length (shorter preferred for ties)
        """
        if not duplicates:
            return []

        groups: List[Group] = []

        for file_hash, files in duplicates.items():
            # Sort by mtime descending, then path length ascending
            # (-mtime for descending, len(path) for ascending)
            sorted_files = sorted(files, key=lambda x: (-x[1], len(x[0])))

            # First file is newest (or shortest path on tie)
            keep_file = sorted_files[0][0]

            # Remaining files are to be deleted
            delete_files = [filepath for filepath, _ in sorted_files[1:]]

            group = Group(hash=file_hash, keep_file=keep_file, delete_files=delete_files)
            groups.append(group)

        return groups
