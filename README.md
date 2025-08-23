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

### Testing the API Endpoints

Once the server is running, you can test the endpoints:

#### 1. Health Check
```bash
curl http://localhost:8000/
```

#### 2. Web Scraping
```bash
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

#### 3. Text Summarization
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text to summarize here", "max_length": 200}'
```

#### 4. Brave Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI finance news", "count": 5}'
```

**Note**: Make sure you have added your actual API keys to the `.env` file before testing the summarize and search endpoints.

### API Endpoints

- `GET /` - Health check
- `POST /scrape` - Scrape data from a URL
- `POST /summarize` - Summarize text using Anthropic Claude
- `POST /search` - Search using Brave Search API

### API Documentation

Once the server is running, visit:
- `http://localhost:8000/docs` - Interactive API documentation (Swagger UI)
- `http://localhost:8000/redoc` - Alternative API documentation

### Getting API Keys

#### Anthropic API Key
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

#### Brave Search API Key
1. Visit [Brave Search API](https://api.search.brave.com/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Copy the key and add it to your `.env` file

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

### Quick Start Example

Here's a complete example of setting up and testing the Brave Search endpoint:

```bash
# 1. Setup environment
make setup

# 2. Edit .env with your API keys
nano .env

# 3. Install dependencies
make dev-install

# 4. Start the server
make dev-server

# 5. In another terminal, test Brave Search
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI finance trends 2024", "count": 3}'
```

Expected response:
```json
{
  "query": "AI finance trends 2024",
  "results": [
    {
      "title": "AI in Finance: Trends and Predictions for 2024",
      "url": "https://example.com/ai-finance-2024",
      "description": "Latest trends in AI adoption in financial services...",
      "published": "2024-01-15"
    }
  ],
  "total_results": 3,
  "status": "success"
}
```

### Running Tests

```bash
make test
```

### Code Formatting

```bash
make format
```

### Troubleshooting

#### Common Issues

1. **"Invalid API key" errors**
   - Make sure you've added your actual API keys to the `.env` file
   - Verify the API keys are correct and active

2. **Server won't start**
   - Check if port 8000 is already in use: `lsof -i :8000`
   - Kill the process or use a different port

3. **Import errors**
   - Run `make dev-install` to ensure all dependencies are installed
   - Check that you're using Python 3.9+ with `python --version`

4. **Rate limit errors**
   - The APIs have rate limits. Wait a moment and try again
   - Consider upgrading your API plan for higher limits
