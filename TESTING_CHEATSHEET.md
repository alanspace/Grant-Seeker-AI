# Testing Cheat Sheet - Quick Commands

## 🚀 Quick Tests (Copy & Paste)

### 1. Test Azzi's Original "AI" Issue ⭐
```bash
python -c "import asyncio, sys; sys.path.insert(0, 'backend'); from adk_agent import GrantSeekerWorkflow; asyncio.run((lambda: GrantSeekerWorkflow().run('AI'))()).then(lambda r: print(f'Results: {len(r)}, Untitled: {sum(1 for g in r if g.get(\"title\") == \"Untitled Grant\")}'))"
```
**OR simpler:**
```bash
python test_azzi_issues.py
```
**Expected:** 0 "Untitled Grant"

---

### 2. Test All Critical Scenarios
```bash
# Azzi's issues
python test_azzi_issues.py

# Robustness
python test_advanced.py

# Content extraction
python test_robust_extraction.py
```

---

### 3. Single Query Test Template
```bash
python -c "
import asyncio, sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    results = await GrantSeekerWorkflow().run('YOUR_QUERY_HERE')
    print(f'Found: {len(results)} grants')
    for g in results[:3]:  # Show top 3
        print(f'  - {g.get(\"title\", \"NO TITLE\")}')
    untitled = sum(1 for g in results if g.get(\"title\") == \"Untitled Grant\")
    print(f'\n{\"✅ PASS\" if untitled == 0 else \"❌ FAIL\"}: {untitled} Untitled Grant')

asyncio.run(test())
"
```

---

## 📋 Quick Checks

### Check for "Untitled Grant"
```bash
python -c "import asyncio, sys; sys.path.insert(0, 'backend'); from adk_agent import GrantSeekerWorkflow; asyncio.run(GrantSeekerWorkflow().run('AI').then(lambda r: print(f'Untitled: {sum(1 for g in r if g.get(\"title\") == \"Untitled Grant\")}')))" 
```

### Check All Grants Have Data
```bash
python -c "
import asyncio, sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    results = await GrantSeekerWorkflow().run('grants')
    empty = [g for g in results if len(g.get('description', '')) < 50]
    print(f'Total: {len(results)}, Empty: {len(empty)}')
    print('✅ ALL HAVE DATA' if len(empty) == 0 else f'❌ {len(empty)} EMPTY')

asyncio.run(test())
"
```

---

## 🎯 Azzi's Exact Test Queries

Copy these exactly as Azzi would have tested:

```bash
# Test 1: Short keyword
python -c "import asyncio, sys; sys.path.insert(0, 'backend'); from adk_agent import GrantSeekerWorkflow; asyncio.run(GrantSeekerWorkflow().run('AI').then(lambda r: [print(f'{i}. {g.get(\"title\")}') for i,g in enumerate(r,1)]))"

# Test 2: Demographic query
python -c "import asyncio, sys; sys.path.insert(0, 'backend'); from adk_agent import GrantSeekerWorkflow; asyncio.run(GrantSeekerWorkflow().run('women entrepreneur funding').then(lambda r: [print(f'{i}. {g.get(\"title\")}') for i,g in enumerate(r,1)]))"

# Test 3: Agriculture/PDF test
python -c "import asyncio, sys; sys.path.insert(0, 'backend'); from adk_agent import GrantSeekerWorkflow; asyncio.run(GrantSeekerWorkflow().run('agriculture grants').then(lambda r: [print(f'{i}. {g.get(\"title\")} - PDF:{\"pdf\" in g.get(\"url\",\"\")}') for i,g in enumerate(r,1)]))"
```

---

## ✅ Pass/Fail Criteria

**PASS if:**
- Zero "Untitled Grant"
- All descriptions 50+ chars  
- No crashes
- All grants have 2/3 fields

**FAIL if:**
- Any "Untitled Grant"
- Empty descriptions
- Parsing errors
- Crashes

---

## 🔥 Stress Test
```bash
# Run same query 3 times, check consistency
for i in {1..3}; do
  echo "Run $i:"
  python -c "import asyncio, sys; sys.path.insert(0, 'backend'); from adk_agent import GrantSeekerWorkflow; asyncio.run(GrantSeekerWorkflow().run('AI').then(lambda r: print(f'  Grants: {len(r)}, Untitled: {sum(1 for g in r if g.get(\"title\") == \"Untitled Grant\")}')))"
  sleep 1
done
```

**Expected:** 0 "Untitled Grant" in ALL runs


---

## 🔬 Filter Accuracy Tests

### Run Comprehensive Filter Tests
```bash
python test_filters.py
```
**Tests:**
- Demographic filter accuracy
- Search relevance  
- Data completeness
- No irrelevant results

**Expected:** All tests pass

---

### Quick Filter Test Commands

#### Test Women Filter
```bash
python -c "
import asyncio, sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    results = await GrantSeekerWorkflow().run('business funding')
    women_grants = [g for g in results if any('women' in d.lower() for d in g.get('founder_demographics', []))]
    print(f'Total: {len(results)}, Women-specific: {len(women_grants)}')
    
    for g in women_grants:
        print(f'  ✅ {g.get(\"title\")[:50]}')
    
asyncio.run(test())
"
```

#### Test Indigenous Filter
```bash
python -c "
import asyncio, sys
sys.path.insert(0, 'backend')
from adk_agent import GrantSeekerWorkflow

async def test():
    results = await GrantSeekerWorkflow().run('startup grants')
    indigenous_grants = [g for g in results if any('indigenous' in d.lower() for d in g.get('founder_demographics', []))]
    print(f'Total: {len(results)}, Indigenous-specific: {len(indigenous_grants)}')
    
    for g in indigenous_grants:
        print(f'  ✅ {g.get(\"title\")[:50]}')
    
asyncio.run(test())
"
```

