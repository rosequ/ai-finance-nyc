
import os
import requests
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# Create a session for web scraping
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

def web_scrape(url: str, timeout: int = 30) -> dict:
    """
    Read text content from a URL
    
    Args:
        url: URL to fetch content from
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with content, status, and source_url
    """
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return {
                "content": "",
                "source_url": url,
                "status": "failed",
                "error": "Invalid URL format"
            }
        
        # Fetch the content
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Check if it's HTML content
        content_type = response.headers.get('content-type', '').lower()
        if 'html' in content_type or 'text/html' in content_type:
            content = _extract_text_from_html(response.text)
        else:
            # Assume it's plain text
            content = _clean_text(response.text)
        
        return {
            "content": content,
            "source_url": url,
            "status": "success",
            "content_type": "text"
        }
            
    except requests.exceptions.RequestException as e:
        return {
            "content": "",
            "source_url": url,
            "status": "failed",
            "error": f"Request error: {str(e)}"
        }
    except Exception as e:
        return {
            "content": "",
            "source_url": url,
            "status": "failed",
            "error": f"Processing error: {str(e)}"
        }

def _extract_text_from_html(html_content: str) -> str:
    """
    Extract clean text from HTML content
    
    Args:
        html_content: HTML content as string
        
    Returns:
        Clean text content
    """
    try:
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up the text
        return _clean_text(text)
        
    except Exception as e:
        raise ValueError(f"Error parsing HTML: {str(e)}")

def _clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text content
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def search_reddit(query: str, n: int = 5, api_key: str = os.getenv("BRAVE_API_KEY")):
    """
    Search Reddit threads using Brave Search API and return top N threads
    with their top 3 replies (by votes).
    """
    headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
    params = {"q": f"site:reddit.com {query}", "count": n, "source": "reddit"}
    
    # Brave Search API call
    resp = requests.get("https://api.search.brave.com/res/v1/web/search",
                        headers=headers, params=params)
    resp.raise_for_status()
    results = resp.json().get("web", {}).get("results", [])

    threads = []
    for r in results:
        url = r.get("url")
        title = r.get("title")
        
        # Reddit JSON endpoint for comments
        if url and "comments" in url:
            try:
                reddit_json = requests.get(url + ".json", headers={"User-agent": "brave-search-script"}).json()
                comments = reddit_json[1]["data"]["children"]
                top_replies = sorted(comments, key=lambda c: c["data"].get("ups", 0), reverse=True)[:3]
                replies = [c["data"].get("body") for c in top_replies]
            except Exception:
                replies = []
        else:
            replies = []
        
        threads.append({
            "title": title,
            "url": url,
            "top_replies": replies
        })

    return threads


def format_threads(threads):
    """
    Turn Reddit thread results into nicely formatted text.
    """
    lines = []
    for i, t in enumerate(threads, 1):
        lines.append(f"🔗 {i}. {t['title']}\n   {t['url']}")
        if t["top_replies"]:
            for j, reply in enumerate(t["top_replies"], 1):
                snippet = reply.replace("\n", " ")
                lines.append(f"     💬 Reply {j}: {snippet}")
        else:
            lines.append("     (No replies found)")
        lines.append("")  # spacing
    return "\n".join(lines)


if __name__ == "__main__":
    threads = search_reddit("Robinhood")
    print(format_threads(threads))