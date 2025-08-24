// Simple popup script for Terms & Conditions Analyzer

document.addEventListener('DOMContentLoaded', function() {
    console.log('Simple Terms & Conditions Analyzer popup loaded');
    
    // Get DOM elements
    const analyzeBtn = document.getElementById('analyze-btn');
    const contentArea = document.getElementById('content-area');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const errorText = document.getElementById('error-text');
    const pageTitle = document.getElementById('page-title');
    const pageUrl = document.getElementById('page-url');
    
    // Load current page info
    loadCurrentPageInfo();
    
    // Set up analyze button
    analyzeBtn.addEventListener('click', analyzeCurrentPage);
    
    async function loadCurrentPageInfo() {
        try {
            const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
            if (tabs.length > 0) {
                const tab = tabs[0];
                pageTitle.textContent = tab.title || 'No title';
                pageUrl.textContent = tab.url || 'No URL';
            }
        } catch (err) {
            console.error('Error loading page info:', err);
            pageTitle.textContent = 'Error loading page info';
            pageUrl.textContent = 'Error';
        }
    }
    
    async function analyzeCurrentPage() {
        // Show loading state
        showLoading();
        hideError();
        hideContent();
        
        try {
            // Get the current active tab
            const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
            if (tabs.length === 0) {
                throw new Error('No active tab found');
            }
            
            const tab = tabs[0];
            console.log('Extracting content from tab:', tab.id, 'URL:', tab.url);
            
            // Send message to content script to extract page content
            const response = await new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    reject(new Error('Timeout - content script not responding'));
                }, 10000); // 10 second timeout
                
                chrome.tabs.sendMessage(tab.id, { action: 'extractPageContent' }, (response) => {
                    clearTimeout(timeout);
                    
                    if (chrome.runtime.lastError) {
                        reject(new Error(chrome.runtime.lastError.message));
                        return;
                    }
                    
                    if (!response) {
                        reject(new Error('No response from content script'));
                        return;
                    }
                    
                    resolve(response);
                });
            });
            
            if (response.content) {
                showContent(response.content);
            } else {
                throw new Error('No content extracted from page');
            }
            
        } catch (err) {
            console.error('Error analyzing page:', err);
            let errorMessage = err.message;
            
            // Provide more helpful error messages
            if (errorMessage.includes('Could not establish connection')) {
                errorMessage = 'Cannot connect to page. Try refreshing the page and trying again.';
            } else if (errorMessage.includes('Receiving end does not exist')) {
                errorMessage = 'Content script not loaded. Try refreshing the page.';
            }
            
            showError(errorMessage);
        } finally {
            hideLoading();
        }
    }
    
    function showLoading() {
        loading.style.display = 'block';
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = '⏳ Analyzing...';
    }
    
    function hideLoading() {
        loading.style.display = 'none';
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = '🔍 Analyze Terms & Conditions';
    }
    
    function showContent(content) {
        contentArea.textContent = content;
        contentArea.style.display = 'block';
    }
    
    function hideContent() {
        contentArea.style.display = 'none';
    }
    
    function showError(message) {
        errorText.textContent = message;
        error.style.display = 'block';
    }
    
    function hideError() {
        error.style.display = 'none';
    }
});