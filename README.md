# mac-dedup

Fast duplicate file finder for macOS.

Find and safely remove duplicate files from your directories with CLI tools.

## Features

- **Fast scanning** - Recursive directory traversal with progress display
- **SHA-256 hashing** - Accurate duplicate detection using cryptographic hashes
- **Safe deletion** - Moves files to macOS Trash (not permanent delete)
- **Dry-run mode** - Preview deletions before executing
- **Type filtering** - Scan specific file types (text, audio, video, archive)
- **Directory exclusion** - Skip `.git`, `node_modules`, and other common directories
- **Multiple report formats** - Table, CSV, or JSON output
- **Intelligent keep strategy** - Keeps newest file in each duplicate group

## Installation

```bash
# Install from source
pip install .

# Development mode with testing tools
pip install -e ".[dev]"
```

## Usage

### Basic Commands

```bash
# Show help
mac-dedup --help

# Scan directory for duplicates
mac-dedup scan /path/to/directory

# Remove duplicate files (with confirmation)
mac-dedup clean /path/to/directory

# Preview deletions without actually deleting
mac-dedup clean --dry-run /path/to/directory

# Remove duplicates without confirmation (for automation)
mac-dedup clean --yes /path/to/directory

# Generate a detailed report
mac-dedup report /path/to/directory
```

### Advanced Options

#### Scan Command

```bash
# Filter by file type (text, audio, video, archive)
mac-dedup scan --file-types text,audio /path/to/dir

# Exclude specific directories
mac-dedup scan --exclude .git --exclude node_modules /path/to/dir

# Don't use default exclude patterns
mac-dedup scan --no-include-defaults /path/to/dir
```

Supported file types:
- `text` - `.txt`, `.md`, `.rtf`, `.doc`, `.docx`, `.pdf`, `.tex`, `.log`, `.csv`, `.json`, `.xml`, `.yaml`, `.yml`, `.ini`, `.cfg`, `.conf`, `.toml`, `.asc`, `.bib`, `.sty`, `.xls`, `.xlsx`, `.xlsm`, `.xlsb`, `.ppt`, `.pptx`, `.potx`, `.pps`, `.wps`, `.et`, `.ett`
- `audio` - `.mp3`, `.m4a`, `.wav`, `.aac`, `.flac`, `.wma`, `.ogg`, `.aiff`, `.mid`, `.mka`, `.opus`
- `video` - `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.flv`, `.wmv`, `.m4v`, `.3gp`, `.ts`, `.mts`, `.ogv`
- `archive` - `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`, `.xz`, `.lzma`, `.tar.gz`, `.tar.bz2`, `.tar.xz`, `.iso`, `.img`, `.dmg`, `.pkg`, `.jar`, `.war`, `.ear`, `.deb`, `.rpm`, `.apk`, `.ipa`

#### Clean Command

```bash
# Dry run to see what would be deleted
mac-dedup clean --dry-run /path/to/directory

# Remove duplicates without confirmation (for automation)
mac-dedup clean --yes /path/to/directory

# Combine with filters and skip confirmation
mac-dedup clean --yes --file-types video /Movies
```

**Keep Strategy**: The newest file in each duplicate group is automatically kept.

#### Report Command

```bash
# Table format (default)
mac-dedup report /path/to/directory

# CSV format
mac-dedup report --format csv /path/to/directory

# JSON format
mac-dedup report --format json /path/to/directory

# Combine with filters
mac-dedup report --file-types text --exclude .git --format json /path/to/dir
```

### Example Output

```
Scanning: /Users/apple/Documents
Estimated files: 150

[████████░░] 80% Files: 120/150 Dir: photos

Found 2 potential duplicate group(s).
Hashing files...

Found 1 duplicate group(s):

  Hash: a3f5e2c0b9a8d7...
    - /Users/apple/Documents/photo_copy.jpg (2.45 MB)
    - /Users/apple/Documents/photo.jpg (2.45 MB)
```

## How It Works

1. **Scan** - Recursively walks directory tree, collecting file metadata
2. **Size grouping** - Groups files by size (only same-size files can be duplicates)
3. **Hashing** - Calculates SHA-256 hash for each file in potential duplicate groups
4. **Detection** - Files with identical hashes are true duplicates
5. **Strategy** - Applies keep strategy (newest file is kept)
6. **Deletion** - Moves duplicates to macOS Trash (reversible)

## Default Excluded Directories

The following directories are automatically excluded (can be disabled with `--no-include-defaults`):

- `.git`, `.hg`, `.svn` - Version control
- `__pycache__`, `.pytest_cache`, `.tox`, `.mypy_cache` - Python
- `.venv`, `venv` - Virtual environments
- `node_modules` - Node.js
- `.idea`, `.vscode` - IDE caches
- `dist`, `build`, `*.egg-info` - Build artifacts

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Format code
black src/ tests/

# Type check
mypy src/

# Run type checking with strict mode
mypy src/ --strict
```

## Test Coverage

Current coverage: **92%**

```
=============================
133 passed in 0.30s
=============================
```

## License

MIT

## Architecture

```
mac-dedup/
├── file_type.py     # File type detection by extension
├── scanner.py       # Recursive directory scanner with progress
├── hash_engine.py   # SHA-256 hashing with chunked reading
├── keep_strategy.py # Duplicate keep/delete logic
├── deleter.py      # Safe deletion to macOS Trash
├── filter.py       # File and directory filtering
├── reporter.py      # Report generation (table/csv/json)
└── cli.py          # Click-based CLI interface
```

## Changelog

### Version 0.1.0 (2026-03-01)

**Added:**
- Fast recursive directory scanning with progress display
- SHA-256 file hashing with chunked reading for large files
- Intelligent keep strategy (newest file is kept in each duplicate group)
- Safe deletion to macOS Trash (not permanent delete)
- Dry-run mode for previewing deletions
- File type filtering (text, audio, video, archive)
- Directory exclusion with default patterns (.git, node_modules, etc.)
- Multiple report formats (table, CSV, JSON)
- CLI interface with scan, clean, and report commands

**Test Coverage:** 92% (133 tests passing)
