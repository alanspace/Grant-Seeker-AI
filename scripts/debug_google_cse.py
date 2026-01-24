"""
Debug script for testing Google Custom Search API integration.

This is a development/debugging tool, not a unit test. It's used to manually
verify that the Google CSE client works correctly with sample queries.

Usage:
    python scripts/debug_google_cse.py
"""
import asyncio
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from google_search_client import GoogleSearchClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file in project root
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Validate that required environment variables are set
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY must be set in .env file")
if not CSE_ID:
    raise ValueError("GOOGLE_CSE_ID must be set in .env file")

async def debug_search():
    """Run debug queries against Google CSE."""
    logger.info(f"Testing Google CSE with ID: {CSE_ID[:10]}...")
    
    client = GoogleSearchClient(api_key=API_KEY, cse_id=CSE_ID)
    
    # Test Queries designed to hit specific parts of your Golden Dataset
    queries = [
        "women entrepreneur funding",   # Targeted at Row 12 / Row 62
        "agriculture grants",           # Targeted at Row 9 / Row 56
        "indigenous business loan",     # Targeted at Row 13 / Row 59
    ]
    
    for q in queries:
        logger.info(f"Query: '{q}'")
        results = await client.search(q, max_results=3)
        
        if not results:
            logger.warning("No results found. Check API Key or CSE Configuration")
        else:
            logger.info(f"Found {len(results)} results:")
            for i, res in enumerate(results):
                logger.info(f"  {i+1}. {res['title']}")
                logger.info(f"     URL: {res['url']}")
        logger.info("")  # Empty line for readability

if __name__ == "__main__":
    asyncio.run(debug_search())
