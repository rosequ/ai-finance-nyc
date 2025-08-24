#!/usr/bin/env python3
"""
Test script to verify the Chrome extension fix
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_api_connection():
    """Test basic API connection"""
    try:
        response = requests.get(f"{API_URL}/test")
        if response.status_code == 200:
            print("✅ API connection successful")
            return True
        else:
            print(f"❌ API connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def test_analysis_with_generic_content():
    """Test analysis with content that should default to 'loan' product type"""
    test_content = """
    Page: Generic Website Terms
    URL: https://example.com/terms
    Domain: example.com
    
    --- PAGE CONTENT ---
    
    Terms of Service
    
    These terms govern your use of our website and services. By using our service, you agree to these terms.
    
    1. User Responsibilities
    You are responsible for maintaining the security of your account.
    
    2. Service Availability
    We do not guarantee 100% uptime of our services.
    
    3. Privacy
    We collect and use your data as described in our privacy policy.
    
    4. Liability
    Our liability is limited to the maximum extent permitted by law.
    
    5. Termination
    We may terminate your account at any time for violation of these terms.
    """
    
    try:
        response = requests.post(f"{API_URL}/analyze", 
            json={
                "content": test_content,
                "page_title": "Generic Website Terms",
                "page_url": "https://example.com/terms"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Analysis successful for generic content")
                print(f"📋 Product: {data['data']['product_info']['name']}")
                print(f"🏢 Company: {data['data']['product_info']['company']}")
                print(f"📊 Type: {data['data']['product_info']['type']}")
                return True
            else:
                print(f"❌ Analysis failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Chrome Extension Fix")
    print("=" * 40)
    
    # Test 1: API connection
    if not test_api_connection():
        print("❌ Cannot proceed with tests - API not available")
        return
    
    print()
    
    # Test 2: Analysis with generic content
    test_analysis_with_generic_content()
    
    print("\n🎉 Tests completed!")

if __name__ == "__main__":
    main()
