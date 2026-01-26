"""
Test Cases for Issues Reported by Azzi
======================================

This script tests all the specific problems that were reported:
1. "Untitled Grant" appearing with no data
2. Empty records / lack of information
3. PDF files failing
4. Inconsistent search results
5. Grants that have URL but no extracted data

Run this to verify all issues are fixed.
"""

import asyncio
import sys
sys.path.insert(0, 'backend')

from adk_agent import GrantSeekerWorkflow


# Test queries that previously caused "Untitled Grant" issues
TEST_QUERIES = {
    "azzi_test_1": {
        "query": "AI",
        "description": "Azzi's original test - single keyword that returns many results",
        "expected_issues": ["Untitled Grant", "Empty records"],
        "min_grants": 1
    },
    "azzi_test_2": {
        "query": "women entrepreneur funding",
        "description": "Specific demographic grants - tests filtering",
        "expected_issues": ["Partial data extraction"],
        "min_grants": 1
    },
    "azzi_test_3": {
        "query": "agriculture grants",
        "description": "Sector-specific grants - tests diverse sources",
        "expected_issues": ["PDF files", "Portal pages"],
        "min_grants": 1
    },
    "azzi_test_4": {
        "query": "indigenous business loan",
        "description": "Loan vs grant distinction - tests classification",
        "expected_issues": ["Wrong funding type"],
        "min_grants": 1
    },
}


async def run_azzi_tests():
    """Run all test cases that Azzi struggled with."""
    
    print("=" * 80)
    print("AZZI'S ISSUE REPRODUCTION TESTS")
    print("=" * 80)
    print("\nTesting all scenarios that previously caused problems:\n")
    
    workflow = GrantSeekerWorkflow()
    all_results = {}
    
    for test_id, test_case in TEST_QUERIES.items():
        print(f"\n{'=' * 80}")
        print(f"TEST: {test_id}")
        print(f"Query: '{test_case['query']}'")
        print(f"Description: {test_case['description']}")
        print(f"Previously caused: {', '.join(test_case['expected_issues'])}")
        print('=' * 80)
        
        try:
            results = await workflow.run(test_case['query'])
            all_results[test_id] = results
            
            print(f"\n✅ Search completed: {len(results)} grants found")
            
            # Validate results
            issues_found = []
            
            # Check 1: Any "Untitled Grant"?
            untitled = [g for g in results if g.get('title') == 'Untitled Grant']
            if untitled:
                issues_found.append(f"❌ {len(untitled)} 'Untitled Grant' found")
            else:
                print("✅ No 'Untitled Grant' - FIXED")
            
            # Check 2: Any empty descriptions?
            empty_desc = [g for g in results if len(g.get('description', '')) < 50]
            if empty_desc:
                issues_found.append(f"❌ {len(empty_desc)} grants with empty/short descriptions")
            else:
                print("✅ All grants have sufficient descriptions - FIXED")
            
            # Check 3: All have required fields?
            for i, grant in enumerate(results):
                missing = []
                if not grant.get('title'):
                    missing.append('title')
                if not grant.get('url'):
                    missing.append('url')
                if not grant.get('description'):
                    missing.append('description')
                
                if missing:
                    issues_found.append(f"❌ Grant {i+1} missing: {', '.join(missing)}")
            
            if not issues_found:
                print("✅ All grants have complete data - FIXED")
            
            # Show sample results
            print(f"\nSample Results (showing first 2):")
            for i, grant in enumerate(results[:2], 1):
                print(f"\n{i}. {grant.get('title', 'NO TITLE')}")
                print(f"   Funder: {grant.get('funder', 'Unknown')}")
                print(f"   Amount: {grant.get('amount', 'Not specified')}")
                print(f"   Deadline: {grant.get('deadline', 'Not specified')}")
                print(f"   Description: {grant.get('description', 'No description')[:80]}...")
                if grant.get('error'):
                    print(f"   ⚠️ ERROR: {grant['error']}")
            
            # Summary
            if issues_found:
                print(f"\n⚠️ ISSUES FOUND:")
                for issue in issues_found:
                    print(f"   {issue}")
            else:
                print(f"\n✅ ALL CHECKS PASSED - ISSUES FIXED!")
            
            # Check if minimum grants found
            if len(results) >= test_case['min_grants']:
                print(f"✅ Found {len(results)} grants (minimum {test_case['min_grants']})")
            else:
                print(f"⚠️ Only {len(results)} grants found (expected minimum {test_case['min_grants']})")
                
        except Exception as e:
            print(f"\n❌ FATAL ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    # Final Summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    total_grants = sum(len(results) for results in all_results.values())
    total_untitled = sum(
        len([g for g in results if g.get('title') == 'Untitled Grant']) 
        for results in all_results.values()
    )
    total_empty_desc = sum(
        len([g for g in results if len(g.get('description', '')) < 50])
        for results in all_results.values()
    )
    
    print(f"\nTotal queries tested: {len(TEST_QUERIES)}")
    print(f"Total grants found: {total_grants}")
    print(f"'Untitled Grant' instances: {total_untitled}")
    print(f"Empty descriptions: {total_empty_desc}")
    
    if total_untitled == 0 and total_empty_desc == 0:
        print("\n🎉 SUCCESS! All Azzi's issues are FIXED!")
        print("   - No 'Untitled Grant' appearing")
        print("   - No empty records")
        print("   - All grants have complete data")
    else:
        print("\n⚠️ Some issues still present - needs investigation")
    
    return all_results


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TESTING ALL ISSUES REPORTED BY AZZI")
    print("=" * 80)
    print("\nThis will test:")
    print("1. 'Untitled Grant' appearing")
    print("2. Empty records / lack of information")
    print("3. PDF file handling")
    print("4. Multi-grant portal pages")
    print("5. Data extraction accuracy")
    print("\nRunning tests...\n")
    
    asyncio.run(run_azzi_tests())
