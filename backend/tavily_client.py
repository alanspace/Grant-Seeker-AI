"""Tavily API Client Wrapper"""
import httpx
from typing import List, Dict, Optional
import asyncio

class TavilyClient:
    """Wrapper for Tavily API with retry logic, error handling, and rate limiting"""
    
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
        include_raw_content: bool = False
    ) -> List[Dict]:
        """Search using Tavily API with retry logic"""
        url = f"{self.base_url}/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content
        }
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    return data.get("results", [])
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
        """Extract content from URLs using Tavily extract endpoint"""
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
