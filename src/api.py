#!/usr/bin/env python3
"""
FastAPI server for AI Finance NYC
"""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
import anthropic
from dotenv import load_dotenv

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


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Finance NYC API is running!"}


@app.post("/scrape", response_model=WebDataResponse)
async def scrape_website(request: UrlRequest):
    """
    Scrape data from a given URL
    """
    try:
        # Make request to the URL
        response = requests.get(str(request.url), timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else "No title found"
        
        # Extract text content (remove scripts, styles, etc.)
        for script in soup(["script", "style"]):
            script.decompose()
        
        content = soup.get_text()
        # Clean up whitespace
        content = ' '.join(content.split())
        
        return WebDataResponse(
            url=str(request.url),
            title=title,
            content=content[:1000] + "..." if len(content) > 1000 else content,
            status="success"
        )
        
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
