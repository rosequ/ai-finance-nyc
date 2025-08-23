#!/usr/bin/env python3
"""
Test script for the generic terms and conditions API
"""

import requests
import json
import time

def test_terms_and_conditions_api():
    """Test the terms and conditions API with various queries"""
    
    print("🧪 Testing Terms & Conditions API")
    print("=" * 50)
    
    # API endpoint
    url = "http://localhost:8000/terms-and-conditions"
    
    # Test cases
    test_cases = [
        {
            "name": "Simple Company Query",
            "data": {
                "query": "Netflix",
                "output_file": "test_netflix_terms.txt"
            }
        },
        {
            "name": "Company with Product",
            "data": {
                "query": "Amex Gold",
                "company_name": "American Express",
                "product_name": "Gold Card",
                "output_file": "test_amex_gold_terms.txt"
            }
        },
        {
            "name": "Generic Company",
            "data": {
                "query": "Spotify",
                "output_file": "test_spotify_terms.txt"
            }
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        test_data = test_case['data']
        
        try:
            start_time = time.time()
            
            # Make the API request
            response = requests.post(url, json=test_data, timeout=60)
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS - {duration:.2f}s")
                print(f"   Status: {result['status']}")
                print(f"   Content length: {len(result['content'])} chars")
                print(f"   URL: {result['terms_url']}")
                
                results.append({
                    "test": test_case['name'],
                    "status": "success",
                    "duration": duration,
                    "content_length": len(result['content']),
                    "api_status": result['status']
                })
                
            else:
                print(f"❌ ERROR {response.status_code}")
                print(f"   Response: {response.text}")
                
                results.append({
                    "test": test_case['name'],
                    "status": "error",
                    "duration": duration,
                    "error_code": response.status_code,
                    "error_message": response.text
                })
                
        except requests.exceptions.Timeout:
            print(f"⏰ TIMEOUT after {duration:.2f}s")
            results.append({
                "test": test_case['name'],
                "status": "timeout",
                "duration": duration
            })
        except requests.exceptions.ConnectionError:
            print("🔌 CONNECTION ERROR - Server not running?")
            results.append({
                "test": test_case['name'],
                "status": "connection_error"
            })
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {str(e)}")
            results.append({
                "test": test_case['name'],
                "status": "unexpected_error",
                "error": str(e)
            })
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 50)
    
    successful = sum(1 for r in results if r['status'] == 'success')
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    if successful > 0:
        avg_duration = sum(r['duration'] for r in results if r['status'] == 'success') / successful
        print(f"⏱️  Average duration: {avg_duration:.2f}s")
        
        avg_content = sum(r['content_length'] for r in results if r['status'] == 'success') / successful
        print(f"📝 Average content length: {avg_content:.0f} characters")
    
    # Detailed results
    print(f"\n📋 Detailed Results:")
    for result in results:
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        print(f"  {status_emoji} {result['test']}: {result['status']}")
        if result['status'] == 'success':
            print(f"     Duration: {result['duration']:.2f}s, Content: {result['content_length']} chars")
        elif 'duration' in result:
            print(f"     Duration: {result['duration']:.2f}s")
    
    return results

if __name__ == "__main__":
    print("Terms & Conditions API Test Suite")
    print("Make sure the server is running: make dev-server")
    print("=" * 50)
    
    test_terms_and_conditions_api()
