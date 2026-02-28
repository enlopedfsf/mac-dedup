.PHONY: help install test lint format clean build upload

help:
	@echo "Available commands:"
	@echo "  make install   - Install package in development mode"
	@echo "  make test      - Run tests"
	@echo "  make lint      - Run linting (black, mypy)"
	@echo "  make format    - Format code with black"
	@echo "  make clean     - Clean build artifacts"
	@echo "  make build     - Build distribution packages"
	@echo "  make upload     - Upload to PyPI (requires PYPI_API_TOKEN)"

install:
	pip install -e ".[dev]"

test:
	pytest --cov=src --cov-report=term-missing

lint:
	@echo "Running black..."
	black --check src/ tests/
	@echo "Running mypy..."
	mypy src/

format:
	black src/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	python -m build

upload:
	twine upload dist/*
