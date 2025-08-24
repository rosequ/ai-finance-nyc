# Personal Financial Advisor - Chrome Extension

## Installation

1. **Start the API server first:**
   ```bash
   cd ../src
   python3 api.py
   ```

2. **Load the extension in Chrome:**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top-right)
   - Click "Load unpacked"
   - Select this `chrome-extension` folder
   - The extension should load successfully with blue icons

## Usage

1. Navigate to any webpage with financial terms & conditions
2. Click the extension icon in the Chrome toolbar  
3. Click "🔍 Get Financial Analysis"
4. Wait for AI analysis to complete
5. View comprehensive results including:
   - Product information
   - Terms analysis
   - Reddit community insights

## Requirements

- Chrome browser with developer mode enabled
- Python API server running on localhost:8000
- Internet connection for Reddit analysis

## Files

- `manifest.json` - Extension configuration
- `popup.html` - Extension popup interface
- `popup.js` - Main extension logic
- `content-script.js` - Page content extraction
- `icons/` - Extension icons (auto-generated)

## Troubleshooting

- **Extension won't load**: Make sure all files are present and icons exist
- **API connection failed**: Ensure the Python API server is running
- **No content extracted**: Try refreshing the page and analyzing again
