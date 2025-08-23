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

### Running the Application

```bash
make run
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
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── pyproject.toml
├── Makefile
├── .gitignore
└── README.md
```
