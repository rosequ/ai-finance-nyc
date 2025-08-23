// Content script for Terms & Conditions Analyzer

// Inject analysis tools into the page
(function() {
  'use strict';
  
  console.log('Terms & Conditions Analyzer content script loaded');
  
  // Track if analysis overlay is active
  let analysisOverlayActive = false;
  let analysisResults = null;
  
  // Listen for messages from popup and background script
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getPageInfo') {
      sendResponse({
        url: window.location.href,
        title: document.title,
        domain: window.location.hostname
      });
    }
    
    if (request.action === 'extractPageContent') {
      const content = extractPageContent();
      sendResponse({ content: content });
    }
    
    if (request.action === 'showAnalysisOverlay') {
      showAnalysisOverlay(request.analysis);
      sendResponse({ success: true });
    }
    
    if (request.action === 'hideAnalysisOverlay') {
      hideAnalysisOverlay();
      sendResponse({ success: true });
    }
    
    if (request.action === 'highlightTermsIndicators') {
      highlightTermsIndicators();
      sendResponse({ success: true });
    }
  });
  
  // Extract meaningful content from the page
  function extractPageContent() {
    // Remove script and style elements
    const elementsToRemove = document.querySelectorAll('script, style, noscript, nav, header, footer, .ads, .advertisement');
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = document.body.innerHTML;
    
    tempDiv.querySelectorAll('script, style, noscript, nav, header, footer, .ads, .advertisement').forEach(el => el.remove());
    
    // Try to find main content areas
    const mainSelectors = [
      'main',
      '[role="main"]',
      '.content',
      '.main-content', 
      '.page-content',
      '.post-content',
      '.article-content',
      '.terms',
      '.legal',
      '.agreement'
    ];
    
    let mainContent = null;
    for (const selector of mainSelectors) {
      const element = tempDiv.querySelector(selector);
      if (element && element.textContent.trim().length > 500) {
        mainContent = element;
        break;
      }
    }
    
    // If no main content found, use body but filter out navigation
    if (!mainContent) {
      mainContent = tempDiv;
    }
    
    // Extract text content
    const text = mainContent.textContent || mainContent.innerText || '';
    
    // Clean up the text
    return text
      .replace(/\s+/g, ' ') // Replace multiple whitespace with single space
      .replace(/\n\s*\n/g, '\n') // Remove empty lines
      .trim();
  }
  
  // Show analysis overlay on the page
  function showAnalysisOverlay(analysis) {
    if (analysisOverlayActive) {
      hideAnalysisOverlay();
    }
    
    analysisResults = analysis;
    
    // Create overlay container
    const overlay = document.createElement('div');
    overlay.id = 'tc-analyzer-overlay';
    overlay.innerHTML = createOverlayHTML(analysis);
    
    // Add styles
    const style = document.createElement('style');
    style.textContent = getOverlayCSS();
    document.head.appendChild(style);
    
    // Add overlay to page
    document.body.appendChild(overlay);
    
    // Add event listeners
    setupOverlayEventListeners();
    
    analysisOverlayActive = true;
    
    // Auto-hide after 10 seconds if not interacted with
    setTimeout(() => {
      if (analysisOverlayActive && !overlay.querySelector(':hover')) {
        hideAnalysisOverlay();
      }
    }, 10000);
  }
  
  // Hide analysis overlay
  function hideAnalysisOverlay() {
    const overlay = document.getElementById('tc-analyzer-overlay');
    if (overlay) {
      overlay.remove();
    }
    
    // Remove highlights
    removeHighlights();
    
    analysisOverlayActive = false;
  }
  
  // Create HTML for the analysis overlay
  function createOverlayHTML(analysis) {
    const isTermsPage = analysis.isTermsPage;
    const confidence = analysis.confidence;
    const statusColor = isTermsPage ? '#28a745' : '#ffc107';
    const statusIcon = isTermsPage ? '✓' : '⚠';
    
    return `
      <div class="tc-overlay-content">
        <div class="tc-overlay-header">
          <div class="tc-status" style="background-color: ${statusColor}">
            <span class="tc-status-icon">${statusIcon}</span>
            <span class="tc-status-text">
              ${isTermsPage ? 'Terms & Conditions Detected' : 'Not a Terms Page'}
            </span>
          </div>
          <button class="tc-close-btn" onclick="this.closest('#tc-analyzer-overlay').remove()">×</button>
        </div>
        
        <div class="tc-overlay-body">
          <div class="tc-confidence">
            <strong>Confidence:</strong> ${confidence.toFixed(1)}%
            <div class="tc-confidence-bar">
              <div class="tc-confidence-fill" style="width: ${confidence}%"></div>
            </div>
          </div>
          
          <div class="tc-summary">
            <strong>Analysis:</strong> ${analysis.summary}
          </div>
          
          <div class="tc-details">
            <strong>Content:</strong> ${analysis.contentLength.toLocaleString()} characters, 
            ${analysis.wordCount.toLocaleString()} words
          </div>
          
          ${analysis.indicators.length > 0 ? `
            <div class="tc-indicators">
              <strong>Found Indicators:</strong>
              <div class="tc-indicator-list">
                ${analysis.indicators.slice(0, 5).map(indicator => `
                  <span class="tc-indicator" data-phrase="${indicator.phrase}">
                    ${indicator.phrase} (${indicator.type})
                  </span>
                `).join('')}
                ${analysis.indicators.length > 5 ? `<span class="tc-more">+${analysis.indicators.length - 5} more</span>` : ''}
              </div>
            </div>
          ` : ''}
          
          <div class="tc-actions">
            <button class="tc-btn tc-btn-primary" onclick="chrome.runtime.sendMessage({action: 'openPopup'})">
              Full Analysis
            </button>
            <button class="tc-btn tc-btn-secondary" id="tc-highlight-btn">
              Highlight Terms
            </button>
          </div>
        </div>
      </div>
    `;
  }
  
  // CSS for the overlay
  function getOverlayCSS() {
    return `
      #tc-analyzer-overlay {
        position: fixed;
        top: 20px;
        right: 20px;
        width: 350px;
        max-width: 90vw;
        background: white;
        border: 2px solid #007bff;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        line-height: 1.4;
      }
      
      .tc-overlay-content {
        padding: 0;
      }
      
      .tc-overlay-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 15px;
        background: #f8f9fa;
        border-bottom: 1px solid #e9ecef;
        border-radius: 8px 8px 0 0;
      }
      
      .tc-status {
        display: flex;
        align-items: center;
        padding: 5px 10px;
        border-radius: 15px;
        color: white;
        font-weight: bold;
        font-size: 12px;
      }
      
      .tc-status-icon {
        margin-right: 5px;
      }
      
      .tc-close-btn {
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
        color: #6c757d;
        padding: 0;
        width: 25px;
        height: 25px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .tc-close-btn:hover {
        background: #e9ecef;
        border-radius: 50%;
      }
      
      .tc-overlay-body {
        padding: 15px;
      }
      
      .tc-confidence {
        margin-bottom: 12px;
      }
      
      .tc-confidence-bar {
        width: 100%;
        height: 6px;
        background: #e9ecef;
        border-radius: 3px;
        margin-top: 5px;
        overflow: hidden;
      }
      
      .tc-confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #dc3545 0%, #ffc107 50%, #28a745 100%);
        transition: width 0.3s ease;
      }
      
      .tc-summary {
        margin-bottom: 12px;
        color: #495057;
      }
      
      .tc-details {
        margin-bottom: 12px;
        color: #6c757d;
        font-size: 12px;
      }
      
      .tc-indicators {
        margin-bottom: 15px;
      }
      
      .tc-indicator-list {
        margin-top: 5px;
      }
      
      .tc-indicator {
        display: inline-block;
        background: #e7f3ff;
        color: #0056b3;
        padding: 2px 6px;
        border-radius: 10px;
        font-size: 11px;
        margin: 2px;
        cursor: pointer;
      }
      
      .tc-indicator:hover {
        background: #cce7ff;
      }
      
      .tc-more {
        color: #6c757d;
        font-style: italic;
        font-size: 11px;
      }
      
      .tc-actions {
        display: flex;
        gap: 8px;
      }
      
      .tc-btn {
        flex: 1;
        padding: 8px 12px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 12px;
        font-weight: 500;
        transition: all 0.2s ease;
      }
      
      .tc-btn-primary {
        background: #007bff;
        color: white;
      }
      
      .tc-btn-primary:hover {
        background: #0056b3;
      }
      
      .tc-btn-secondary {
        background: #6c757d;
        color: white;
      }
      
      .tc-btn-secondary:hover {
        background: #545b62;
      }
      
      .tc-highlight {
        background: yellow !important;
        padding: 2px 4px !important;
        border-radius: 3px !important;
        box-shadow: 0 0 3px rgba(255,255,0,0.5) !important;
      }
    `;
  }
  
  // Set up event listeners for the overlay
  function setupOverlayEventListeners() {
    // Highlight button
    const highlightBtn = document.getElementById('tc-highlight-btn');
    if (highlightBtn) {
      highlightBtn.addEventListener('click', highlightTermsIndicators);
    }
    
    // Indicator clicking
    document.querySelectorAll('.tc-indicator').forEach(indicator => {
      indicator.addEventListener('click', function() {
        const phrase = this.dataset.phrase;
        highlightSpecificPhrase(phrase);
      });
    });
  }
  
  // Highlight terms and conditions indicators on the page
  function highlightTermsIndicators() {
    if (!analysisResults || !analysisResults.indicators) return;
    
    const indicators = analysisResults.indicators;
    const phrases = indicators.map(i => i.phrase).slice(0, 10); // Limit to avoid performance issues
    
    phrases.forEach(phrase => {
      highlightSpecificPhrase(phrase);
    });
  }
  
  // Highlight a specific phrase on the page
  function highlightSpecificPhrase(phrase) {
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      null,
      false
    );
    
    const textNodes = [];
    let node;
    
    while (node = walker.nextNode()) {
      if (node.nodeValue.toLowerCase().includes(phrase.toLowerCase())) {
        textNodes.push(node);
      }
    }
    
    textNodes.forEach(textNode => {
      const parent = textNode.parentNode;
      if (parent && parent.tagName !== 'SCRIPT' && parent.tagName !== 'STYLE') {
        const text = textNode.nodeValue;
        const regex = new RegExp(`(${phrase})`, 'gi');
        const highlightedText = text.replace(regex, '<span class="tc-highlight">$1</span>');
        
        if (highlightedText !== text) {
          const wrapper = document.createElement('span');
          wrapper.innerHTML = highlightedText;
          parent.replaceChild(wrapper, textNode);
        }
      }
    });
  }
  
  // Remove all highlights
  function removeHighlights() {
    document.querySelectorAll('.tc-highlight').forEach(highlight => {
      const parent = highlight.parentNode;
      if (parent) {
        parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
        parent.normalize(); // Merge adjacent text nodes
      }
    });
  }
  
  // Add floating action button for quick access
  function addFloatingButton() {
    const button = document.createElement('button');
    button.id = 'tc-analyzer-fab';
    button.innerHTML = '📋';
    button.title = 'Analyze Terms & Conditions';
    button.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 50px;
      height: 50px;
      border-radius: 50%;
      background: #007bff;
      color: white;
      border: none;
      font-size: 20px;
      cursor: pointer;
      box-shadow: 0 4px 20px rgba(0,123,255,0.3);
      z-index: 9999;
      transition: all 0.3s ease;
    `;
    
    button.addEventListener('click', () => {
      chrome.runtime.sendMessage({ action: 'analyzeCurrentPage' });
    });
    
    button.addEventListener('mouseenter', () => {
      button.style.transform = 'scale(1.1)';
    });
    
    button.addEventListener('mouseleave', () => {
      button.style.transform = 'scale(1)';
    });
    
    document.body.appendChild(button);
  }
  
  // Initialize - add floating button after page loads
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addFloatingButton);
  } else {
    addFloatingButton();
  }
  
})();
