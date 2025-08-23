#!/usr/bin/env python3
"""
Demo script for DSPy Company Analysis Agent
"""

import sys
import os
sys.path.append('src')

from dspy_tools import analyze_company, APIClient, CompanyAnalysisWorkflow
import time
import requests


def check_server_running(base_url="http://localhost:8000"):
    """Check if the FastAPI server is running"""
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        return response.status_code == 200
    except:
        return False


def simple_analysis():
    """Simplified single input analysis with detailed logging"""
    
    print("🤖 DSPy Company Analysis Agent")
    print("=" * 60)
    
    # Step 1: Check server
    print("📋 STEP 1: Checking FastAPI server...")
    if not check_server_running():
        print("❌ FastAPI server is not running!")
        print("💡 Please start the server with: make dev-server")
        return
    print("✅ Server is running and ready")
    
    # Step 2: Get user input  
    print(f"\n📋 STEP 2: Getting user input")
    print(f"   You can provide:")
    print(f"   • A company name (e.g., 'Netflix', 'Tesla', 'Google')")
    print(f"   • A URL to analyze (e.g., 'https://company.com/terms')")
    
    input_query = input("\n🔍 Enter company name or URL: ").strip()
    
    if not input_query:
        print("❌ Please enter a valid input")
        return
    
    print(f"✅ Input received: {input_query}")
    
    # Step 3: Determine input type and strategy
    print(f"\n📋 STEP 3: Analyzing input type...")
    from urllib.parse import urlparse
    parsed = urlparse(input_query)
    is_url = bool(parsed.netloc and parsed.scheme)
    
    if is_url:
        print(f"✅ Detected URL input - will scrape directly")
        analysis_type = "URL Scraping"
    else:
        print(f"✅ Detected company name - will find terms & search Reddit")
        analysis_type = "Company Analysis"
    
    # Step 4: Generate output filename
    print(f"\n📋 STEP 4: Generating output filename...")
    safe_name = "".join(c for c in input_query if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_').lower()
    if is_url:
        domain = parsed.netloc.replace('www.', '')
        safe_name = domain.replace('.', '_')
    output_file = f"{safe_name}_analysis.txt"
    print(f"✅ Output file: {output_file}")
    
    try:
        print(f"\n📋 STEP 5: Starting {analysis_type}...")
        print("=" * 60)
        start_time = time.time()
        
        # Use the simplified dspy_tools logic
        sys.path.append('src')
        from dspy_tools import analyze_input
        
        # Run the simplified analysis
        result = analyze_input(
            input_query=input_query,
            output_file=output_file
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Analysis complete!")
        print(f"💾 File size: {os.path.getsize(result['file_path']):,} bytes")
        
        print(f"\n📋 STEP 6: Analysis complete!")
        print("=" * 60)
        print(f"⏱️  Total duration: {duration:.2f} seconds")
        print(f"📁 Report location: {result['file_path']}")
        print(f"📄 Content status: {result['content_status']}")
        print(f"🔍 Reddit status: {result['reddit_status']}")
        
        # Show brief summary
        print(f"\n📄 Report Summary:")
        print(f"   📊 Analysis Type: {analysis_type}")
        print(f"   📄 Status: {result['status']}")
        print(f"   🔍 Reddit Status: {result['reddit_status']}")
        print(f"   💾 Full report saved to: {result['file_path']}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        print("💡 Make sure the FastAPI server is running and API keys are configured")


def repeat_analysis():
    """Simple repeat analysis option"""
    
    while True:
        print(f"\n🔄 Would you like to analyze another company or URL? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice in ['y', 'yes']:
            print("\n" + "="*60)
            simple_analysis()
        else:
            print("👋 Thanks for using DSPy Company Analysis Agent!")
            break


if __name__ == "__main__":
    print("🤖 DSPy Company Analysis Agent (Simplified)")
    print("Make sure the FastAPI server is running: make dev-server")
    print("=" * 60)
    
    # Run simple analysis
    simple_analysis()
    
    # Option to repeat
    repeat_analysis()
