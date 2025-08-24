.PHONY: help install dev-install test lint format clean run setup

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - copy .env.example to .env
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file from .env.example"; \
		echo "📝 Please edit .env and add your API keys:"; \
		echo "   - ANTHROPIC_API_KEY=your_anthropic_api_key_here"; \
		echo "   - BRAVE_API_KEY=your_brave_api_key_here"; \
	else \
		echo "⚠️  .env file already exists. Skipping setup."; \
	fi

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

server: ## Run the FastAPI server
	uv run python src/api.py

dev-server: ## Run the FastAPI server in development mode
	uv run uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

debug-server: ## Run the FastAPI server with debug logging
	uv run uvicorn src.api:app --reload --host 0.0.0.0 --port 8000 --log-level debug

debug-analyzer: ## Run the integrated analyzer with debug output
	PYTHONPATH=. uv run python -u src/integrated_analyzer.py
