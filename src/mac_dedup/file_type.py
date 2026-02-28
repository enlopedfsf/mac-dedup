"""File type detection module for classifying files by extension.

This module provides a type-safe enum-based API for determining file types
based on their extensions. It supports text documents, audio files, video files,
and archives with case-insensitive matching.
"""

from enum import Enum
from typing import List


class FileType(Enum):
    """Enumeration of supported file types."""

    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    ARCHIVE = "archive"
    UNKNOWN = "unknown"


# Extension mapping dictionary (lowercase extensions as keys)
_EXTENSION_MAP: dict[str, FileType] = {
    # Text documents
    "txt": FileType.TEXT,
    "md": FileType.TEXT,
    "rtf": FileType.TEXT,
    "doc": FileType.TEXT,
    "docx": FileType.TEXT,
    "pdf": FileType.TEXT,
    # Audio files
    "mp3": FileType.AUDIO,
    "m4a": FileType.AUDIO,
    "wav": FileType.AUDIO,
    "aac": FileType.AUDIO,
    "flac": FileType.AUDIO,
    # Video files
    "mp4": FileType.VIDEO,
    "mov": FileType.VIDEO,
    "avi": FileType.VIDEO,
    "mkv": FileType.VIDEO,
    "webm": FileType.VIDEO,
    # Archives
    "zip": FileType.ARCHIVE,
    "rar": FileType.ARCHIVE,
    "7z": FileType.ARCHIVE,
    "tar": FileType.ARCHIVE,
    "gz": FileType.ARCHIVE,
    "bz2": FileType.ARCHIVE,
    "dmg": FileType.ARCHIVE,
    "pkg": FileType.ARCHIVE,
}


def get_type(extension: str) -> FileType:
    """Get the FileType for a given file extension.

    Args:
        extension: File extension with or without leading dot (e.g., ".pdf" or "pdf")

    Returns:
        FileType enum value corresponding to the extension
        FileType.UNKNOWN if extension is not recognized

    Examples:
        >>> get_type("pdf")
        <FileType.TEXT: 'text'>
        >>> get_type(".mp3")
        <FileType.AUDIO: 'audio'>
        >>> get_type("xyz")
        <FileType.UNKNOWN: 'unknown'>
        >>> get_type("PDF")  # Case-insensitive
        <FileType.TEXT: 'text'>
    """
    # Strip leading dot if present
    if extension.startswith("."):
        extension = extension[1:]

    # Convert to lowercase for case-insensitive matching
    extension = extension.lower()

    # Look up in extension mapping
    return _EXTENSION_MAP.get(extension, FileType.UNKNOWN)


def is_supported(extension: str) -> bool:
    """Check if a file extension is supported.

    Args:
        extension: File extension with or without leading dot

    Returns:
        True if extension is recognized, False otherwise

    Examples:
        >>> is_supported("pdf")
        True
        >>> is_supported("xyz")
        False
        >>> is_supported(".mp3")
        True
    """
    return get_type(extension) != FileType.UNKNOWN


def get_supported_extensions(file_type: FileType) -> List[str]:
    """Get all extensions for a given file type.

    Args:
        file_type: FileType enum value

    Returns:
        List of extensions with leading dots (e.g., [".pdf", ".txt"])
        Empty list for FileType.UNKNOWN

    Examples:
        >>> get_supported_extensions(FileType.TEXT)
        ['.txt', '.md', '.rtf', '.doc', '.docx', '.pdf']
        >>> get_supported_extensions(FileType.AUDIO)
        ['.mp3', '.m4a', '.wav', '.aac', '.flac']
        >>> get_supported_extensions(FileType.UNKNOWN)
        []
    """
    if file_type == FileType.UNKNOWN:
        return []

    extensions = [ext for ext, ft in _EXTENSION_MAP.items() if ft == file_type]
    # Add leading dots and sort for consistency
    return sorted([f".{ext}" for ext in extensions])
