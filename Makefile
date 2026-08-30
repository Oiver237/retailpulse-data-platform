PYTHON := python

.PHONY: help install format format-check lint type-check test coverage quality clean

help:
	@echo "RetailPulse development commands"
	@echo ""
	@echo "  make install       Install development dependencies"
	@echo "  make format        Format Python code"
	@echo "  make format-check  Check Python formatting"
	@echo "  make lint          Run Ruff"
	@echo "  make type-check    Run MyPy"
	@echo "  make test          Run unit tests"
	@echo "  make quality       Run all local quality checks"
	@echo "  make clean         Remove generated local artifacts"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

format:
	$(PYTHON) -m black src tests
	$(PYTHON) -m ruff check src tests --fix

format-check:
	$(PYTHON) -m black src tests --check

lint:
	$(PYTHON) -m ruff check src tests

type-check:
	$(PYTHON) -m mypy

test:
	$(PYTHON) -m pytest tests/unit

coverage:
	$(PYTHON) -m pytest

quality: format-check lint type-check coverage

clean:
	rm -rf .coverage .mypy_cache .pytest_cache .ruff_cache htmlcov
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
