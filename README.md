# AI Finance NYC

A simple Python project using uv for dependency management and Make for automation.

## Setup

1. Install uv (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install dependencies:
   ```bash
   make dev-install
   ```

## Usage

### Available Commands

- `make help` - Show all available commands
- `make install` - Install production dependencies
- `make dev-install` - Install development dependencies
- `make test` - Run tests
- `make lint` - Run linting
- `make format` - Format code with black
- `make clean` - Clean up cache and temporary files
- `make run` - Run the main application
- `make server` - Run the FastAPI server
- `make dev-server` - Run the FastAPI server in development mode with auto-reload

### Running the Application

```bash
make run
```

### Running the FastAPI Server

```bash
# Production mode
make server

# Development mode with auto-reload
make dev-server
```

The server will be available at `http://localhost:8000`

### API Endpoints

- `GET /` - Health check
- `POST /scrape` - Scrape data from a URL
- `POST /summarize` - Summarize text using Anthropic Claude

### API Documentation

Once the server is running, visit:
- `http://localhost:8000/docs` - Interactive API documentation (Swagger UI)
- `http://localhost:8000/redoc` - Alternative API documentation

### Environment Setup

1. Copy the `.env` file and add your Anthropic API key:
   ```bash
   cp .env .env.local
   # Edit .env.local and add your actual API key
   ```

2. Install dependencies:
   ```bash
   make dev-install
   ```

### Running Tests

```bash
make test
```

### Code Formatting

```bash
make format
```

## Project Structure

```
ai-finance-nyc/
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── api.py
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── test_api.py
├── pyproject.toml
├── Makefile
├── .env
├── .gitignore
└── README.md
```
