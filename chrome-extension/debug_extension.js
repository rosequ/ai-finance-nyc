// Debug script for Chrome Extension
// Run this in the Chrome DevTools console (F12) when the extension popup is open

console.log('🔍 Chrome Extension Debug Script');
console.log('================================');

// Test 1: Check if chrome.runtime is available
console.log('1. Chrome Runtime API:', chrome.runtime ? '✅ Available' : '❌ Not Available');

// Test 2: Check extension ID
console.log('2. Extension ID:', chrome.runtime.id);

// Test 3: Test message to background script
console.log('3. Testing background script communication...');
chrome.runtime.sendMessage({ action: 'test' }, (response) => {
    if (chrome.runtime.lastError) {
        console.log('❌ Background script error:', chrome.runtime.lastError.message);
    } else {
        console.log('✅ Background script response:', response);
    }
});

// Test 4: Check current tab access
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (chrome.runtime.lastError) {
        console.log('❌ Tab access error:', chrome.runtime.lastError.message);
    } else if (tabs.length > 0) {
        console.log('✅ Current tab:', tabs[0].url);
    } else {
        console.log('❌ No active tab found');
    }
});

// Test 5: Check API server
fetch('http://localhost:8000/')
    .then(response => response.json())
    .then(data => {
        console.log('✅ API Server response:', data);
    })
    .catch(error => {
        console.log('❌ API Server error:', error.message);
    });

console.log('Debug tests initiated. Check results above.');
