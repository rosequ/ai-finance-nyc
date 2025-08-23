#!/usr/bin/env python3
"""
DSPy tools that wrap FastAPI endpoints for intelligent agent workflows
"""

import requests
import dspy
from typing import Optional, Union, List, Dict, Any
import json
import os
from datetime import datetime
from urllib.parse import urlparse


class APIClient:
    """Client for interacting with our FastAPI endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def call_endpoint(self, endpoint: str, data: dict, timeout: int = 120) -> dict:
        """Make a request to an API endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}", 
                json=data, 
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "failed"}


class ContentRetrieverTool(dspy.Signature):
    """Tool to retrieve content either from a URL or by finding terms & conditions for a company"""
    
    input_query: str = dspy.InputField(desc="Either a URL to scrape or a company name to find terms for")
    company_name: Optional[str] = dspy.InputField(desc="Optional company name for more specific searches", default=None)
    product_name: Optional[str] = dspy.InputField(desc="Optional product name for more specific searches", default=None)
    
    content: str = dspy.OutputField(desc="Retrieved content from URL or terms & conditions")
    source_url: str = dspy.OutputField(desc="The source URL of the content")
    content_type: str = dspy.OutputField(desc="Type of content: 'scraped_url' or 'terms_and_conditions'")
    status: str = dspy.OutputField(desc="Status of the retrieval: 'success' or 'failed'")


class RedditSearchTool(dspy.Signature):
    """Tool to search for Reddit discussions about a company or topic"""
    
    query: str = dspy.InputField(desc="Company name or topic to search for on Reddit")
    count: Optional[int] = dspy.InputField(desc="Number of results to return", default=10)
    
    reddit_discussions: str = dspy.OutputField(desc="Summary of Reddit discussions and sentiment")
    search_results: List[Dict] = dspy.OutputField(desc="Raw search results from Reddit")
    status: str = dspy.OutputField(desc="Status of the search: 'success' or 'failed'")


class ContentRetriever(dspy.Module):
    """Module that implements content retrieval logic"""
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.signature = ContentRetrieverTool
    
    def forward(self, input_query: str, company_name: Optional[str] = None, product_name: Optional[str] = None):
        """Retrieve content from URL or find terms & conditions"""
        
        # Check if input is a URL
        parsed = urlparse(input_query)
        is_url = bool(parsed.netloc and parsed.scheme)
        
        if is_url:
            # Scrape the URL directly
            print(f"🌐 Scraping URL: {input_query}")
            data = {"url": input_query}
            result = self.api_client.call_endpoint("/scrape", data)
            
            if "error" not in result and result.get("status") == "success":
                content = result.get("content", "")
                # Check if we got meaningful content
                if len(content) > 200:  # Minimum threshold for meaningful content
                    return dspy.Prediction(
                        content=content,
                        source_url=result.get("url", input_query),
                        content_type="scraped_url",
                        status="success"
                    )
                else:
                    return dspy.Prediction(
                        content=f"URL scraped but content too short ({len(content)} chars). May be blocked or requires JavaScript.",
                        source_url=input_query,
                        content_type="scraped_url",
                        status="failed"
                    )
            else:
                error_msg = result.get('error', 'Unknown scraping error')
                return dspy.Prediction(
                    content=f"Error scraping URL: {error_msg}",
                    source_url=input_query,
                    content_type="scraped_url",
                    status="failed"
                )
        else:
            # Find terms & conditions for the company
            print(f"🔍 Finding terms & conditions for: {input_query}")
            data = {
                "query": input_query,
                "company_name": company_name,
                "product_name": product_name
            }
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}
            
            result = self.api_client.call_endpoint("/terms-and-conditions", data)
            
            if "error" not in result and result.get("status") == "success":
                return dspy.Prediction(
                    content=result.get("content", ""),
                    source_url=result.get("terms_url", ""),
                    content_type="terms_and_conditions",
                    status="success"
                )
            else:
                return dspy.Prediction(
                    content=f"No terms & conditions found for {input_query}",
                    source_url="",
                    content_type="terms_and_conditions", 
                    status="failed"
                )


class RedditSearcher(dspy.Module):
    """Module that implements Reddit search logic"""
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.signature = RedditSearchTool
    
    def forward(self, query: str, count: Optional[int] = 10):
        """Search for Reddit discussions about a company or topic"""
        
        print(f"🔍 Searching Reddit for: {query}")
        
        # Create Reddit-specific search query
        reddit_query = f"{query} site:reddit.com"
        
        data = {
            "query": reddit_query,
            "count": count or 10
        }
        
        result = self.api_client.call_endpoint("/search", data)
        
        if "error" not in result and result.get("status") == "success":
            results = result.get("results", [])
            
            # Process and summarize Reddit discussions
            reddit_summary = self._summarize_reddit_results(results, query)
            
            return dspy.Prediction(
                reddit_discussions=reddit_summary,
                search_results=results,
                status="success"
            )
        else:
            return dspy.Prediction(
                reddit_discussions=f"No Reddit discussions found for {query}",
                search_results=[],
                status="failed"
            )
    
    def _summarize_reddit_results(self, results: List[Dict], query: str) -> str:
        """Summarize Reddit search results"""
        if not results:
            return f"No Reddit discussions found for {query}"
        
        summary = f"Reddit Discussions about {query}:\n"
        summary += "=" * 50 + "\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            description = result.get("description", "No description")
            
            summary += f"{i}. {title}\n"
            summary += f"   URL: {url}\n"
            summary += f"   Description: {description[:200]}...\n\n"
        
        summary += f"\nTotal discussions found: {len(results)}\n"
        return summary


class CompanyAnalysisWorkflow(dspy.Module):
    """Main workflow that orchestrates content retrieval and Reddit search"""
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.content_retriever = ContentRetriever(api_client)
        self.reddit_searcher = RedditSearcher(api_client)
    
    def forward(self, input_query: str, company_name: Optional[str] = None, product_name: Optional[str] = None, output_file: Optional[str] = None):
        """
        Main workflow:
        1. Retrieve content (URL or terms & conditions)
        2. Search Reddit for discussions
        3. Combine outputs and save to file
        """
        
        print(f"🚀 Starting Company Analysis Workflow")
        print(f"📋 Input: {input_query}")
        if company_name:
            print(f"🏢 Company: {company_name}")
        if product_name:
            print(f"📦 Product: {product_name}")
        print("=" * 60)
        
        # Step 1: Retrieve content
        print("\n📄 Step 1: Retrieving Content...")
        content_result = self.content_retriever(
            input_query=input_query,
            company_name=company_name,
            product_name=product_name
        )
        
        # Step 2: Search Reddit (use company name if provided, otherwise use input_query)
        search_query = company_name or input_query
        # Remove URL protocol/domain if it's a URL for better Reddit search
        parsed = urlparse(search_query)
        if parsed.netloc:
            search_query = parsed.netloc.replace("www.", "")
        
        print(f"\n🔍 Step 2: Searching Reddit for discussions about '{search_query}'...")
        reddit_result = self.reddit_searcher(query=search_query)
        
        # Step 3: Combine and save results
        print(f"\n💾 Step 3: Combining results and saving to file...")
        combined_output = self._combine_results(
            content_result, 
            reddit_result, 
            input_query,
            company_name,
            product_name
        )
        
        # Save to file
        file_path = self._save_to_file(combined_output, output_file, input_query)
        
        print(f"✅ Analysis complete! Results saved to: {file_path}")
        
        return dspy.Prediction(
            analysis_report=combined_output,
            file_path=file_path,
            content_status=content_result.status,
            reddit_status=reddit_result.status,
            status="success"
        )
    
    def _combine_results(self, content_result, reddit_result, input_query: str, company_name: Optional[str], product_name: Optional[str]) -> str:
        """Combine content and Reddit results into a comprehensive report"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""COMPANY ANALYSIS REPORT
Generated on: {timestamp}
Query: {input_query}
Company: {company_name or 'N/A'}
Product: {product_name or 'N/A'}

{'=' * 80}

SECTION 1: CONTENT ANALYSIS
{'=' * 80}

Content Type: {content_result.content_type}
Source URL: {content_result.source_url}
Status: {content_result.status}

Content:
{'-' * 40}
{content_result.content}

{'=' * 80}

SECTION 2: REDDIT DISCUSSIONS & SENTIMENT
{'=' * 80}

Status: {reddit_result.status}

{reddit_result.reddit_discussions}

{'=' * 80}

SUMMARY
{'=' * 80}

This report contains:
1. {content_result.content_type.replace('_', ' ').title()} from {content_result.source_url or 'N/A'}
2. Reddit community discussions and sentiment analysis
3. Generated on {timestamp}

Content Status: {content_result.status}
Reddit Search Status: {reddit_result.status}

Total Reddit Results: {len(reddit_result.search_results)}
"""
        return report
    
    def _save_to_file(self, content: str, output_file: Optional[str], input_query: str) -> str:
        """Save the combined report to a file"""
        
        if not output_file:
            # Generate filename from input
            safe_name = "".join(c for c in input_query if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_').lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"company_analysis_{safe_name}_{timestamp}.txt"
        
        # Ensure .txt extension
        if not output_file.endswith('.txt'):
            output_file += '.txt'
        
        # Create output directory
        output_dir = "company_analysis_reports"
        os.makedirs(output_dir, exist_ok=True)
        
        file_path = os.path.join(output_dir, output_file)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path


# Simple URL Scraper Tool
class URLScraperTool(dspy.Signature):
    """Tool to scrape content from a URL"""
    
    url: str = dspy.InputField(desc="URL to scrape")
    
    content: str = dspy.OutputField(desc="Scraped content from the URL")
    title: str = dspy.OutputField(desc="Page title")
    status: str = dspy.OutputField(desc="Status of the scraping: 'success' or 'failed'")


class URLScraper(dspy.Module):
    """Module that scrapes URLs"""
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.signature = URLScraperTool
    
    def forward(self, url: str):
        """Scrape content from a URL"""
        
        print(f"🌐 Scraping URL: {url}")
        
        data = {"url": url}
        result = self.api_client.call_endpoint("/scrape", data)
        
        # Accept success, timeout, and even failed if we got some content
        status = result.get("status", "failed")
        content = result.get("content", "")
        title = result.get("title", "")
        
        if "error" not in result and status in ["success", "timeout"] and len(content) > 0:
            return dspy.Prediction(
                content=content,
                title=title,
                status="success"
            )
        elif len(content) > 50:  # If we got some meaningful content even on "failed"
            print(f"⚠️ Partial success: Got {len(content)} characters despite status '{status}'")
            return dspy.Prediction(
                content=content,
                title=title,
                status="partial_success"
            )
        else:
            error_msg = result.get('error', f'Scraping returned status: {status}')
            return dspy.Prediction(
                content=f"Error scraping URL: {error_msg}",
                title="",
                status="failed"
            )


# Main analysis function with simple logic
def analyze_input(
    input_query: str, 
    company_name: Optional[str] = None, 
    product_name: Optional[str] = None,
    output_file: Optional[str] = None,
    api_base_url: str = "http://localhost:8000"
) -> Dict[str, Any]:
    """
    Main analysis function with simple logic:
    1. If URL provided -> call URL scraper
    2. If company name -> call CompanyAnalysisWorkflow
    
    Args:
        input_query: Either a URL to scrape or a company name
        company_name: Optional company name for more specific searches
        product_name: Optional product name
        output_file: Optional custom output filename
        api_base_url: Base URL for the FastAPI server
    
    Returns:
        Dictionary with analysis results and file path
    """
    
    print(f"📋 STEP 1: Analyzing input type for '{input_query}'")
    
    # Check if input is a URL
    parsed = urlparse(input_query)
    is_url = bool(parsed.netloc and parsed.scheme)
    
    # Create API client
    api_client = APIClient(api_base_url)
    
    if is_url:
        print(f"📋 STEP 2: Detected URL - calling scraper")
        
        # Use URL scraper
        scraper = URLScraper(api_client)
        scrape_result = scraper(url=input_query)
        
        print(f"📋 STEP 3: Scraping completed with status: {scrape_result.status}")
        if scrape_result.status == "partial_success":
            print(f"   ⚠️ Partial success: Got content despite some issues")
        
        # Also search Reddit for the domain
        domain = parsed.netloc.replace('www.', '').split('.')[0]
        print(f"📋 STEP 4: Searching Reddit for '{domain}'")
        
        reddit_searcher = RedditSearcher(api_client)
        reddit_result = reddit_searcher(query=domain)
        
        print(f"📋 STEP 5: Reddit search completed with status: {reddit_result.status}")
        
        # Generate report
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""URL ANALYSIS REPORT
Generated on: {timestamp}
Input URL: {input_query}
Analysis Type: URL Scraping

{'=' * 80}

SECTION 1: URL CONTENT
{'=' * 80}

URL: {input_query}
Title: {scrape_result.title}
Status: {scrape_result.status}

Content:
{'-' * 40}
{scrape_result.content}

{'=' * 80}

SECTION 2: REDDIT DISCUSSIONS
{'=' * 80}

{reddit_result.reddit_discussions}

{'=' * 80}

SUMMARY
{'=' * 80}

Analysis Type: URL Scraping
Scraping Status: {scrape_result.status}
Reddit Search Status: {reddit_result.status}
Generated: {timestamp}
"""
        
        # Save report
        output_dir = "company_analysis_reports"
        os.makedirs(output_dir, exist_ok=True)
        
        if not output_file:
            domain_clean = domain.replace('.', '_')
            output_file = f"{domain_clean}_url_analysis.txt"
        
        file_path = os.path.join(output_dir, output_file)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📋 STEP 6: Report saved to {file_path}")
        
        return {
            "analysis_report": report,
            "file_path": file_path,
            "content_status": scrape_result.status,
            "reddit_status": reddit_result.status,
            "status": "success"
        }
    
    else:
        print(f"📋 STEP 2: Detected company name - calling CompanyAnalysisWorkflow")
        
        # Use company analysis workflow
        workflow = CompanyAnalysisWorkflow(api_client)
        result = workflow(
            input_query=input_query,
            company_name=company_name,
            product_name=product_name,
            output_file=output_file
        )
        
        print(f"📋 STEP 3: CompanyAnalysisWorkflow completed")
        
        return {
            "analysis_report": result.analysis_report,
            "file_path": result.file_path,
            "content_status": result.content_status,
            "reddit_status": result.reddit_status,
            "status": result.status
        }


# Keep the old function name for backward compatibility
def analyze_company(*args, **kwargs):
    """Backward compatibility wrapper"""
    return analyze_input(*args, **kwargs)


if __name__ == "__main__":
    # Example usage
    print("DSPy Company Analysis Tools Demo")
    print("=" * 40)
    
    # Test with a company name
    result = analyze_company(
        input_query="Netflix",
        company_name="Netflix Inc",
        output_file="netflix_analysis_demo.txt"
    )
    
    print(f"Analysis complete!")
    print(f"Report saved to: {result['file_path']}")
    print(f"Status: {result['status']}")
