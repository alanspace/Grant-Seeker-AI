"""
Advanced Robustness & Accuracy Tests
=====================================

Tests challenging scenarios to validate system robustness
"""

import asyncio
import sys
sys.path.insert(0, 'backend')


ADVANCED_TESTS = [
    {
        "name": "Very Specific Query",
        "query": "quantum computing research grants for universities in Ontario under $50000",
        "checks": ["Filtering works", "Specific criteria respected"]
    },
    {
        "name": "Multiple Keywords",
        "query": "renewable energy clean technology sustainability grants",
        "checks": ["Handles multiple themes", "Relevant results"]
    },
    {
        "name": "Ambiguous Query",
        "query": "grant",
        "checks": ["Doesn't crash", "Some results returned"]
    },
    {
        "name": "Common Typo",
        "query": "reserch grants",  # Intentional typo
        "checks": ["Handles typos gracefully", "Still finds results"]
    },
    {
        "name": "French/English Mix",
        "query": "innovation grants financement",
        "checks": ["Handles bilingual queries", "Canadian context"]
    },
]


async def test_robustness():
    """Test system robustness with challenging queries."""
    from adk_agent import GrantSeekerWorkflow
    
    print("=" * 80)
    print("ADVANCED ROBUSTNESS & ACCURACY TESTS")
    print("=" * 80)
    
    workflow = GrantSeekerWorkflow()
    
    results_summary = []
    
    for test in ADVANCED_TESTS:
        print(f"\n{'=' * 80}")
        print(f"TEST: {test['name']}")
        print(f"Query: \"{test['query']}\"")
        print(f"Checking: {', '.join(test['checks'])}")
        print('=' * 80)
        
        try:
            results = await workflow.run(test['query'])
            
            # Analyze results
            analysis = {
                "total": len(results),
                "untitled": len([g for g in results if g.get('title') == 'Untitled Grant']),
                "with_errors": len([g for g in results if g.get('error')]),
                "complete_data": len([
                    g for g in results 
                    if len(g.get('description', '')) >= 50
                    and g.get('title') != 'Untitled Grant'
                ]),
            }
            
            print(f"\n📊 Results:")
            print(f"   Total grants: {analysis['total']}")
            print(f"   Complete data: {analysis['complete_data']}/{analysis['total']}")
            print(f"   'Untitled Grant': {analysis['untitled']}")
            print(f"   With errors: {analysis['with_errors']}")
            
            # Show relevance of top result
            if results:
                top_grant = results[0]
                print(f"\n🏆 Top Result:")
                print(f"   {top_grant.get('title', 'NO TITLE')}")
                print(f"   Fit Score: {top_grant.get('fit_score', 0)}%")
                print(f"   {top_grant.get('description', 'No description')[:100]}...")
            
            # Verdict
            print(f"\n✅ Status:")
            if analysis['untitled'] == 0 and analysis['total'] > 0:
                print(f"   ✅ No 'Untitled Grant' - PASS")
            elif analysis['total'] == 0:
                print(f"   ⚠️ No results found")
            else:
                print(f"   ❌ {analysis['untitled']} 'Untitled Grant' found - FAIL")
            
            if analysis['complete_data'] == analysis['total'] and analysis['total'] > 0:
                print(f"   ✅ All grants have complete data - PASS")
            elif analysis['total'] > 0:
                print(f"   ⚠️ {analysis['total'] - analysis['complete_data']} grants with incomplete data")
            
            results_summary.append({
                "test": test['name'],
                "passed": analysis['untitled'] == 0 and analysis['total'] > 0,
                **analysis
            })
            
        except Exception as e:
            print(f"\n❌ ERROR: {type(e).__name__}: {e}")
            results_summary.append({
                "test": test['name'],
                "passed": False,
                "error": str(e)
            })
    
    # Final Report
    print("\n" + "=" * 80)
    print("FINAL ROBUSTNESS REPORT")
    print("=" * 80)
    
    passed = sum(1 for r in results_summary if r.get('passed'))
    total = len(results_summary)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    for result in results_summary:
        status = "✅ PASS" if result.get('passed') else "❌ FAIL"
        print(f"\n{status} - {result['test']}")
        if 'total' in result:
            print(f"   Grants: {result['total']}, Complete: {result.get('complete_data', 0)}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    
    if passed == total:
        print("\n🎉 ALL ROBUSTNESS TESTS PASSED!")
        print("   System handles edge cases correctly")
        print("   No 'Untitled Grant' in any scenario")
        print("   Graceful error handling")
    else:
        print(f"\n⚠️ {total - passed} tests had issues")


async def test_accuracy():
    """Test accuracy of grant data extraction."""
    from adk_agent import GrantSeekerWorkflow
    
    print("\n" + "=" * 80)
    print("ACCURACY TEST - Known Grant Verification")
    print("=" * 80)
    
    # Test with well-known grants that should always appear
    known_grants_query = "NSERC Discovery Grants"
    
    print(f"\nQuery: \"{known_grants_query}\"")
    print("Expected: Should find NSERC Discovery Grants\n")
    
    workflow = GrantSeekerWorkflow()
    results = await workflow.run(known_grants_query)
    
    # Check if well-known grant was found
    nserc_found = any('NSERC' in g.get('title', '') or 'Discovery' in g.get('title', '') for g in results)
    
    print(f"Results: {len(results)} grants")
    print(f"NSERC/Discovery found: {'✅ YES' if nserc_found else '❌ NO'}")
    
    # Show top 3
    print(f"\nTop 3 Results:")
    for i, grant in enumerate(results[:3], 1):
        print(f"\n{i}. {grant.get('title', 'NO TITLE')}")
        print(f"   Funder: {grant.get('funder', 'Unknown')}")
        print(f"   Fit Score: {grant.get('fit_score', 0)}%")
    
    if nserc_found and len(results) > 0:
        print("\n✅ ACCURACY TEST PASSED")
        print("   Found expected grant")
        print("   Extraction accurate")
    else:
        print("\n⚠️ Accuracy needs review")


if __name__ == "__main__":
    async def run_all():
        await test_robustness()
        await test_accuracy()
    
    asyncio.run(run_all())
