# Terms & Conditions Analyzer - Chrome Extension

A powerful Chrome extension that analyzes terms and conditions on any webpage using AI-powered analysis tools.

## Features

### 🔍 **Intelligent Page Analysis**
- Automatically detects if a webpage contains terms and conditions
- Provides confidence scores and detailed analysis
- Highlights relevant terms and phrases on the page
- Real-time analysis with visual overlays

### 🌐 **URL Analysis**
- Analyze any URL for terms and conditions content
- Scrape and analyze external websites
- Support for multiple document formats

### 🏢 **Company Terms Search**
- Find terms and conditions for any company
- Intelligent search across multiple sources
- Automated discovery of legal documents

### 📊 **Analysis Features**
- Content analysis with confidence scoring
- Terms indicator detection
- Word count and content length analysis
- Visual highlighting of key terms

## Installation

### Prerequisites
1. **Backend API Server**: The extension requires the AI Finance NYC backend to be running
   ```bash
   cd /path/to/ai-finance-nyc
   make dev-server  # Starts server on http://localhost:8000
   ```

2. **API Keys**: Configure the following in your `.env` file:
   - `ANTHROPIC_API_KEY` - For AI-powered analysis
   - `BRAVE_API_KEY` - For web search capabilities

### Install Extension

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd ai-finance-nyc/chrome-extension
   ```

2. **Load extension in Chrome**:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the `chrome-extension` folder

3. **Pin the extension**:
   - Click the puzzle piece icon in Chrome toolbar
   - Find "Terms & Conditions Analyzer"
   - Click the pin icon to keep it visible

## Usage

### Quick Analysis
1. **Floating Action Button**: Look for the 📋 button on any webpage
2. **Extension Popup**: Click the extension icon in the toolbar
3. **Auto-Analysis**: Enable auto-analysis in settings for automatic detection

### Analysis Methods

#### 1. Current Page Analysis
- Click "Analyze Current Page" in the popup
- Automatically extracts and analyzes page content
- Shows confidence score and detection results
- Highlights terms on the page

#### 2. Custom URL Analysis
- Enter any URL in the "Analyze Custom URL" field
- Extension will scrape and analyze the target page
- Useful for analyzing external terms pages

#### 3. Company Search
- Enter a company name in "Find Company Terms"
- Uses intelligent search to find official terms documents
- Automatically analyzes found terms pages

### Visual Features

#### Analysis Overlay
- Appears automatically after analysis (if enabled)
- Shows confidence score and key indicators
- Quick access to highlighting features
- Auto-hides after 10 seconds

#### Term Highlighting
- Click "Highlight Terms" to mark relevant phrases
- Supports multiple indicator types
- Click specific indicators to highlight individual terms
- Highlighted terms are marked with yellow background

### Settings

Access settings by clicking the ⚙️ icon in the popup:

- **API Base URL**: Configure backend server URL (default: http://localhost:8000)
- **Auto-analyze pages**: Automatically analyze pages when loaded
- **Show analysis overlay**: Display visual overlay with results

## Technical Architecture

### Components

1. **Background Script** (`background.js`)
   - Manages API communication
   - Handles content analysis logic
   - Caches analysis results
   - Coordinates between popup and content scripts

2. **Content Script** (`content-script.js`)
   - Extracts page content
   - Displays analysis overlays
   - Handles term highlighting
   - Provides floating action button

3. **Popup Interface** (`popup.html/js/css`)
   - Main user interface
   - Settings management
   - Analysis controls
   - Results display

### API Integration

The extension integrates with the AI Finance NYC backend APIs:

- **`/scrape`**: Extracts content from URLs
- **`/terms-and-conditions`**: Intelligent terms discovery
- **`/search`**: Web search for company information

### Analysis Logic

The extension uses a sophisticated scoring system:

1. **Content Indicators**: Searches for terms-related phrases
2. **URL Indicators**: Analyzes URL structure
3. **Confidence Calculation**: Combines multiple factors
4. **Threshold Detection**: Determines if page contains terms

## Troubleshooting

### Common Issues

1. **"API Offline" Status**
   - Ensure backend server is running: `make dev-server`
   - Check API URL in settings (should be http://localhost:8000)
   - Verify API keys are configured in backend `.env` file

2. **Analysis Fails**
   - Check browser console for error messages
   - Verify the page has meaningful content
   - Try analyzing a different URL

3. **Extension Not Loading**
   - Reload the extension in `chrome://extensions/`
   - Check for JavaScript errors in extension console
   - Ensure all files are present in the extension folder

4. **Highlighting Not Working**
   - Try refreshing the page
   - Ensure analysis was completed successfully
   - Check if page has protective measures against content modification

### Debug Mode

Enable debug mode by:
1. Opening Chrome DevTools (F12)
2. Go to Console tab
3. Extension logs are prefixed with component names

## Development

### File Structure
```
chrome-extension/
├── manifest.json          # Extension configuration
├── background.js          # Background service worker
├── content-script.js      # Page content interaction
├── popup.html            # Main UI
├── popup.js              # UI logic
├── popup.css             # UI styles
├── icons/                # Extension icons
└── README.md             # This file
```

### Adding Features

1. **New Analysis Types**: Extend `analyzeContentForTerms()` in `background.js`
2. **UI Components**: Add to `popup.html` and style in `popup.css`
3. **Page Interactions**: Extend `content-script.js`

### API Endpoints

The extension expects these endpoints from the backend:
- `GET /` - Health check
- `POST /scrape` - URL content extraction
- `POST /terms-and-conditions` - Terms discovery
- `POST /search` - Web search

## Privacy & Security

- **No Data Collection**: Extension doesn't collect or transmit personal data
- **Local Processing**: Analysis happens locally or via your own API server
- **Secure Communication**: Uses HTTPS where possible
- **Permission Scoped**: Only requests necessary Chrome permissions

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review console logs for error messages
3. Ensure backend API server is running correctly
4. Verify all dependencies are installed

## License

This extension is part of the AI Finance NYC project.
