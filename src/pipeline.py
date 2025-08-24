#!/usr/bin/env python3
"""
ML Pipeline for Financial Product Analysis
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union
from urllib.parse import urlparse
import PyPDF2
import io

# Import our components
from data_sources import search_reddit, web_scrape, format_threads
from analyzer import FinancialProductAnalyzer


def is_url(input_str: str) -> bool:
    """Check if input string is a URL"""
    try:
        result = urlparse(input_str)
        return all([result.scheme, result.netloc])
    except:
        return False


def analyzer_pipeline(terms_content: Union[str]) -> Dict[str, Any]:
    analyzer = FinancialProductAnalyzer()
    product_info = analyzer.extract_product_info(terms_content)
    
    if "error" in product_info:
        return {
            "error": f"Failed to extract product info: {product_info['error']}",
            "input": terms_content[:200] + "..." if len(terms_content) > 200 else terms_content
        }
    
    product_name = product_info["product_name"]
    product_type = product_info["product_type"]
    company_name = product_info.get("company_name", "")
    
    print(f"✅ Extracted: {product_name} ({product_type}) by {company_name}")
    
    # Step 3: Analyze terms and conditions
    print("📋 Step 3: Analyzing terms and conditions...")
    terms_analysis = analyzer.analyze_terms_and_conditions(product_type, terms_content)
    
    if "error" in terms_analysis:
        return {
            "error": f"Failed to analyze terms: {terms_analysis['error']}",
            "product_info": product_info
        }
    
    # Step 4: Search Reddit discussions
    print("🔍 Step 4: Searching Reddit discussions...")
    reddit_data = search_reddit(f"{product_name} ({product_type}) by {company_name}")
    reddit_discussions = format_threads(reddit_data)
    
    print(f"✅ Got {len(reddit_data)} Reddit posts")
    
    # Step 5: Analyze Reddit discussions
    print("💬 Step 5: Analyzing Reddit discussions...")
    reddit_analysis = analyzer.reddit_analysis(reddit_discussions, product_name, product_type, company_name)
    
    if "error" in reddit_analysis:
        return {
            "error": f"Failed to analyze Reddit: {reddit_analysis['error']}",
            "product_info": product_info,
            "terms_analysis": terms_analysis,
            "reddit_data": reddit_data
        }
    
    # Step 6: Compile final results
    print("📊 Step 6: Compiling final results...")
    
    res = {
        "product_info": {
            "name": product_name,
            "type": product_type,
            "company": company_name
        },
        "terms_analysis": {
            "key_information": terms_analysis["key_information"],
            "risks": terms_analysis["risks"],
            "financial_ramifications": terms_analysis.get("financial_ramifications", ""),
            "consumer_score": terms_analysis.get("consumer_score", ""),
            "details": terms_analysis["details"]
        },
        "reddit_insights": {
            "positive": reddit_analysis["positive_insights"],
            "negative": reddit_analysis["negative_insights"]
        },
        "metadata": {
            "input": terms_content[:200] + "..." if len(terms_content) > 200 else terms_content,
            "terms_source": "chrome_extension",
            "reddit_posts_analyzed": len(reddit_data),
            "status": "success"
        },
        "reddit_data": reddit_data  # Include raw reddit data for URL display
    }
    return res


def main():
    """Example usage of the financial product pipeline"""
    print("Financial Product Pipeline")
    print("=" * 50)
    
    # Test with Wells Fargo Active Cash
    test_input = "https://www.wellsfargo.com/credit-cards/agreements/active-cash-agreement"
    
    try:
        result = analyzer_pipeline(test_input)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print("✅ Analysis completed successfully!")
            print(f"\n📋 Product: {result['product_info']['name']}")
            print(f"🏢 Company: {result['product_info']['company']}")
            print(f"📊 Type: {result['product_info']['type']}")
            print(f"\n📄 Key Information:\n{result['terms_analysis']['key_information']}")
            if result['terms_analysis'].get('consumer_score'):
                print(f"\n⭐ Consumer Score:\n{result['terms_analysis']['consumer_score']}")
            print(f"\n⚠️ Risks:\n{result['terms_analysis']['risks']}")
            print(f"\n💭 Reddit Insights:")
            print(f"👍 Positive:\n{result['reddit_insights']['positive']}")
            print(f"👎 Negative:\n{result['reddit_insights']['negative']}")
            
            # Save results
            os.makedirs("data/results", exist_ok=True)
            with open("data/results/analysis_results.json", "w") as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to data/results/analysis_results.json")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
