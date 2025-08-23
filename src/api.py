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
        print(f"📡 Making HTTP request...")
        response = requests.get(str(request.url), headers=headers, timeout=30, allow_redirects=True)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📄 Content length: {len(response.content)} bytes")
        
        # Even if we get a non-200 status, try to extract content if possible
        if response.status_code not in [200, 301, 302]:
            print(f"⚠️ Non-200 status code: {response.status_code}")
            # Don't raise an error, just note it
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
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
        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        
        # Try to get main content first
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            content = main_content.get_text(separator=' ', strip=True)
            print(f"📋 Found main content: {len(content)} characters")
        else:
            # Fallback to full body
            content = soup.get_text(separator=' ', strip=True)
            print(f"📋 Using full page content: {len(content)} characters")
        
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
            model="claude-3-sonnet-20240229",
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
