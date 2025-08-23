#!/usr/bin/env python3
"""
Quick test to verify the scraper fixes work
"""

import requests
import json

def test_scraper_endpoint():
    """Test the improved /scrape endpoint directly"""
    
    print("🧪 Testing Improved Scraper Endpoint")
    print("=" * 50)
    
    # Test URLs
    test_urls = [
        "https://www.americanexpress.com/us/credit-cards/card-application/apply/prospect/terms/gold-card/25330-10-0#offer-terms",
        "https://www.netflix.com/legal/termsofuse",
        "https://www.google.com",
    ]
    
    api_url = "http://localhost:8000/scrape"
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🧪 Test {i}: {url}")
        print("-" * 40)
        
        try:
            # Make request to scraper endpoint
            payload = {"url": url}
            response = requests.post(api_url, json=payload, timeout=45)
            
            print(f"📊 HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Scraper Status: {data.get('status', 'unknown')}")
                print(f"📝 Title: {data.get('title', 'No title')[:100]}...")
                print(f"📄 Content Length: {len(data.get('content', ''))} characters")
                
                content_preview = data.get('content', '')[:200]
                if content_preview:
                    print(f"📋 Content Preview: {content_preview}...")
                else:
                    print(f"❌ No content returned")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error: FastAPI server not running")
            print(f"💡 Start server with: make dev-server")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def show_what_fixed():
    """Show what was fixed in the scraper"""
    
    print(f"\n🔧 What Was Fixed:")
    print("=" * 50)
    print(f"""
Old scraper issues:
❌ Limited content to 1000 characters only
❌ Too strict error handling 
❌ No proper browser headers
❌ Short timeout (10s)
❌ Failed completely on any error

New scraper improvements:
✅ Returns full content (no truncation)
✅ Robust error handling with fallbacks
✅ Proper browser headers to avoid blocking
✅ Longer timeout (30s)
✅ Accepts partial success if we get content
✅ Better logging for debugging
✅ Graceful degradation on errors
✅ Multiple content extraction strategies

The key fix: Download whatever content exists, don't fail completely!
""")


if __name__ == "__main__":
    print("🤖 Scraper Fix Verification Test")
    print("=" * 60)
    
    # Show what was fixed
    show_what_fixed()
    
    # Test the endpoint
    test_scraper_endpoint()
    
    print(f"\n✅ Test completed!")
    print(f"💡 If server is running, try the original demo:")
    print(f"   python demo_dspy_agent.py")
