"""Filter Module

Implements file filtering by extension and directory exclusion.
"""

import fnmatch
from pathlib import Path
from typing import List, Set, Optional

from mac_dedup.file_type import FileType, get_supported_extensions


class FileFilter:
    """Filters files by extension and directory exclusion.

    Supports:
    - Filtering by file type (extension groups)
    - Excluding directories by pattern (.git, node_modules, etc.)
    - Combining multiple filters
    """

    # Default exclude patterns
    DEFAULT_EXCLUDE_DIRS = {
        ".git",
        ".gitignore",
        ".hg",
        ".hgignore",
        ".svn",
        "__pycache__",
        ".pytest_cache",
        ".tox",
        ".venv",
        "venv",
        "node_modules",
        ".idea",
        ".vscode",
        "dist",
        "build",
        ".mypy_cache",
        "*.egg-info",
    }

    def __init__(
        self,
        file_types: Optional[List[FileType]] = None,
        exclude_dirs: Optional[List[str]] = None,
        use_default_excludes: bool = True,
    ) -> None:
        """Initialize file filter.

        Args:
            file_types: List of file types to include (None = all)
            exclude_dirs: List of directory patterns to exclude
                        (None = use defaults)
            use_default_excludes: Whether to use default exclude patterns
        """
        self._allowed_extensions: Set[str] = set()
        if file_types:
            for ft in file_types:
                self._allowed_extensions.update(get_supported_extensions(ft))

        self._exclude_patterns: Set[str] = set()
        if exclude_dirs is not None:
            self._exclude_patterns.update(exclude_dirs)
        elif use_default_excludes:
            self._exclude_patterns = self.DEFAULT_EXCLUDE_DIRS.copy()

        # Track if filters were explicitly set
        self._explicit_filters = file_types is not None or exclude_dirs is not None

    def should_include_file(self, filepath: str) -> bool:
        """Check if file should be included based on filters.

        Args:
            filepath: Absolute path to file

        Returns:
            True if file passes all filters
        """
        path = Path(filepath)

        # Check extension filter
        if self._allowed_extensions:
            ext = path.suffix.lower()
            if ext not in self._allowed_extensions:
                return False

        # Check directory exclusion
        for parent in path.parents:
            parent_name = parent.name
            for pattern in self._exclude_patterns:
                if fnmatch.fnmatch(parent_name, pattern):
                    return False

        return True

    def filter_files(self, filepaths: List[str]) -> List[str]:
        """Filter a list of file paths.

        Args:
            filepaths: List of absolute file paths

        Returns:
            Filtered list of paths
        """
        return [fp for fp in filepaths if self.should_include_file(fp)]

    def add_exclude_pattern(self, pattern: str) -> None:
        """Add an additional exclude directory pattern.

        Args:
            pattern: Directory pattern to exclude
        """
        self._exclude_patterns.add(pattern)

    def set_file_types(self, file_types: List[FileType]) -> None:
        """Set the allowed file types.

        Args:
            file_types: List of file types to include
        """
        self._allowed_extensions.clear()
        for ft in file_types:
            self._allowed_extensions.update(get_supported_extensions(ft))

    def is_filtering_active(self) -> bool:
        """Check if any filters are active.

        Returns:
            True if extension or directory filtering is enabled
        """
        return getattr(self, "_explicit_filters", False)
