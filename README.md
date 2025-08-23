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
- `POST /search` - Search using Brave Search API

### API Documentation

Once the server is running, visit:
- `http://localhost:8000/docs` - Interactive API documentation (Swagger UI)
- `http://localhost:8000/redoc` - Alternative API documentation

### Environment Setup

1. Run the setup command to create your `.env` file:
   ```bash
   make setup
   ```

2. Edit the `.env` file and add your API keys:
   ```bash
   nano .env
   # Add your actual API keys:
   # ANTHROPIC_API_KEY=your_anthropic_api_key_here
   # BRAVE_API_KEY=your_brave_api_key_here
   ```

3. Install dependencies:
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
├── .env.example
├── .gitignore
└── README.md
```
