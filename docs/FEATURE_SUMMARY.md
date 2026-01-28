# New Feature: User-Controlled Search Thoroughness + Token Tracking

## What Was Added

### 1. Minimum Results Selector 🎯
- **Dropdown menu**: Choose 1-10 minimum results
- **Default**: 3 results
- **Behavior**: System keeps searching until it finds at least this many RELEVANT grants matching your filters
- **Location**: Below "Data Source" toggle

### 2. Token Usage Display 💰
- **Estimated Tokens**: Shows approximate token usage BEFORE search
- **Formula**: `min_results × 15,000 tokens`
- **Last Search Tokens**: Shows actual usage from previous search
- **Purpose**: Transparency about API costs

## How It Works

```
User selects: Minimum 5 results
Estimated cost: 75,000 tokens

System behavior:
1. Search attempt 1 → Finds 2 matching grants
2. Search attempt 2 (broader query) → Finds 3 more (5 total) ✅
3. Stop searching (minimum met)
4. Display actual token usage: ~68,000 tokens
```

## UI Layout

```
🎛️ Data Source
☑️ Use Real Data (apply filters to actual search results)
✅ Using REAL data from backend search

🎯 Search Thoroughness
┌─────────────────────────────────┬──────────────┐
│ Minimum results: [3] ▼          │ Est. Tokens  │
│                                  │   45,000     │
└─────────────────────────────────┴──────────────┘
💰 Last search used ~52,341 tokens
```

## Benefits

### For Users
- ✅ **Control**: Choose between fast (1-2 results) or thorough (8-10 results)
- ✅ **Transparency**: See API cost before searching
- ✅ **Flexibility**: Adjust based on needs and budget

### For Demos
- ✅ **Quick demos**: Select 1-2 results for fast demonstrations
- ✅ **Comprehensive**: Select 8-10 for thorough grant discovery
- ✅ **Cost-aware**: Users know what they're spending

## Example Scenarios

### Scenario 1: Quick Check (Budget-conscious)
```
Minimum results: 2
Est. tokens: 30,000
Use case: "Just want to see if grants exist in this area"
```

### Scenario 2: Standard Search (Recommended)
```
Minimum results: 3
Est. tokens: 45,000
Use case: "Normal grant discovery"
```

### Scenario 3: Comprehensive (Thorough)
```
Minimum results: 10
Est. tokens: 150,000
Use case: "Need complete picture of all available grants"
```

## Token Estimation

**Per Grant Estimate**: ~15,000 tokens
- Search query processing: ~5,000 tokens
- Content extraction: ~7,000 tokens  
- LLM processing: ~3,000 tokens

**Actual Usage May Vary**:
- Simpler grants: ~10,000 tokens
- Complex multi-grant pages: ~20,000 tokens
- PDF extractions: ~25,000 tokens

## Integration with Iterative Search

When implemented, the system will:
1. Read `min_results_target` from session state
2. Keep searching until that many RELEVANT grants found
3. Track actual token usage
4. Update `last_search_tokens` after completion
5. Display actual usage to user

## Testing

Try different minimum results:
```python
# Fast search (1 result)
min_results = 1
Expected: Quick, ~15K tokens

# Standard (3 results) 
min_results = 3
Expected: Moderate, ~45K tokens

# Thorough (10 results)
min_results = 10
Expected: Comprehensive, ~150K tokens
```

## Future Enhancements

- **Real-time token counter**: Show tokens as search progresses
- **Budget limit**: Set maximum token budget, stop when reached
- **Historical tracking**: Show token usage over time
- **Cost in dollars**: Convert tokens to actual API costs

