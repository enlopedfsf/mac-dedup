"""Hash Engine Module

Implements SHA-256 file hashing with memory-efficient chunked reading
for large files. Supports duplicate detection through hash mapping.
"""

import hashlib
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple


class HashEngine:
    """Calculate SHA-256 hashes for files with chunked reading.

    Uses 4MB chunks for files > 10MB to avoid memory issues.
    """

    CHUNK_THRESHOLD = 10 * 1024 * 1024  # 10MB
    CHUNK_SIZE = 4 * 1024 * 1024  # 4MB

    def __init__(self) -> None:
        """Initialize hash engine."""
        self._hash_cache: Dict[str, str] = {}

    def _calculate_hash(self, filepath: str) -> str:
        """Calculate SHA-256 hash for a file.

        Uses chunked reading for files > CHUNK_THRESHOLD to avoid
        loading entire file into memory.

        Args:
            filepath: Absolute path to file

        Returns:
            Hexadecimal SHA-256 hash string

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
            OSError: For other I/O errors
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {filepath}")

        # Check cache first
        if filepath in self._hash_cache:
            return self._hash_cache[filepath]

        hasher = hashlib.sha256()

        try:
            file_size = path.stat().st_size

            if file_size > self.CHUNK_THRESHOLD:
                # Chunked reading for large files
                with path.open("rb") as f:
                    while chunk := f.read(self.CHUNK_SIZE):
                        hasher.update(chunk)
            else:
                # Read small files entirely
                hasher.update(path.read_bytes())

            hash_value = hasher.hexdigest()
            self._hash_cache[filepath] = hash_value
            return hash_value

        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {filepath}")
        except OSError as e:
            raise OSError(f"Error reading file {filepath}: {e}")

    def find_duplicates(
        self, file_infos: List[Dict[str, object]]
    ) -> Dict[str, List[Tuple[str, float]]]:
        """Find duplicate files by comparing hash values.

        Args:
            file_infos: List of dicts with keys:
                - path: str (absolute file path)
                - size: int (file size in bytes)
                - mtime: float (modification timestamp)

        Returns:
            Dict mapping hash to list of (filepath, mtime) tuples.
            Only includes hashes with multiple files (duplicates).

        Raises:
            ValueError: If file_infos is invalid
        """
        if not file_infos:
            return {}

        # Build hash mapping
        hash_map: Dict[str, List[Tuple[str, float]]] = {}

        for info in file_infos:
            filepath = str(info["path"])
            mtime = float(info["mtime"])  # type: ignore[arg-type]

            try:
                file_hash = self._calculate_hash(filepath)

                if file_hash not in hash_map:
                    hash_map[file_hash] = []
                hash_map[file_hash].append((filepath, mtime))

            except (FileNotFoundError, PermissionError, OSError) as e:
                # Log error but continue processing other files
                # TODO: Add proper logging in Phase 6
                continue

        # Filter to only duplicates (hashes with > 1 file)
        duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}

        return duplicates

    def find_duplicates_with_progress(
        self,
        file_infos: List[Dict[str, object]],
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Dict[str, List[Tuple[str, float]]]:
        """Find duplicates with optional progress callback.

        Args:
            file_infos: List of file info dicts
            progress_callback: Optional callable(int) called with progress %
                               (0-100) during hashing

        Returns:
            Dict of duplicates (same as find_duplicates)
        """
        if not file_infos:
            return {}

        total_files = len(file_infos)
        hash_map: Dict[str, List[Tuple[str, float]]] = {}

        for i, info in enumerate(file_infos):
            filepath = str(info["path"])
            mtime = float(info["mtime"])  # type: ignore[arg-type]

            try:
                file_hash = self._calculate_hash(filepath)

                if file_hash not in hash_map:
                    hash_map[file_hash] = []
                hash_map[file_hash].append((filepath, mtime))

                # Update progress
                if progress_callback:
                    percentage = int((i + 1) / total_files * 100)
                    progress_callback(percentage)

            except (FileNotFoundError, PermissionError, OSError):
                continue

        duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}

        return duplicates

    def clear_cache(self) -> None:
        """Clear the internal hash cache.

        Useful for processing multiple directories separately.
        """
        self._hash_cache.clear()
