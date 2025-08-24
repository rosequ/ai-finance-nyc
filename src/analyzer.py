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
    
    def _fix_markdown_formatting(self, text: str) -> str:
        """Remove all asterisks to eliminate markdown formatting issues"""
        if not text:
            return text
        
        # Remove all asterisks to eliminate markdown formatting completely
        # This ensures clean, readable text without formatting issues
        text = text.replace('**', '')
        text = text.replace('*', '')
        
        return text
    
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
        
        # Get the prompt file name, fallback to loan template
        prompt_file = prompt_mapping.get(product_type.lower(), "loan.txt")
        if not prompt_file:
            prompt_file = "loan.txt"  # Default to loan template
        
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", prompt_file)
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content or content.startswith("#"):
                    raise ValueError(f"Prompt template for {product_type} is empty or not implemented")
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt template file not found: {prompt_path}")

    def _load_rating_prompt(self) -> str:
        """
        Load the rating prompt template
        
        Returns:
            Rating prompt template string
        """
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "rating.txt")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content or content.startswith("#"):
                    raise ValueError("Rating prompt template is empty or not implemented")
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"Rating prompt template file not found: {prompt_path}")

    def extract_product_info(self, terms_content: str) -> Dict[str, Any]:
        """
        Step 1: Extract product name, type, and company from terms content
        
        Args:
            terms_content: Raw text containing product terms and conditions
            
        Returns:
            Dictionary with product_name, product_type, and company_name
        """
        prompt = f"""
        You are an expert AI financial analyst. Read the input and extract the product information.

        <input_data>
        {terms_content}
        </input_data>

        Task:
        1) Extract the product's marketed or legal name.
        2) Extract the company/bank name that offers this product.
        3) Classify the product type as exactly one of: credit card, loan. If unclear, default to loan.

        Output only:
        <product_name>
        {{PRODUCT_NAME}}
        </product_name>

        <company_name>
        {{COMPANY_NAME}}
        </company_name>

        <product_type>
        {{PRODUCT_TYPE}}  <!-- credit card | loan -->
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
            company_name = self._extract_xml_tag(response_content, "company_name")
            product_type = self._extract_xml_tag(response_content, "product_type")
            
            # Ensure product_type is valid, default to loan
            if not product_type or product_type.lower() not in ["credit card", "loan"]:
                product_type = "loan"
            
            if not product_name or not product_type:
                return {
                    "error": "Failed to extract product information",
                    "raw_response": response_content,
                    "terms_content": terms_content
                }
            
            return {
                "product_name": product_name.strip(),
                "company_name": company_name.strip() if company_name else "",
                "product_type": product_type.strip().lower(),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": f"Error extracting product info: {str(e)}",
                "terms_content": terms_content
            }
    
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
            PRODUCT_TYPE=product_type,
            TERMS_AND_CONDITIONS=terms_and_conditions,
            product_type=product_type,
            terms_and_conditions=terms_and_conditions,
            terms_content=terms_and_conditions
        )
        
        try:
            # Call Claude Sonnet 4
            message = self.client.messages.create(
                model="claude-opus-4-1-20250805",
                # model="claude-3-5-haiku-20241022",
                max_tokens=5000,
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
            parsed_product_type = self._extract_xml_tag(response_content, "product_type")
            key_information = self._extract_xml_tag(response_content, "key_information")
            risks = self._extract_xml_tag(response_content, "risks")
            financial_ramifications = self._extract_xml_tag(response_content, "financial_ramifications")
            consumer_score = self._extract_xml_tag(response_content, "consumer_score")
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
                "key_information": self._fix_markdown_formatting(key_information.strip()),
                "risks": self._fix_markdown_formatting(risks.strip()),
                "financial_ramifications": self._fix_markdown_formatting(financial_ramifications.strip()) if financial_ramifications else "",
                "consumer_score": self._fix_markdown_formatting(consumer_score.strip()) if consumer_score else "",
                "details": self._fix_markdown_formatting(details.strip()),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": f"Error analyzing terms and conditions: {str(e)}",
                "product_type": product_type,
                "terms_and_conditions": terms_and_conditions[:500] + "..." if len(terms_and_conditions) > 500 else terms_and_conditions
            }

    def reddit_analysis(self, reddit_discussions: str, product_name: str = "", product_type: str = "", company_name: str = "") -> Dict[str, Any]:
        """
        Step 3: Analyze Reddit discussions and return insights
        
        Args:
            reddit_discussions: Reddit discussions as string
            product_name: Name of the product
            product_type: Type of the product
            company_name: Name of the company
            
        Returns:
            Dictionary with positive and negative insights
        """
        prompt = f"""
        You are an expert financial analyst. Analyze the Reddit discussions about {product_name} ({product_type}) by {company_name} and provide concise insights.

        <reddit_discussions>
        {reddit_discussions}
        </reddit_discussions>

        Task: Extract 2-3 SHORT bullet points each (max 15 words per bullet):
        - 2-3 positive insights/experiences
        - 2-3 negative insights/concerns

        Keep each bullet point VERY brief and specific. Focus on the most important themes only.

        Output only:
        <positive_insights>
        - [Brief positive insight 1]
        - [Brief positive insight 2]
        - [Brief positive insight 3]
        </positive_insights>

        <negative_insights>
        - [Brief negative insight 1]
        - [Brief negative insight 2]
        - [Brief negative insight 3]
        </negative_insights>

        Remember:
        - Return the text nicely formatted in Markdown (bold, bullet points, etc.).
        """
        
        try:
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=800,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_content = message.content[0].text.strip()
            
            positive_insights = self._extract_xml_tag(response_content, "positive_insights")
            negative_insights = self._extract_xml_tag(response_content, "negative_insights")
            
            if not positive_insights and not negative_insights:
                return {
                    "error": "Failed to parse Reddit analysis response",
                    "raw_response": response_content
                }
            
            return {
                "positive_insights": positive_insights.strip(),
                "negative_insights": negative_insights.strip(),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": f"Error analyzing Reddit discussions: {str(e)}"
            }

    def gen_analysis(self, terms_content: str) -> Dict[str, Any]:
        """
        Complete two-step analysis of financial product
        
        Args:
            terms_content: Raw text containing product terms and conditions
            
        Returns:
            Dictionary with complete analysis
        """
        # Step 1: Extract product information
        print("🔍 Step 1: Extracting product information...")
        product_info = self.extract_product_info(terms_content)
        
        if "error" in product_info:
            return {
                "error": f"Step 1 failed: {product_info['error']}",
                "step": "product_extraction",
                "terms_content": terms_content
            }
        
        product_name = product_info["product_name"]
        product_type = product_info["product_type"]
        company_name = product_info.get("company_name", "")
        
        print(f"✅ Extracted: {product_name} ({product_type}) by {company_name}")
        
        # Check if it's a financial product
        if product_type == "neither":
            return {
                "error": "Not a financial product",
                "product_name": product_name,
                "product_type": product_type,
                "terms_content": terms_content
            }
        
        # Step 2: Analyze terms and conditions
        print("📋 Step 2: Analyzing terms and conditions...")
        analysis = self.analyze_terms_and_conditions(product_type, terms_content)
        
        if "error" in analysis:
            return {
                "error": f"Step 2 failed: {analysis['error']}",
                "step": "terms_analysis",
                "product_name": product_name,
                "product_type": product_type,
                "terms_content": terms_content
            }
        
        # Combine results
        return {
            "product_name": product_name,
            "product_type": product_type,
            "company_name": company_name,
            "key_information": analysis["key_information"],
            "risks": analysis["risks"],
            "consumer_score": analysis.get("consumer_score", ""),
            "details": analysis["details"],
            "status": "success"
        }


def main():
    """Example usage of the financial product analyzer"""
    print("Financial Product Analyzer")
    print("=" * 60)
    
    # Path to the PDF file
    # path = "terms_and_conditions/AGREEMENT_CRKE_95.pdf"
    path = "https://www.wellsfargo.com/credit-cards/agreements/active-cash-agreement"
    
    try:
        # Read content from URL using ContentReader
        from data_collector import ContentReader
        content_reader = ContentReader()
        
        print(f"📄 Reading URL: {path}")
        input_text = content_reader.read_from_url(path)
        
        print(f"✅ URL read successfully!")
        print(f"📊 Input text length: {len(input_text)} characters")
        print(f"📄 First 200 characters: {input_text[:200]}...")
        print("\n" + "=" * 60)
        
        # Initialize analyzer and analyze the text
        analyzer = FinancialProductAnalyzer()
        result = analyzer.gen_analysis(input_text)
        
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
