#!/usr/bin/env python3
"""
Debug script to see what's happening with the analysis
"""

from src.analyzer import FinancialProductAnalyzer
from src.pipeline import analyzer_pipeline

def test_simple_analysis():
    """Test with simple content"""
    
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
        print("🔍 Testing product info extraction...")
        analyzer = FinancialProductAnalyzer()
        
        # Test product info extraction
        product_info = analyzer.extract_product_info(test_content)
        print("Product info result:", product_info)
        
        if "error" not in product_info:
            product_type = product_info["product_type"]
            print(f"✅ Product type: {product_type}")
            
            # Test terms analysis
            print(f"\n🔍 Testing terms analysis for {product_type}...")
            terms_analysis = analyzer.analyze_terms_and_conditions(product_type, test_content)
            print("Terms analysis result:", terms_analysis)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_pipeline():
    """Test the full pipeline"""
    test_content = """
    Personal Loan Terms
    
    XYZ Credit Union offers personal loans with the following terms:
    - Loan amounts from $1,000 to $50,000
    - Fixed APR from 6.99% to 18.99%
    - Terms from 12 to 60 months
    - No prepayment penalties
    """
    
    try:
        print("\n🔍 Testing full pipeline...")
        result = analyzer_pipeline(test_content)
        print("Pipeline result:", result)
        
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_analysis()
    test_pipeline()
