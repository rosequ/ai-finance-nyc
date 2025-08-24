#!/usr/bin/env python3
"""
Simple debug script to test the analyzer directly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer import FinancialProductAnalyzer

def test_analyzer():
    """Test the analyzer directly"""
    
    test_content = """
    Personal Loan Agreement
    
    This agreement is between ABC Bank and the borrower for a personal loan.
    
    Loan Amount: Up to $50,000
    Interest Rate: 8.99% APR (fixed)
    Term: 36 months
    Monthly Payment: Calculated based on loan amount and term
    
    Fees:
    - Origination Fee: 2% of loan amount
    - Late Payment Fee: $35
    
    The borrower agrees to repay the loan according to the payment schedule.
    Default occurs if payment is more than 30 days late.
    """
    
    try:
        print("🔍 Testing analyzer...")
        analyzer = FinancialProductAnalyzer()
        
        # Test product info extraction
        print("1. Testing product info extraction...")
        product_info = analyzer.extract_product_info(test_content)
        print(f"   Result: {product_info}")
        
        if "error" in product_info:
            print("❌ Product info extraction failed")
            return
        
        product_type = product_info["product_type"]
        print(f"   ✅ Product type: {product_type}")
        
        # Test terms analysis
        print(f"\n2. Testing terms analysis for '{product_type}'...")
        terms_analysis = analyzer.analyze_terms_and_conditions(product_type, test_content)
        
        if "error" in terms_analysis:
            print(f"   ❌ Terms analysis failed: {terms_analysis['error']}")
            if 'raw_response' in terms_analysis:
                print(f"   Raw response: {terms_analysis['raw_response'][:500]}...")
        else:
            print("   ✅ Terms analysis successful!")
            print(f"   Key info: {terms_analysis.get('key_information', 'N/A')[:200]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analyzer()
