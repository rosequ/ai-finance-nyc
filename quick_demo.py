#!/usr/bin/env python3
"""
Quick demo showing the user input interface
"""

import sys
sys.path.append('src')

from dspy_tools import analyze_company
import requests


def check_server():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False


def quick_demo():
    """Quick demo with user input"""
    
    print("🤖 Quick DSPy Analysis Demo")
    print("=" * 40)
    
    if not check_server():
        print("❌ Server not running. Start with: make dev-server")
        return
    
    print("✅ Server is running!")
    
    # Simulate user input for demo
    example_query = "Netflix"
    print(f"\n📝 Example analysis: {example_query}")
    
    try:
        result = analyze_company(
            input_query=example_query,
            output_file="quick_demo_netflix.txt"
        )
        
        print(f"✅ Success!")
        print(f"📁 Report: {result['file_path']}")
        print(f"📄 Content: {result['content_status']}")
        print(f"🔍 Reddit: {result['reddit_status']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    quick_demo()
