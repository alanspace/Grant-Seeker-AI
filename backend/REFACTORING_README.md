"""README for refactored Grant Seeker application."""

# Grant Seeker - Refactored Architecture

## Project Structure

```
backend/
├── config/
│   └── __init__.py            # Configuration management
├── models/
│   └── __init__.py            # Pydantic data models
├── agents/
│   └── __init__.py            # LLM agent definitions
├── utils/
│   ├── helpers.py             # Utility functions
│   └── cache.py               # Caching service
├── services/
│   ├── __init__.py
│   ├── grant_finder.py        # Grant search service
│   └── grant_extractor.py     # Grant extraction service
├── tests/
│   ├── conftest.py            # Pytest fixtures
│   ├── test_models.py         # Model tests
│   ├── test_utils.py          # Utility tests
│   └── test_exceptions.py     # Exception tests
├── exceptions.py              # Custom exceptions
├── tavily_client.py           # Tavily API client wrapper
├── adk_agent_v2.py            # Legacy monolithic version
└── adk_agent_v2_refactored.py # New refactored version with caching
```

## Architecture Improvements

### 1. **Separation of Concerns**

- **config/**: All configuration in one place
- **models/**: Pydantic schemas for data validation
- **agents/**: Agent creation logic
- **utils/**: Helper functions and caching service
- **services/**: Business logic separated by domain

### 2. **Dependency Injection**

- Services receive dependencies via constructor
- Easy to mock for testing
- Flexible configuration

### 3. **Error Handling**

- Custom exception hierarchy
- Proper logging throughout
- Graceful error responses

### 4. **Type Safety**

- Full type hints on all functions
- Pydantic validation for data
- Better IDE support

### 5. **Testability**

- Unit tests for all components
- Fixtures for mocking
- Async test support

## Usage

### Running the refactored version:

```bash
# Navigate to backend directory
cd D:\adk-grant-seeker-copilot\backend

# Activate virtual environment
..\.venv\Scripts\Activate.ps1

# Run the script
python adk_agent_v2_refactored.py
```

### Running tests:

```bash
# Navigate to project root and activate venv
cd D:\adk-grant-seeker-copilot
.venv\Scripts\Activate.ps1

# Install test dependencies (first time only)
pip install -r backend/tests/requirements-test.txt

# Run all tests
python -m pytest backend/tests/

# Run with verbose output
python -m pytest backend/tests/ -v

# Run with coverage
python -m pytest backend/tests/ --cov=backend --cov-report=html
```

### Configuration

All settings can be modified in `config/__init__.py` or via environment variables:

- `GOOGLE_API_KEY`
- `TAVILY_API_KEY`
- `MODEL_NAME`
- `TAVILY_MAX_RESULTS`
- `MAX_CONCURRENT_EXTRACTIONS`
- `CACHE_ENABLED` (default: True)
- `CACHE_TTL_HOURS` (default: 24)
