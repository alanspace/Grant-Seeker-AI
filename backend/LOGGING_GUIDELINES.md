# Logging Guidelines

This document establishes consistent logging practices for the Grant Seeker AI application.

## Log Levels

### 📊 INFO - User-Visible Milestones & Results
Use `logger.info()` for significant workflow milestones and actionable results that users/ops teams care about.

**When to use:**
- Workflow phase transitions
- Actionable results and counts
- Cache hits/misses (performance-relevant)
- API provider switches and fallback activations
- Successful completions

**Examples:**
```python
logger.info("Phase 1: Discovery - Generating search query")
logger.info("Phase 2: Grant Filtering - Analyzing results")
logger.info("Phase 3: Extraction - Fetching grant details")

logger.info(f"Found {len(results)} search results")
logger.info(f"Identified {len(leads)} promising grants")
logger.info(f"Successfully extracted {len(grants)} valid grants")

logger.info("Cache hit: Using cached search results")
logger.info("Using Google CSE for discovery")
logger.info("Fallback: Google scraper successful after Tavily timeout")
```

### 🔍 DEBUG - Internal Workflow Steps
Use `logger.debug()` for detailed internal operations useful during development and troubleshooting.

**When to use:**
- Query strings and parameters
- Loop iterations
- Data transformations
- Session/request IDs
- Intermediate processing steps

**Examples:**
```python
logger.debug(f"Searching with query: {query}")
logger.debug(f"Extracting data from URL: {url}")
logger.debug(f"Running agent with session_id: {session_id}")
logger.debug(f"Processing lead {i+1}/{len(leads)}")
logger.debug(f"Normalized funding_nature: {value} -> {normalized}")
logger.debug(f"Parsed {len(items)} items from LLM response")
```

### ⚠️ WARNING - Recoverable Issues
Use `logger.warning()` for issues that don't prevent operation but indicate degraded functionality or data quality concerns.

**When to use:**
- Fallback mechanisms triggered
- Data quality issues
- Skipped/filtered items
- Cache corruption (recoverable)
- Missing optional data

**Examples:**
```python
logger.warning("Tavily content empty, trying Google scraper fallback")
logger.warning(f"Skipping invalid grant at index {i}: {error_details}")
logger.warning("Cache file corrupted, performing fresh search")
logger.warning(f"Grant {title} marked as expired: {deadline}")
logger.warning(f"USA grant filtered out: {geography}")
```

### ❌ ERROR - Failures Requiring Attention
Use `logger.error()` for failures that prevent normal operation and require investigation.

**When to use:**
- API failures (after retries exhausted)
- Critical parsing failures
- Unrecoverable errors
- Configuration issues

**Examples:**
```python
logger.error(f"Search failed after {max_retries} retries: {error}")
logger.error(f"Failed to extract content from {url}: {error_type}")
logger.error(f"LLM returned unparseable JSON: {response_text[:200]}")
logger.error(f"All retries exhausted for query: '{query}'")
```

## Best Practices

### DO:
✅ Use appropriate log levels consistently  
✅ Include context (URLs, query strings, counts, indices)  
✅ Truncate long values (JSON, error messages) to prevent log bloat  
✅ Use exception type names (`type(e).__name__`) for quick identification  
✅ Log results and counts, not every iteration  
✅ Include timing information for slow operations  

### DON'T:
❌ Log at INFO level for every internal step  
❌ Log sensitive data (API keys, full credentials)  
❌ Use generic error messages ("Something went wrong")  
❌ Log entire LLM responses (summary or truncate)  
❌ Mix multiple concerns in one log line  

## Examples of Good Logging

### Workflow Phases
```python
# Good: Clear milestone
logger.info("Phase 1: Discovery - Generating search query")

# Bad: Too verbose, internal detail
logger.info("Calling create_query_agent() with description parameter")
```

### Search Operations
```python
# Good: Shows result, not the action
logger.debug(f"Searching with query: {query}")  # Internal step
logger.info(f"Found {len(results)} search results")  # Result

# Bad: Logs the obvious action with no useful info
logger.info("Performing search...")
```

### Error Handling
```python
# Good: Context, error type, truncated details
logger.error(f"Failed to extract grant at index {i}/{total}: {type(e).__name__}")
logger.error(f"   Grant data: {json.dumps(data)[:200]}...")
logger.error(f"   Error: {str(e)[:200]}")

# Bad: No context or details
logger.error(f"Error: {e}")
```

### Cache Operations
```python
# Good: Performance-relevant event
logger.info(f"Cache hit for query: {query[:50]}...")  # Saved API call

# Bad: Too verbose for internal detail
logger.debug(f"Checking cache for key: {cache_key}")
logger.debug(f"Cache file path: {cache_path}")
```

## Configuration

Set log level in environment or code:
```python
# Development: See DEBUG and above
logger.setLevel(logging.DEBUG)

# Production: See INFO and above (default)
logger.setLevel(logging.INFO)

# Production (quiet): See WARNING and above only
logger.setLevel(logging.WARNING)
```

## Review Checklist

Before committing logging code, verify:
- [ ] Log level matches the guideline for the event type
- [ ] Sensitive data is not logged
- [ ] Long values are truncated
- [ ] Error messages include enough context for debugging
- [ ] Loop iterations log the result, not every item
- [ ] Workflow milestones use INFO level

---

**Last Updated:** 2026-01-17  
**Version:** 1.0
