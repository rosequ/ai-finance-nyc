#!/bin/bash

# Simple Chrome Extension Test Script - T&C Analysis Focus Only
# This script tests only the core T&C analysis functionality

echo "📋 Simple T&C Extension Testing"
echo "================================"
echo "Focus: Terms & Conditions analysis only (no external search)"
echo ""

# Check if backend server is running
echo "📡 Testing backend server (T&C analysis endpoints only)..."
if curl -s http://localhost:8000/ | grep -q "AI Finance NYC API is running"; then
    echo "✅ Backend server is running on port 8000"
else
    echo "❌ Backend server is not running!"
    echo "💡 Start it with: make dev-server"
    echo "   Then run this test script again"
    exit 1
fi

# Test only the scrape endpoint (core functionality)
echo ""
echo "🔍 Testing core scraping endpoint..."

SCRAPE_RESPONSE=$(curl -s -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html"}')

if echo "$SCRAPE_RESPONSE" | grep -q "status"; then
    echo "✅ /scrape endpoint working (core T&C analysis functionality)"
else
    echo "❌ /scrape endpoint failed"
    echo "This is required for T&C analysis"
fi

# Check extension files
echo ""
echo "📁 Checking extension files..."
EXTENSION_DIR="chrome-extension"

if [ ! -d "$EXTENSION_DIR" ]; then
    echo "❌ Extension directory not found!"
    exit 1
fi

# Check core files needed for T&C analysis
CORE_FILES=(
    "manifest.json"
    "background.js" 
    "content-script.js"
    "popup.html"
    "popup.js"
    "popup.css"
)

echo "Checking core T&C analysis files:"
for file in "${CORE_FILES[@]}"; do
    if [ -f "$EXTENSION_DIR/$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
    fi
done

# Check icons
if [ -d "$EXTENSION_DIR/icons" ] && [ -f "$EXTENSION_DIR/icons/icon-16.svg" ]; then
    echo "✅ Extension icons present"
else
    echo "❌ Extension icons missing"
fi

# Validate manifest
echo ""
echo "🔧 Validating manifest.json..."
if python3 -m json.tool "$EXTENSION_DIR/manifest.json" > /dev/null 2>&1; then
    echo "✅ manifest.json is valid"
else
    echo "❌ manifest.json has syntax errors"
fi

# Environment check (simplified)
echo ""
echo "🔧 Environment check..."
if [ -f ".env" ]; then
    if grep -q "ANTHROPIC_API_KEY" .env; then
        echo "✅ ANTHROPIC_API_KEY found (for content analysis)"
    else
        echo "⚠️  ANTHROPIC_API_KEY missing (T&C analysis may be limited)"
    fi
    
    # Note: BRAVE_API_KEY not needed for simple T&C analysis
    if grep -q "BRAVE_API_KEY" .env; then
        echo "ℹ️  BRAVE_API_KEY found (not needed for basic T&C analysis)"
    fi
else
    echo "⚠️  .env file not found"
fi

echo ""
echo "🧪 T&C Analysis Testing Guide:"
echo "================================"
echo ""
echo "📋 Step 1: Load Extension"
echo "   • Chrome → chrome://extensions/"
echo "   • Enable 'Developer mode'"
echo "   • Click 'Load unpacked'"
echo "   • Select: $PWD/chrome-extension"
echo ""
echo "📋 Step 2: Test Known Terms Pages"
echo "   Try these URLs for HIGH confidence detection:"
echo "   • https://www.netflix.com/legal/termsofuse"
echo "   • https://policies.google.com/terms"
echo "   • https://www.apple.com/legal/internet-services/terms/site.html"
echo "   Expected: 80%+ confidence, 'Terms & Conditions Page'"
echo ""
echo "📋 Step 3: Test Non-Terms Pages"
echo "   Try these URLs for LOW confidence detection:"
echo "   • https://www.google.com (homepage)"
echo "   • https://www.netflix.com (homepage)"
echo "   • https://news.ycombinator.com"
echo "   Expected: <30% confidence, 'Not a Terms Page'"
echo ""
echo "📋 Step 4: Test Visual Highlighting"
echo "   • Analyze a terms page"
echo "   • Click 'Highlight Terms'"
echo "   • Look for yellow highlighting on key terms"
echo ""
echo "📋 Step 5: Test Custom URL Analysis"
echo "   • Enter custom URL: https://www.dropbox.com/terms"
echo "   • Click 'Analyze'"
echo "   • Should detect as terms page"
echo ""
echo "💡 Simplified Features:"
echo "   • Company search now provides search suggestions only"
echo "   • Focus on direct T&C analysis without external API calls"
echo "   • Use 'Analyze Custom URL' for specific terms pages"
echo ""
echo "📖 For detailed testing: chrome-extension/SIMPLE_TESTING.md"
echo ""
echo "✅ Ready to test T&C analysis functionality!"
