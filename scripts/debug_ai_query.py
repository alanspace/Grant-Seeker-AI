"""Debug: trace the exact pipeline for 'Artificial intelligence' to find where results are lost."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()

import asyncio, logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

from backend import adk_agent

async def main():
    w = adk_agent.GrantSeekerWorkflow()

    # Step 1: What query does the LLM generate?
    search_query = await w.generate_search_query("Artificial intelligence")
    print(f"\n=== GENERATED QUERY: '{search_query}' ===\n")

    # Step 2: What does the search provider return?
    search_results = await w.search_grants(search_query)
    print(f"=== SEARCH RESULTS: {len(search_results)} leads ===")
    for i, r in enumerate(search_results[:5]):
        print(f"  {i+1}. {r.get('title','??')[:60]} | {r.get('url','')[:60]}")

    # Step 3: Full run
    print("\n=== RUNNING FULL PIPELINE ===")
    results = await w.run("Artificial intelligence")
    print(f"\n=== FINAL: {len(results)} results ===")
    for r in results:
        print(f"  - {r.get('title','??')[:60]} | fit={r.get('fit_score',0)}%")

asyncio.run(main())
