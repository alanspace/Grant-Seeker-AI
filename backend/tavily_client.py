"""Tavily API Client Wrapper"""
import httpx
from typing import List, Dict, Optional
import asyncio

class TavilyClient:
    """
    Wrapper for Tavily API with retry logic, error handling, and rate limiting.
    
    This client handles the communication with the Tavily Search API.
    It includes built-in resilience features:
    - **Retries**: Automatically retries failed requests.
    - **Exponential Backoff**: Waits longer between each retry to avoid overwhelming the server.
    - **Timeout Handling**: Prevents the app from hanging indefinitely if the API is slow.
    """
    
    def __init__(self, api_key: str, max_retries: int = 3, timeout: float = 30.0):
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout
        self.base_url = "https://api.tavily.com"
    
    async def search(
        self, 
        query: str, 
        max_results: int = 5,
        search_depth: str = "basic",
        include_answer: bool = False,
        include_raw_content: bool = False,
        days: Optional[int] = None  # Filter by recency (e.g., last 90 days)
    ) -> List[Dict]:
        """
        Search using Tavily API with retry logic.
        
        Args:
            query: The search query string.
            max_results: Maximum number of results to return.
            search_depth: "basic" or "advanced" (advanced is slower but deeper).
            include_answer: Whether to include an AI-generated answer.
            include_raw_content: Whether to include the full HTML content.
            days: Optional filter for recency (e.g., last 30 days).
            
        Returns:
            A list of search result dictionaries.
        """
        url = f"{self.base_url}/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content
        }
        
        # Add days filter if specified
        if days is not None:
            payload["days"] = days
        
        
        for attempt in range(self.max_retries):
            try:
                # Create client with more lenient settings
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(self.timeout, connect=10.0),
                    follow_redirects=True,
                    verify=True
                ) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    return data.get("results", [])
            except httpx.ConnectTimeout:
                print(f"⚠️ Connection timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    print("❌ Could not connect to Tavily API. Check your internet connection or firewall.")
                    return []
                await asyncio.sleep(2)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"⚠️ Rate limited. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                print(f"❌ HTTP error: {e}")
                if attempt == self.max_retries - 1:
                    return []
            except Exception as e:
                print(f"⚠️ Tavily search error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    return []
                await asyncio.sleep(1)
        
        return []
    
    async def extract(self, urls: List[str]) -> Dict[str, str]:
        """
        Extract content from URLs using Tavily extract endpoint.
        
        This method uses Tavily's ability to scrape and clean webpage content,
        converting cluttered HTML into clean text that LLMs can process easily.
        """
        url = f"{self.base_url}/extract"
        payload = {
            "api_key": self.api_key,
            "urls": urls
        }
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Return dict mapping URL -> content
                    result = {}
                    for item in data.get("results", []):
                        result[item.get("url", "")] = item.get("raw_content", "")
                    return result
            except Exception as e:
                print(f"⚠️ Extract error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    return {}
                await asyncio.sleep(1)
        
        return {}
    
    async def get_page_content(self, url: str) -> str:
        """Get content for a single URL"""
        result = await self.extract([url])
        return result.get(url, "")
