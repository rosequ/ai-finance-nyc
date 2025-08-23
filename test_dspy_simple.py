#!/usr/bin/env python3
"""
Simple test of DSPy tools without requiring a running server
"""

import sys
sys.path.append('src')

import requests
from dspy_tools import APIClient, ContentRetriever, RedditSearcher


def test_api_connection():
    """Test if the API server is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False


def demo_dspy_tools():
    """Demo the DSPy tools"""
    
    print("🤖 DSPy Tools Demo")
    print("=" * 40)
    
    # Check server
    print("🔍 Checking FastAPI server...")
    if not test_api_connection():
        print("❌ FastAPI server not running")
        print("💡 Start with: make dev-server")
        print("\n📝 Here's what the DSPy agent would do:")
        print("1. 🌐 Detect if input is URL or company name")
        print("2. 📄 Retrieve content (scrape URL or find terms)")
        print("3. 🔍 Search Reddit for company discussions") 
        print("4. 📊 Combine into comprehensive report")
        print("5. 💾 Save to file with timestamp and sources")
        return
    
    print("✅ Server is running!")
    
    # Initialize components
    api_client = APIClient()
    
    # Test a simple example
    print(f"\n📋 Testing content retrieval...")
    
    # This would normally work with the server running
    try:
        from dspy_tools import analyze_company
        
        print("🚀 Running Netflix analysis...")
        result = analyze_company(
            input_query="Netflix", 
            output_file="test_netflix.txt"
        )
        
        print(f"✅ Success!")
        print(f"📁 Report: {result['file_path']}")
        print(f"📄 Content: {result['content_status']}")
        print(f"🔍 Reddit: {result['reddit_status']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure server is running and API keys are configured")


if __name__ == "__main__":
    demo_dspy_tools()
