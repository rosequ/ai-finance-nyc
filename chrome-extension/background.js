// Background script for Terms & Conditions Analyzer
const API_BASE_URL = 'http://localhost:8000';

// Storage for analysis results
let analysisCache = new Map();

// Handle extension installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('Terms & Conditions Analyzer installed');
});

// Handle messages from content script and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeCurrentPage') {
    analyzeCurrentPage(sender.tab.id, sender.tab.url)
      .then(result => sendResponse({ success: true, data: result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Will respond asynchronously
  }
  
  if (request.action === 'analyzeUrl') {
    analyzeUrl(request.url)
      .then(result => sendResponse({ success: true, data: result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Will respond asynchronously
  }
  
  if (request.action === 'findTermsAndConditions') {
    findTermsAndConditions(request.query, request.companyName)
      .then(result => sendResponse({ success: true, data: result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Will respond asynchronously
  }
});

// Analyze the current page content
async function analyzeCurrentPage(tabId, url) {
  try {
    console.log('Analyzing current page for T&C content:', url);
    
    // Check cache first
    const cacheKey = `page_${url}`;
    if (analysisCache.has(cacheKey)) {
      console.log('Returning cached T&C analysis');
      return analysisCache.get(cacheKey);
    }
    
    // Call the scraping API
    const response = await fetch(`${API_BASE_URL}/scrape`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url })
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Analyze the content specifically for terms & conditions indicators
    const analysis = analyzeContentForTerms(data.content, url);
    
    const result = {
      url: url,
      title: data.title,
      content: data.content,
      analysis: analysis,
      timestamp: new Date().toISOString(),
      status: data.status,
      analysisType: 'terms_only' // Flag to indicate simplified analysis
    };
    
    // Cache the result
    analysisCache.set(cacheKey, result);
    
    return result;
    
  } catch (error) {
    console.error('Error analyzing current page for T&C:', error);
    throw error;
  }
}

// Analyze a specific URL
async function analyzeUrl(url) {
  try {
    console.log('Analyzing URL:', url);
    
    const response = await fetch(`${API_BASE_URL}/scrape`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url })
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }
    
    const data = await response.json();
    const analysis = analyzeContentForTerms(data.content, url);
    
    return {
      url: url,
      title: data.title,
      content: data.content,
      analysis: analysis,
      timestamp: new Date().toISOString(),
      status: data.status
    };
    
  } catch (error) {
    console.error('Error analyzing URL:', error);
    throw error;
  }
}

// Find terms and conditions for a company (simplified - no external search)
async function findTermsAndConditions(query, companyName = null) {
  try {
    console.log('Finding terms and conditions for (T&C focus):', query);
    
    // For now, just return a simplified response suggesting manual URL entry
    // This avoids complex search functionality and focuses on T&C analysis
    return {
      query: query,
      companyName: companyName,
      termsUrl: '',
      content: `To analyze ${query}'s terms and conditions:\n\n1. Search for "${query} terms and conditions" in your browser\n2. Copy the terms page URL\n3. Use "Analyze Custom URL" feature in this extension\n\nThis approach gives you direct control over which terms page to analyze.`,
      filePath: '',
      status: 'manual_search_required',
      timestamp: new Date().toISOString(),
      suggestion: `Try searching: "${query} terms and conditions" OR "${query} terms of service"`
    };
    
  } catch (error) {
    console.error('Error in simplified terms finder:', error);
    throw error;
  }
}

// Analyze content to determine if it contains terms & conditions
function analyzeContentForTerms(content, url) {
  if (!content) {
    return {
      isTermsPage: false,
      confidence: 0,
      indicators: [],
      summary: "No content available for analysis"
    };
  }
  
  const contentLower = content.toLowerCase();
  
  // Terms & conditions indicators
  const termsIndicators = [
    { phrase: 'terms and conditions', weight: 10 },
    { phrase: 'terms of service', weight: 10 },
    { phrase: 'terms of use', weight: 10 },
    { phrase: 'user agreement', weight: 8 },
    { phrase: 'legal agreement', weight: 8 },
    { phrase: 'end user license agreement', weight: 9 },
    { phrase: 'eula', weight: 7 },
    { phrase: 'privacy policy', weight: 6 },
    { phrase: 'by using this', weight: 5 },
    { phrase: 'you agree to', weight: 5 },
    { phrase: 'acceptance of terms', weight: 8 },
    { phrase: 'liability', weight: 4 },
    { phrase: 'disclaimer', weight: 4 },
    { phrase: 'governing law', weight: 6 },
    { phrase: 'intellectual property', weight: 5 },
    { phrase: 'limitation of liability', weight: 7 },
    { phrase: 'dispute resolution', weight: 6 },
    { phrase: 'arbitration', weight: 5 },
    { phrase: 'termination', weight: 4 },
    { phrase: 'prohibited uses', weight: 5 }
  ];
  
  // URL indicators
  const urlIndicators = [
    { phrase: '/terms', weight: 8 },
    { phrase: '/legal', weight: 6 },
    { phrase: '/privacy', weight: 5 },
    { phrase: '/agreement', weight: 7 },
    { phrase: '/conditions', weight: 8 }
  ];
  
  let score = 0;
  let foundIndicators = [];
  
  // Check content indicators
  termsIndicators.forEach(indicator => {
    if (contentLower.includes(indicator.phrase)) {
      score += indicator.weight;
      foundIndicators.push({
        type: 'content',
        phrase: indicator.phrase,
        weight: indicator.weight
      });
    }
  });
  
  // Check URL indicators
  const urlLower = url.toLowerCase();
  urlIndicators.forEach(indicator => {
    if (urlLower.includes(indicator.phrase)) {
      score += indicator.weight;
      foundIndicators.push({
        type: 'url',
        phrase: indicator.phrase,
        weight: indicator.weight
      });
    }
  });
  
  // Calculate confidence percentage
  const maxPossibleScore = 100; // Adjust based on typical scores
  const confidence = Math.min(100, (score / maxPossibleScore) * 100);
  
  // Determine if this is likely a terms page
  const isTermsPage = score >= 15; // Threshold for considering it a terms page
  
  // Generate summary
  let summary = "";
  if (isTermsPage) {
    summary = `This appears to be a terms and conditions page (${confidence.toFixed(1)}% confidence). `;
    summary += `Found ${foundIndicators.length} relevant indicators. `;
    
    const topIndicators = foundIndicators
      .sort((a, b) => b.weight - a.weight)
      .slice(0, 3)
      .map(i => i.phrase);
    
    if (topIndicators.length > 0) {
      summary += `Key terms: ${topIndicators.join(', ')}.`;
    }
  } else {
    summary = `This does not appear to be a terms and conditions page (${confidence.toFixed(1)}% confidence). `;
    if (foundIndicators.length > 0) {
      summary += `Found ${foundIndicators.length} weak indicators.`;
    } else {
      summary += `No relevant terms indicators found.`;
    }
  }
  
  return {
    isTermsPage: isTermsPage,
    confidence: confidence,
    score: score,
    indicators: foundIndicators,
    summary: summary,
    contentLength: content.length,
    wordCount: content.split(/\s+/).length
  };
}

// Clear cache periodically (every 30 minutes)
setInterval(() => {
  console.log('Clearing analysis cache');
  analysisCache.clear();
}, 30 * 60 * 1000);
