# Contributing

Thank you for your interest in contributing to mac-dedup!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/mac-dedup.git
cd mac-dedup

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_scanner.py

# Run tests matching a pattern
pytest -k "test_scan"
```

## Code Quality

```bash
# Format code
black src/ tests/

# Type check
mypy src/

# Run type check with strict mode
mypy src/ --strict

# Check with pre-commit hooks
pre-commit run --all-files
```

## Commit Guidelines

- Write meaningful commit messages (conventional commits preferred)
  - `feat: add keep strategy module`
  - `fix: handle permission errors in scanner`
  - `docs: update README with usage examples`
  - `test: add tests for hash engine`
  - `refactor: improve file type detection`

- Run tests and ensure they pass before committing
- Format code with black
- Type check with mypy

## Pull Request Process

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m "feat: add amazing feature"`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Adding New Features

1. Discuss the feature in an issue first
2. Implement the feature following TDD (write tests first)
3. Ensure tests pass and coverage is maintained
4. Update documentation if needed

## Reporting Issues

When reporting issues, please include:
- macOS version
- Python version (`python --version`)
- Steps to reproduce
- Expected vs actual behavior
- Error messages or stack traces
