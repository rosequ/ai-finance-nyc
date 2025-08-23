#!/bin/bash

echo "🧪 Testing Chrome Extension - Review T&C Functionality"
echo "=================================================="

# Test 1: Check if API server is running
echo "1. Testing API server..."
API_RESPONSE=$(curl -s http://localhost:8000/)
if [[ $API_RESPONSE == *"AI Finance NYC API is running"* ]]; then
    echo "✅ API server is running"
else
    echo "❌ API server is not responding"
    exit 1
fi

# Test 2: Test scraping endpoint
echo "2. Testing scraping endpoint..."
SCRAPE_RESPONSE=$(curl -s -X POST http://localhost:8000/scrape \
    -H "Content-Type: application/json" \
    -d '{"url": "https://example.com"}')

if [[ $SCRAPE_RESPONSE == *"success"* ]]; then
    echo "✅ Scraping endpoint is working"
else
    echo "❌ Scraping endpoint failed"
    echo "Response: $SCRAPE_RESPONSE"
    exit 1
fi

# Test 3: Check extension files
echo "3. Checking extension files..."
if [ -f "manifest.json" ] && [ -f "popup.html" ] && [ -f "popup.js" ] && [ -f "background.js" ]; then
    echo "✅ All extension files are present"
else
    echo "❌ Missing extension files"
    exit 1
fi

# Test 4: Validate manifest.json using Python
echo "4. Validating manifest.json..."
if python3 -m json.tool manifest.json > /dev/null 2>&1; then
    echo "✅ manifest.json is valid JSON"
else
    echo "❌ manifest.json has invalid JSON syntax"
    exit 1
fi

# Test 5: Check for "Review T&C" button in popup.html
echo "5. Checking for 'Review T&C' button..."
if grep -q "Review T&C" popup.html; then
    echo "✅ 'Review T&C' button found in popup.html"
else
    echo "❌ 'Review T&C' button not found in popup.html"
    exit 1
fi

echo ""
echo "🎉 All tests passed! The extension should work correctly."
echo ""
echo "🧠 NEW: LLM-ONLY Analysis!"
echo "- Extension uses ONLY AI (Claude 3.5 Sonnet) for analysis"
echo "- NO rule-based pattern matching fallbacks"
echo "- Comprehensive legal document analysis with consumer focus"
echo "- Fails gracefully if LLM is unavailable (no degraded fallbacks)"
echo ""
echo "📋 Installation Instructions:"
echo "1. Open Chrome and go to chrome://extensions/"
echo "2. Enable 'Developer mode'"
echo "3. Click 'Load unpacked' and select this folder"
echo "4. The extension should appear in your toolbar"
echo "5. Click the extension icon and use 'Review T&C' button"
echo ""
echo "🔧 Troubleshooting:"
echo "- Make sure the API server is running on http://localhost:8000"
echo "- Check Chrome DevTools console for any JavaScript errors"
echo "- Verify the extension has permission to access the current tab"
echo "- If you see connection errors, try reloading the extension"
echo "- Run debug_extension.js in Chrome DevTools console for detailed diagnostics"
