"""Tests for file type detection module."""

import pytest
from mac_dedup.file_type import FileType, get_type, is_supported, get_supported_extensions


def test_filetype_enum_values():
    """Test that all FileType enum values exist."""
    assert FileType.TEXT
    assert FileType.AUDIO
    assert FileType.VIDEO
    assert FileType.ARCHIVE
    assert FileType.UNKNOWN


@pytest.mark.parametrize("ext", ["txt", "md", "rtf", "doc", "docx", "pdf"])
def test_text_extensions(ext):
    """Test text document extensions."""
    assert get_type(ext) == FileType.TEXT
    assert get_type(f".{ext}") == FileType.TEXT
    assert get_type(ext.upper()) == FileType.TEXT
    assert get_type(f".{ext.upper()}") == FileType.TEXT


@pytest.mark.parametrize("ext", ["mp3", "m4a", "wav", "aac", "flac"])
def test_audio_extensions(ext):
    """Test audio file extensions."""
    assert get_type(ext) == FileType.AUDIO
    assert get_type(f".{ext}") == FileType.AUDIO
    assert get_type(ext.upper()) == FileType.AUDIO
    assert get_type(f".{ext.upper()}") == FileType.AUDIO


@pytest.mark.parametrize("ext", ["mp4", "mov", "avi", "mkv", "webm"])
def test_video_extensions(ext):
    """Test video file extensions."""
    assert get_type(ext) == FileType.VIDEO
    assert get_type(f".{ext}") == FileType.VIDEO
    assert get_type(ext.upper()) == FileType.VIDEO
    assert get_type(f".{ext.upper()}") == FileType.VIDEO


@pytest.mark.parametrize("ext", ["zip", "rar", "7z", "tar", "gz", "bz2", "dmg", "pkg"])
def test_archive_extensions(ext):
    """Test archive extensions."""
    assert get_type(ext) == FileType.ARCHIVE
    assert get_type(f".{ext}") == FileType.ARCHIVE
    assert get_type(ext.upper()) == FileType.ARCHIVE
    assert get_type(f".{ext.upper()}") == FileType.ARCHIVE


def test_unknown_extensions():
    """Test unknown extension handling."""
    assert get_type("xyz") == FileType.UNKNOWN
    assert get_type("") == FileType.UNKNOWN
    assert get_type("   ") == FileType.UNKNOWN
    assert get_type(".xyz") == FileType.UNKNOWN


def test_is_supported_known():
    """Test is_supported() for known extensions."""
    assert is_supported("pdf") is True
    assert is_supported("mp3") is True
    assert is_supported("mp4") is True
    assert is_supported("zip") is True
    assert is_supported(".pdf") is True
    assert is_supported("PDF") is True


def test_is_supported_unknown():
    """Test is_supported() for unknown extensions."""
    assert is_supported("xyz") is False
    assert is_supported("") is False
    assert is_supported(".xyz") is False


def test_get_supported_extensions_text():
    """Test get_supported_extensions() for TEXT type."""
    exts = get_supported_extensions(FileType.TEXT)
    assert ".pdf" in exts
    assert ".txt" in exts
    assert ".md" in exts
    assert ".doc" in exts
    assert ".docx" in exts
    assert ".rtf" in exts
    assert len(exts) == 6


def test_get_supported_extensions_audio():
    """Test get_supported_extensions() for AUDIO type."""
    exts = get_supported_extensions(FileType.AUDIO)
    assert ".mp3" in exts
    assert ".m4a" in exts
    assert ".wav" in exts
    assert ".aac" in exts
    assert ".flac" in exts
    assert len(exts) == 5


def test_get_supported_extensions_video():
    """Test get_supported_extensions() for VIDEO type."""
    exts = get_supported_extensions(FileType.VIDEO)
    assert ".mp4" in exts
    assert ".mov" in exts
    assert ".avi" in exts
    assert ".mkv" in exts
    assert ".webm" in exts
    assert len(exts) == 5


def test_get_supported_extensions_archive():
    """Test get_supported_extensions() for ARCHIVE type."""
    exts = get_supported_extensions(FileType.ARCHIVE)
    assert ".zip" in exts
    assert ".rar" in exts
    assert ".7z" in exts
    assert ".tar" in exts
    assert ".gz" in exts
    assert ".bz2" in exts
    assert ".dmg" in exts
    assert ".pkg" in exts
    assert len(exts) == 8


def test_get_supported_extensions_unknown():
    """Test get_supported_extensions() for UNKNOWN type."""
    exts = get_supported_extensions(FileType.UNKNOWN)
    assert exts == []


def test_extensions_are_sorted():
    """Test that get_supported_extensions() returns sorted lists."""
    text_exts = get_supported_extensions(FileType.TEXT)
    assert text_exts == sorted(text_exts)

    audio_exts = get_supported_extensions(FileType.AUDIO)
    assert audio_exts == sorted(audio_exts)
