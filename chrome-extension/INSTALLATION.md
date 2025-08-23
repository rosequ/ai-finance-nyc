# Chrome Extension Installation Guide

## Prerequisites

1. **Start the Backend Server**
   ```bash
   cd /path/to/ai-finance-nyc
   make dev-server
   ```
   The server should be running on `http://localhost:8000`

2. **Verify API Keys**
   Make sure your `.env` file contains:
   ```
   ANTHROPIC_API_KEY=your_key_here
   BRAVE_API_KEY=your_key_here
   ```

## Install the Extension

1. **Open Chrome Extensions Page**
   - Open Chrome browser
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right corner)

2. **Load the Extension**
   - Click "Load unpacked"
   - Select the `chrome-extension` folder from this project
   - The extension should appear in your extensions list

3. **Pin the Extension**
   - Click the puzzle piece icon (Extensions) in Chrome toolbar
   - Find "Terms & Conditions Analyzer"
   - Click the pin icon to keep it visible in toolbar

## Test the Extension

### Test 1: Basic Functionality
1. Navigate to any webpage
2. Click the 📋 extension icon
3. Click "Analyze Current Page"
4. Verify that analysis completes and shows results

### Test 2: Terms & Conditions Detection
1. Go to a known terms page (e.g., https://www.netflix.com/legal/termsofuse)
2. Click the extension icon
3. Click "Analyze Current Page"
4. Should show high confidence that it's a terms page

### Test 3: Custom URL Analysis
1. Open the extension popup
2. Enter a URL in "Analyze Custom URL" field
3. Click "Analyze"
4. Verify that the URL is analyzed successfully

### Test 4: Company Search
1. Open the extension popup
2. Enter "Netflix" in "Find Company Terms" field
3. Click "Find Terms"
4. Should find and analyze Netflix's terms and conditions

### Test 5: Highlighting
1. Analyze a terms page
2. Click "Highlight Terms" button
3. Verify that relevant terms are highlighted on the page

## Troubleshooting

### Extension Won't Load
- Check that all files are present in the chrome-extension folder
- Look for errors in the Chrome extensions page
- Reload the extension if needed

### Analysis Fails
- Verify backend server is running on port 8000
- Check browser console (F12) for error messages
- Ensure API keys are configured correctly

### No Results
- Try with a known terms and conditions page
- Check if the page has meaningful text content
- Verify internet connection for external URL analysis

## Debug Mode

To see detailed logs:
1. Right-click the extension icon
2. Select "Inspect popup" to see popup console
3. Open any webpage and press F12 to see content script logs
4. Check `chrome://extensions/` and click "background page" for background script logs

## Success Indicators

✅ Extension icon appears in Chrome toolbar  
✅ Popup opens when clicking the icon  
✅ "API Ready" status shows in popup footer  
✅ Current page analysis completes without errors  
✅ Terms pages are detected with high confidence  
✅ Highlighting works on analyzed pages  
✅ Settings can be opened and saved  

## Next Steps

Once the extension is working:
1. Test on various websites to see analysis quality
2. Customize settings (API URL, auto-analyze, etc.)
3. Try the company search feature with different companies
4. Use the help feature for detailed usage instructions

The extension is now ready to analyze terms and conditions on any webpage!
