"""
Debug script for testing Tavily API content extraction.

This is a development/debugging tool, not a unit test. It's used to manually
verify that the Tavily client can extract content from problematic URLs.

Usage:
    python scripts/debug_tavily.py
"""
import asyncio
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from tavily_client import TavilyClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file in project root
load_dotenv()

# URL that was causing issues in previous testing
TEST_URL = "https://www.sac-isc.gc.ca/eng/1375201178602/1610797286236"
API_KEY = os.getenv("TAVILY_API_KEY")

# Validate that required environment variable is set
if not API_KEY:
    raise ValueError("TAVILY_API_KEY must be set in .env file")

async def debug_tavily_extraction():
    """Test Tavily content extraction with a known problematic URL."""
    logger.info(f"Testing Tavily Extraction for: {TEST_URL}")
    logger.info(f"Using API Key: {API_KEY[:5]}...")
    
    client = TavilyClient(api_key=API_KEY)
    
    logger.info("Attempting content extraction...")
    content = await client.get_page_content(TEST_URL)
    
    logger.info("=" * 60)
    if content:
        logger.info(f"✓ SUCCESS: Extracted {len(content)} characters")
        logger.info(f"Preview (first 500 chars):\n{content[:500]}...")
    else:
        logger.error("✗ FAILED: Content is empty or None")
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(debug_tavily_extraction())
