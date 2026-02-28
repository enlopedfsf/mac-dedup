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


TEXT_EXTENSIONS = [
    "txt",
    "md",
    "rtf",
    "doc",
    "docx",
    "docm",
    "pdf",
    "tex",
    "log",
    "csv",
    "json",
    "xml",
    "yaml",
    "yml",
    "ini",
    "cfg",
    "conf",
    "toml",
    "asc",
    "bib",
    "sty",
    # Microsoft Office
    "xls",
    "xlsx",
    "xlsm",
    "xlsb",
    # WPS Office
    "ppt",
    "pptx",
    "potx",
    "pps",
    "wps",
    "et",
    "ett",
]

AUDIO_EXTENSIONS = [
    "mp3",
    "m4a",
    "wav",
    "aac",
    "flac",
    "wma",
    "ogg",
    "aiff",
    "mid",
    "mka",
    "opus",
]

VIDEO_EXTENSIONS = [
    "mp4",
    "mov",
    "avi",
    "mkv",
    "webm",
    "flv",
    "wmv",
    "m4v",
    "3gp",
    "ts",
    "mts",
    "ogv",
]

ARCHIVE_EXTENSIONS = [
    "zip",
    "rar",
    "7z",
    "tar",
    "gz",
    "bz2",
    "xz",
    "lzma",
    "tar.gz",
    "tar.bz2",
    "tar.xz",
    "iso",
    "img",
    "dmg",
    "pkg",
    "jar",
    "war",
    "ear",
    "deb",
    "rpm",
    "apk",
    "ipa",
]


@pytest.mark.parametrize("ext", TEXT_EXTENSIONS)
def test_text_extensions(ext):
    """Test text document extensions."""
    assert get_type(ext) == FileType.TEXT
    assert get_type(f".{ext}") == FileType.TEXT
    assert get_type(ext.upper()) == FileType.TEXT
    assert get_type(f".{ext.upper()}") == FileType.TEXT


@pytest.mark.parametrize("ext", AUDIO_EXTENSIONS)
def test_audio_extensions(ext):
    """Test audio file extensions."""
    assert get_type(ext) == FileType.AUDIO
    assert get_type(f".{ext}") == FileType.AUDIO
    assert get_type(ext.upper()) == FileType.AUDIO
    assert get_type(f".{ext.upper()}") == FileType.AUDIO


@pytest.mark.parametrize("ext", VIDEO_EXTENSIONS)
def test_video_extensions(ext):
    """Test video file extensions."""
    assert get_type(ext) == FileType.VIDEO
    assert get_type(f".{ext}") == FileType.VIDEO
    assert get_type(ext.upper()) == FileType.VIDEO
    assert get_type(f".{ext.upper()}") == FileType.VIDEO


@pytest.mark.parametrize("ext", ARCHIVE_EXTENSIONS)
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
    assert ".xlsx" in exts
    assert ".ppt" in exts
    assert ".wps" in exts
    assert len(exts) == len(TEXT_EXTENSIONS)


def test_get_supported_extensions_audio():
    """Test get_supported_extensions() for AUDIO type."""
    exts = get_supported_extensions(FileType.AUDIO)
    assert ".mp3" in exts
    assert ".m4a" in exts
    assert ".wav" in exts
    assert ".wma" in exts
    assert ".ogg" in exts
    assert len(exts) == len(AUDIO_EXTENSIONS)


def test_get_supported_extensions_video():
    """Test get_supported_extensions() for VIDEO type."""
    exts = get_supported_extensions(FileType.VIDEO)
    assert ".mp4" in exts
    assert ".mov" in exts
    assert ".mkv" in exts
    assert ".flv" in exts
    assert ".3gp" in exts
    assert len(exts) == len(VIDEO_EXTENSIONS)


def test_get_supported_extensions_archive():
    """Test get_supported_extensions() for ARCHIVE type."""
    exts = get_supported_extensions(FileType.ARCHIVE)
    assert ".zip" in exts
    assert ".rar" in exts
    assert ".tar" in exts
    assert ".xz" in exts
    assert ".iso" in exts
    assert ".jar" in exts
    assert ".deb" in exts
    assert len(exts) == len(ARCHIVE_EXTENSIONS)


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

    video_exts = get_supported_extensions(FileType.VIDEO)
    assert video_exts == sorted(video_exts)

    archive_exts = get_supported_extensions(FileType.ARCHIVE)
    assert archive_exts == sorted(archive_exts)
