// Content script for AI Terms & Conditions Analyzer

console.log('Personal Financial Guardian content script loaded');

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

// Extract text content from the page with enhanced filtering
function extractPageContent() {
    // Create a copy of the document to work with
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = document.body.innerHTML;
    
    // Remove unwanted elements that don't contain meaningful content
    const unwantedSelectors = [
        'script', 'style', 'noscript', 'iframe', 'embed', 'object',
        'nav', 'header', 'footer', 'aside', 
        '.ads', '.advertisement', '.ad', '.banner', '.ad-container',
        '.navigation', '.nav', '.menu', '.sidebar', '.widget',
        '.social', '.share', '.comment', '.comments', '.discussion',
        '.related', '.recommended', '.suggestions',
        '[class*="ad-"]', '[id*="ad-"]', '[class*="ads-"]',
        '[class*="social"]', '[class*="share"]', '[class*="follow"]',
        '.cookie-notice', '.cookie-banner', '.gdpr-notice'
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
    
    // If we didn't get much content, try a more targeted approach
    if (textContent.length < 200) {
        console.log('Content too short, trying alternative extraction methods...');
        
        // Try to get content from main content areas
        const contentSelectors = [
            'main', '[role="main"]', '.main', '.content', '.main-content',
            'article', '.article', '.post', '.entry', '.document',
            '.terms', '.conditions', '.policy', '.agreement', '.contract',
            '.legal', '.privacy', '.tos', '.eula',
            '.text-content', '.page-content', '.body-content',
            'section', 'div[class*="content"]', 'div[class*="text"]'
        ];
        
        let bestContent = '';
        let bestScore = 0;
        
        for (const selector of contentSelectors) {
            const elements = document.querySelectorAll(selector);
            for (const element of elements) {
                const text = element.textContent || element.innerText || '';
                const cleanText = text.replace(/\s+/g, ' ').trim();
                
                // Score based on length and keywords that suggest terms/conditions content
                let score = cleanText.length;
                const keywords = ['terms', 'conditions', 'agreement', 'policy', 'contract', 'legal', 'privacy', 'user', 'service', 'liability', 'warranty'];
                const keywordCount = keywords.filter(keyword => 
                    cleanText.toLowerCase().includes(keyword)
                ).length;
                
                score += keywordCount * 100; // Boost score for relevant keywords
                
                if (score > bestScore && cleanText.length > 100) {
                    bestScore = score;
                    bestContent = cleanText;
                }
            }
        }
        
        if (bestContent.length > textContent.length) {
            textContent = bestContent;
            console.log('Used alternative extraction, found better content');
        }
    }
    
    // If still too short, try getting all paragraph text
    if (textContent.length < 200) {
        console.log('Still too short, extracting all paragraphs...');
        const paragraphs = document.querySelectorAll('p, div, span, td, li');
        let paragraphContent = '';
        
        paragraphs.forEach(p => {
            const text = p.textContent || p.innerText || '';
            if (text.length > 20) { // Only include substantial paragraphs
                paragraphContent += text + '\n\n';
            }
        });
        
        if (paragraphContent.length > textContent.length) {
            textContent = paragraphContent.replace(/\s+/g, ' ').replace(/\n\s*\n/g, '\n\n').trim();
        }
    }
    
    // Add page metadata
    const pageInfo = `Page: ${document.title}\nURL: ${window.location.href}\nDomain: ${window.location.hostname}\nExtracted: ${new Date().toISOString()}\n\n--- PAGE CONTENT ---\n\n`;
    
    const finalContent = pageInfo + textContent;
    console.log(`Final content length: ${finalContent.length} characters`);
    
    return finalContent;
}
