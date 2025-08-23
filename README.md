# AI Finance NYC

FastAPI server with web scraping, text summarization, and Brave Search.

## Quick Start

### 1. Setup Environment
```bash
make setup
nano .env  # Add your API keys
make dev-install
```

### 2. Run Server
```bash
make dev-server
```

### 3. Test Brave Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI finance", "count": 3}'
```

## API Keys Needed
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com/)
- **Brave Search**: key on the event website. 

## Endpoints
- `GET /` - Health check
- `POST /scrape` - Scrape website
- `POST /summarize` - Summarize text
- `POST /search` - Brave Search


