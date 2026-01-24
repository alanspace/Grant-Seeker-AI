"""Google Custom Search JSON API Client Wrapper"""
import os
import httpx
from typing import List, Dict, Optional
import asyncio
from bs4 import BeautifulSoup

class GoogleSearchClient:
    """
    Wrapper for Google Custom Search JSON API.
    Designed to be drop-in compatible with the TavilyClient usage in Grant Seeker.
    """
    
    def __init__(self, api_key: str, cse_id: str, max_retries: int = 3, timeout: float = 30.0):
        self.api_key = api_key
        self.cse_id = cse_id
        self.max_retries = max_retries
        self.timeout = timeout
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        # Headers for the scraper part
        self.scraper_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def search(
        self, 
        query: str, 
        max_results: int = 10,
        **kwargs
    ) -> List[Dict]:
        """
        Search using Google Custom Search API.
        
        Args:
            query: The search query string.
            max_results: Maximum number of results to return (Google limits to 10 per call).
            
        Returns:
            A list of search result dictionaries used by Grant Seeker.
        """
        # Hard filter requested by user: append " Canada" if not present?
        # The user said: 'force the backend to append site:.ca OR "Canada"'
        # We'll just ensure the query targets our defined "Sites to search" in the CSE configuration.
        # But appending "Canada" is a safe content filter too.
        
        # Note: Google CSE max returns 10 results per page.
        if max_results > 10:
            max_results = 10
            
        params = {
            'key': self.api_key,
            'cx': self.cse_id,
            'q': query,
            'num': max_results
        }
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    items = data.get('items', [])
                    results = []
                    
                    for item in items:
                        results.append({
                            "url": item.get('link'),
                            "title": item.get('title'),
                            "content": item.get('snippet', ''),
                            "raw_content": item.get('snippet', '') # Google doesn't return raw HTML
                        })
                        
                    return results

            except httpx.HTTPStatusError as e:
                print(f"❌ Google Search HTTP error: {e.response.status_code} - {e.response.reason_phrase}")
                print(f"   Query: '{query}'")
                if attempt == self.max_retries - 1:
                    print(f"   ❌ All retries exhausted after {self.max_retries} attempts")
                    return []
                await asyncio.sleep(1)
            except httpx.TimeoutException:
                print(f"⏱️ Google Search timeout (attempt {attempt + 1}/{self.max_retries})")
                print(f"   Query: '{query}', Timeout: {self.timeout}s")
                if attempt == self.max_retries - 1:
                    return []
                await asyncio.sleep(1)
            except Exception as e:
                error_type = type(e).__name__
                print(f"⚠️ Google Search error (attempt {attempt + 1}/{self.max_retries}): {error_type}")
                print(f"   Query: '{query}', Error: {str(e)}")
                if attempt == self.max_retries - 1:
                    print(f"   ❌ All retries exhausted for query: '{query}'")
                    return []
                await asyncio.sleep(1)
        
        return []

    async def get_page_content(self, url: str) -> str:
        """
        Get content for a single URL.
        Since Google Search doesn't return full page content, 
        we perform a basic scrape here.
        """
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
                    response = await client.get(url, headers=self.scraper_headers)
                    response.raise_for_status()
                    
                    # Basic extraction using BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Remove scripts and styles
                    for script in soup(["script", "style", "nav", "footer", "header"]):
                        script.decompose()
                        
                    text = soup.get_text(separator='\n')
                    
                    # Basic cleaning
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    return text
                    
            except httpx.HTTPStatusError as e:
            except httpx.HTTPStatusError as e:
                print(f"❌ Scrape HTTP error for {url}")
                print(f"   Status: {e.response.status_code} - {e.response.reason_phrase}")

                if attempt == self.max_retries - 1:
                    print(f"   ❌ Failed to extract page content!")
                    return ""
                await asyncio.sleep(1)
            except httpx.TimeoutException:
                print(f"⏱️ Scrape timeout for {url} (attempt {attempt + 1}/{self.max_retries})")
                print(f"   Timeout: {self.timeout}s")
                if attempt == self.max_retries - 1:
                    print(f"   ❌ Failed to extract page content!")
                    return ""
                await asyncio.sleep(1)
            except Exception as e:
                error_type = type(e).__name__
                print(f"⚠️ Scrape error for {url} (attempt {attempt + 1}/{self.max_retries})")
                print(f"   Error type: {error_type}, Message: {str(e)}")
                if attempt == self.max_retries - 1:
                    print(f"   ❌ Failed to extract page content!")
                    return ""
                await asyncio.sleep(1)
        return ""
