#!/usr/bin/env python3
"""
FastAPI server for AI Finance NYC
"""

import os
import json
import asyncio
import tempfile
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
import anthropic
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import PyPDF2

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Finance NYC API",
    description="API for web scraping and text summarization",
    version="1.0.0"
)

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Pydantic models for request/response
class UrlRequest(BaseModel):
    url: HttpUrl

class TextRequest(BaseModel):
    text: str
    max_length: Optional[int] = 500

class SearchRequest(BaseModel):
    query: str
    count: Optional[int] = 10

class WebDataResponse(BaseModel):
    url: str
    title: str
    content: str
    status: str

class SummaryResponse(BaseModel):
    original_length: int
    summary: str
    summary_length: int

class SearchResponse(BaseModel):
    query: str
    results: list
    total_results: int
    status: str

class TermsAndConditionsRequest(BaseModel):
    query: str  # Can be company name, product name, or specific search query
    company_name: Optional[str] = None  # Optional company name for more specific searches
    product_name: Optional[str] = None  # Optional product name
    output_file: Optional[str] = None

class TermsAndConditionsResponse(BaseModel):
    query: str
    terms_url: str
    content: str
    file_path: str
    status: str

class TermsAnalysisRequest(BaseModel):
    text: str
    url: Optional[str] = None
    title: Optional[str] = None

class ComplianceIndicators(BaseModel):
    gdpr: str
    ccpa: str
    plainLanguage: str

class TermsAnalysisResponse(BaseModel):
    isTermsPage: bool
    confidence: float
    documentType: str
    summary: str
    keyFindings: list
    riskLevel: str
    riskFactors: list
    consumerProtections: list
    recommendations: list
    complianceIndicators: ComplianceIndicators
    lastUpdated: str
    redFlags: list
    analysisMethod: str = "llm_powered"




@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Finance NYC API is running!"}


@app.post("/scrape", response_model=WebDataResponse)
async def scrape_website(request: UrlRequest):
    """
    Scrape data from a given URL - download whatever content exists
    """
    try:
        print(f"🌐 Attempting to scrape: {request.url}")
        
        # Set up headers to appear more like a regular browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Make request to the URL with longer timeout and better headers
        print(f"📡 Making HTTP request to: {request.url}")
        response = requests.get(str(request.url), headers=headers, timeout=30, allow_redirects=True)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"🔗 Final URL after redirects: {response.url}")
        print(f"📄 Content length: {len(response.content)} bytes")
        print(f"📋 Content type: {response.headers.get('content-type', 'unknown')}")
        print(f"🔤 Response encoding: {response.encoding}")
        
        # Show first 200 bytes of raw content for debugging
        print(f"🔍 Raw content preview: {response.content[:200]}")
        
        # Even if we get a non-200 status, try to extract content if possible
        if response.status_code not in [200, 301, 302]:
            print(f"⚠️ Non-200 status code: {response.status_code}")
            # Don't raise an error, just note it
        
        # Ensure proper encoding
        if response.encoding is None:
            response.encoding = 'utf-8'
            print(f"🔤 Set default encoding to utf-8")
        
        # Check if content is actually HTML
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type and 'application/xhtml' not in content_type:
            print(f"⚠️ Non-HTML content type: {content_type}")
        
        # Parse HTML content with proper encoding
        print(f"🔧 Parsing HTML content...")
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding=response.encoding)
        print(f"📋 Parsed HTML, found {len(soup.find_all())} elements")
        
        # Extract title - try multiple approaches
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find('h1'):
            title = soup.find('h1').get_text().strip()
        else:
            title = "No title found"
        
        print(f"📝 Page title: {title}")
        
        # Extract text content - be less aggressive with removal
        # Only remove clearly problematic elements
        for element in soup(["script", "style", "noscript", "nav", "header", "footer"]):
            element.decompose()
        
        # Try multiple strategies to find the main content
        content_selectors = [
            'main',
            'article', 
            '.content',
            '.main-content',
            '#content',
            '#main',
            '.post-content',
            '.entry-content',
            '.terms',
            '.legal',
            '.policy'
        ]
        
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                print(f"📋 Found content using selector: {selector}")
                break
        
        if main_content:
            content = main_content.get_text(separator=' ', strip=True)
            print(f"📋 Extracted main content: {len(content)} characters")
            print(f"🔍 Main content preview: {content[:200]}...")
        else:
            print(f"⚠️ No main content found, trying body...")
            # Fallback to body content
            body = soup.find('body')
            if body:
                content = body.get_text(separator=' ', strip=True)
                print(f"📋 Using body content: {len(content)} characters")
                print(f"🔍 Body content preview: {content[:200]}...")
            else:
                print(f"⚠️ No body found, using full page...")
                # Last resort - full page
                content = soup.get_text(separator=' ', strip=True)
                print(f"📋 Using full page content: {len(content)} characters")
                print(f"🔍 Full page preview: {content[:200]}...")
        
        # Clean up the content
        import re
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        # Check for JavaScript redirects or very short content
        if len(content) < 100:
            print(f"⚠️ Content is very short ({len(content)} chars), checking for redirects...")
            
            # Look for meta refresh or JavaScript redirects
            meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
            if meta_refresh and meta_refresh.get('content'):
                redirect_content = meta_refresh.get('content')
                print(f"🔄 Found meta refresh: {redirect_content}")
                
                # Extract URL from content like "0; URL=https://example.com"
                import re
                url_match = re.search(r'URL=([^"\'>\s]+)', redirect_content, re.IGNORECASE)
                if url_match:
                    redirect_url = url_match.group(1)
                    print(f"🔄 Attempting to follow redirect to: {redirect_url}")
                    
                    # Try to fetch the redirect URL
                    try:
                        redirect_response = requests.get(redirect_url, headers=headers, timeout=30, allow_redirects=True)
                        if redirect_response.status_code == 200:
                            redirect_soup = BeautifulSoup(redirect_response.content, 'html.parser')
                            
                            # Remove problematic elements
                            for element in redirect_soup(["script", "style", "noscript", "nav", "header", "footer"]):
                                element.decompose()
                            
                            redirect_content = redirect_soup.get_text(separator=' ', strip=True)
                            redirect_content = re.sub(r'\s+', ' ', redirect_content).strip()
                            
                            if len(redirect_content) > len(content):
                                print(f"✅ Redirect content is better ({len(redirect_content)} chars)")
                                content = redirect_content
                                title = redirect_soup.title.string.strip() if redirect_soup.title and redirect_soup.title.string else title
                            else:
                                print(f"⚠️ Redirect content not better ({len(redirect_content)} chars)")
                    except Exception as e:
                        print(f"❌ Failed to follow redirect: {e}")
        
        # Check if content looks like binary or encoded data
        if len(content) > 0:
            # Check for high ratio of non-printable or non-ASCII characters
            printable_chars = sum(1 for c in content[:1000] if c.isprintable())
            if len(content) > 100 and printable_chars / min(len(content), 1000) < 0.7:
                print(f"⚠️ Content appears to be binary or encoded data")
                content = "Content appears to be binary or encoded data and cannot be analyzed."
            
            print(f"🔍 Final content preview (first 200 chars): {content[:200]}...")
        else:
            print(f"⚠️ No text content extracted from page")
        
        # Clean up whitespace but preserve structure
        content = ' '.join(content.split())
        
        # Don't truncate content - return full content
        print(f"✅ Successfully scraped {len(content)} characters")
        
        return WebDataResponse(
            url=str(request.url),
            title=title,
            content=content,  # Return full content, no truncation
            status="success"
        )
        
    except requests.Timeout:
        print(f"⏰ Request timed out")
        return WebDataResponse(
            url=str(request.url),
            title="Timeout Error",
            content="Request timed out while trying to fetch the webpage",
            status="timeout"
        )
    except requests.RequestException as e:
        print(f"🌐 Request error: {str(e)}")
        return WebDataResponse(
            url=str(request.url),
            title="Request Error",
            content=f"Failed to fetch URL: {str(e)}",
            status="failed"
        )
    except Exception as e:
        print(f"⚠️ Unexpected error: {str(e)}")
        return WebDataResponse(
            url=str(request.url),
            title="Parse Error", 
            content=f"Error parsing webpage: {str(e)}",
            status="failed"
        )


@app.post("/summarize", response_model=SummaryResponse)
async def summarize_text(request: TextRequest):
    """
    Summarize text using Anthropic Claude
    """
    try:
        # Check if API key is configured
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="Anthropic API key not configured. Please set ANTHROPIC_API_KEY in your .env file."
            )
        
        # Create prompt for summarization
        prompt = f"""Please provide a concise summary of the following text. 
        The summary should be approximately {request.max_length} characters or less.
        
        Text to summarize:
        {request.text}
        
        Summary:"""
        
        # Call Anthropic API
        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        summary = message.content[0].text.strip()
        
        return SummaryResponse(
            original_length=len(request.text),
            summary=summary,
            summary_length=len(summary)
        )
        
    except anthropic.AuthenticationError:
        raise HTTPException(
            status_code=401, 
            detail="Invalid Anthropic API key. Please check your credentials."
        )
    except anthropic.RateLimitError:
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Please try again later."
        )
    except Exception as e:
                 raise HTTPException(
             status_code=500, 
             detail=f"Error generating summary: {str(e)}"
         )


@app.post("/analyze-terms", response_model=TermsAnalysisResponse)
async def analyze_terms_with_llm(request: TermsAnalysisRequest):
    """
    Analyze text content to determine if it contains terms and conditions using LLM
    """
    try:
        # Check if API key is configured
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="Anthropic API key not configured. Please set ANTHROPIC_API_KEY in your .env file."
            )
        
        # Create sophisticated prompt focused on T&C gotchas and consumer traps
        prompt = f"""You are a consumer protection advocate and legal analyst specializing in identifying hidden traps, gotchas, and unfair terms in legal documents. Your mission is to protect users from being taken advantage of by companies through deceptive or one-sided terms.

🚨 PRIMARY FOCUS: IDENTIFY GOTCHAS & TRAPS
Your main goal is to find terms that could surprise, harm, or disadvantage the average user:

1. HIDDEN GOTCHAS & TRAPS
   - Automatic renewals with difficult cancellation
   - Hidden fees or charges buried in text
   - Broad data collection beyond what users expect
   - Terms that allow unilateral changes without notice
   - Clauses that waive important user rights
   - Forced arbitration preventing class action lawsuits
   - Broad content licensing that users don't realize they're granting
   - Account termination triggers that are vague or unfair

2. DECEPTIVE PRACTICES
   - Important terms buried in dense legal text
   - Misleading headings that don't match content
   - Terms that contradict marketing promises
   - Vague language that favors the company
   - "Free" services with hidden costs or commitments
   - Data usage beyond the stated purpose

3. UNFAIR POWER IMBALANCES
   - Company can change terms anytime, user cannot
   - Company has broad termination rights, user has none
   - All liability on user, company disclaims everything
   - User must resolve disputes in company's preferred jurisdiction
   - Company owns user-generated content permanently
   - No compensation for service outages or data loss

4. CONSUMER VULNERABILITY EXPLOITATION
   - Terms that take advantage of user's lack of legal knowledge
   - Clauses that are unreasonable for typical consumer use
   - Rights that users think they have but actually don't
   - Penalties or consequences disproportionate to violations
   - Terms that lock users into long commitments they can't escape

5. REGULATORY EVASION
   - Terms that try to circumvent consumer protection laws
   - Jurisdiction shopping to avoid user-friendly regulations
   - Waiving rights that may not be legally waivable
   - Data practices that push boundaries of privacy laws

ANALYSIS CONTEXT:
URL: {request.url or 'Not provided'}
Page Title: {request.title or 'Not provided'}
Content Length: {len(request.text)} characters

CONTENT TO ANALYZE:
{request.text[:12000]}{'...[content truncated for analysis]' if len(request.text) > 12000 else ''}

🎯 ANALYSIS OUTPUT REQUIREMENTS:
Focus your analysis on helping users avoid being taken advantage of. Prioritize identifying gotchas, traps, and unfair terms that could harm users.

Provide your analysis as a JSON response with this exact structure:
{{
    "isTermsPage": boolean,
    "confidence": number (0-100),
    "documentType": "string (e.g., 'Terms of Service', 'Privacy Policy', 'User Agreement', 'Not Legal Document')",
    "summary": "string (2-3 sentences focusing on the biggest gotchas and risks for users)",
    "keyFindings": [
        "string (specific gotchas or traps found - be very specific)",
        "string (hidden costs, fees, or commitments)",
        "string (rights users lose or don't realize they're giving up)"
    ],
    "riskLevel": "string (low/medium/high - err on side of caution for users)",
    "riskFactors": [
        "string (specific gotchas that could surprise users)",
        "string (unfair terms that disadvantage consumers)",
        "string (ways the company could exploit these terms)"
    ],
    "consumerProtections": [
        "string (rare positive protections for users, if any exist)"
    ],
    "recommendations": [
        "string (specific actions users should take to protect themselves)",
        "string (what to watch out for or be careful about)",
        "string (alternatives or workarounds if possible)"
    ],
    "complianceIndicators": {{
        "gdpr": "string (compliant/partial/non-compliant/unclear)",
        "ccpa": "string (compliant/partial/non-compliant/unclear)",
        "plainLanguage": "string (good/fair/poor - is it deliberately confusing?)"
    }},
    "lastUpdated": "string (date if found, or 'not specified')",
    "redFlags": [
        "string (🚨 BIGGEST GOTCHAS - terms that could really hurt users)",
        "string (hidden traps users won't notice until it's too late)",
        "string (unfair terms that are particularly egregious)"
    ]
}}

🚨 CRITICAL INSTRUCTIONS:
- PRIORITIZE USER PROTECTION over legal technicalities
- ASSUME users don't read fine print - what would surprise them?
- IDENTIFY terms that companies hope users won't notice or understand
- BE SPECIFIC - quote exact problematic language when possible
- WARN about automatic renewals, hidden fees, data collection, etc.
- HIGHLIGHT any terms that waive important rights
- CONSIDER what could go wrong for the user in the worst case scenario

Provide only the JSON response, no additional text:"""
        
        # Call Anthropic API
        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Updated to correct model name
            max_tokens=3000,  # Increased for comprehensive analysis
            temperature=0.1,  # Lower temperature for more consistent analysis
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        response_text = message.content[0].text.strip()
        
        # Try to extract JSON from the response
        try:
            # Look for JSON content between curly braces
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                analysis_result = json.loads(json_str)
            else:
                # Fallback parsing if no clear JSON structure
                raise ValueError("No JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Raw response: {response_text}")
            
            # No fallbacks - raise an error for LLM-only approach
            raise HTTPException(
                status_code=500,
                detail=f"LLM response parsing failed. Raw response was not in expected JSON format. Error: {str(e)}"
            )
        
        return TermsAnalysisResponse(
            isTermsPage=analysis_result.get("isTermsPage", False),
            confidence=float(analysis_result.get("confidence", 0)),
            documentType=analysis_result.get("documentType", "Unknown"),
            summary=analysis_result.get("summary", "Analysis completed"),
            keyFindings=analysis_result.get("keyFindings", []),
            riskLevel=analysis_result.get("riskLevel", "unknown"),
            riskFactors=analysis_result.get("riskFactors", []),
            consumerProtections=analysis_result.get("consumerProtections", []),
            recommendations=analysis_result.get("recommendations", []),
            complianceIndicators=ComplianceIndicators(
                gdpr=analysis_result.get("complianceIndicators", {}).get("gdpr", "unclear"),
                ccpa=analysis_result.get("complianceIndicators", {}).get("ccpa", "unclear"),
                plainLanguage=analysis_result.get("complianceIndicators", {}).get("plainLanguage", "fair")
            ),
            lastUpdated=analysis_result.get("lastUpdated", "not specified"),
            redFlags=analysis_result.get("redFlags", []),
            analysisMethod="llm_powered"
        )
        
    except anthropic.AuthenticationError:
        raise HTTPException(
            status_code=401, 
            detail="Invalid Anthropic API key. Please check your credentials."
        )
    except anthropic.RateLimitError:
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Please try again later."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error analyzing terms: {str(e)}"
        )


@app.post("/search", response_model=SearchResponse)
async def brave_search(request: SearchRequest):
    """
    Search using Brave Search API
    """
    try:
        # Check if API key is configured
        brave_api_key = os.getenv("BRAVE_API_KEY")
        if not brave_api_key:
            raise HTTPException(
                status_code=500, 
                detail="Brave API key not configured. Please set BRAVE_API_KEY in your .env file."
            )
        
        # Prepare search request
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": brave_api_key
        }
        
        params = {
            "q": request.query,
            "count": request.count
        }
        
        # Make request to Brave Search API
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers,
            params=params,
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Brave Search API error: {response.text}"
            )
        
        search_data = response.json()
        
        # Extract results
        results = []
        if "web" in search_data and "results" in search_data["web"]:
            for result in search_data["web"]["results"]:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", ""),
                    "published": result.get("published", "")
                })
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            status="success"
        )
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to search: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error performing search: {str(e)}"
        )


@app.post("/terms-and-conditions", response_model=TermsAndConditionsResponse)
async def get_terms_and_conditions(request: TermsAndConditionsRequest):
    """
    Get terms and conditions for any company or product using intelligent web search and browser automation
    """
    try:
        # Build intelligent search queries
        search_queries = []
        
        # Primary query - direct terms search
        primary_query = f"{request.query} terms and conditions"
        if request.company_name:
            primary_query = f"{request.company_name} {request.query} terms and conditions"
        if request.product_name:
            primary_query = f"{request.company_name or request.query} {request.product_name} terms and conditions"
        
        search_queries.append(primary_query)
        
        # Alternative queries
        alternative_queries = [
            f"{request.query} terms of service",
            f"{request.query} user agreement",
            f"{request.query} legal terms",
            f"{request.query} privacy policy terms",
            f"{request.company_name or request.query} legal documents",
            f"{request.company_name or request.query} terms of use"
        ]
        
        search_queries.extend(alternative_queries)
        
        # Search for terms and conditions pages using Brave Search
        brave_api_key = os.getenv("BRAVE_API_KEY")
        if not brave_api_key:
            raise HTTPException(
                status_code=500, 
                detail="Brave API key not configured. Please set BRAVE_API_KEY in your .env file."
            )
        
        all_search_results = []
        
        # Search with multiple queries to get better results
        for i, query in enumerate(search_queries[:3]):  # Limit to first 3 queries to avoid rate limits
            try:
                print(f"🔍 Search {i+1}: '{query}'")
                
                headers = {
                    "Accept": "application/json",
                    "X-Subscription-Token": brave_api_key
                }
                
                params = {
                    "q": query,
                    "count": 8
                }
                
                search_response = requests.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers=headers,
                    params=params,
                    timeout=10
                )
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    
                    if "web" in search_data and "results" in search_data["web"]:
                        for result in search_data["web"]["results"]:
                            # Avoid duplicates
                            if not any(r['url'] == result.get('url', '') for r in all_search_results):
                                all_search_results.append({
                                    'title': result.get('title', ''),
                                    'url': result.get('url', ''),
                                    'snippet': result.get('description', ''),
                                    'query': query
                                })
                
                # Small delay between searches
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Search {i+1} error: {e}")
                continue
        
        print(f"✅ Found {len(all_search_results)} unique search results")
        
        # Use Playwright to navigate and extract content
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            # Set user agent to avoid detection
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            # Show search results visually
            search_results_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Search Results - {request.query}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ background: #1a1a1a; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                    .result {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                    .title {{ color: #1a0dab; font-size: 18px; font-weight: bold; }}
                    .url {{ color: #006621; font-size: 14px; }}
                    .snippet {{ color: #545454; margin-top: 5px; }}
                    .query {{ color: #666; font-size: 12px; font-style: italic; }}
                    .highlight {{ background: yellow; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🔍 Terms & Conditions Search Results</h1>
                    <p><strong>Query:</strong> {request.query}</p>
                    <p><strong>Company:</strong> {request.company_name or 'N/A'}</p>
                    <p><strong>Product:</strong> {request.product_name or 'N/A'}</p>
                    <p><strong>Found:</strong> {len(all_search_results)} results</p>
                </div>
            """
            
            for i, result in enumerate(all_search_results, 1):
                title = result['title']
                url = result['url']
                snippet = result['snippet']
                query = result['query']
                
                # Highlight terms-related keywords
                for keyword in ['terms', 'conditions', 'agreement', 'disclosure', 'legal', 'privacy']:
                    if keyword in title.lower():
                        title = title.replace(keyword, f'<span class="highlight">{keyword}</span>')
                        title = title.replace(keyword.title(), f'<span class="highlight">{keyword.title()}</span>')
                
                search_results_html += f"""
                <div class="result">
                    <div class="title">{title}</div>
                    <div class="url">{url}</div>
                    <div class="snippet">{snippet[:200]}...</div>
                    <div class="query">Found via: {query}</div>
                </div>
                """
            
            search_results_html += "</body></html>"
            
            await page.set_content(search_results_html)
            await page.wait_for_timeout(3000)
            
            content = ""
            final_url = ""
            
            # Intelligent content extraction
            print(f"\n🔍 Step 2: Analyzing search results and extracting content...")
            
            # Score and prioritize results
            scored_results = []
            for result in all_search_results:
                score = 0
                title_lower = result['title'].lower()
                url_lower = result['url'].lower()
                snippet_lower = result['snippet'].lower()
                
                # Score based on relevance indicators
                terms_keywords = ['terms', 'conditions', 'agreement', 'disclosure', 'legal', 'privacy']
                for keyword in terms_keywords:
                    if keyword in title_lower:
                        score += 10
                    if keyword in url_lower:
                        score += 5
                    if keyword in snippet_lower:
                        score += 3
                
                # Bonus for official domains
                if any(domain in url_lower for domain in ['.com', '.org', '.net', '.gov']):
                    score += 2
                
                # Penalty for social media or news sites
                if any(site in url_lower for site in ['facebook.com', 'twitter.com', 'linkedin.com', 'news.', 'blog.']):
                    score -= 5
                
                scored_results.append((score, result))
            
            # Sort by score (highest first)
            scored_results.sort(key=lambda x: x[0], reverse=True)
            
            print(f"📊 Top 5 scored results:")
            for i, (score, result) in enumerate(scored_results[:5], 1):
                print(f"  {i}. Score {score}: {result['title']}")
            
            # Try to extract content from top results
            for score, result in scored_results[:8]:  # Try top 8 results
                if score < 5:  # Skip very low scoring results
                    continue
                    
                try:
                    url = result['url']
                    title = result['title']
                    
                    print(f"\n🌐 Trying: {title}")
                    print(f"🔗 URL: {url}")
                    print(f"📊 Score: {score}")
                    
                    # Navigate to the page
                    try:
                        await page.goto(url, wait_until='networkidle', timeout=15000)
                        await page.wait_for_timeout(2000)
                        print(f"✅ Page loaded successfully")
                    except Exception as e:
                        print(f"⚠️  Page load timeout: {e}")
                        continue
                    
                    # Extract page content
                    page_content = await page.inner_text('body')
                    
                    # Validate if this is actually terms and conditions
                    if len(page_content) > 1000:
                        # Check for terms-related content
                        terms_indicators = [
                            'terms and conditions', 'terms of service', 'terms of use',
                            'user agreement', 'legal agreement', 'privacy policy',
                            'disclosure', 'legal terms', 'conditions of use',
                            'acceptance of terms', 'by using this', 'you agree to',
                            'liability', 'disclaimer', 'governing law'
                        ]
                        
                        content_lower = page_content.lower()
                        indicator_count = sum(1 for indicator in terms_indicators if indicator in content_lower)
                        
                        print(f"📊 Content length: {len(page_content)} characters")
                        print(f"🎯 Terms indicators found: {indicator_count}")
                        
                        if indicator_count >= 3:  # At least 3 indicators suggest this is terms
                            print(f"🎉 SUCCESS! Found valid terms and conditions!")
                            content = page_content
                            final_url = url
                            break
                        else:
                            print(f"❌ REJECTED - Not enough terms indicators")
                    else:
                        print(f"❌ REJECTED - Content too short ({len(page_content)} characters)")
                    
                except Exception as e:
                    print(f"❌ ERROR processing {url}: {e}")
                    continue
            
            # If no content found, try direct company URL patterns
            if not content:
                print(f"\n🔄 FALLBACK: Trying direct company URL patterns...")
                content, final_url = await try_direct_company_urls(request, p)
                if content:
                    print(f"✅ FALLBACK SUCCESS! Found content via direct URL")
                else:
                    print(f"❌ FALLBACK FAILED - No content found via direct URLs")
            
            # Show final summary
            if content:
                summary_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>✅ Extraction Complete - {request.query}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        .header {{ background: #28a745; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                        .content {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>✅ Terms & Conditions Found!</h1>
                        <p><strong>Query:</strong> {request.query}</p>
                        <p><strong>Company:</strong> {request.company_name or 'N/A'}</p>
                        <p><strong>Product:</strong> {request.product_name or 'N/A'}</p>
                        <p><strong>Source:</strong> {final_url}</p>
                        <p><strong>Content Length:</strong> {len(content)} characters</p>
                    </div>
                    <div class="content">
                        <h3>Extracted Content Preview:</h3>
                        <p>{content[:500]}...</p>
                    </div>
                </body>
                </html>
                """
            else:
                summary_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>❌ No Results - {request.query}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        .header {{ background: #dc3545; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>❌ No Terms & Conditions Found</h1>
                        <p><strong>Query:</strong> {request.query}</p>
                        <p><strong>Company:</strong> {request.company_name or 'N/A'}</p>
                        <p><strong>Product:</strong> {request.product_name or 'N/A'}</p>
                        <p>No terms and conditions were found after trying {len(all_search_results)} search results.</p>
                    </div>
                </body>
                </html>
                """
            
            try:
                await page.set_content(summary_html)
                await page.wait_for_timeout(3000)
            except:
                print("Note: Could not display summary page")
            
            await browser.close()
            
            # Generate filename if not provided
            if not request.output_file:
                safe_query = "".join(c for c in request.query if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"terms_and_conditions_{safe_query.replace(' ', '_').lower()}.txt"
            else:
                filename = request.output_file
            
            # Ensure the filename has .txt extension
            if not filename.endswith('.txt'):
                filename += '.txt'
            
            # Create output directory if it doesn't exist
            output_dir = "terms_and_conditions"
            os.makedirs(output_dir, exist_ok=True)
            
            file_path = os.path.join(output_dir, filename)
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Terms and Conditions\n")
                f.write(f"Query: {request.query}\n")
                if request.company_name:
                    f.write(f"Company: {request.company_name}\n")
                if request.product_name:
                    f.write(f"Product: {request.product_name}\n")
                f.write(f"Source URL: {final_url}\n")
                f.write(f"Retrieved: {asyncio.get_event_loop().time()}\n")
                f.write("=" * 80 + "\n\n")
                f.write(content if content else "No terms and conditions found.")
            
            return TermsAndConditionsResponse(
                query=request.query,
                terms_url=final_url,
                content=content[:1000] + "..." if len(content) > 1000 else content,
                file_path=file_path,
                status="success" if content else "no_content_found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error getting terms and conditions: {str(e)}"
        )


async def try_direct_company_urls(request: TermsAndConditionsRequest, p):
    """
    Try to find terms and conditions using common company URL patterns
    """
    # Common URL patterns for different types of companies
    company_url_patterns = {
        # Tech companies
        'google': [
            f'https://policies.google.com/terms',
            f'https://www.google.com/terms',
            f'https://cloud.google.com/terms'
        ],
        'facebook': [
            f'https://www.facebook.com/terms',
            f'https://www.facebook.com/legal/terms'
        ],
        'amazon': [
            f'https://www.amazon.com/gp/help/customer/display.html?nodeId=508088',
            f'https://www.amazon.com/conditionsofuse'
        ],
        'apple': [
            f'https://www.apple.com/legal/internet-services/itunes/dev/stdeula/',
            f'https://www.apple.com/legal/sales-support/'
        ],
        'microsoft': [
            f'https://www.microsoft.com/en-us/legal/intellectualproperty/copyright',
            f'https://www.microsoft.com/en-us/legal/terms-of-use'
        ],
        'netflix': [
            f'https://help.netflix.com/legal/termsofuse',
            f'https://www.netflix.com/legal/terms'
        ],
        'spotify': [
            f'https://www.spotify.com/legal/end-user-agreement/',
            f'https://www.spotify.com/legal/terms-of-use/'
        ],
        # Financial companies
        'chase': [
            f'https://www.chase.com/personal/credit-cards/{request.query.lower().replace(" ", "-")}/terms',
            f'https://www.chase.com/terms'
        ],
        'american express': [
            f'https://www.americanexpress.com/us/credit-cards/card/{request.query.lower().replace(" ", "-")}/terms/',
            f'https://www.americanexpress.com/legal/terms.html'
        ],
        'capital one': [
            f'https://www.capitalone.com/credit-cards/{request.query.lower().replace(" ", "-")}/terms/',
            f'https://www.capitalone.com/legal/'
        ],
        # Generic patterns for any company
        'generic': [
            f'https://www.{request.query.lower().replace(" ", "")}.com/terms',
            f'https://www.{request.query.lower().replace(" ", "")}.com/legal/terms',
            f'https://www.{request.query.lower().replace(" ", "")}.com/terms-of-service',
            f'https://www.{request.query.lower().replace(" ", "")}.com/legal',
            f'https://{request.query.lower().replace(" ", "")}.com/terms',
            f'https://{request.query.lower().replace(" ", "")}.com/legal'
        ]
    }
    
    company_name_lower = request.company_name.lower() if request.company_name else ""
    query_lower = request.query.lower()
    
    # Try specific company patterns first
    for company, urls in company_url_patterns.items():
        if company != 'generic' and (company in company_name_lower or company in query_lower):
            print(f"🏢 Trying {company} URL patterns...")
            for i, url in enumerate(urls, 1):
                try:
                    print(f"  📋 [{i}/{len(urls)}] Trying: {url}")
                    browser = await p.chromium.launch(headless=False)
                    page = await browser.new_page()
                    
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    await page.wait_for_timeout(2000)
                    
                    content = await page.inner_text('body')
                    
                    # Validate content is actually terms
                    if len(content) > 1000:
                        terms_indicators = [
                            'terms and conditions', 'terms of service', 'terms of use',
                            'user agreement', 'legal agreement', 'privacy policy'
                        ]
                        content_lower = content.lower()
                        indicator_count = sum(1 for indicator in terms_indicators if indicator in content_lower)
                        
                        if indicator_count >= 2:
                            print(f"  ✅ SUCCESS - Found terms content ({len(content)} characters)")
                            await browser.close()
                            return content, url
                        else:
                            print(f"  ❌ REJECTED - Not terms content")
                    else:
                        print(f"  ❌ REJECTED - Content too short ({len(content)} characters)")
                    
                    await browser.close()
                    
                except Exception as e:
                    print(f"  ❌ ERROR - Failed to load: {e}")
                    continue
    
    # Try generic patterns if no specific company found
    print(f"🌐 Trying generic URL patterns...")
    generic_urls = company_url_patterns['generic']
    for i, url in enumerate(generic_urls, 1):
        try:
            print(f"  📋 [{i}/{len(generic_urls)}] Trying: {url}")
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(2000)
            
            content = await page.inner_text('body')
            
            if len(content) > 1000:
                terms_indicators = [
                    'terms and conditions', 'terms of service', 'terms of use',
                    'user agreement', 'legal agreement', 'privacy policy'
                ]
                content_lower = content.lower()
                indicator_count = sum(1 for indicator in terms_indicators if indicator in content_lower)
                
                if indicator_count >= 2:
                    print(f"  ✅ SUCCESS - Found terms content ({len(content)} characters)")
                    await browser.close()
                    return content, url
                else:
                    print(f"  ❌ REJECTED - Not terms content")
            else:
                print(f"  ❌ REJECTED - Content too short ({len(content)} characters)")
            
            await browser.close()
            
        except Exception as e:
            print(f"  ❌ ERROR - Failed to load: {e}")
            continue
    
    return "", ""





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
