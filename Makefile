.PHONY: help install dev-install test lint format clean run

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv sync

dev-install: ## Install development dependencies
	uv sync --dev

test: ## Run tests
	uv run pytest

lint: ## Run linting
	uv run flake8 src/ tests/

format: ## Format code with black
	uv run black src/ tests/

clean: ## Clean up cache and temporary files
	uv cache clean
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run: ## Run the main application
	uv run python src/main.py
