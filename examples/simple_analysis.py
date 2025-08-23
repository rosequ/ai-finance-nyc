#!/usr/bin/env python3
"""
Simple example of using DSPy Company Analysis Tools
"""

import sys
import os
sys.path.append('../src')

from dspy_tools import analyze_company


def main():
    """Simple examples of company analysis"""
    
    print("🔍 Simple Company Analysis Examples")
    print("=" * 50)
    
    examples = [
        {
            "name": "Analyze Netflix by company name",
            "query": "Netflix",
            "company": "Netflix Inc"
        },
        {
            "name": "Analyze from a URL",
            "query": "https://www.google.com/terms",
            "company": "Google"
        },
        {
            "name": "Analyze a financial company",
            "query": "Chase Sapphire",
            "company": "Chase",
            "product": "Credit Card"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n📋 Example {i}: {example['name']}")
        print("-" * 40)
        
        try:
            result = analyze_company(
                input_query=example["query"],
                company_name=example.get("company"),
                product_name=example.get("product"),
                output_file=f"example_{i}_analysis.txt"
            )
            
            print(f"✅ Success!")
            print(f"📁 Report: {result['file_path']}")
            print(f"📄 Content: {result['content_status']}")
            print(f"🔍 Reddit: {result['reddit_status']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
