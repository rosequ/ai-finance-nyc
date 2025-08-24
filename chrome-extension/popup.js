// Enhanced popup script for AI Terms & Conditions Analyzer

document.addEventListener('DOMContentLoaded', function() {
    console.log('Personal Financial Advisor popup loaded');
    
    // Configuration
    const API_BASE_URL = 'http://localhost:8000';
    
    // Get DOM elements
    const elements = {
        analyzeBtn: document.getElementById('analyze-btn'),
        loading: document.getElementById('loading'),
        loadingText: document.getElementById('loading-text'),
        error: document.getElementById('error'),
        errorText: document.getElementById('error-text'),
        results: document.getElementById('results'),
        pageTitle: document.getElementById('page-title'),
        pageUrl: document.getElementById('page-url'),
        productInfo: document.getElementById('product-info'),
        termsAnalysis: document.getElementById('terms-analysis'),
        redditInsights: document.getElementById('reddit-insights'),
        apiStatus: document.getElementById('api-status')
    };
    
    // Initialize
    init();
    
    async function init() {
        await loadCurrentPageInfo();
        await checkApiStatus();
        setupEventListeners();
    }
    
    function setupEventListeners() {
        elements.analyzeBtn.addEventListener('click', analyzeCurrentPage);
    }
    
    async function loadCurrentPageInfo() {
        try {
            const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
            if (tabs.length > 0) {
                const tab = tabs[0];
                elements.pageTitle.textContent = tab.title || 'No title';
                elements.pageUrl.textContent = tab.url || 'No URL';
            }
        } catch (err) {
            console.error('Error loading page info:', err);
            elements.pageTitle.textContent = 'Error loading page info';
            elements.pageUrl.textContent = 'Error';
        }
    }
    
    async function checkApiStatus() {
        try {
            const response = await fetch(`${API_BASE_URL}/test`);
            if (response.ok) {
                const data = await response.json();
                showApiStatus('API Ready', 'success');
                console.log('✅ API connection successful:', data);
            } else {
                showApiStatus('API Error', 'error');
            }
        } catch (error) {
            console.error('API check failed:', error);
            showApiStatus('API Offline', 'error');
        }
    }
    
    async function analyzeCurrentPage() {
        showLoading('Extracting page content...');
        hideError();
        hideResults();
        
        try {
            // Step 1: Get page content from content script
            const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
            if (tabs.length === 0) {
                throw new Error('No active tab found');
            }
            
            const tab = tabs[0];
            console.log('📄 Extracting content from:', tab.url);
            
            const contentResponse = await new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    reject(new Error('Timeout - content script not responding'));
                }, 10000);
                
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
            
            if (!contentResponse.content) {
                throw new Error('No content extracted from page');
            }
            
            console.log('📄 Content extracted, length:', contentResponse.content.length);
            
            // Step 2: Send content to AI analysis API
            showLoading('Analyzing with AI...');
            
            const analysisResponse = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: contentResponse.content,
                    page_title: tab.title,
                    page_url: tab.url
                })
            });
            
            if (!analysisResponse.ok) {
                const errorData = await analysisResponse.json();
                throw new Error(errorData.error || `API error: ${analysisResponse.status}`);
            }
            
            const analysisData = await analysisResponse.json();
            console.log('🤖 Analysis response:', analysisData);
            
            if (!analysisData.success) {
                throw new Error(analysisData.error || 'Analysis failed');
            }
            
            // Step 3: Display results
            displayAnalysisResults(analysisData.data);
            
        } catch (err) {
            console.error('❌ Analysis error:', err);
            let errorMessage = err.message;
            
            // Provide more helpful error messages
            if (errorMessage.includes('Could not establish connection')) {
                errorMessage = 'Cannot connect to page. Try refreshing the page and trying again.';
            } else if (errorMessage.includes('Receiving end does not exist')) {
                errorMessage = 'Content script not loaded. Try refreshing the page.';
            } else if (errorMessage.includes('Failed to fetch')) {
                errorMessage = 'Cannot connect to AI API. Make sure the server is running on localhost:8000';
            }
            
            showError(errorMessage);
        } finally {
            hideLoading();
        }
    }
    
    function displayAnalysisResults(data) {
        console.log('📊 Displaying analysis results:', data);
        
        // Product Information
        if (data.product_info) {
            const productInfo = data.product_info;
            elements.productInfo.innerHTML = `
                <div class="product-item">
                    <span class="product-label">Product:</span>
                    <span class="product-value">${productInfo.name || 'Not specified'}</span>
                </div>
                <div class="product-item">
                    <span class="product-label">Type:</span>
                    <span class="product-value">${productInfo.type || 'Not specified'}</span>
                </div>
                <div class="product-item">
                    <span class="product-label">Company:</span>
                    <span class="product-value">${productInfo.company || 'Not specified'}</span>
                </div>
            `;
        }
        
        // Terms Analysis
        if (data.terms_analysis) {
            const analysis = data.terms_analysis;
            let termsHtml = '';
            
            // Consumer Score
            if (analysis.consumer_score) {
                termsHtml += `<div style="margin-bottom: 15px;"><strong>Consumer Score:</strong><br>${formatMarkdown(analysis.consumer_score)}</div>`;
            }
            
            // Key Information
            if (analysis.key_information) {
                termsHtml += `<h4>📋 Key Information</h4><div>${formatMarkdown(analysis.key_information)}</div>`;
            }
            
            // Risks
            if (analysis.risks) {
                termsHtml += `<h4>⚠️ Risks & Concerns</h4><div>${formatMarkdown(analysis.risks)}</div>`;
            }
            
            // Details
            if (analysis.details) {
                termsHtml += `<h4>📖 Additional Details</h4><div>${formatMarkdown(analysis.details)}</div>`;
            }
            
            elements.termsAnalysis.innerHTML = termsHtml;
        }
        
        // Reddit Insights
        if (data.reddit_insights) {
            const insights = data.reddit_insights;
            let redditHtml = '';
            
            if (insights.positive) {
                redditHtml += `
                    <div class="insight-box insight-positive">
                        <div class="insight-title">👍 Positive Feedback</div>
                        <div>${formatMarkdown(insights.positive)}</div>
                    </div>
                `;
            }
            
            if (insights.negative) {
                redditHtml += `
                    <div class="insight-box insight-negative">
                        <div class="insight-title">👎 Concerns & Issues</div>
                        <div>${formatMarkdown(insights.negative)}</div>
                    </div>
                `;
            }
            
            if (!insights.positive && !insights.negative) {
                redditHtml = '<div style="text-align: center; color: #666; padding: 20px;">No Reddit discussions found for this product.</div>';
            }
            
            elements.redditInsights.innerHTML = redditHtml;
        }
        
        showResults();
    }
    
    // UI helper functions
    function showLoading(message) {
        elements.loadingText.textContent = message;
        elements.loading.style.display = 'block';
        elements.analyzeBtn.disabled = true;
        elements.analyzeBtn.textContent = '⏳ Analyzing...';
    }
    
    function hideLoading() {
        elements.loading.style.display = 'none';
        elements.analyzeBtn.disabled = false;
        elements.analyzeBtn.textContent = '🔍 Get Financial Analysis';
    }
    
    function showError(message) {
        elements.errorText.textContent = message;
        elements.error.style.display = 'block';
    }
    
    function hideError() {
        elements.error.style.display = 'none';
    }
    
    function showResults() {
        elements.results.style.display = 'block';
    }
    
    function hideResults() {
        elements.results.style.display = 'none';
    }
    
    function showApiStatus(message, type) {
        const statusElement = elements.apiStatus;
        const dotElement = statusElement.querySelector('.status-dot');
        
        statusElement.innerHTML = `<span class="status-dot status-${type}"></span>${message}`;
    }
    
    function formatMarkdown(text) {
        if (!text) return '';
        
        // Split into sections to handle different formatting
        let formatted = text
            // Convert **bold** to <strong> (handle nested formatting)
            .replace(/\*\*([^*]+(?:\*[^*]*\*[^*]*)*)\*\*/g, '<strong>$1</strong>')
            // Handle bullet points at start of lines
            .replace(/^[\s]*[•\-\*]\s+(.+)$/gm, '<li>$1</li>')
            // Handle numbered lists
            .replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>')
            // Convert double line breaks to paragraph breaks
            .replace(/\n\s*\n/g, '|||PARAGRAPH|||')
            // Convert single line breaks to <br>
            .replace(/\n/g, '<br>')
            // Restore paragraph breaks
            .replace(/\|\|\|PARAGRAPH\|\|\|/g, '</p><p>')
            // Handle **[RISK LEVEL]** patterns specially
            .replace(/\*\*\[([^\]]+)\]\*\*/g, '<span class="risk-badge risk-$1"><strong>[$1]</strong></span>')
            // Handle **Pro:** and **Con:** specially  
            .replace(/\*\*(Pro|Con):\*\*/g, '<strong class="pro-con-label">$1:</strong>')
            // Handle **Impact:** specially
            .replace(/\*\*Impact:\*\*/g, '<strong class="impact-label">Impact:</strong>');
        
        // Wrap consecutive list items in <ul> tags
        formatted = formatted.replace(/(<li>.*?<\/li>)(\s*<li>.*?<\/li>)*/gs, function(match) {
            return '<ul>' + match + '</ul>';
        });
        
        // Wrap everything in paragraphs if not already wrapped
        if (!formatted.includes('<p>') && !formatted.includes('<ul>')) {
            formatted = '<p>' + formatted + '</p>';
        } else if (!formatted.startsWith('<p>') && !formatted.startsWith('<ul>')) {
            formatted = '<p>' + formatted;
        }
        
        if (!formatted.endsWith('</p>') && !formatted.endsWith('</ul>')) {
            formatted = formatted + '</p>';
        }
        
        return formatted
            // Clean up empty paragraphs
            .replace(/<p><\/p>/g, '')
            .replace(/<p>\s*<\/p>/g, '')
            .replace(/<p>(<ul>.*?<\/ul>)<\/p>/gs, '$1')
            // Fix spacing issues
            .replace(/<\/li><br>/g, '</li>')
            .replace(/<br><li>/g, '<li>')
            .trim();
    }
});