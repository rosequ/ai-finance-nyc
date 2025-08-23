#!/usr/bin/env python3
"""
Financial Product Analyzer using Anthropic Claude Sonnet 4
"""

import os
import json
import anthropic
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FinancialProductAnalyzer:
    """Analyze financial product information using Claude Sonnet 4"""
    
    def __init__(self):
        """Initialize the analyzer with Anthropic client"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def extract_product_info(self, input_text: str) -> Dict[str, Any]:
        """
        Step 1: Extract product name and type from input text
        
        Args:
            input_text: Raw text containing product information
            
        Returns:
            Dictionary with product_name and product_type
        """
        prompt = f"""
        You are an expert AI financial analyst. Read the input and decide the product name and type.

        <input_data>
        {input_text}
        </input_data>

        Task:
        1) Extract the product's marketed or legal name.
        2) Classify the product type as exactly one of: credit card, loan, neither.

        Output only:
        <product_name>
        {{PRODUCT_NAME}}
        </product_name>

        <product_type>
        {{PRODUCT_TYPE}}  <!-- credit card | loan | neither -->
        </product_type>
        """
        
        try:
            # Call Claude Sonnet 4
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=500,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_content = message.content[0].text.strip()
            
            # Parse the XML-like response
            product_name = self._extract_xml_tag(response_content, "product_name")
            product_type = self._extract_xml_tag(response_content, "product_type")
            
            if not product_name or not product_type:
                return {
                    "error": "Failed to extract product information",
                    "raw_response": response_content,
                    "input_text": input_text
                }
            
            return {
                "product_name": product_name.strip(),
                "product_type": product_type.strip().lower(),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": f"Error extracting product info: {str(e)}",
                "input_text": input_text
            }
    
    def _load_prompt_template(self, product_type: str) -> str:
        """
        Load the appropriate prompt template based on product type
        
        Args:
            product_type: Type of financial product
            
        Returns:
            Prompt template string
        """
        # Map product types to prompt files
        prompt_mapping = {
            "credit card": "credit_card.txt",
            "loan": "loan.txt"
        }
        
        # Get the prompt file name
        prompt_file = prompt_mapping.get(product_type.lower())
        if not prompt_file:
            raise ValueError(f"No prompt template found for product type: {product_type}")
        
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", prompt_file)
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content or content.startswith("#"):
                    raise ValueError(f"Prompt template for {product_type} is empty or not implemented")
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt template file not found: {prompt_path}")
    
    def analyze_terms_and_conditions(self, product_type: str, terms_and_conditions: str) -> Dict[str, Any]:
        """
        Step 2: Analyze terms and conditions for financial products
        
        Args:
            product_type: Type of financial product (credit card, loan, etc.)
            terms_and_conditions: The terms and conditions text
            
        Returns:
            Dictionary with comprehensive analysis
        """
        # Load the appropriate prompt template
        prompt_template = self._load_prompt_template(product_type)
        
        # Format the prompt with the specific data
        prompt = prompt_template.format(
            product_type=product_type,
            terms_and_conditions=terms_and_conditions
        )
        
        try:
            # Call Claude Sonnet 4
            message = self.client.messages.create(
                # model="claude-opus-4-1-20250805",
                model="claude-3-5-haiku-20241022",
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_content = message.content[0].text.strip()
            
            # Parse the XML-like response
            parsed_product_type = self._extract_xml_tag(response_content, "product_type")
            key_information = self._extract_xml_tag(response_content, "key_information")
            risks = self._extract_xml_tag(response_content, "risks")
            details = self._extract_xml_tag(response_content, "details")
            
            if not all([parsed_product_type, key_information, risks, details]):
                return {
                    "error": "Failed to parse analysis response",
                    "raw_response": response_content,
                    "product_type": product_type,
                    "terms_and_conditions": terms_and_conditions[:500] + "..." if len(terms_and_conditions) > 500 else terms_and_conditions
                }
            
            return {
                "product_type": parsed_product_type.strip(),
                "key_information": key_information.strip(),
                "risks": risks.strip(),
                "details": details.strip(),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": f"Error analyzing terms and conditions: {str(e)}",
                "product_type": product_type,
                "terms_and_conditions": terms_and_conditions[:500] + "..." if len(terms_and_conditions) > 500 else terms_and_conditions
            }
    
    def _extract_xml_tag(self, text: str, tag_name: str) -> str:
        """Extract content from XML-like tags"""
        start_tag = f"<{tag_name}>"
        end_tag = f"</{tag_name}>"
        
        start_idx = text.find(start_tag)
        if start_idx == -1:
            return ""
        
        start_idx += len(start_tag)
        end_idx = text.find(end_tag, start_idx)
        
        if end_idx == -1:
            return ""
        
        return text[start_idx:end_idx].strip()
    
    def analyze_financial_product(self, input_text: str) -> Dict[str, Any]:
        """
        Complete two-step analysis of financial product
        
        Args:
            input_text: Raw text containing product information and terms
            
        Returns:
            Dictionary with complete analysis
        """
        # Step 1: Extract product information
        print("🔍 Step 1: Extracting product information...")
        product_info = self.extract_product_info(input_text)
        
        if "error" in product_info:
            return {
                "error": f"Step 1 failed: {product_info['error']}",
                "step": "product_extraction",
                "input_text": input_text
            }
        
        product_name = product_info["product_name"]
        product_type = product_info["product_type"]
        
        print(f"✅ Extracted: {product_name} ({product_type})")
        
        # Check if it's a financial product
        if product_type == "neither":
            return {
                "error": "Not a financial product",
                "product_name": product_name,
                "product_type": product_type,
                "input_text": input_text
            }
        
        # Step 2: Analyze terms and conditions
        print("📋 Step 2: Analyzing terms and conditions...")
        analysis = self.analyze_terms_and_conditions(product_type, input_text)
        
        if "error" in analysis:
            return {
                "error": f"Step 2 failed: {analysis['error']}",
                "step": "terms_analysis",
                "product_name": product_name,
                "product_type": product_type,
                "input_text": input_text
            }
        
        # Combine results
        return {
            "product_name": product_name,
            "product_type": product_type,
            "key_information": analysis["key_information"],
            "risks": analysis["risks"],
            "details": analysis["details"],
            "status": "success"
        }
    

def analyze_financial_product_simple(input_text: str) -> Dict[str, Any]:
    """
    Simple function to analyze a financial product
    
    Args:
        input_text: Raw text containing product information and terms
        
    Returns:
        Dictionary containing the analysis results
    """
    analyzer = FinancialProductAnalyzer()
    return analyzer.analyze_financial_product(input_text)


def main():
    """Example usage of the financial product analyzer"""
    print("Financial Product Analyzer")
    print("=" * 60)
    
    # Path to the PDF file
    # path = "terms_and_conditions/AGREEMENT_CRKE_95.pdf"
    path = "https://www.wellsfargo.com/credit-cards/agreements/active-cash-agreement"
    
    try:
        # Read content from PDF using ContentReader
        from content_reader import ContentReader
        content_reader = ContentReader()
        
        print(f"📄 Reading PDF file: {path}")
        input_text = content_reader.read_content(path)
        
        print(f"✅ PDF read successfully!")
        print(f"📊 Input text length: {len(input_text)} characters")
        print(f"📄 First 200 characters: {input_text[:200]}...")
        print("\n" + "=" * 60)
        
        # Initialize analyzer and analyze the text
        analyzer = FinancialProductAnalyzer()
        result = analyzer.analyze_financial_product(input_text)
        
        # Print results
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            if "raw_response" in result:
                print(f"Raw response: {result['raw_response']}")
        else:
            print("✅ Analysis completed successfully!")
        
            print(f"Product: {result['product_name']}")
            print(f"Type: {result['product_type']}")
            print(result['key_information'])
            print(result['risks'])
            print(result['details'])
        
    except Exception as e:
        print(f"❌ Failed to analyze product: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
