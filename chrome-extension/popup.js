// Popup script for Terms & Conditions Analyzer

document.addEventListener('DOMContentLoaded', function() {
    console.log('Terms & Conditions Analyzer popup loaded');
    
    // Get DOM elements
    const elements = {
        // Page info
        pageTitle: document.getElementById('page-title'),
        pageUrl: document.getElementById('page-url'),
        
        // Analysis result
        analysisResult: document.getElementById('analysis-result'),
        resultStatus: document.getElementById('result-status'),
        resultIcon: document.getElementById('result-icon'),
        resultText: document.getElementById('result-text'),
        resultConfidence: document.getElementById('result-confidence'),
        resultSummary: document.getElementById('result-summary'),
        resultDetails: document.getElementById('result-details'),
        
        // Buttons
        analyzeCurrentBtn: document.getElementById('analyze-current'),
        highlightTermsBtn: document.getElementById('highlight-terms'),
        analyzeUrlBtn: document.getElementById('analyze-url'),
        findTermsBtn: document.getElementById('find-terms'),
        
        // Inputs
        customUrl: document.getElementById('custom-url'),
        companyName: document.getElementById('company-name'),
        
        // Status indicators
        statusIndicator: document.getElementById('status-indicator'),
        statusText: document.querySelector('.status-text'),
        statusDot: document.querySelector('.status-dot'),
        apiStatus: document.getElementById('api-status'),
        apiDot: document.querySelector('.api-dot'),
        
        // Loading and error
        loading: document.getElementById('loading'),
        error: document.getElementById('error'),
        errorText: document.getElementById('error-text'),
        retryBtn: document.getElementById('retry-btn'),
        
        // Modal and settings
        settingsBtn: document.getElementById('settings-btn'),
        helpBtn: document.getElementById('help-btn'),
        reportBtn: document.getElementById('report-btn'),
        settingsModal: document.getElementById('settings-modal'),
        settingsClose: document.getElementById('settings-close'),
        saveSettingsBtn: document.getElementById('save-settings'),
        apiUrlInput: document.getElementById('api-url'),
        autoAnalyzeCheckbox: document.getElementById('auto-analyze'),
        showOverlayCheckbox: document.getElementById('show-overlay')
    };
    
    // State management
    let currentPageInfo = null;
    let currentAnalysis = null;
    let settings = {
        apiUrl: 'http://localhost:8000',
        autoAnalyze: true,
        showOverlay: true
    };
    
    // Initialize
    init();
    
    async function init() {
        await loadSettings();
        await checkApiStatus();
        await loadCurrentPageInfo();
        setupEventListeners();
        
        // Auto-analyze if enabled
        if (settings.autoAnalyze) {
            setTimeout(() => {
                analyzeCurrentPage();
            }, 1000);
        }
    }
    
    // Load settings from Chrome storage
    async function loadSettings() {
        try {
            const result = await chrome.storage.sync.get(['settings']);
            if (result.settings) {
                settings = { ...settings, ...result.settings };
            }
            
            // Update UI
            elements.apiUrlInput.value = settings.apiUrl;
            elements.autoAnalyzeCheckbox.checked = settings.autoAnalyze;
            elements.showOverlayCheckbox.checked = settings.showOverlay;
            
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }
    
    // Save settings to Chrome storage
    async function saveSettings() {
        try {
            settings.apiUrl = elements.apiUrlInput.value.trim();
            settings.autoAnalyze = elements.autoAnalyzeCheckbox.checked;
            settings.showOverlay = elements.showOverlayCheckbox.checked;
            
            await chrome.storage.sync.set({ settings: settings });
            
            // Update API status
            await checkApiStatus();
            
            // Close modal
            elements.settingsModal.style.display = 'none';
            
            showStatus('Settings saved successfully', 'success');
            
        } catch (error) {
            console.error('Error saving settings:', error);
            showStatus('Failed to save settings', 'error');
        }
    }
    
    // Check API server status
    async function checkApiStatus() {
        try {
            const response = await fetch(`${settings.apiUrl}/`, {
                method: 'GET',
                timeout: 5000
            });
            
            if (response.ok) {
                updateApiStatus(true);
                return true;
            } else {
                updateApiStatus(false);
                return false;
            }
        } catch (error) {
            console.error('API status check failed:', error);
            updateApiStatus(false);
            return false;
        }
    }
    
    // Update API status indicator
    function updateApiStatus(isOnline) {
        const statusText = elements.apiStatus.querySelector('span:last-child');
        
        if (isOnline) {
            elements.apiDot.classList.remove('offline');
            statusText.textContent = 'API Ready';
            elements.statusDot.style.background = '#28a745';
            elements.statusText.textContent = 'Ready';
        } else {
            elements.apiDot.classList.add('offline');
            statusText.textContent = 'API Offline';
            elements.statusDot.style.background = '#dc3545';
            elements.statusText.textContent = 'Offline';
        }
    }
    
    // Load current page information
    async function loadCurrentPageInfo() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (tab) {
                currentPageInfo = {
                    url: tab.url,
                    title: tab.title,
                    domain: new URL(tab.url).hostname
                };
                
                // Update UI
                elements.pageTitle.textContent = currentPageInfo.title || 'Unknown Page';
                elements.pageUrl.textContent = currentPageInfo.url;
                elements.pageUrl.title = currentPageInfo.url;
            }
        } catch (error) {
            console.error('Error loading page info:', error);
            elements.pageTitle.textContent = 'Error loading page';
            elements.pageUrl.textContent = '-';
        }
    }
    
    // Set up event listeners
    function setupEventListeners() {
        // Main action buttons
        elements.analyzeCurrentBtn.addEventListener('click', analyzeCurrentPage);
        elements.highlightTermsBtn.addEventListener('click', highlightTermsOnPage);
        elements.analyzeUrlBtn.addEventListener('click', analyzeCustomUrl);
        elements.findTermsBtn.addEventListener('click', findCompanyTerms);
        
        // Settings and modal
        elements.settingsBtn.addEventListener('click', () => {
            elements.settingsModal.style.display = 'flex';
        });
        
        elements.settingsClose.addEventListener('click', () => {
            elements.settingsModal.style.display = 'none';
        });
        
        elements.saveSettingsBtn.addEventListener('click', saveSettings);
        
        // Help and reports
        elements.helpBtn.addEventListener('click', showHelp);
        elements.reportBtn.addEventListener('click', openReportsFolder);
        
        // Error retry
        elements.retryBtn.addEventListener('click', retryLastAction);
        
        // Enter key handlers
        elements.customUrl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                analyzeCustomUrl();
            }
        });
        
        elements.companyName.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                findCompanyTerms();
            }
        });
        
        // Close modal when clicking outside
        elements.settingsModal.addEventListener('click', (e) => {
            if (e.target === elements.settingsModal) {
                elements.settingsModal.style.display = 'none';
            }
        });
    }
    
    // Analyze current page
    async function analyzeCurrentPage() {
        if (!currentPageInfo) {
            showError('No page information available');
            return;
        }
        
        showLoading('Analyzing current page...');
        
        try {
            const result = await chrome.runtime.sendMessage({
                action: 'analyzeCurrentPage'
            });
            
            if (result.success) {
                currentAnalysis = result.data;
                displayAnalysisResult(currentAnalysis);
                
                // Show overlay if enabled
                if (settings.showOverlay) {
                    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                        chrome.tabs.sendMessage(tabs[0].id, {
                            action: 'showAnalysisOverlay',
                            analysis: currentAnalysis.analysis
                        });
                    });
                }
                
                showStatus('Analysis completed', 'success');
            } else {
                throw new Error(result.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Error analyzing current page:', error);
            showError(`Analysis failed: ${error.message}`);
        } finally {
            hideLoading();
        }
    }
    
    // Analyze custom URL
    async function analyzeCustomUrl() {
        const url = elements.customUrl.value.trim();
        
        if (!url) {
            showError('Please enter a valid URL');
            return;
        }
        
        if (!isValidUrl(url)) {
            showError('Please enter a valid URL (must include http:// or https://)');
            return;
        }
        
        showLoading('Analyzing URL...');
        
        try {
            const result = await chrome.runtime.sendMessage({
                action: 'analyzeUrl',
                url: url
            });
            
            if (result.success) {
                const analysis = result.data;
                displayAnalysisResult(analysis);
                showStatus('URL analysis completed', 'success');
            } else {
                throw new Error(result.error || 'URL analysis failed');
            }
        } catch (error) {
            console.error('Error analyzing URL:', error);
            showError(`URL analysis failed: ${error.message}`);
        } finally {
            hideLoading();
        }
    }
    
    // Find company terms and conditions
    async function findCompanyTerms() {
        const companyName = elements.companyName.value.trim();
        
        if (!companyName) {
            showError('Please enter a company name');
            return;
        }
        
        showLoading('Finding terms and conditions...');
        
        try {
            const result = await chrome.runtime.sendMessage({
                action: 'findTermsAndConditions',
                query: companyName,
                companyName: companyName
            });
            
            if (result.success) {
                const termsData = result.data;
                displayTermsResult(termsData);
                showStatus('Terms and conditions found', 'success');
            } else {
                throw new Error(result.error || 'Terms search failed');
            }
        } catch (error) {
            console.error('Error finding terms:', error);
            showError(`Terms search failed: ${error.message}`);
        } finally {
            hideLoading();
        }
    }
    
    // Display analysis result
    function displayAnalysisResult(analysis) {
        const { analysis: analysisData } = analysis;
        
        // Show result section
        elements.analysisResult.style.display = 'block';
        
        // Update status
        if (analysisData.isTermsPage) {
            elements.analysisResult.classList.add('terms-page');
            elements.resultIcon.textContent = '✅';
            elements.resultText.textContent = 'Terms & Conditions Page';
        } else {
            elements.analysisResult.classList.remove('terms-page');
            elements.resultIcon.textContent = '⚠️';
            elements.resultText.textContent = 'Not a Terms Page';
        }
        
        // Update confidence
        elements.resultConfidence.textContent = `${analysisData.confidence.toFixed(1)}%`;
        
        // Update summary
        elements.resultSummary.textContent = analysisData.summary;
        
        // Update details
        elements.resultDetails.innerHTML = `
            <strong>Content:</strong> ${analysisData.contentLength.toLocaleString()} characters, 
            ${analysisData.wordCount.toLocaleString()} words<br>
            <strong>Indicators found:</strong> ${analysisData.indicators.length}
        `;
        
        // Show highlight button if terms found
        if (analysisData.indicators.length > 0) {
            elements.highlightTermsBtn.style.display = 'flex';
        } else {
            elements.highlightTermsBtn.style.display = 'none';
        }
    }
    
    // Display terms search result (simplified)
    function displayTermsResult(termsData) {
        // Show result section
        elements.analysisResult.style.display = 'block';
        elements.analysisResult.classList.remove('terms-page');
        
        // Update status for manual search suggestion
        elements.resultIcon.textContent = '💡';
        elements.resultText.textContent = 'Search Suggestions';
        elements.resultConfidence.textContent = 'Manual';
        elements.resultConfidence.style.background = '#17a2b8'; // Info color
        
        // Show the suggestion content
        elements.resultSummary.textContent = `Search suggestions for ${termsData.query}:`;
        
        // Update details with suggestions and instructions
        elements.resultDetails.innerHTML = `
            <strong>Suggested searches:</strong><br>
            • "${termsData.query} terms and conditions"<br>
            • "${termsData.query} terms of service"<br>
            • "${termsData.query} user agreement"<br><br>
            <strong>Next steps:</strong><br>
            1. Search for the company's terms page<br>
            2. Copy the URL of the terms page<br>
            3. Use "Analyze Custom URL" feature above<br><br>
            <em>This approach gives you direct control over which specific terms page to analyze.</em>
        `;
        
        // Hide highlight button since no analysis was performed
        elements.highlightTermsBtn.style.display = 'none';
    }
    
    // Highlight terms on the current page
    function highlightTermsOnPage() {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            chrome.tabs.sendMessage(tabs[0].id, {
                action: 'highlightTermsIndicators'
            });
        });
        
        showStatus('Terms highlighted on page', 'success');
    }
    
    // Show loading state
    function showLoading(message = 'Loading...') {
        elements.loading.style.display = 'flex';
        elements.loading.querySelector('.loading-text').textContent = message;
        elements.error.style.display = 'none';
        
        // Disable buttons
        elements.analyzeCurrentBtn.disabled = true;
        elements.analyzeUrlBtn.disabled = true;
        elements.findTermsBtn.disabled = true;
    }
    
    // Hide loading state
    function hideLoading() {
        elements.loading.style.display = 'none';
        
        // Re-enable buttons
        elements.analyzeCurrentBtn.disabled = false;
        elements.analyzeUrlBtn.disabled = false;
        elements.findTermsBtn.disabled = false;
    }
    
    // Show error message
    function showError(message) {
        elements.error.style.display = 'flex';
        elements.errorText.textContent = message;
        hideLoading();
    }
    
    // Show status message
    function showStatus(message, type = 'info') {
        const originalText = elements.statusText.textContent;
        const originalColor = elements.statusDot.style.background;
        
        elements.statusText.textContent = message;
        
        switch (type) {
            case 'success':
                elements.statusDot.style.background = '#28a745';
                break;
            case 'error':
                elements.statusDot.style.background = '#dc3545';
                break;
            default:
                elements.statusDot.style.background = '#007bff';
        }
        
        // Reset after 3 seconds
        setTimeout(() => {
            elements.statusText.textContent = originalText;
            elements.statusDot.style.background = originalColor;
        }, 3000);
    }
    
    // Retry last action
    function retryLastAction() {
        elements.error.style.display = 'none';
        
        // Simple retry - just re-analyze current page
        analyzeCurrentPage();
    }
    
    // Show help information
    function showHelp() {
        const helpUrl = chrome.runtime.getURL('help.html');
        chrome.tabs.create({ url: helpUrl });
    }
    
    // Open reports folder
    function openReportsFolder() {
        // This would need to be implemented to show saved analysis reports
        showStatus('Reports feature coming soon', 'info');
    }
    
    // Utility: Validate URL
    function isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }
    
    // Handle keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'Enter':
                    e.preventDefault();
                    analyzeCurrentPage();
                    break;
                case 'h':
                    e.preventDefault();
                    highlightTermsOnPage();
                    break;
            }
        }
    });
    
});
