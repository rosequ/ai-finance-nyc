# AI Finance NYC

FastAPI server with web scraping, text summarization, and intelligent terms & conditions finder.

## Quick Start

### 1. Setup Environment
```bash
make setup
nano .env  # Add your API keys
make dev-install
uv run playwright install chromium  # Install browser for automation
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

### 4. Test Terms & Conditions Finder
```bash
curl -X POST "http://localhost:8000/terms-and-conditions" \
  -H "Content-Type: application/json" \
  -d '{"query": "Netflix", "output_file": "netflix_terms.txt"}'
```

Or run the demo script:
```bash
uv run python demo_amex_gold.py
```

Or run the test suite:
```bash
uv run python test_credit_card_terms.py
```

## API Keys Needed
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com/)
- **Brave Search**: key on the event website

## Endpoints
- `GET /` - Health check
- `POST /scrape` - Scrape website
- `POST /summarize` - Summarize text
- `POST /search` - Brave Search
- `POST /terms-and-conditions` - Get terms and conditions for any company or product using intelligent browser automation

## Terms & Conditions Finder

The `/terms-and-conditions` endpoint uses intelligent web search and Playwright browser automation to find and extract terms and conditions for any company or product. It will:

1. **Intelligent Search**: Use multiple search queries to find relevant terms pages
2. **Smart Scoring**: Score and prioritize search results based on relevance
3. **Content Validation**: Verify that extracted content is actually terms and conditions
4. **Fallback Patterns**: Try common URL patterns for known companies
5. **Save Results**: Save the content to a file in the `terms_and_conditions/` directory

### Features
- **Generic**: Works with any company, product, or service
- **Intelligent**: Uses multiple search strategies and content validation
- **Visual**: Shows the search and extraction process in a browser window
- **Robust**: Includes fallback mechanisms for different company types
- **Comprehensive**: Supports tech companies, financial services, and generic patterns

### Request Format
```json
{
  "query": "Netflix",
  "company_name": "Netflix Inc",
  "product_name": "Streaming Service",
  "output_file": "optional_custom_filename.txt"
}
```

### Response Format
```json
{
  "query": "Netflix",
  "terms_url": "https://help.netflix.com/legal/termsofuse",
  "content": "Terms and conditions text...",
  "file_path": "terms_and_conditions/netflix_terms.txt",
  "status": "success"
}
```

### Example Use Cases
- **Tech Companies**: Google, Facebook, Amazon, Apple, Microsoft
- **Financial Services**: Chase, American Express, Capital One
- **Entertainment**: Netflix, Spotify, Disney+
- **Any Company**: Just provide the company name or product

### How It Works
1. **Multi-Query Search**: Searches with variations like "terms and conditions", "terms of service", "user agreement"
2. **Result Scoring**: Scores results based on relevance keywords, domain authority, and content indicators
3. **Content Extraction**: Navigates to pages and extracts full content
4. **Validation**: Verifies content contains terms-related indicators
5. **Fallback**: Tries direct URL patterns for known companies
6. **File Output**: Saves validated content to text files

## DSPy Company Analysis Agent 🤖

The project now includes an intelligent DSPy agent that wraps the FastAPI endpoints into a comprehensive company analysis workflow.

### Features
- **Intelligent Content Retrieval**: Automatically detects if input is a URL (scrapes directly) or company name (finds terms & conditions)
- **Reddit Sentiment Analysis**: Searches for community discussions about the company
- **Comprehensive Reports**: Combines all findings into structured text reports
- **Automated Workflow**: Orchestrates multiple API calls intelligently

### Quick Start with DSPy Agent

```bash
# Install DSPy dependencies
uv sync

# Run the demo
uv run python demo_dspy_agent.py

# Or try interactive mode
uv run python demo_dspy_agent.py --interactive
```

### DSPy Agent Usage

```python
from src.dspy_tools import analyze_company

# Analyze by company name
result = analyze_company(
    input_query="Netflix",
    company_name="Netflix Inc",
    output_file="netflix_analysis.txt"
)

# Analyze by URL
result = analyze_company(
    input_query="https://www.spotify.com/legal/terms/",
    company_name="Spotify"
)
```

### What the Agent Does

1. **Smart Input Detection**: 
   - If input is URL → scrapes content directly
   - If input is company name → finds terms & conditions

2. **Reddit Analysis**: 
   - Searches for discussions about the company
   - Summarizes community sentiment

3. **Report Generation**:
   - Combines terms/content + Reddit discussions
   - Saves comprehensive analysis to text file
   - Includes timestamps and source URLs

### Example Output Structure

```
COMPANY ANALYSIS REPORT
Generated on: 2024-01-20 15:30:45
Query: Netflix
Company: Netflix Inc

SECTION 1: CONTENT ANALYSIS
Content Type: terms_and_conditions
Source URL: https://help.netflix.com/legal/termsofuse
[Full terms and conditions content]

SECTION 2: REDDIT DISCUSSIONS & SENTIMENT
[Community discussions and sentiment analysis]

SUMMARY
[Analysis summary with status and metrics]
```

## 🎨 Web Interface

The AI Finance Analyzer now includes a beautiful web interface built with Streamlit! 

### Features
- **Beautiful UI**: Modern gradient design with interactive components
- **Real-time Analysis**: Progress tracking with animated status updates
- **Comprehensive Results**: Organized display of all analysis components
- **Data Visualization**: Charts and metrics for analysis summary
- **Download Results**: Export analysis results as JSON
- **Responsive Design**: Works on desktop and mobile devices

### Quick Start Web UI

```bash
# Install dependencies (if not already done)
uv sync

# Launch the web interface
python run_app.py
```

Or run directly with Streamlit:
```bash
uv run streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

### How to Use the Web Interface

1. **Enter URL**: Paste the URL of a financial product's terms & conditions page
2. **Click Analyze**: The AI will automatically:
   - Extract terms and conditions
   - Identify the product type and company
   - Analyze risks and key information
   - Search Reddit for community insights
   - Generate a comprehensive report

3. **View Results**: The interface displays:
   - **Product Information**: Name, type, and company
   - **Terms Analysis**: Key information, risks, and consumer scores
   - **Community Insights**: Positive and negative feedback from Reddit
   - **Analysis Summary**: Data sources and metrics
   - **Download Option**: Full results as JSON

### Supported Financial Products
- Credit Cards
- Personal Loans
- Mortgages
- Investment Products
- Banking Services

### Example URLs to Try
- Wells Fargo Active Cash: `https://www.wellsfargo.com/credit-cards/agreements/active-cash-agreement`
- Chase Sapphire Preferred: Credit card terms pages
- Capital One Venture: Terms and conditions URLs

The web interface provides the same powerful analysis as the command-line tools but with a beautiful, user-friendly interface that anyone can use!


