# Manual Testing Guide for Azzi's Issues

## Quick Test Commands

Run these commands one by one to test each scenario:

### Test 1: Azzi's Original "AI" Search
```bash
python -c "
import asyncio
import sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    workflow = GrantSeekerWorkflow()
    results = await workflow.run('AI')
    
    print(f'\n{\"=\" * 60}')
    print(f'RESULTS FOR: AI')
    print(f'{\"=\" * 60}')
    print(f'Total grants: {len(results)}')
    
    # Check for issues
    untitled = [g for g in results if g.get('title') == 'Untitled Grant']
    print(f'\"Untitled Grant\" instances: {len(untitled)}')
    
    # Show all results
    for i, grant in enumerate(results, 1):
        print(f'\n{i}. {grant.get(\"title\", \"NO TITLE\")}')
        print(f'   Amount: {grant.get(\"amount\", \"Not specified\")}')
        print(f'   Deadline: {grant.get(\"deadline\", \"Not specified\")}')
        desc = grant.get('description', 'No description')
        print(f'   Description ({len(desc)} chars): {desc[:80]}...')
        
asyncio.run(test())
"
```

### Test 2: Women Entrepreneur Funding
```bash
python -c "
import asyncio
import sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    workflow = GrantSeekerWorkflow()
    results = await workflow.run('women entrepreneur funding')
    
    print(f'\nFound {len(results)} grants for: women entrepreneur funding')
    for grant in results:
        print(f'\n- {grant.get(\"title\", \"NO TITLE\")}')
        print(f'  Funder: {grant.get(\"funder\", \"Unknown\")}')
        print(f'  Demographics: {grant.get(\"founder_demographics\", [])}')
        
asyncio.run(test())
"
```

### Test 3: Agriculture Grants (PDF Test)
```bash
python -c "
import asyncio
import sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    workflow = GrantSeekerWorkflow()
    results = await workflow.run('agriculture grants')
    
    print(f'\nFound {len(results)} grants for: agriculture grants')
    
    # Check for PDF URLs
    for grant in results:
        url = grant.get('url', '')
        is_pdf = url.lower().endswith('.pdf')
        print(f'\n- {grant.get(\"title\", \"NO TITLE\")}')
        print(f'  URL: {url}')
        print(f'  PDF: {\"YES\" if is_pdf else \"NO\"}')
        print(f'  Has data: {\"YES\" if len(grant.get(\"description\", \"\")) > 50 else \"NO\"}')
        
asyncio.run(test())
"
```

### Test 4: Indigenous Business Loan
```bash
python -c "
import asyncio
import sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    workflow = GrantSeekerWorkflow()
    results = await workflow.run('indigenous business loan')
    
    print(f'\nFound {len(results)} grants for: indigenous business loan')
    
    for grant in results:
        print(f'\n- {grant.get(\"title\", \"NO TITLE\")}')
        print(f'  Funding Type: {grant.get(\"funding_nature\", \"Unknown\")}')
        print(f'  Demographics: {grant.get(\"founder_demographics\", [])}')
        
asyncio.run(test())
"
```

### Test 5: Run All Azzi's Tests (Comprehensive)
```bash
python test_azzi_issues.py
```

---

## What to Look For

### 🔍 Red Flags (Things That Should NOT Appear):
- ❌ "Untitled Grant" as a title
- ❌ "Unknown" as funder when grant exists
- ❌ "Not specified" for ALL fields (some missing is OK if 2/3 present)
- ❌ Description less than 50 characters
- ❌ Empty description: "No description available"
- ❌ Any grants with an "error" field

### ✅ Good Signs (Things That SHOULD Appear):
- ✅ Real grant titles
- ✅ Specific funder names
- ✅ At least 2 of 3: title, deadline, amount
- ✅ Description 50+ characters
- ✅ Valid URLs
- ✅ No parsing errors in console

---

## Comparison Test (Results Should Be Similar)

Run the same query twice to verify consistency:

```bash
# First run
python -c "
import asyncio
import sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    workflow = GrantSeekerWorkflow()
    results = await workflow.run('AI grants Canada')
    titles = [g.get('title') for g in results]
    print('RUN 1 - Grant Titles:')
    for t in titles:
        print(f'  - {t}')

asyncio.run(test())
"

# Wait a moment, then second run
sleep 2

python -c "
import asyncio
import sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    workflow = GrantSeekerWorkflow()
    results = await workflow.run('AI grants Canada')
    titles = [g.get('title') for g in results]
    print('RUN 2 - Grant Titles:')
    for t in titles:
        print(f'  - {t}')

asyncio.run(test())
"
```

**Note:** Results may differ slightly (Tavily API varies), but quality should be consistent (no "Untitled Grant" in either run).

---

## Specific Edge Cases to Test

### Test Empty Query
```bash
python -c "
import asyncio
import sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    workflow = GrantSeekerWorkflow()
    try:
        results = await workflow.run('')
        print(f'Empty query returned {len(results)} grants')
    except Exception as e:
        print(f'Empty query handled: {type(e).__name__}')

asyncio.run(test())
"
```

### Test Very Long Query
```bash
python -c "
import asyncio
import sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    long_query = 'artificial intelligence machine learning deep learning research grants funding opportunities for Canadian universities and research institutions focusing on natural language processing computer vision and robotics'
    workflow = GrantSeekerWorkflow()
    results = await workflow.run(long_query)
    print(f'Long query returned {len(results)} grants')
    print(f'No \"Untitled Grant\": {not any(g.get(\"title\") == \"Untitled Grant\" for g in results)}')

asyncio.run(test())
"
```

---

## Success Criteria

For each test, you should see:
1. ✅ At least 1 grant returned
2. ✅ No "Untitled Grant" titles
3. ✅ All grants have descriptions 50+ chars
4. ✅ At least 2/3 critical fields populated
5. ✅ No error messages in results
6. ✅ All URLs are valid

If ALL tests pass these criteria, then:
**🎉 ALL AZZI'S ISSUES ARE FIXED!**
