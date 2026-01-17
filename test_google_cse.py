import asyncio
import os
from dotenv import load_dotenv
from backend.google_search_client import GoogleSearchClient

# Load environment variables from .env file in project root
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Validate that required environment variables are set
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY must be set in .env file")
if not CSE_ID:
    raise ValueError("GOOGLE_CSE_ID must be set in .env file")

async def test_search():
    print(f"Testing Google CSE with ID: {CSE_ID}...\n")
    
    client = GoogleSearchClient(api_key=API_KEY, cse_id=CSE_ID)
    
    # Test Queries designed to hit specific parts of your Golden Dataset
    queries = [
        "women entrepreneur funding",   # Targeted at Row 12 / Row 62
        "agriculture grants",           # Targeted at Row 9 / Row 56
        "indigenous business loan",     # Targeted at Row 13 / Row 59
    ]
    
    for q in queries:
        print(f"--- Query: '{q}' ---")
        results = await client.search(q, max_results=3)
        
        if not results:
            print("No results found. (Check API Key or CSE Configuration)")
        
        for i, res in enumerate(results):
            print(f"{i+1}. {res['title']}")
            print(f"   URL: {res['url']}")
            # print(f"   Snippet: {res['content'][:100]}...")
        print("\n")

if __name__ == "__main__":
    asyncio.run(test_search())
