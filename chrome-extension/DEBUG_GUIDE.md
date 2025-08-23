# Chrome Extension Debug Guide

## 🔍 **Debugging the Connection Error**

The extension now has comprehensive logging to help debug any connection issues.

### **How to Debug**

1. **Open Chrome DevTools**:
   - Right-click on the extension popup
   - Select "Inspect" 
   - Go to the "Console" tab

2. **Click "Review T&C" and watch console logs**:
   - Look for messages with emojis (🚀, 📨, ❌, etc.)
   - These will show exactly what's happening

### **Console Log Messages to Look For**

#### **Popup.js Logs (Frontend)**
```
🚀 Sending message to background script for tab: [ID] URL: [URL]
📨 Received response from background script: [response]
❌ Chrome runtime error: [error details]
❌ Response is undefined - background script may not be running
```

#### **Background.js Logs (Backend)**
```
🔍 Handling analyzeCurrentPage request: [request details]
📝 Sender info: [sender details]
📋 Initial tab info - ID: [ID] URL: [URL]
🌐 Starting analysis for URL: [URL]
📄 Scraping completed!
📊 Content length: [number]
📝 Title: [page title]
🔍 Content preview (first 500 chars): [content preview]
🤖 Starting LLM analysis...
✅ Analysis completed successfully: [results]
❌ Error in handleAnalyzeCurrentPage: [error]
```

## 🚨 **Enhanced Gotcha Detection**

The LLM prompt now focuses specifically on **identifying traps and gotchas** in T&C:

### **What the AI Now Looks For**

#### **🎯 Hidden Gotchas & Traps**
- Automatic renewals with difficult cancellation
- Hidden fees or charges buried in text
- Broad data collection beyond user expectations
- Terms allowing unilateral changes without notice
- Clauses that waive important user rights
- Forced arbitration preventing class action lawsuits
- Broad content licensing users don't realize they're granting

#### **🚩 Deceptive Practices**
- Important terms buried in dense legal text
- Misleading headings that don't match content
- Terms that contradict marketing promises
- Vague language that favors the company
- "Free" services with hidden costs

#### **⚖️ Unfair Power Imbalances**
- Company can change terms anytime, user cannot
- Company has broad termination rights, user has none
- All liability on user, company disclaims everything
- Company owns user-generated content permanently

### **Example Analysis Output**

For terms containing gotchas, you'll now see:

```json
{
  "riskLevel": "high",
  "summary": "These terms contain major red flags: permanent license to user content and ability to change terms without notice.",
  "keyFindings": [
    "Perpetual, irrevocable license to all user content",
    "Unilateral right to change terms without notice"
  ],
  "redFlags": [
    "🚨 'Perpetual, irrevocable license' means users can never revoke content permissions",
    "🚨 Company can change terms 'at any time without notice'"
  ],
  "recommendations": [
    "Do not upload valuable content you want to maintain control over",
    "Regularly check terms for changes since no notice will be given"
  ]
}
```

## 🔧 **Content Parsing Debug**

The extension now logs detailed information about scraped content:

### **What Gets Logged**
- **Content Length**: How much text was scraped
- **Page Title**: The title of the webpage
- **Content Preview**: First 500 characters of scraped content
- **Full Data Structure**: Complete scraped data object

### **Common Issues & Solutions**

#### **Issue**: "No content available to analyze"
**Debug**: Check console for content length = 0
**Solutions**:
- Page might be JavaScript-heavy (SPA)
- Content might be behind login/paywall
- Page might be blocking scraping

#### **Issue**: "LLM analysis failed"
**Debug**: Look for API error messages
**Solutions**:
- Check Anthropic API key is set
- Verify API server is running
- Check for rate limiting

#### **Issue**: "Extension connection error"
**Debug**: Look for Chrome runtime errors
**Solutions**:
- Reload the extension
- Refresh the webpage
- Check extension permissions

## 🧪 **Testing the Enhanced Extension**

### **Test with Known Problematic Terms**
Try these URLs to test gotcha detection:
- Instagram Terms (content licensing gotchas)
- Netflix Terms (automatic renewal gotchas) 
- Discord Terms (arbitration gotchas)
- Facebook Terms (data usage gotchas)

### **Expected Behavior**
- **High Risk Level**: For terms with major gotchas
- **Specific Red Flags**: Exact problematic language quoted
- **Actionable Recommendations**: What users should do to protect themselves
- **Consumer Focus**: Analysis written for average users, not lawyers

## 📋 **Troubleshooting Checklist**

1. **✅ API Server Running**: `curl http://localhost:8000/` should return success
2. **✅ Extension Loaded**: Check chrome://extensions/ 
3. **✅ Permissions Granted**: Extension should have activeTab permission
4. **✅ Console Logs**: No JavaScript errors in DevTools
5. **✅ Background Script**: Should see logging messages when clicking button
6. **✅ API Key**: Anthropic key should be set in .env file

## 🎯 **Success Indicators**

When working correctly, you should see:
- Rich console logging with emoji indicators
- Detailed content parsing information
- Gotcha-focused analysis results
- Specific red flags and recommendations
- Consumer-protection oriented language

The extension now prioritizes **protecting users from being taken advantage of** rather than just identifying legal documents!
