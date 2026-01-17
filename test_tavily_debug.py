import asyncio
import os
from dotenv import load_dotenv
from backend.tavily_client import TavilyClient

# Load env vars
load_dotenv()
load_dotenv("../.env")

# URL causing issues
TEST_URL = "https://www.sac-isc.gc.ca/eng/1375201178602/1610797286236"
API_KEY = os.getenv("TAVILY_API_KEY")

async def test_tavily_extraction():
    print(f"Testing Tavily Extraction for: {TEST_URL}\nUsing API Key: {API_KEY[:5]}...")
    
    client = TavilyClient(api_key=API_KEY)
    
    # Try extract
    print("Attempting extract...")
    content = await client.get_page_content(TEST_URL)
    
    print("\n--- RESULT ---")
    if content:
        print(f"Length: {len(content)} chars")
        print(f"Preview: {content[:500]}...")
    else:
        print("❌ FAILED: Content is empty or None.")

if __name__ == "__main__":
    asyncio.run(test_tavily_extraction())
