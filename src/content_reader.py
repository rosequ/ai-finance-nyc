#!/usr/bin/env python3
"""
Content Reader for extracting text from various sources
"""

import os
import requests
from typing import Optional
import PyPDF2
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re


class ContentReader:
    """Read content from various sources (PDF, URL, HTML)"""
    
    def __init__(self):
        """Initialize the content reader"""
        self.session = requests.Session()
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def read_pdf_file(self, pdf_path: str) -> str:
        """
        Read text content from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content from the PDF
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
                
                return self._clean_text(text_content)
        except Exception as e:
            raise ValueError(f"Error reading PDF file {pdf_path}: {str(e)}")
    
    def read_from_url(self, url: str, timeout: int = 30) -> str:
        """
        Read text content from a URL
        
        Args:
            url: URL to fetch content from
            timeout: Request timeout in seconds
            
        Returns:
            Extracted text content from the URL
        """
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError(f"Invalid URL: {url}")
            
            # Fetch the content
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Check if it's HTML content
            content_type = response.headers.get('content-type', '').lower()
            if 'html' in content_type or 'text/html' in content_type:
                return self._extract_text_from_html(response.text)
            else:
                # Assume it's plain text
                return self._clean_text(response.text)
                
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error fetching URL {url}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing URL {url}: {str(e)}")
    
    def read_from_html(self, html_content: str) -> str:
        """
        Extract text content from HTML
        
        Args:
            html_content: HTML content as string
            
        Returns:
            Extracted text content from HTML
        """
        try:
            return self._extract_text_from_html(html_content)
        except Exception as e:
            raise ValueError(f"Error processing HTML content: {str(e)}")
    
    def _extract_text_from_html(self, html_content: str) -> str:
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
            return self._clean_text(text)
            
        except Exception as e:
            raise ValueError(f"Error parsing HTML: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
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
    
    def read_content(self, source: str, source_type: Optional[str] = None) -> str:
        """
        Read content from various sources based on source type or auto-detection
        
        Args:
            source: Source (file path, URL, or HTML content)
            source_type: Type of source ('pdf', 'url', 'html', 'text', or None for auto-detection)
            
        Returns:
            Extracted text content
        """
        if source_type:
            source_type = source_type.lower()
        
        # Auto-detect source type if not specified
        if not source_type:
            if source.lower().endswith('.pdf'):
                source_type = 'pdf'
            elif source.startswith(('http://', 'https://')):
                source_type = 'url'
            else:
                # Assume it's HTML content if it contains HTML tags
                if '<html' in source.lower() or '<body' in source.lower():
                    source_type = 'html'
                else:
                    # Default to treating as plain text
                    return self._clean_text(source)
        
        # Read based on source type
        if source_type == 'pdf':
            return self.read_pdf_file(source)
        elif source_type == 'url':
            return self.read_from_url(source)
        elif source_type == 'html':
            return self.read_from_html(source)
        elif source_type == 'text':
            return self._clean_text(source)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")


def main():
    """Test various content reading capabilities"""
    print("Content Reader Test")
    print("=" * 40)
    
    reader = ContentReader()
    
    # Test 1: PDF reading
    print("\n1. Testing PDF reading...")
    try:
        pdf_path = "terms_and_conditions/AGREEMENT_CRKE_95.pdf"
        content = reader.read_content(pdf_path)
        print(f"✅ PDF read successfully! Length: {len(content)} characters")
        print(f"📄 First 200 chars: {content[:200]}...")
    except Exception as e:
        print(f"❌ PDF test failed: {e}")
    
    # Test 2: HTML reading
    print("\n2. Testing HTML reading...")
    try:
        html_content = """
        <html>
        <body>
        <h1>Test Credit Card</h1>
        <p>APR: 15% variable rate</p>
        <p>Annual Fee: $50</p>
        <script>alert('test');</script>
        </body>
        </html>
        """
        content = reader.read_content(html_content)
        print(f"✅ HTML read successfully! Length: {len(content)} characters")
        print(f"📄 First 200 chars: {content[:200]}...")
    except Exception as e:
        print(f"❌ HTML test failed: {e}")
    
    # Test 3: Auto-detection
    print("\n3. Testing auto-detection...")
    try:
        # Test URL auto-detection
        url = "https://www.wellsfargo.com/credit-cards/agreements/active-cash-agreement"
        print(f"Testing URL auto-detection: {url}")
        content = reader.read_content(url)
        print(f"✅ URL auto-detection successful! Length: {len(content)} characters")
        print(f"📄 First 200 chars: {content[:200]}...")
    except Exception as e:
        print(f"❌ URL auto-detection failed: {e}")
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    main()
