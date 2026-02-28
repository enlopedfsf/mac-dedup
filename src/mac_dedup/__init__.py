"""mac-dedup: Fast duplicate file finder for macOS."""

from mac_dedup.deleter import Deleter, DeletionResult
from mac_dedup.file_type import FileType
from mac_dedup.filter import FileFilter
from mac_dedup.keep_strategy import Group, KeepStrategy
from mac_dedup.reporter import Reporter, ScanStats

__version__ = "0.1.0"

__all__ = [
    "Deleter",
    "DeletionResult",
    "FileFilter",
    "FileType",
    "Group",
    "KeepStrategy",
    "Reporter",
    "ScanStats",
]
