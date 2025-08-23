# Simple T&C Testing Guide

## Focus: Terms & Conditions Analysis Only

This simplified testing approach focuses purely on analyzing terms and conditions content without external search functionality.

## Quick Setup

### 1. Start Backend (T&C Analysis Only)
```bash
cd /Users/royalsequiera/Projects/hackathons/ai-finance-nyc
make dev-server
```

### 2. Test Backend is Ready
```bash
curl http://localhost:8000/
# Should return: {"message": "AI Finance NYC API is running!"}
```

### 3. Install Extension
1. Chrome → `chrome://extensions/`
2. Enable "Developer mode"
3. "Load unpacked" → Select `chrome-extension` folder
4. Pin the extension (📋 icon)

## Simple Testing Scenarios

### ✅ Test 1: Known Terms Pages
Test these URLs that definitely contain terms and conditions:

**High-confidence terms pages:**
- `https://www.netflix.com/legal/termsofuse`
- `https://policies.google.com/terms`
- `https://www.apple.com/legal/internet-services/terms/site.html`
- `https://www.spotify.com/legal/end-user-agreement/`

**Steps:**
1. Navigate to one of these URLs
2. Click extension icon (📋)
3. Click "Analyze Current Page"
4. **Expected:** 80%+ confidence, "Terms & Conditions Page"

### ✅ Test 2: Non-Terms Pages
Test pages that should NOT be detected as terms:

**Regular web pages:**
- `https://www.google.com`
- `https://www.netflix.com` (homepage)
- `https://news.ycombinator.com`
- `https://github.com`

**Steps:**
1. Navigate to one of these URLs
2. Click extension icon
3. Click "Analyze Current Page"
4. **Expected:** Low confidence (<30%), "Not a Terms Page"

### ✅ Test 3: Custom URL Analysis
**Steps:**
1. Open extension popup
2. Enter this URL: `https://www.dropbox.com/terms`
3. Click "Analyze" button
4. **Expected:** Should detect as terms page with high confidence

### ✅ Test 4: Visual Highlighting
**Steps:**
1. Analyze a terms page (from Test 1)
2. Click "Highlight Terms" button
3. **Expected:** Yellow highlighting appears on key terms like "agreement", "liability", "terms", etc.

### ✅ Test 5: Search Suggestions (Simplified)
**Steps:**
1. Open extension popup
2. Enter "Slack" in company field
3. Click "Get Search Tips"
4. **Expected:** Shows search suggestions like "Slack terms and conditions"
5. Manually search for Slack's terms page
6. Use "Analyze Custom URL" with the found URL

## What to Check

### ✅ **Success Indicators**
- Extension loads without errors
- Shows "API Ready" status (green dot)
- High confidence (80%+) on known terms pages
- Low confidence (<30%) on regular pages
- Highlighting works on terms pages
- Search suggestions appear for company names

### ❌ **Red Flags**
- "API Offline" status
- JavaScript errors in console (F12)
- No highlighting on terms pages
- Same confidence score for all pages
- Popup doesn't open

## Debug if Issues

### Check Logs
- **Popup logs:** Right-click extension → "Inspect popup"
- **Page logs:** F12 → Console tab
- **Background logs:** `chrome://extensions/` → "background page"

### Test API Directly
```bash
# Test scraping
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.netflix.com/legal/termsofuse"}'
```

### Common Fixes
- **API Offline:** Restart backend with `make dev-server`
- **No highlighting:** Refresh the page first
- **Extension errors:** Reload extension in `chrome://extensions/`

## Confidence Score Guide

**What the percentages mean:**
- **90-100%:** Definitely terms and conditions
- **70-89%:** Very likely terms content
- **50-69%:** Some legal language detected
- **30-49%:** Minimal legal indicators
- **0-29%:** Not a terms page

## Test Results to Expect

| URL | Expected Confidence | Expected Detection |
|-----|-------------------|-------------------|
| Netflix terms | 90%+ | ✅ Terms Page |
| Google terms | 85%+ | ✅ Terms Page |
| Apple terms | 85%+ | ✅ Terms Page |
| Google homepage | <20% | ❌ Not Terms |
| News sites | <30% | ❌ Not Terms |

## Quick Test Checklist

- [ ] Backend server running on port 8000
- [ ] Extension loads in Chrome without errors
- [ ] Netflix terms page → High confidence detection
- [ ] Google homepage → Low confidence detection
- [ ] Custom URL analysis works
- [ ] Highlighting appears on terms pages
- [ ] Search suggestions work for company names
- [ ] No JavaScript errors in console

**This simplified approach focuses purely on T&C analysis quality without complex search features!**
