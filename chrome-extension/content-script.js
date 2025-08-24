// Simple content script for Terms & Conditions Analyzer

console.log('Simple Terms & Conditions Analyzer content script loaded');

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Content script received message:', request);
    
    if (request.action === 'extractPageContent') {
        try {
            const content = extractPageContent();
            console.log('Extracted content length:', content.length);
            sendResponse({ content: content });
        } catch (error) {
            console.error('Error extracting content:', error);
            sendResponse({ content: null, error: error.message });
        }
    }
    
    return true; // Keep the message channel open for async response
});

// Extract text content from the page
function extractPageContent() {
    // Create a copy of the document to work with
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = document.body.innerHTML;
    
    // Remove unwanted elements
    const unwantedSelectors = [
        'script', 'style', 'noscript', 'iframe',
        'nav', 'header', 'footer', 'aside',
        '.ads', '.advertisement', '.ad', '.banner',
        '.navigation', '.nav', '.menu', '.sidebar',
        '.social', '.share', '.comment', '.comments',
        '[class*="ad-"]', '[id*="ad-"]', '[class*="ads-"]'
    ];
    
    unwantedSelectors.forEach(selector => {
        const elements = tempDiv.querySelectorAll(selector);
        elements.forEach(el => el.remove());
    });
    
    // Get text content
    let textContent = tempDiv.textContent || tempDiv.innerText || '';
    
    // Clean up the text
    textContent = textContent
        .replace(/\s+/g, ' ')  // Replace multiple whitespace with single space
        .replace(/\n\s*\n/g, '\n\n')  // Keep paragraph breaks
        .trim();
    
    // If we didn't get much content, try a different approach
    if (textContent.length < 100) {
        // Try to get content from main content areas
        const contentSelectors = [
            'main', '[role="main"]', '.main', '.content', '.main-content',
            'article', '.article', '.post', '.entry',
            '.terms', '.conditions', '.policy', '.agreement',
            'p', 'div', 'section'
        ];
        
        let alternativeContent = '';
        for (const selector of contentSelectors) {
            const elements = document.querySelectorAll(selector);
            for (const element of elements) {
                const text = element.textContent || element.innerText || '';
                if (text.length > alternativeContent.length) {
                    alternativeContent = text;
                }
            }
            if (alternativeContent.length > 100) break;
        }
        
        if (alternativeContent.length > textContent.length) {
            textContent = alternativeContent
                .replace(/\s+/g, ' ')
                .replace(/\n\s*\n/g, '\n\n')
                .trim();
        }
    }
    
    // Add page metadata
    const pageInfo = `Page: ${document.title}\nURL: ${window.location.href}\nDomain: ${window.location.hostname}\n\n--- PAGE CONTENT ---\n\n`;
    
    return pageInfo + textContent;
}