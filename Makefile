.PHONY: docs docs-clean docs-serve help install test lint format quality pre-commit pre-commit-install

help:
	@echo "SLURM Monitoring Development Commands"
	@echo "====================================="
	@echo ""
	@echo "Documentation:"
	@echo "  make docs          Build HTML documentation"
	@echo "  make docs-clean    Clean build artifacts"
	@echo "  make docs-serve    Build and serve docs locally (http://localhost:8000)"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test          Run tests with coverage"
	@echo "  make lint          Run linters"
	@echo "  make format        Format code with black"
	@echo "  make quality       Run all quality checks"
	@echo ""
	@echo "Pre-commit Hooks:"
	@echo "  make pre-commit-install  Install pre-commit hooks"
	@echo "  make pre-commit          Run pre-commit on all files"
	@echo ""
	@echo "Development:"
	@echo "  make install       Install development dependencies"
	@echo "  make help          Show this help message"

# Documentation targets
docs: docs-clean
	pixi run docs-build

docs-clean:
	rm -rf docs/_build

docs-serve: docs
	cd docs/_build/html && python -m http.server 8000

# Testing and quality
install:
	pixi install

test:
	pixi run test

lint:
	pixi run lint

format:
	pixi run format

quality: lint
	pixi run type-check

# Pre-commit hooks
pre-commit-install:
	pixi run pre-commit-install

pre-commit:
	pixi run pre-commit-run
