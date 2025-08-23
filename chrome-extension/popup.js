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
        testConnectionBtn: document.getElementById('test-connection'),
        analyzeCurrentBtn: document.getElementById('analyze-current'),
        highlightTermsBtn: document.getElementById('highlight-terms'),
        
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
            settings.apiUrl = elements.apiUrlInput.value;
            settings.autoAnalyze = elements.autoAnalyzeCheckbox.checked;
            settings.showOverlay = elements.showOverlayCheckbox.checked;
            
            await chrome.storage.sync.set({ settings: settings });
            showStatus('Settings saved', 'success');
            
        } catch (error) {
            console.error('Error saving settings:', error);
            showError('Failed to save settings');
        }
    }
    
    // Check API status
    async function checkApiStatus() {
        try {
            const response = await fetch(`${settings.apiUrl}/`);
            if (response.ok) {
                showApiStatus('API Ready', 'success');
            } else {
                showApiStatus('API Error', 'error');
            }
        } catch (error) {
            console.error('API check failed:', error);
            showApiStatus('API Offline', 'error');
        }
    }
    
    // Load current page information
    async function loadCurrentPageInfo() {
        try {
            const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
            if (tabs.length > 0) {
                const tab = tabs[0];
                currentPageInfo = {
                    title: tab.title,
                    url: tab.url
                };
                
                elements.pageTitle.textContent = tab.title || 'No title';
                elements.pageUrl.textContent = tab.url || 'No URL';
            }
        } catch (error) {
            console.error('Error loading page info:', error);
            elements.pageTitle.textContent = 'Error loading page info';
            elements.pageUrl.textContent = 'Error';
        }
    }
    
    // Setup event listeners
    function setupEventListeners() {
        // Test connection button
        elements.testConnectionBtn.addEventListener('click', testConnection);
        
        // Main analysis button
        elements.analyzeCurrentBtn.addEventListener('click', analyzeCurrentPage);
        
        // Retry button
        elements.retryBtn.addEventListener('click', analyzeCurrentPage);
        
        // Settings
        elements.settingsBtn.addEventListener('click', () => {
            elements.settingsModal.style.display = 'block';
        });
        
        elements.settingsClose.addEventListener('click', () => {
            elements.settingsModal.style.display = 'none';
        });
        
        elements.saveSettingsBtn.addEventListener('click', async () => {
            await saveSettings();
            elements.settingsModal.style.display = 'none';
        });
        
        // Help button
        elements.helpBtn.addEventListener('click', () => {
            chrome.tabs.create({ url: chrome.runtime.getURL('help.html') });
        });
        
        // Highlight terms button
        elements.highlightTermsBtn.addEventListener('click', () => {
            if (currentAnalysis) {
                chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                    chrome.tabs.sendMessage(tabs[0].id, {
                        action: 'highlightTerms',
                        analysis: currentAnalysis.analysis
                    });
                });
            }
        });
    }
    
    // Test connection to background script
    async function testConnection() {
        console.log('🧪 Testing connection to background script...');
        showStatus('Testing connection...', 'info');
        
        try {
            const result = await new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    reject(new Error('Test timeout'));
                }, 5000);
                
                chrome.runtime.sendMessage({ action: 'test' }, (response) => {
                    clearTimeout(timeout);
                    
                    if (chrome.runtime.lastError) {
                        reject(new Error(chrome.runtime.lastError.message));
                        return;
                    }
                    
                    resolve(response);
                });
            });
            
            if (result && result.success) {
                showStatus('✅ Connection successful!', 'success');
                console.log('✅ Background script response:', result.message);
            } else {
                showStatus('❌ Connection failed', 'error');
                console.error('❌ Unexpected response:', result);
            }
        } catch (error) {
            showStatus('❌ Connection failed', 'error');
            console.error('❌ Connection test error:', error);
            showError(`Connection test failed: ${error.message}`);
        }
    }
    
    // Analyze current page
    async function analyzeCurrentPage() {
        if (!currentPageInfo) {
            showError('No page information available');
            return;
        }
        
        showLoading('Analyzing current page...');
        hideError();
        
        try {
            // Get the current active tab
            const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
            if (tabs.length === 0) {
                throw new Error('No active tab found');
            }
            
            const tab = tabs[0];
            
            // Send message to background script with timeout
            console.log('🚀 Sending message to background script for tab:', tab.id, 'URL:', tab.url);
            
            const result = await new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    console.error('⏰ Background script timeout after 15 seconds');
                    reject(new Error('Background script timeout - please try again'));
                }, 15000); // 15 second timeout (increased)
                
                try {
                    chrome.runtime.sendMessage({
                        action: 'analyzeCurrentPage',
                        tabId: tab.id,
                        url: tab.url
                    }, (response) => {
                        clearTimeout(timeout);
                        
                        console.log('📨 Received response from background script:', response);
                        
                        // Check for Chrome extension errors
                        if (chrome.runtime.lastError) {
                            console.error('❌ Chrome runtime error:', chrome.runtime.lastError);
                            reject(new Error(`Extension error: ${chrome.runtime.lastError.message}`));
                            return;
                        }
                        
                        if (response === undefined) {
                            console.error('❌ Response is undefined - background script may not be running');
                            reject(new Error('No response from background script - try reloading extension'));
                            return;
                        }
                        
                        resolve(response);
                    });
                } catch (error) {
                    clearTimeout(timeout);
                    console.error('❌ Error sending message:', error);
                    reject(error);
                }
            });
            
            console.log('Analysis result:', result);
            
            // Check if result exists and has success property
            if (result && result.success) {
                currentAnalysis = result.data;
                displayAnalysisResult(currentAnalysis);
                
                // Show overlay if enabled
                if (settings.showOverlay && currentAnalysis.analysis) {
                    try {
                        chrome.tabs.sendMessage(tab.id, {
                            action: 'showAnalysisOverlay',
                            analysis: currentAnalysis.analysis
                        });
                    } catch (overlayError) {
                        console.warn('Could not show overlay:', overlayError);
                    }
                }
                
                showStatus('Analysis completed', 'success');
            } else {
                // Handle case where result is undefined or doesn't have success property
                const errorMessage = result ? (result.error || 'Analysis failed') : 'No response from background script';
                throw new Error(errorMessage);
            }
        } catch (error) {
            console.error('Error analyzing current page:', error);
            let errorMessage = error.message;
            
            // Provide more helpful error messages
            if (errorMessage.includes('Could not establish connection')) {
                errorMessage = 'Extension connection error. Try reloading the extension or refreshing the page.';
            } else if (errorMessage.includes('Receiving end does not exist')) {
                errorMessage = 'Background script not responding. Try reloading the extension.';
            }
            
            showError(`Analysis failed: ${errorMessage}`);
        } finally {
            hideLoading();
        }
    }
    
    // Display analysis result
    function displayAnalysisResult(analysis) {
        if (!analysis || !analysis.analysis) {
            showError('Invalid analysis result');
            return;
        }
        
        const result = analysis.analysis;
        
        // Update result display
        elements.resultIcon.textContent = result.isTermsPage ? '✅' : '⚠️';
        elements.resultText.textContent = result.isTermsPage ? 'Terms Page Detected' : 'Not a Terms Page';
        elements.resultConfidence.textContent = `${result.confidence.toFixed(1)}%`;
        elements.resultSummary.textContent = result.summary || 'No summary available';
        
        // Show details based on analysis method
        let details = '';
        
        if (result.analysisMethod === 'llm_powered') {
            // LLM-powered comprehensive analysis results
            
            // Document type
            if (result.documentType) {
                details += `<strong>Document Type:</strong> ${result.documentType}<br><br>`;
            }
            
            // Risk Level with color coding
            if (result.riskLevel) {
                const riskColors = {
                    'low': '#28a745',
                    'medium': '#ffc107', 
                    'high': '#dc3545'
                };
                const riskColor = riskColors[result.riskLevel] || '#6c757d';
                details += `<strong>Risk Level:</strong> <span style="color: ${riskColor}; font-weight: bold; padding: 2px 8px; border-radius: 4px; background: ${riskColor}20;">${result.riskLevel.toUpperCase()}</span><br><br>`;
            }
            
            // Key Findings
            if (result.keyFindings && result.keyFindings.length > 0) {
                details += `<strong>🔍 Key Findings:</strong><br>`;
                result.keyFindings.slice(0, 3).forEach(finding => {
                    details += `• ${finding}<br>`;
                });
                details += `<br>`;
            }
            
            // Red Flags (if any)
            if (result.redFlags && result.redFlags.length > 0) {
                details += `<strong>🚩 Red Flags:</strong><br>`;
                result.redFlags.slice(0, 3).forEach(flag => {
                    details += `• <span style="color: #dc3545;">${flag}</span><br>`;
                });
                details += `<br>`;
            }
            
            // Consumer Protections
            if (result.consumerProtections && result.consumerProtections.length > 0) {
                details += `<strong>✅ Consumer Protections:</strong><br>`;
                result.consumerProtections.slice(0, 3).forEach(protection => {
                    details += `• <span style="color: #28a745;">${protection}</span><br>`;
                });
                details += `<br>`;
            }
            
            // Recommendations
            if (result.recommendations && result.recommendations.length > 0) {
                details += `<strong>💡 Recommendations:</strong><br>`;
                result.recommendations.slice(0, 2).forEach(rec => {
                    details += `• ${rec}<br>`;
                });
                details += `<br>`;
            }
            
            // Compliance Indicators
            if (result.complianceIndicators) {
                details += `<strong>📋 Compliance:</strong><br>`;
                const complianceColors = {
                    'compliant': '#28a745',
                    'partial': '#ffc107',
                    'non-compliant': '#dc3545',
                    'unclear': '#6c757d'
                };
                
                if (result.complianceIndicators.gdpr) {
                    const color = complianceColors[result.complianceIndicators.gdpr] || '#6c757d';
                    details += `• GDPR: <span style="color: ${color};">${result.complianceIndicators.gdpr}</span><br>`;
                }
                if (result.complianceIndicators.ccpa) {
                    const color = complianceColors[result.complianceIndicators.ccpa] || '#6c757d';
                    details += `• CCPA: <span style="color: ${color};">${result.complianceIndicators.ccpa}</span><br>`;
                }
                if (result.complianceIndicators.plainLanguage) {
                    const langColors = { 'good': '#28a745', 'fair': '#ffc107', 'poor': '#dc3545' };
                    const color = langColors[result.complianceIndicators.plainLanguage] || '#6c757d';
                    details += `• Plain Language: <span style="color: ${color};">${result.complianceIndicators.plainLanguage}</span><br>`;
                }
                details += `<br>`;
            }
            
            // Last Updated
            if (result.lastUpdated && result.lastUpdated !== 'not specified') {
                details += `<strong>📅 Last Updated:</strong> ${result.lastUpdated}<br><br>`;
            }
            
            details += `<strong>🤖 Analysis:</strong> AI-powered comprehensive review`;
        } else {
            // This should not happen with LLM-only approach
            details += `<strong>⚠️ Analysis Method:</strong> ${result.analysisMethod || 'unknown'}<br>`;
            details += `<strong>Note:</strong> LLM analysis should be the only method used.`;
        }
        
        if (result.contentLength) {
            details += `<br><strong>Content:</strong> ${result.contentLength.toLocaleString()} characters`;
            if (result.wordCount) {
                details += `, ${result.wordCount.toLocaleString()} words`;
            }
        }
        
        if (analysis.note) {
            details += `<br><br><em>Note: ${analysis.note}</em>`;
        }
        
        elements.resultDetails.innerHTML = details;
        
        // Show result and highlight button if terms page
        elements.analysisResult.style.display = 'block';
        if (result.isTermsPage && result.confidence > 30) {
            elements.highlightTermsBtn.style.display = 'inline-block';
        } else {
            elements.highlightTermsBtn.style.display = 'none';
        }
    }
    
    // UI helper functions
    function showLoading(message) {
        elements.loading.querySelector('.loading-text').textContent = message;
        elements.loading.style.display = 'block';
        elements.analyzeCurrentBtn.disabled = true;
    }
    
    function hideLoading() {
        elements.loading.style.display = 'none';
        elements.analyzeCurrentBtn.disabled = false;
    }
    
    function showError(message) {
        elements.errorText.textContent = message;
        elements.error.style.display = 'block';
    }
    
    function hideError() {
        elements.error.style.display = 'none';
    }
    
    function showStatus(message, type = 'info') {
        elements.statusText.textContent = message;
        elements.statusDot.className = `status-dot ${type}`;
    }
    
    function showApiStatus(message, type = 'info') {
        const apiText = elements.apiStatus.querySelector('.api-dot').nextSibling;
        if (apiText) {
            apiText.textContent = message;
        }
        elements.apiDot.className = `api-dot ${type}`;
    }
    
    // Utility functions
    function isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }
});
