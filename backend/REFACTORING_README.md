"""README for Grant Seeker application."""

# Grant Seeker - Production Version with Caching

## Project Structure

```
backend/
├── adk_agent_v2.py            # Main production file with integrated caching
├── tavily_client.py           # Tavily API client wrapper
├── exceptions.py              # Custom exceptions
├── tests/                     # Unit tests
│   ├── conftest.py            # Pytest configuration
│   ├── test_cache.py          # Cache service tests
│   ├── test_models.py         # Pydantic model tests
│   ├── test_utils.py          # Utility function tests
│   └── requirements-test.txt  # Test dependencies
└── REFACTORING_README.md      # This file
```

## Key Features

### 1. **Integrated Caching System**

- File-based cache in `.cache/` directory
- 24-hour TTL (time-to-live) for cached data
- Caches both search results and grant extractions
- 80%+ faster on repeat queries (~7s vs ~30s)

### 2. **Optimized Performance**

- 5 search results (focused quality)
- 3 parallel extractions (controlled concurrency)
- Gemini Flash model (15 RPM vs Pro's 2 RPM)
- ~20-30 seconds for fresh queries
- ~5-7 seconds for cached queries

### 3. **Clean Logging**

- INFO level for application logs
- WARNING level for libraries (reduces noise)
- Structured log format with timestamps

### 4. **Type Safety**

- Full type hints on all functions
- Pydantic validation for data models
- Better IDE support and error detection

### 5. **Frontend-Compatible Output**

- 13-field JSON structure
- Saves to `grants_output.json`
- Direct integration with existing frontend

## Usage

### Running the application:

```bash
# Navigate to backend directory
cd D:\adk-grant-seeker-copilot\backend

# Activate virtual environment
..\.venv\Scripts\Activate.ps1

# Run the script
python adk_agent_v2.py
```

### Configuration

All settings can be modified at the top of `adk_agent_v2.py`:

```python
# Model configuration
MODEL_NAME = "gemini-flash-latest"
TAVILY_MAX_RESULTS = 5
MAX_CONCURRENT_EXTRACTIONS = 3
CONTENT_PREVIEW_LENGTH = 3000

# Cache settings
CACHE_ENABLED = True
CACHE_DIR = ".cache"
CACHE_TTL_HOURS = 24

# Retry configuration
RETRY_ATTEMPTS = 1
RETRY_EXP_BASE = 2
RETRY_INITIAL_DELAY = 1.0
```

Environment variables required:

- `GOOGLE_API_KEY` - For Gemini API access
- `TAVILY_API_KEY` - For Tavily search API

### Running tests:

```bash
# Navigate to backend directory
cd D:\adk-grant-seeker-copilot\backend

# Activate virtual environment
..\.venv\Scripts\Activate.ps1

# Install test dependencies (first time only)
pip install -r tests/requirements-test.txt

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_cache.py -v
```

**Test Coverage:**

- `test_cache.py` - CacheService functionality (set, get, expiration, clearing)
- `test_models.py` - Pydantic model validation (DiscoveredLead, GrantData)
- `test_utils.py` - Utility functions (normalize_value, clean_json_string, get_current_date)

## Cache Management

### Clear all cache:

```python
workflow = GrantSeekerWorkflow()
workflow.cache.clear()  # Removes all cached files
```

### Cache behavior:

- Search results cached by query + max_results
- Grant extractions cached by URL
- Automatic expiration after 24 hours
- Cache files stored in `.cache/` directory

## Output Format

Results are saved to `grants_output.json` with this structure:

```json
[
  {
    "id": 1,
    "title": "Grant Program Name",
    "funder": "Organization Name",
    "deadline": "2025-12-31",
    "amount": "$10,000 - $50,000",
    "description": "Brief 1-2 sentence summary",
    "detailed_overview": "Comprehensive description...",
    "tags": ["Education", "Youth", "Community"],
    "eligibility": "Full eligibility requirements",
    "url": "https://example.com/grant",
    "application_requirements": ["501(c)(3) status", "Budget"],
    "funding_type": "Grant",
    "geography": "Chicago, Illinois"
  }
]
```
