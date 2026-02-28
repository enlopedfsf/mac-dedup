# mac-dedup

Fast duplicate file finder for macOS.

## Installation

```bash
pip install .
```

## Usage

```bash
# Show help
mac-dedup --help

# Scan directory for duplicates
mac-dedup scan /path/to/directory

# Remove duplicate files
mac-dedup clean /path/to/directory

# Dry run (show what would be deleted)
mac-dedup clean /path/to/directory --dry-run

# Generate report
mac-dedup report /path/to/directory
```

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src

# Format code
black src/ tests/

# Type check
mypy src/
```
