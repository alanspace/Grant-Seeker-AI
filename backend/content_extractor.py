"""
Robust Content Extraction Module

Provides multiple strategies for extracting content from URLs:
1. Tavily API (best quality, but sometimes fails)
2. Google scraper (fallback if configured)
3. Direct HTML scraping with BeautifulSoup
4. PDF text extraction

This module solves the "Untitled Grant" problem caused by failed content extraction.
"""

import httpx
import logging
from io import BytesIO
from typing import Optional, Tuple
from bs4 import BeautifulSoup
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class RobustContentExtractor:
    """Multi-strategy content extractor with fallback mechanisms."""
    
    def __init__(self, tavily_client=None, google_client=None, timeout: float = 30.0):
        """
        Initialize the extractor with optional clients.
        
        Args:
            tavily_client: TavilyClient instance (optional)
            google_client: GoogleSearchClient instance (optional)  
            timeout: HTTP timeout in seconds
        """
        self.tavily = tavily_client
        self.google = google_client
        self.timeout = timeout
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    async def extract(self, url: str, min_length: int = 200) -> Tuple[str, str]:
        """
        Extract content from URL using multiple fallback strategies.
        
        Args:
            url: The URL to extract content from
            min_length: Minimum acceptable content length
            
        Returns:
            Tuple of (content, extraction_method)
            - content: Extracted text content
            - extraction_method: Name of the method that succeeded
        """
        logger.debug(f"Starting content extraction for: {url}")
        
        # Strategy 1: Tavily (best quality when it works)
        if self.tavily:
            content, method = await self._try_tavily(url, min_length)
            if content:
                return content, method
        
        # Strategy 2: Google scraper (if available)
        if self.google:
            content, method = await self._try_google_scraper(url, min_length)
            if content:
                return content, method
        
        # Strategy 3: PDF extraction (if URL is a PDF)
        if self._is_pdf_url(url):
            content, method = await self._try_pdf_extraction(url, min_length)
            if content:
                return content, method
        
        # Strategy 4: Direct HTML scraping (last resort)
        content, method = await self._try_direct_scrape(url, min_length)
        if content:
            return content, method
        
        # All strategies failed
        logger.error(f"All extraction strategies failed for {url}")
        return "", "all_failed"
    
    async def _try_tavily(self, url: str, min_length: int) -> Tuple[str, str]:
        """Try Tavily API extraction."""
        try:
            logger.debug(f"Trying Tavily extraction for {url}")
            content = await self.tavily.get_page_content(url)
            
            if content and len(content) >= min_length:
                logger.info(f"✅ Tavily extraction successful ({len(content)} chars)")
                return content, "tavily"
            else:
                logger.debug(f"Tavily returned insufficient content ({len(content) if content else 0} chars)")
                return "", ""
                
        except Exception as e:
            logger.debug(f"Tavily extraction failed: {type(e).__name__}: {str(e)[:100]}")
            return "", ""
    
    async def _try_google_scraper(self, url: str, min_length: int) -> Tuple[str, str]:
        """Try Google scraper extraction."""
        try:
            logger.debug(f"Trying Google scraper for {url}")
            content = await self.google.get_page_content(url)
            
            if content and len(content) >= min_length:
                logger.info(f"✅ Google scraper successful ({len(content)} chars)")
                return content, "google_scraper"
            else:
                logger.debug(f"Google scraper returned insufficient content ({len(content) if content else 0} chars)")
                return "", ""
                
        except Exception as e:
            logger.debug(f"Google scraper failed: {type(e).__name__}: {str(e)[:100]}")
            return "", ""
    
    async def _try_pdf_extraction(self, url: str, min_length: int) -> Tuple[str, str]:
        """Extract text from PDF files."""
        try:
            logger.info(f"PDF detected, attempting extraction from {url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers={'User-Agent': self.user_agent})
                response.raise_for_status()
                
                # Read PDF from bytes
                pdf_file = BytesIO(response.content)
                pdf_reader = PdfReader(pdf_file)
                
                # Extract text from all pages
                text_parts = []
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num}: {e}")
                        continue
                
                content = "\n\n".join(text_parts).strip()
                
                if content and len(content) >= min_length:
                    logger.info(f"✅ PDF extraction successful ({len(content)} chars from {len(pdf_reader.pages)} pages)")
                    return content, "pdf_extraction"
                else:
                    logger.warning(f"PDF extraction returned insufficient content ({len(content)} chars)")
                    return "", ""
                    
        except Exception as e:
            logger.error(f"PDF extraction failed: {type(e).__name__}: {str(e)[:200]}")
            return "", ""
    
    async def _try_direct_scrape(self, url: str, min_length: int) -> Tuple[str, str]:
        """Direct HTML scraping with BeautifulSoup (last resort)."""
        try:
            logger.debug(f"Trying direct HTML scrape for {url}")
            
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                verify=True
            ) as client:
                response = await client.get(url, headers={'User-Agent': self.user_agent})
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove noise elements
                for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
                    tag.decompose()
                
                # Try to find main content area first
                main_content = soup.find('main') or soup.find('article') or soup.find(id='content') or soup.find(class_='content')
                
                if main_content:
                    text = main_content.get_text(separator='\n', strip=True)
                else:
                    text = soup.get_text(separator='\n', strip=True)
                
                # Clean up whitespace
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                content = '\n'.join(lines)
                
                if content and len(content) >= min_length:
                    logger.info(f"✅ Direct scrape successful ({len(content)} chars)")
                    return content, "direct_scrape"
                else:
                    logger.warning(f"Direct scrape returned insufficient content ({len(content)} chars)")
                    return "", ""
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"Direct scrape HTTP error: {e.response.status_code} for {url}")
            return "", ""
        except Exception as e:
            logger.error(f"Direct scrape failed: {type(e).__name__}: {str(e)[:200]}")
            return "", ""
    
    def _is_pdf_url(self, url: str) -> bool:
        """Check if URL points to a PDF file."""
        url_lower = url.lower()
        return url_lower.endswith('.pdf') or '/pdf/' in url_lower or '.pdf?' in url_lower


def is_viable_grant(grant: dict) -> bool:
    """
    Check if a grant has minimum viable information to show to users.
    
    Args:
        grant: Grant dictionary
        
    Returns:
        True if grant has sufficient data, False otherwise
    """
    # Check for error field
    if grant.get('error'):
        return False
    
    # Must have at least 2 of these 3 critical fields with real values
    has_title = grant.get('title') and grant['title'] not in ['Untitled Grant', '', 'N/A']
    has_deadline = grant.get('deadline') and grant['deadline'] not in ['Not specified', '', 'N/A', 'Unknown']
    has_amount = grant.get('amount') and grant['amount'] not in ['Not specified', '', 'N/A', 'Unknown']
    
    critical_fields_count = sum([has_title, has_deadline, has_amount])
    
    # Must have at least 2 out of 3 critical fields
    if critical_fields_count < 2:
        logger.debug(f"Grant rejected: Only {critical_fields_count}/3 critical fields present")
        return False
    
    # Must have some meaningful description
    description = grant.get('description', '')
    if not description or description in ['No description available', '', 'N/A']:
        logger.debug(f"Grant rejected: No meaningful description")
        return False
    
    # Description should be substantial (at least 50 characters)
    if len(description) < 50:
        logger.debug(f"Grant rejected: Description too short ({len(description)} chars)")
        return False
    
    return True
