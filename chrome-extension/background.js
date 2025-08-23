// Background script for Terms & Conditions Analyzer - Service Worker
console.log('🚀 Background service worker starting...');

const API_BASE_URL = 'http://localhost:8000';

// Storage for analysis results
let analysisCache = new Map();

// Service worker installation
self.addEventListener('install', (event) => {
  console.log('🔧 Service worker installing...');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('✅ Service worker activated');
  event.waitUntil(self.clients.claim());
});

// Handle extension installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('📦 Terms & Conditions Analyzer installed');
});

// Handle messages from content script and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('📨 Background script received message:', request);
  console.log('👤 Message sender:', sender);
  
  try {
    // Handle different message types
    switch (request.action) {
      case 'analyzeCurrentPage':
        console.log('🔍 Handling analyzeCurrentPage action');
        handleAnalyzeCurrentPage(request, sender, sendResponse);
        return true; // Will respond asynchronously
        
      case 'test':
        console.log('🧪 Handling test action');
        sendResponse({ success: true, message: 'Background script is working!' });
        return false;
        
      default:
        console.log('❓ Unknown action:', request.action);
        sendResponse({ success: false, error: `Unknown action: ${request.action}` });
        return false;
    }
  } catch (error) {
    console.error('❌ Error in message listener:', error);
    sendResponse({ success: false, error: error.message });
    return false;
  }
});

// Handle analyze current page request
async function handleAnalyzeCurrentPage(request, sender, sendResponse) {
  try {
    console.log('🔍 Handling analyzeCurrentPage request:', request);
    console.log('📝 Sender info:', sender);
    
    // Get tab info from request or sender
    let tabId = request.tabId;
    let url = request.url;
    
    console.log('📋 Initial tab info - ID:', tabId, 'URL:', url);
    
    // If not provided in request, try to get from sender
    if (!tabId || !url) {
      if (sender && sender.tab) {
        tabId = sender.tab.id;
        url = sender.tab.url;
        console.log('📋 Got tab info from sender - ID:', tabId, 'URL:', url);
      } else {
        // Try to get current active tab
        try {
          const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
          if (tabs.length > 0) {
            tabId = tabs[0].id;
            url = tabs[0].url;
            console.log('📋 Got tab info from query - ID:', tabId, 'URL:', url);
          }
        } catch (error) {
          console.error('❌ Error getting active tab:', error);
        }
      }
    }
    
    if (!tabId || !url) {
      console.error('❌ No tab information available');
      sendResponse({ success: false, error: 'No tab information available' });
      return;
    }
    
    console.log('🌐 Starting analysis for URL:', url);
    
    // Check cache first
    const cacheKey = `page_${url}`;
    if (analysisCache.has(cacheKey)) {
      console.log('💾 Returning cached analysis');
      sendResponse({ success: true, data: analysisCache.get(cacheKey) });
      return;
    }
    
    // Analyze the page
    console.log('🤖 Starting LLM analysis...');
    const result = await analyzePageWithLLM(url);
    
    // Cache the result
    analysisCache.set(cacheKey, result);
    
    console.log('✅ Analysis completed successfully:', result);
    sendResponse({ success: true, data: result });
    
  } catch (error) {
    console.error('❌ Error in handleAnalyzeCurrentPage:', error);
    console.error('❌ Error stack:', error.stack);
    sendResponse({ success: false, error: error.message });
  }
}

// Analyze page content using LLM ONLY
async function analyzePageWithLLM(url) {
  try {
    console.log('Scraping and analyzing URL with LLM (no fallbacks):', url);
    
    // First, scrape the content
    const scrapeResponse = await fetch(`${API_BASE_URL}/scrape`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url })
    });
    
    if (!scrapeResponse.ok) {
      throw new Error(`Scraping failed: ${scrapeResponse.status} ${scrapeResponse.statusText}`);
    }
    
    const scrapeData = await scrapeResponse.json();
    console.log('📄 Scraping completed!');
                console.log('📊 Content length:', scrapeData.content?.length || 0);
            console.log('📝 Title:', scrapeData.title);
            console.log('🔍 Content preview (first 500 chars):');
            console.log(scrapeData.content?.substring(0, 500) + '...');
            
            // Check content readability
            if (scrapeData.content) {
                const sample = scrapeData.content.substring(0, 1000);
                const printableChars = sample.split('').filter(c => c.match(/[\x20-\x7E]/) || c.match(/[\n\r\t]/)).length;
                const readabilityRatio = printableChars / sample.length;
                console.log('📊 Content readability ratio:', (readabilityRatio * 100).toFixed(1) + '%');
                
                if (readabilityRatio < 0.7) {
                    console.log('⚠️ WARNING: Content appears to be binary/encoded data');
                    console.log('🔍 First 100 char codes:', sample.substring(0, 100).split('').map(c => c.charCodeAt(0)));
                } else {
                    console.log('✅ Content appears readable');
                }
            }
            
            console.log('📋 Full scraped data structure:', scrapeData);
    
    // Ensure we have content to analyze
    if (!scrapeData.content || scrapeData.content.trim().length === 0) {
      console.error('❌ No content available to analyze');
      throw new Error('No content available to analyze');
    }
    
    // Now analyze with LLM - this is the ONLY analysis method
    console.log('Calling LLM analysis endpoint...');
    const analysisResponse = await fetch(`${API_BASE_URL}/analyze-terms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        text: scrapeData.content,
        url: url,
        title: scrapeData.title
      })
    });
    
    if (!analysisResponse.ok) {
      const errorText = await analysisResponse.text();
      console.error('LLM analysis failed:', errorText);
      throw new Error(`LLM analysis failed: ${analysisResponse.status} - ${errorText}`);
    }
    
    const analysisData = await analysisResponse.json();
    console.log('LLM analysis completed successfully:', analysisData);
    
    // Combine scrape data with LLM analysis
    const result = {
      url: url,
      title: scrapeData.title,
      content: scrapeData.content,
      analysis: analysisData,
      timestamp: new Date().toISOString(),
      status: 'success',
      analysisType: 'llm_powered'
    };
    
    return result;
    
  } catch (error) {
    console.error('LLM-only analysis failed:', error);
    
    // NO FALLBACKS - fail gracefully with clear message
    throw new Error(`LLM analysis unavailable: ${error.message}. Please check your API key and try again.`);
  }
}

// LLM-only analysis - no pattern matching fallbacks

// Clear cache periodically (every 30 minutes)
setInterval(() => {
  console.log('Clearing analysis cache');
  analysisCache.clear();
}, 30 * 60 * 1000);

console.log('Background script setup complete');