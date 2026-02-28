"""mac-dedup: Fast duplicate file finder for macOS."""

from mac_dedup.file_type import FileType
from mac_dedup.keep_strategy import Group, KeepStrategy

__version__ = "0.1.0"

__all__ = ["FileType", "Group", "KeepStrategy"]
