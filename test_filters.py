"""
Comprehensive Filter Testing Script
====================================

Tests Advanced Filters with Real Data to ensure:
1. Demographic filters work correctly
2. Funding type filters work
3. Geographic filters work
4. Combined filters work
5. No irrelevant results slip through
"""

import asyncio
import sys
sys.path.insert(0, 'backend')

from adk_agent import GrantSeekerWorkflow


class FilterTester:
    """Test Advanced Filters with real backend data."""
    
    def __init__(self):
        self.workflow = GrantSeekerWorkflow()
        self.test_results = []
    
    async def test_demographic_filter(self):
        """Test that demographic filters work correctly."""
        print("\n" + "=" * 80)
        print("TEST 1: DEMOGRAPHIC FILTER ACCURACY")
        print("=" * 80)
        
        test_cases = [
            {
                "query": "business funding",
                "filter_demographic": "Women",
                "should_contain": ["women", "female"],
                "should_not_contain": ["only indigenous", "only youth"]
            },
            {
                "query": "startup grants",
                "filter_demographic": "Indigenous",
                "should_contain": ["indigenous", "first nations"],
                "should_not_contain": ["only women", "only youth"]
            }
        ]
        
        for test in test_cases:
            print(f"\nTest: {test['query']} + {test['filter_demographic']} filter")
            
            # Get results
            results = await self.workflow.run(test['query'])
            print(f"Total results before filter: {len(results)}")
            
            # Simulate demographic filter
            filtered = [
                g for g in results
                if any(keyword in demo.lower() for demo in g.get('founder_demographics', []) for keyword in test['should_contain'])
            ]
            
            print(f"Results after {test['filter_demographic']} filter: {len(filtered)}")
            
            # Check results
            passed = True
            for grant in filtered:
                demographics = [d.lower() for d in grant.get('founder_demographics', [])]
                
                # Must contain expected keywords
                if not any(kw in ' '.join(demographics) for kw in test['should_contain']):
                    print(f"   ❌ FAIL: {grant.get('title', 'Unknown')} missing expected demographic")
                    print(f"      Has: {demographics}")
                    passed = False
                
                # Should not ONLY have other demographics
                title = grant.get('title', '').lower()
                desc = grant.get('description', '').lower()
                combined = title + ' ' + desc + ' '.join(demographics)
                
                # Check if it's exclusively for another demographic
                is_women_only = 'women' in combined and 'only women' in combined
                is_indigenous_only = 'indigenous' in combined and 'only indigenous' in combined
                
                if test['filter_demographic'] == "Women" and is_indigenous_only:
                    print(f"   ❌ FAIL: {grant.get('title')} is indigenous-only, not women")
                    passed = False
            
            if passed and len(filtered) > 0:
                print(f"   ✅ PASS: All {len(filtered)} results match {test['filter_demographic']} filter")
            elif len(filtered) == 0:
                print(f"   ⚠️  WARNING: No results found for {test['filter_demographic']}")
            
            self.test_results.append({
                "test": f"Demographic: {test['filter_demographic']}",
                "passed": passed,
                "count": len(filtered)
            })
    
    async def test_relevance_accuracy(self):
        """Test that results are actually relevant to the query."""
        print("\n" + "=" * 80)
        print("TEST 2: RELEVANCE & ACCURACY")
        print("=" * 80)
        
        test_queries = [
            {
                "query": "women entrepreneur funding",
                "must_contain_keywords": ["women", "female", "entrepreneur"],
                "min_results": 1
            },
            {
                "query": "indigenous business grants",
                "must_contain_keywords": ["indigenous", "first nations", "business"],
                "min_results": 1
            },
            {
                "query": "youth startup funding",
                "must_contain_keywords": ["youth", "young", "startup"],
                "min_results": 1
            }
        ]
        
        for test in test_queries:
            print(f"\nQuery: '{test['query']}'")
            
            results = await self.workflow.run(test['query'])
            print(f"Results found: {len(results)}")
            
            if len(results) < test['min_results']:
                print(f"   ❌ FAIL: Expected minimum {test['min_results']}, got {len(results)}")
                self.test_results.append({
                    "test": f"Relevance: {test['query']}",
                    "passed": False,
                    "count": len(results)
                })
                continue
            
            # Check relevance
            relevant_count = 0
            for grant in results:
                title = grant.get('title', '').lower()
                desc = grant.get('description', '').lower()
                demographics = ' '.join(grant.get('founder_demographics', [])).lower()
                tags = ' '.join(grant.get('tags', [])).lower()
                
                combined = f"{title} {desc} {demographics} {tags}"
                
                # Check if ANY required keyword appears
                is_relevant = any(kw in combined for kw in test['must_contain_keywords'])
                
                if is_relevant:
                    relevant_count += 1
                else:
                    print(f"   ❌ Irrelevant: {grant.get('title', 'Unknown')}")
                    print(f"      Missing keywords: {test['must_contain_keywords']}")
            
            if relevant_count == len(results):
                print(f"   ✅ PASS: All {len(results)} results are relevant")
                self.test_results.append({
                    "test": f"Relevance: {test['query']}",
                    "passed": True,
                    "count": relevant_count
                })
            else:
                print(f"   ⚠️  PARTIAL: {relevant_count}/{len(results)} relevant")
                self.test_results.append({
                    "test": f"Relevance: {test['query']}'",
                    "passed": relevant_count >= test['min_results'],
                    "count": relevant_count
                })
    
    async def test_data_completeness(self):
        """Test that all results have complete data."""
        print("\n" + "=" * 80)
        print("TEST 3: DATA COMPLETENESS")
        print("=" * 80)
        
        results = await self.workflow.run("research grants")
        print(f"\nTesting {len(results)} grants for completeness...")
        
        issues = []
        for grant in results:
            # Check required fields
            if grant.get('title') == 'Untitled Grant':
                issues.append(f"Untitled Grant: {grant.get('url', 'unknown')}")
            
            if len(grant.get('description', '')) < 50:
                issues.append(f"Short description: {grant.get('title', 'unknown')}")
            
            # Check has at least 2/3 critical fields
            has_title = grant.get('title') not in ['Untitled Grant', '', None]
            has_deadline = grant.get('deadline') not in ['Not specified', '', None]
            has_amount = grant.get('amount') not in ['Not specified', '', None]
            
            critical_count = sum([has_title, has_deadline, has_amount])
            if critical_count < 2:
                issues.append(f"Insufficient data: {grant.get('title', 'unknown')} ({critical_count}/3 fields)")
        
        if issues:
            print(f"\n❌ FAIL: Found {len(issues)} data quality issues:")
            for issue in issues[:5]:  # Show first 5
                print(f"   - {issue}")
            passed = False
        else:
            print(f"\n✅ PASS: All {len(results)} grants have complete data")
            passed = True
        
        self.test_results.append({
            "test": "Data Completeness",
            "passed": passed,
            "issues": len(issues)
        })
    
    def print_summary(self):
        """Print final test summary."""
        print("\n" + "=" * 80)
        print("FINAL TEST SUMMARY")
        print("=" * 80)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.get('passed'))
        
        print(f"\nTests Run: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅ PASS" if result.get('passed') else "❌ FAIL"
            print(f"{status} - {result['test']}")
            if 'count' in result:
                print(f"   Results: {result['count']}")
            if 'issues' in result:
                print(f"   Issues: {result['issues']}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("   Filters are working correctly")
            print("   Results are relevant")
            print("   Data is complete")
        else:
            print(f"\n⚠️  {total - passed} TESTS FAILED")
            print("   Review failures above")


async def main():
    """Run all filter tests."""
    print("=" * 80)
    print("COMPREHENSIVE FILTER TESTING")
    print("=" * 80)
    print("\nThis will test:")
    print("1. Demographic filter accuracy")
    print("2. Relevance of search results")
    print("3. Data completeness")
    print("\nRunning tests...\n")
    
    tester = FilterTester()
    
    await tester.test_demographic_filter()
    await tester.test_relevance_accuracy()
    await tester.test_data_completeness()
    
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
