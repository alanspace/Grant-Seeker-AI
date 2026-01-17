# Testing Guide - Azzi's Issues & System Robustness

## Overview

This directory contains comprehensive tests to verify all issues reported by Azzi are fixed, plus additional robustness and accuracy tests.

---

## Quick Start

### 1. Run Azzi's Specific Issue Tests
```bash
python test_azzi_issues.py
```
**Tests:** All 4 scenarios Azzi reported (AI search, women entrepreneur, agriculture, indigenous)  
**Expected:** 0 "Untitled Grant", all grants have complete data

### 2. Run Advanced Robustness Tests
```bash
python test_advanced.py
```
**Tests:** Edge cases (typos, ambiguous queries, bilingual, etc.)  
**Expected:** Graceful handling, no crashes, no "Untitled Grant"

### 3. Run Content Extraction Tests
```bash
python test_robust_extraction.py
```
**Tests:** Multi-strategy extraction, PDF handling, viability filtering  
**Expected:** All strategies working, bad grants filtered

---

## What's Being Tested

### Issues Azzi Reported:

1. **"Untitled Grant" Appearing**
   - Query: `AI` (single keyword)
   - Problem: Grants with no title or data
   - Fix: Viability filtering + better extraction

2. **Empty Records / Lack of Information**
   - Query: `women entrepreneur funding`
   - Problem: Grants showing but missing all data
   - Fix: Multi-strategy extraction + minimum data requirements

3. **PDF Files Failing**
   - Query: `agriculture grants`
   - Problem: PDF URLs return no content
   - Fix: Added PDF text extraction (pypdf)

4. **Inconsistent Results**
   - Query: Same query, different results
   - Problem: Different grants each time
   - Note: This is expected (Tavily API varies), but quality now consistent

---

## Test Scripts

| Script | Purpose | What It Tests |
|--------|---------|---------------|
| `test_azzi_issues.py` | Reproduce Azzi's bugs | All reported issues |
| `test_advanced.py` | Robustness | Edge cases, accuracy |
| `test_robust_extraction.py` | Content extraction | All strategies, PDF, filtering |
| `MANUAL_TESTING_GUIDE.md` | Step-by-step manual tests | Individual commands |

---

## Expected Results

### ✅ What You SHOULD See:

After each test:
- **0 instances of "Untitled Grant"**
- **All grants have descriptions 50+ characters**
- **At least 2/3 critical fields (title, deadline, amount) populated**
- **Valid URLs for all grants**
- **No parsing errors in console**
- **No crashes or exceptions**

### Example Good Result:
```
1. Innovation Fund
   Funder: Canada Foundation for Innovation
   Amount: $10,000 - $5,000,000
   Deadline: 2026-04-30
   Description (187 chars): The Innovation Fund supports research infrastructure...
```

### ❌ What You Should NOT See:

```
1. Untitled Grant                    ← BAD
   Funder: Unknown                   ← BAD (if grant exists)
   Amount: Not specified             ← BAD (all fields)
   Deadline: Not specified              
   Description (24 chars): No description available  ← BAD (too short)
```

---

## Running Individual Tests

### Test "Untitled Grant" Issue
```bash
python -c "
import asyncio, sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    results = await GrantSeekerWorkflow().run('AI')
    untitled = [g for g in results if g.get('title') == 'Untitled Grant']
    print(f'Total: {len(results)}, Untitled: {len(untitled)}')
    print('✅ PASS' if len(untitled) == 0 else '❌ FAIL')

asyncio.run(test())
"
```

### Test PDF Handling
```bash
python -c "
import asyncio, sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    results = await GrantSeekerWorkflow().run('agriculture grants PDF')
    pdfs = [g for g in results if '.pdf' in g.get('url', '').lower()]
    print(f'Found {len(pdfs)} PDF grants')
    for g in pdfs:
        has_data = len(g.get('description', '')) > 50
        print(f'  - {g.get(\"title\")}: {\"✅ Has data\" if has_data else \"❌ No data\"}')

asyncio.run(test())
"
```

### Test Empty Records
```bash
python -c "
import asyncio, sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    results = await GrantSeekerWorkflow().run('research grants')
    for g in results:
        fields = sum([
            bool(g.get('title') and g['title'] != 'Untitled Grant'),
            bool(g.get('deadline') and g['deadline'] != 'Not specified'),
            bool(g.get('amount') and g['amount'] != 'Not specified')
        ])
        has_desc = len(g.get('description', '')) >= 50
        complete = fields >= 2 and has_desc
        print(f'{\"✅\" if complete else \"❌\"} {g.get(\"title\", \"NO TITLE\")[:50]} ({fields}/3 fields, desc:{len(g.get(\"description\",\"\"))} chars)')

asyncio.run(test())
"
```

---

## Success Criteria

To consider all issues fixed, ALL of these must be true:

- [ ] `test_azzi_issues.py` shows 0 "Untitled Grant"
- [ ] `test_azzi_issues.py` shows 0 empty descriptions
- [ ] `test_advanced.py` passes all robustness tests
- [ ] `test_robust_extraction.py` shows all extraction strategies work
- [ ] Manual tests confirm no regression
- [ ] No crashes or unhandled exceptions

---

## Troubleshooting

### If you see "Untitled Grant":
1. Check if URL is accessible
2. Check if content extraction logged strategies tried
3. Look for "All extraction strategies failed" in logs
4. This grant should have been filtered out

### If you see empty descriptions:
1. Check if description < 50 chars
2. These should be filtered by `is_viable_grant()`
3. Review viability filter logs

### If tests crash:
1. Check environment variables are set (.env file)
2. Check API keys are valid
3. Check network connectivity

---

## Next Steps After Testing

If all tests pass:
1. ✅ Branch is production-ready
2. ✅ Create Pull Request
3. ✅ Merge to main
4. ✅ Deploy

If any tests fail:
1. Note which test failed
2. Check logs for error details
3. Review the specific failure scenario
4. Report findings for investigation

---

**Happy Testing!** 🧪
