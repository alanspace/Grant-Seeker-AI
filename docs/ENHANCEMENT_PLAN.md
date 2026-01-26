# Enhancement Plan: Iterative Search + Advanced Features

## Overview
Major enhancements to improve grant discovery and accuracy based on user feedback.

## Priority 1: Iterative Search (Keep Finding Until Minimum)

### Problem
Current: Single search may return 0-2 results after filtering
Desired: Always return at least 3 **RELEVANT** grants that match BOTH:
  - The search query (e.g., "women entrepreneur funding")
  - The advanced filters (e.g., Women-led + Non-repayable Grant)

### Solution
```python
MIN_VIABLE_GRANTS = 3
MAX_SEARCH_ATTEMPTS = 5  # Increased to ensure we find enough

async def run_with_minimum_results(self, query: str, filters: dict, min_results=3):
    """
    Keep searching until minimum RELEVANT results found.
    
    A result is "relevant" if:
    1. Matches the search query (high fit_score)
    2. Passes all advanced filters
    3. Has complete data (is_viable_grant)
    4. Is not expired or USA-based
    
    Strategy:
    1. Try initial search with exact query
    2. Count results after ALL filters applied
    3. If < min_results:
       a. Broaden query (e.g., "women entrepreneur" → "women business funding")
       b. Try related keywords
       c. Search adjacent categories
    4. Combine all results
    5. Deduplicate by URL
    6. Apply ALL filters again
    7. Rank by comprehensive score
    8. Return top results
    """
    
    all_results = []
    attempted_queries = set()
    attempt = 1
    
    while len(all_results) < min_results and attempt <= MAX_SEARCH_ATTEMPTS:
        # Generate query variant
        search_query = self._generate_search_variant(query, filters, attempt)
        
        # Skip if already tried
        if search_query in attempted_queries:
            attempt += 1
            continue
        
        attempted_queries.add(search_query)
        logger.info(f"Search attempt {attempt}: {search_query}")
        
        # Run full workflow
        results = await self.run(search_query)
        
        # Apply advanced filters if provided
        if filters:
            from frontend.search_grants import apply_filters_to_results
            results = apply_filters_to_results(results, filters)
        
        # Add to collection
        all_results.extend(results)
        
        # Remove duplicates (same URL)
        all_results = self._deduplicate_results(all_results)
        
        logger.info(f"After attempt {attempt}: {len(all_results)} relevant results")
        attempt += 1
    
    # Final ranking by comprehensive score
    ranked_results = self._rank_results(all_results, query)
    
    logger.info(f"Final: {len(ranked_results)} relevant grants (target: {min_results})")
    return ranked_results


def _generate_search_variant(self, query: str, filters: dict, attempt: int) -> str:
    """
    Generate search query variants to find more relevant results.
    
    Attempt 1: Original query
    Attempt 2: Broaden (remove specific words)
    Attempt 3: Add filter keywords (e.g., + "women" if women filter active)
    Attempt 4: Related terms (entrepreneur → business owner)
    Attempt 5: Category search (e.g., "startup funding Canada")
    """
    
    if attempt == 1:
        return query
    
    elif attempt == 2:
        # Broaden: Remove restrictive words
        broader = query.replace(" startup", "").replace(" entrepreneur", " business")
        return broader
    
    elif attempt == 3:
        # Add filter context
        filter_keywords = []
        if filters.get('demographic_focus'):
            filter_keywords.extend(filters['demographic_focus'])
        if filters.get('funding_types'):
            filter_keywords.append('grant' if 'grant' in str(filters['funding_types']).lower() else 'funding')
        
        return f"{query} {' '.join(filter_keywords[:2])}"
    
    elif attempt == 4:
        # Related terms
        synonyms = {
            'entrepreneur': 'business owner',
            'startup': 'small business',
            'funding': 'grants',
            'loan': 'financing'
        }
        variant = query
        for word, synonym in synonyms.items():
            if word in query.lower():
                variant = variant.replace(word, synonym)
                break
        return variant
    
    else:
        # Generic category
        return "business grants Canada"


def _deduplicate_results(self, results: list) -> list:
    """
    Remove duplicate grants based on URL.
    Keep the one with higher fit_score.
    """
    seen_urls = {}
    
    for grant in results:
        url = grant.get('url', '')
        if not url:
            continue
        
        if url in seen_urls:
            # Keep higher fit score
            if grant.get('fit_score', 0) > seen_urls[url].get('fit_score', 0):
                seen_urls[url] = grant
        else:
            seen_urls[url] = grant
    
    return list(seen_urls.values())
```

### Files to Modify
- `backend/adk_agent.py`: Add iterative search logic
- `frontend/search_grants.py`: Call new method

---

## Priority 2: Multi-Select Filters

### Problem
Current: Can only select ONE demographic (Women OR Indigenous)
Desired: Select MULTIPLE (Women AND Indigenous AND Youth)

### Solution - Frontend Changes
```python
# OLD (single select)
st.selectbox("Select demographic", options)

# NEW (multi-select)
st.multiselect("Select demographics", options)
```

### Files to Modify
- `frontend/search_grants.py` lines 514-518: Change to multiselect
- `frontend/search_grants.py` lines 537-544: Change funding_types to multiselect  
- `frontend/search_grants.py` filter logic: Update to handle lists

---

## Priority 3: Deadline Verification

### Problem
Grants with "Ongoing" deadline may be closed
Example: "Grand Challenges Canada" shows "Ongoing" but website says closed

### Solution
```python
def verify_deadline(grant):
    """
    Verify if deadline is valid.
    
    Rules:
    - "Ongoing" without specific date → Flag as uncertain
    - Past dates → Mark as expired
    - Future dates → Valid
    - "Rolling" with active program → Valid
    """
    deadline = grant.get('deadline', '').lower()
    
    # Flag vague deadlines
    if 'ongoing' in deadline and 'specific' not in deadline:
        grant['deadline_verified'] = False
        grant['deadline_note'] = 'Check website for current availability'
    
    # Verify date-specific deadlines
    elif any(month in deadline for month in MONTHS):
        grant['deadline_verified'] = True
    
    return grant
```

### Files to Modify
- `backend/adk_agent.py`: Add deadline verification
- `frontend/search_grants.py`: Display verification status

---

## Priority 4: URL Validation (404 Check)

### Problem
Grants may have dead links or moved pages

### Solution
```python
import httpx

async def validate_grant_url(url: str) -> dict:
    """
    Check if URL is accessible.
    
    Returns:
        {
            'accessible': bool,
            'status_code': int,
            'verified_at': datetime,
            'issue': str (if any)
        }
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.head(url, follow_redirects=True)
            return {
                'accessible': response.status_code < 400,
                'status_code': response.status_code,
                'verified_at': datetime.now(),
                'issue': None if response.status_code < 400 else f'HTTP {response.status_code}'
            }
    except Exception as e:
        return {
            'accessible': False,
            'status_code': None,
            'verified_at': datetime.now(),
            'issue': str(e)
        }
```

### Implementation Notes
- Run validation AFTER extraction (don't slow down initial search)
- Cache validation results (24 hours)
- Show user: "✅ Verified" or "⚠️ Link may be outdated"

### Files to Modify
- `backend/adk_agent.py`: Add URL validation
- Cache validation results to avoid repeated checks

---

## Priority 5: Freshness Indicator

### Problem
Users don't know when grant data was last verified

### Solution
Add metadata to each grant:
```python
grant_metadata = {
    'extracted_at': datetime.now(),
    'last_verified': datetime.now(),
    'verification_status': 'verified' | 'unverified' | 'failed',
    'freshness_score': 1.0  # 1.0 = today, 0.5 = 12 hours old, etc.
}
```

Display in UI:
```
✅ Verified 2 hours ago
⚠️ Last checked 3 days ago - may be outdated
❌ Could not verify - please check website
```

### Files to Modify
- `backend/adk_agent.py`: Add metadata to grants
- `frontend/search_grants.py`: Display freshness indicator

---

## Priority 6: Improved Ranking

### Current Ranking
Only uses fit_score from LLM

### Enhanced Ranking
```python
def calculate_comprehensive_rank(grant, query):
    """
    Multi-factor ranking:
    1. Relevance (LLM fit_score): 40%
    2. Freshness (how recent): 20%
    3. Data completeness: 20%
    4. Deadline proximity: 10%
    5. URL accessibility: 10%
    """
    
    relevance_score = grant.get('fit_score', 0) / 100
    freshness_score = calculate_freshness(grant)
    completeness_score = calculate_completeness(grant)
    deadline_score = calculate_deadline_urgency(grant)
    url_score = 1.0 if grant.get('url_accessible') else 0.5
    
    final_score = (
        relevance_score * 0.4 +
        freshness_score * 0.2 +
        completeness_score * 0.2 +
        deadline_score * 0.1 +
        url_score * 0.1
    )
    
    return final_score * 100  # Convert to percentage
```

### Files to Modify
- `backend/adk_agent.py`: Add comprehensive ranking function

---

## Implementation Order

### Phase 1 (High Impact, Quick)
1. ✅ Multi-select filters (30 mins)
2. ✅ Deadline verification (20 mins)
3. ✅ Freshness indicator (15 mins)

### Phase 2 (Medium Impact)
4. ✅ Iterative search loop (45 mins)
5. ✅ Enhanced ranking (30 mins)

### Phase 3 (Nice to Have)
6. ✅ URL validation (30 mins)

**Total Estimated Time: 2-3 hours**

---

## Testing Plan

After each phase:
```bash
# Test multi-select
python -c "# Test with multiple demographics"

# Test iterative search
python -c "# Should return min 3 results"

# Test deadline verification
python test_filters.py

# Test URL validation
python -c "# Check 404 detection"

# Test ranking
python -c "# Verify fresh grants ranked higher"
```

---

## Files That Will Be Modified

1. **backend/adk_agent.py** (main changes)
   - Add iterative search
   - Add deadline verification
   - Add URL validation
   - Add enhanced ranking
   - Add freshness metadata

2. **backend/content_extractor.py**
   - Add URL accessibility check

3. **frontend/search_grants.py**
   - Change filters to multi-select
   - Display freshness indicators
   - Show verification status

4. **requirements.txt** (if needed)
   - May need additional libs (already have httpx)

---

## Next Steps

1. **Approve this plan**
2. **Implement Phase 1** (multi-select + verification)
3. **Test Phase 1**
4. **Implement Phase 2** (iterative search + ranking)
5. **Test comprehensive**
6. **Optional: Phase 3** (URL validation)

**Ready to proceed?** Let me know which phase to start with, or if you'd like all at once!
