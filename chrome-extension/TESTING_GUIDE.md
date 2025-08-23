# Chrome Extension Testing Guide

## Prerequisites for Testing

### 1. Start the Backend Server
```bash
cd /Users/royalsequiera/Projects/hackathons/ai-finance-nyc
make dev-server
```

The server should start on `http://localhost:8000`. You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 2. Verify API Keys
Make sure your `.env` file contains:
```
ANTHROPIC_API_KEY=your_key_here
BRAVE_API_KEY=your_key_here
```

### 3. Test Backend is Working
```bash
curl http://localhost:8000/
```
Should return: `{"message": "AI Finance NYC API is running!"}`

## Install the Extension

### Step 1: Open Chrome Extensions
1. Open Google Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top-right corner)

### Step 2: Load the Extension
1. Click "Load unpacked" button
2. Navigate to and select the `chrome-extension` folder:
   ```
   /Users/royalsequiera/Projects/hackathons/ai-finance-nyc/chrome-extension
   ```
3. The extension should appear with the name "Terms & Conditions Analyzer"

### Step 3: Pin the Extension
1. Click the puzzle piece icon (Extensions) in Chrome toolbar
2. Find "Terms & Conditions Analyzer"
3. Click the pin icon to keep it visible

## Testing Scenarios

### Test 1: Basic Installation Verification

**What to Check:**
- [ ] Extension appears in `chrome://extensions/`
- [ ] Extension icon (📋) appears in Chrome toolbar
- [ ] No errors shown in extension details

**If Issues:**
- Check that all files are present in the chrome-extension folder
- Look for errors in the extension console
- Try reloading the extension

### Test 2: Popup Interface Test

**Steps:**
1. Click the extension icon in toolbar
2. Popup should open showing the interface

**What to Verify:**
- [ ] Popup opens without errors
- [ ] "API Ready" status shows in footer (green dot)
- [ ] Current page title and URL are displayed
- [ ] All buttons are visible and clickable

**If "API Offline" shows:**
- Verify backend server is running on port 8000
- Check API URL in settings (⚙️ button)

### Test 3: Current Page Analysis

**Steps:**
1. Navigate to any webpage (start with a simple site)
2. Click extension icon
3. Click "Analyze Current Page" button
4. Wait for analysis to complete

**Expected Results:**
- [ ] Loading spinner appears
- [ ] Analysis completes within 10-30 seconds
- [ ] Results show confidence percentage
- [ ] Status changes to "Analysis completed"

**Test with Known Terms Pages:**
Try these URLs to test detection:
- `https://www.netflix.com/legal/termsofuse`
- `https://policies.google.com/terms`
- `https://www.apple.com/legal/internet-services/terms/site.html`

Should show high confidence (80%+) for terms detection.

### Test 4: Visual Overlay Test

**Steps:**
1. Analyze a page (as in Test 3)
2. Look for analysis overlay in top-right of page
3. Overlay should show confidence and key indicators

**What to Check:**
- [ ] Overlay appears automatically after analysis
- [ ] Shows confidence percentage
- [ ] Lists found indicators
- [ ] Has "Full Analysis" and "Highlight Terms" buttons
- [ ] Auto-hides after 10 seconds (if not interacted with)

### Test 5: Term Highlighting

**Steps:**
1. Analyze a terms page with indicators found
2. Click "Highlight Terms" button (in popup or overlay)
3. Look for yellow highlighting on the page

**Expected Results:**
- [ ] Relevant terms are highlighted in yellow
- [ ] Multiple terms are highlighted across the page
- [ ] Highlights are visible and properly positioned
- [ ] Page scrolling works normally with highlights

### Test 6: Custom URL Analysis

**Steps:**
1. Open extension popup
2. Enter a URL in "Analyze Custom URL" field
   - Try: `https://www.spotify.com/legal/end-user-agreement/`
3. Click "Analyze" button

**Expected Results:**
- [ ] Analysis starts (loading spinner)
- [ ] Results appear showing confidence and analysis
- [ ] Works with external URLs (not current page)

### Test 7: Company Search

**Steps:**
1. Open extension popup
2. Enter "Netflix" in "Find Company Terms" field
3. Click "Find Terms" button

**Expected Results:**
- [ ] Search starts (loading spinner)
- [ ] Finds Netflix's terms and conditions
- [ ] Shows source URL and analysis
- [ ] Offers to open the terms page

**Try Other Companies:**
- "Google"
- "Apple" 
- "Microsoft"
- "Spotify"

### Test 8: Settings Functionality

**Steps:**
1. Click ⚙️ (settings) button in popup
2. Settings modal should open
3. Try changing the API URL
4. Click "Save Settings"

**What to Test:**
- [ ] Settings modal opens and closes
- [ ] Can modify API URL
- [ ] Can toggle auto-analyze and show overlay
- [ ] Settings are saved (persist after closing popup)
- [ ] API status updates after changing URL

### Test 9: Error Handling

**Test Network Errors:**
1. Stop the backend server (`Ctrl+C`)
2. Try to analyze a page
3. Should show "API Offline" and error message

**Test Invalid URLs:**
1. Enter an invalid URL in custom URL field
2. Should show appropriate error message

**Test Empty Inputs:**
1. Try analyzing without entering company name
2. Should show validation error

### Test 10: Keyboard Shortcuts

**While popup is open:**
- [ ] `Ctrl+Enter` (or `Cmd+Enter` on Mac) - Analyzes current page
- [ ] `Ctrl+H` (or `Cmd+H` on Mac) - Highlights terms
- [ ] `Enter` in input fields - Submits form

### Test 11: Floating Action Button

**Steps:**
1. Navigate to any webpage
2. Look for floating 📋 button in bottom-right corner
3. Click the button

**Expected Results:**
- [ ] Button appears on every page
- [ ] Clicking triggers page analysis
- [ ] Button has hover effects

## Debug Mode Testing

### View Extension Logs

**Background Script Logs:**
1. Go to `chrome://extensions/`
2. Find "Terms & Conditions Analyzer"
3. Click "background page" link
4. DevTools opens with background script console

**Popup Logs:**
1. Right-click extension icon
2. Select "Inspect popup"
3. DevTools opens with popup console

**Content Script Logs:**
1. Open any webpage
2. Press F12 to open DevTools
3. Look for extension logs in Console tab

**What to Look For:**
- Error messages in red
- Network request failures
- API response issues
- JavaScript errors

### Test API Endpoints Directly

**Test Scraping Endpoint:**
```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.netflix.com/legal/termsofuse"}'
```

**Test Terms Search:**
```bash
curl -X POST http://localhost:8000/terms-and-conditions \
  -H "Content-Type: application/json" \
  -d '{"query": "Netflix"}'
```

## Performance Testing

### Load Testing
1. Analyze multiple pages quickly
2. Check for memory leaks in task manager
3. Verify extension doesn't slow down browsing

### Cache Testing
1. Analyze the same page twice
2. Second analysis should be faster (cached)
3. Check that cache clears appropriately

## Common Issues & Solutions

### ❌ "API Offline" Status
**Solution:**
```bash
# Start the backend server
cd /Users/royalsequiera/Projects/hackathons/ai-finance-nyc
make dev-server
```

### ❌ Extension Won't Load
**Solutions:**
- Check that all files exist in chrome-extension folder
- Reload extension in chrome://extensions/
- Check for syntax errors in JavaScript files

### ❌ Analysis Fails
**Debug Steps:**
1. Check browser console for errors
2. Verify API endpoints are responding
3. Check network tab for failed requests
4. Ensure API keys are configured

### ❌ No Highlighting
**Possible Causes:**
- Page doesn't have terms indicators
- Website blocks content modification
- Content script didn't load properly

### ❌ Popup Doesn't Open
**Solutions:**
- Check for JavaScript errors in popup console
- Verify popup.html exists and is valid
- Try reloading the extension

## Success Criteria

The extension passes testing if:
- ✅ Installs without errors
- ✅ Shows "API Ready" status
- ✅ Analyzes current pages successfully
- ✅ Detects known terms pages with high confidence
- ✅ Highlights terms visually on pages
- ✅ Custom URL analysis works
- ✅ Company search finds terms
- ✅ Settings can be modified and saved
- ✅ Error handling works appropriately
- ✅ No console errors during normal operation

## Advanced Testing

### Cross-Site Testing
Test on various types of websites:
- E-commerce sites (Amazon, eBay)
- Social media (Twitter, Facebook)
- SaaS platforms (GitHub, Slack)
- News sites (CNN, BBC)
- Government sites (.gov domains)

### Content Type Testing
- Pages with heavy JavaScript
- Pages with PDFs embedded
- Pages with minimal text content
- Pages that require login
- Pages with anti-scraping measures

The extension should handle all these scenarios gracefully without breaking or causing errors.
