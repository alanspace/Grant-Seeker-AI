"""
Test script for robust content extraction

Tests the new multi-strategy content extraction system with:
1. Regular HTML pages
2. PDF documents  
3. Complex/JavaScript sites
4. Grant viability filtering
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
from backend.tavily_client import TavilyClient
from backend.content_extractor import RobustContentExtractor, is_viable_grant

load_dotenv()

# Test URLs
TEST_URLS = {
    "regular_html": "https://www.nserc-crsng.gc.ca/innovate-innover/partnership_alliances-partenariat_alliance_eng.asp",
    "pdf_example": "https://www.nserc-crsng.gc.ca/Professors-Professeurs/Grants-Subs/Alliance-Alliance_eng.asp",
    "complex_site": "https://www.sac-isc.gc.ca/eng/1375201178602/1610797286236",
}

# Test grant data
TEST_GRANTS = [
    {
        "title": "Innovation Grant",
        "deadline": "2026-06-30",
        "amount": "$50,000",
        "description": "This is a grant for innovative projects in technology and research.",
        "funder": "NSERC"
    },
    {
        "title": "Untitled Grant",
        "deadline": "Not specified",
        "amount": "Not specified", 
        "description": "No description available",
        "funder": "Unknown"
    },
    {
        "title": "Research Grant",
        "deadline": "2026-12-31",
        "amount": "$100,000",
        "description": "Short",  # Too short
        "funder": "CIHR"
    },
    {
        "title": "Good Grant",
        "deadline": "Not specified",  # Missing deadline
        "amount": "$75,000",
        "description": "This grant supports research in artificial intelligence and machine learning applications for healthcare innovation.",
        "funder": "CFI"
    },
]


async def test_content_extraction():
    """Test multi-strategy content extraction."""
    print("=" * 80)
    print("TESTING MULTI-STRATEGY CONTENT EXTRACTION")
    print("=" * 80)
    
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        print("❌ TAVILY_API_KEY not set - cannot test")
        return
    
    tavily = TavilyClient(api_key=tavily_api_key)
    extractor = RobustContentExtractor(tavily_client=tavily, timeout=30.0)
    
    for name, url in TEST_URLS.items():
        print(f"\n{'='*80}")
        print(f"Testing: {name}")
        print(f"URL: {url}")
        print(f"{'='*80}")
        
        try:
            content, method = await extractor.extract(url, min_length=200)
            
            if content:
                print(f"✅ SUCCESS")
                print(f"   Method: {method}")
                print(f"   Length: {len(content)} chars")
                print(f"   Preview: {content[:200]}...")
            else:
                print(f"❌ FAILED - No content extracted")
                
        except Exception as e:
            print(f"❌ ERROR: {type(e).__name__}: {e}")


def test_grant_viability():
    """Test grant viability filtering."""
    print("\n" + "=" * 80)
    print("TESTING GRANT VIABILITY FILTERING")
    print("=" * 80)
    
    for i, grant in enumerate(TEST_GRANTS, 1):
        viable = is_viable_grant(grant)
        status = "✅ VIABLE" if viable else "❌ FILTERED"
        
        print(f"\nGrant {i}: {grant['title']}")
        print(f"  Status: {status}")
        print(f"  Title: {grant['title']}")
        print(f"  Deadline: {grant['deadline']}")
        print(f"  Amount: {grant['amount']}")
        print(f"  Description length: {len(grant['description'])} chars")


async def main():
    """Run all tests."""
    # Test 1: Content Extraction
    await test_content_extraction()
    
    # Test 2: Grant Viability
    test_grant_viability()
    
    print("\n" + "=" * 80)
    print("TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
