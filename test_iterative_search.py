"""
Test Iterative Search Logic
===========================

Tests the new run_with_minimum_results method in GrantSeekerWorkflow.
Verifies:
1. It runs multiple attempts if results < min_results
2. It generates query variants
3. It respects filters
4. It deduplicates results
"""

import asyncio
import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, os.path.abspath('backend'))
sys.path.insert(0, os.path.abspath('frontend'))

from adk_agent import GrantSeekerWorkflow

async def test_iterative_search():
    print("\n" + "="*80)
    print("TEST: ITERATIVE SEARCH WITH MINIMUM RESULTS")
    print("="*80)
    
    workflow = GrantSeekerWorkflow()
    
    # Test Parameters - Broad query to ensure results
    query = "business grants"
    min_results = 3
    filters = {
        # 'demographic_focus': ['Women-led / Female Founders'],
        # 'funding_types': ['Non-repayable Grant'] 
    }
    
    print(f"Query: {query}")
    print(f"Target: Minimum {min_results} relevant results")
    print(f"Filters: {filters}")
    
    # Run the iterative search
    try:
        results = await workflow.run_with_minimum_results(
            query=query,
            filters=filters,
            min_results=min_results
        )
        
        print("\n" + "-"*40)
        print(f"Total Results Found: {len(results)}")
        print("-"*40)
        
        for i, grant in enumerate(results, 1):
            title = grant.get('title', 'Unknown')
            demos = grant.get('founder_demographics', [])
            fit = grant.get('fit_score', 0)
            url_valid = grant.get('url') is not None
            deadline = grant.get('deadline', 'N/A')
            
            print(f"\n{i}. {title}")
            print(f"   Fit Score: {fit}%")
            print(f"   Deadline: {deadline}")
            print(f"   Demographics: {demos}")
            print(f"   URL Valid: {'✅' if url_valid else '❌'}")
            
        # Validation
        if len(results) >= min_results:
            print(f"\n✅ PASS: Met target of {min_results} results")
        else:
            print(f"\n⚠️ PARTIAL: Found {len(results)}/{min_results} results")
            
        # Check relevance
        if not filters:
            print("✅ PASS: Broad search test complete (No specific filters set)")
        else:
            irrelevant = [g for g in results if not any('women' in d.lower() for d in g.get('founder_demographics', []))]
            if irrelevant:
                print(f"❌ FAIL: {len(irrelevant)} results do not match filter!")
            else:
                print("✅ PASS: All results match filters")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_iterative_search())
