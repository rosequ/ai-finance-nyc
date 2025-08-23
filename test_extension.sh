#!/bin/bash

# Chrome Extension Quick Test Script
# This script helps you quickly test the Chrome extension setup

echo "🧪 Chrome Extension Testing Script"
echo "=================================="

# Check if extension files exist
echo ""
echo "📁 Checking extension files..."
EXTENSION_DIR="chrome-extension"

if [ ! -d "$EXTENSION_DIR" ]; then
    echo "❌ Extension directory not found!"
    echo "Expected: $PWD/$EXTENSION_DIR"
    exit 1
fi

# Check required files
REQUIRED_FILES=(
    "manifest.json"
    "background.js" 
    "content-script.js"
    "popup.html"
    "popup.js"
    "popup.css"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$EXTENSION_DIR/$file" ]; then
        echo "✅ $file exists"
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

# Check manifest.json syntax
echo ""
echo "🔧 Validating manifest.json..."
if python3 -m json.tool "$EXTENSION_DIR/manifest.json" > /dev/null 2>&1; then
    echo "✅ manifest.json is valid JSON"
else
    echo "❌ manifest.json has syntax errors"
fi


# Final instructions
echo ""
echo "🚀 Next Steps:"
echo "1. Open Chrome and go to chrome://extensions/"
echo "2. Enable 'Developer mode' (toggle in top-right)"
echo "3. Click 'Load unpacked'"
echo "4. Select the 'chrome-extension' folder from this directory:"
echo "   $PWD/chrome-extension"
echo "5. Pin the extension and start testing!"
echo ""
echo "📋 Test URLs to try:"
echo "   • https://www.netflix.com/legal/termsofuse"
echo "   • https://policies.google.com/terms"
echo "   • https://www.apple.com/legal/internet-services/terms/site.html"
echo ""
echo "📖 For detailed testing instructions, see:"
echo "   chrome-extension/TESTING_GUIDE.md"
