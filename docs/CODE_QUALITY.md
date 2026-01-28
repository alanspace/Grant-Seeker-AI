# Code Quality Checklist

This document establishes standards to prevent common code quality issues identified during code reviews.

## Security

### ❌ **NEVER** Hardcode Sensitive Data
**Bad:**
```python
API_KEY = "sk-abc123..."
CSE_ID = os.getenv("GOOGLE_CSE_ID", "c7810cabc13b24433")  # ❌ Hardcoded default
```

**Good:**
```python
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY must be set in .env file")

CSE_ID = os.getenv("GOOGLE_CSE_ID")  # ✅ No default
```

**What to check:**
- [ ] No API keys, passwords, or secrets in code
- [ ] All sensitive config from environment variables
- [ ] Environment variables validated at startup
- [ ] No hardcoded defaults for credentials

---

## Error Handling

### ✅ **DO** Provide Specific, Actionable Error Messages

**Bad:**
```python
except Exception as e:
    logger.warning(f"Error: {e}")  # ❌ Too vague
    
except Exception as e:
    logger.warning(f"Skipping ONE invalid item: {e}")  # ❌ Which item?
```

**Good:**
```python
except FileNotFoundError as e:
    logger.error(f"❌ File not found: {filename}")
    logger.error(f"   Expected location: {expected_path}")
except ValueError as e:
    error_type = type(e).__name__ 
    logger.warning(f"⚠️ Invalid grant at index {i+1}/{total}: {error_type}")
    logger.warning(f"   Data: {json.dumps(data)[:200]}...")
    logger.warning(f"   Error: {str(e)[:200]}")
```

**What to include:**
- [ ] Exception type name (`type(e).__name__`)
- [ ] Context (which file, which item, which index)
- [ ] Actual problematic data (truncated if long)
- [ ] Specific error message
- [ ] Helpful hint for resolution

---

## Logging

### ✅ **DO** Follow Logging Guidelines

See `backend/LOGGING_GUIDELINES.md` for full details.

**Quick Reference:**
- **INFO**: User-visible milestones, results, cache hits
- **DEBUG**: Internal Steps, query strings, loop details
- **WARNING**: Recoverable issues, fallbacks, data quality
- **ERROR**: Failures requiring attention

**Bad:**
```python
logger.info(f"Processing item {i}")  # ❌ Too verbose
print(f"Error: {e}")  # ❌ Use logging, not print
```

**Good:**
```python
logger.debug(f"Processing item {i}/{total}")  # ✅ Internal detail
logger.info(f"Processed {total} items successfully")  # ✅ Result
logger.error(f"Failed to process batch: {error_type}")  # ✅ Failure
```

**What to check:**
- [ ] Use `logging` module, not `print()` (except debug scripts)
- [ ] Appropriate log level for the message type
- [ ] Results logged at INFO, not every iteration
- [ ] Include context in error/warning logs

---

## Code Duplication

### ❌ **NEVER** Copy-Paste Code Without Refactoring

**Bad:**
```python
# In prompt (lines 366-368)
The text might be:
1. A specific grant page -> Extract details
2. A list page -> Summarize

# Duplicate (lines 370-372)  ❌
The text might be:
1. A specific grant page -> Extract details
2. A list page -> Summarize
```

**Good:**
```python
# Single instance
The text might be:
1. A specific grant page -> Extract details
2. A list page -> Summarize
```

**Or refactor to function:**
```python
def get_page_type_instruction():
    return """
    The text might be:
    1. A specific grant page -> Extract details
    2. A list page -> Summarize
    """
```

**What to check:**
- [ ] No duplicate code blocks
- [ ] Common logic extracted to functions
- [ ] DRY principle (Don't Repeat Yourself)
- [ ] Reuse existing utilities

---

## Environment Variables

### ✅ **DO** Validate All Required Environment Variables

**Bad:**
```python
API_KEY = os.getenv("API_KEY")
# ... later, cryptic error when API_KEY is None
```

**Good:**
```python
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY must be set in .env file")
```

**For conditional requirements:**
```python
SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "TAVILY")

if SEARCH_PROVIDER == "GOOGLE":
    GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
    if not GOOGLE_CSE_ID:
        raise ValueError("GOOGLE_CSE_ID required when SEARCH_PROVIDER=GOOGLE")
```

**What to check:**
- [ ] All `os.getenv()` calls validated
- [ ] Clear error messages stating which variable is missing
- [ ] Conditional validation for optional providers
- [ ] Fail fast at startup, not during execution

---

## Git Hygiene

### ✅ **DO** Keep Repository Clean

**What to ignore:**
```gitignore
# Always ignore
__pycache__/
*.pyc
*.pyo
.env
.cache/
*.log

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

**What to check:**
- [ ] `.gitignore` includes `__pycache__/`, `*.pyc`
- [ ] `.env` file never committed
- [ ] No binary files unless necessary
- [ ] No large test data files
- [ ] Cache directories excluded

---

## Code Review Checklist

Before committing, verify:

### Security
- [ ] No hardcoded credentials or secrets
- [ ] All sensitive config from environment variables
- [ ] Environment variables validated

### Error Handling
- [ ] Specific exception types caught where possible
- [ ] Error messages include exception type
- [ ] Error messages include context (file, index, data)
- [ ] Helpful hints for resolution included

### Logging  
- [ ] Using `logging` module, not `print()` (backend)
- [ ] Appropriate log levels (INFO for results, DEBUG for steps)
- [ ] Error logs include full context
- [ ] No sensitive data in logs

### Code Quality
- [ ] No duplicate code blocks
- [ ] Common logic extracted to functions
- [ ] Docstrings for public functions
- [ ] Type hints where helpful

### Testing (when applicable)
- [ ] Debug scripts in `scripts/` directory
- [ ] Unit tests in `tests/` directory  
- [ ] Tests use `pytest` with assertions
- [ ] No `print()` in unit tests (use logging)

---

## Common Anti-Patterns to Avoid

### 1. Silent Failures
```python
# Bad
try:
    do_something()
except:
    pass  # ❌ Silent failure

# Good
try:
    do_something()
except Exception as e:
    logger.error(f"Failed to do_something: {type(e).__name__}: {e}")
    raise  # Or handle appropriately
```

### 2. Magic Numbers
```python
# Bad  
if len(results) > 15:  # ❌ What is 15?

# Good
MAX_RESULTS = 15  # Or from environment
if len(results) > MAX_RESULTS:
```

### 3. Overly Broad Exception Handling
```python
# Bad
except Exception:  # ❌ Too broad

# Good
except (ValueError, KeyError) as e:  # ✅ Specific
except Exception as e:  # ✅ But log with type
    logger.error(f"Unexpected {type(e).__name__}: {e}")
```

### 4. Missing Context in Loops
```python
# Bad
for item in items:
    try:
        process(item)
    except Exception as e:
        logger.error(f"Error: {e}")  # ❌ Which item?

# Good
for i, item in enumerate(items):
    try:
        process(item)
    except Exception as e:
        logger.error(f"Error processing item {i+1}/{len(items)}: {type(e).__name__}")
        logger.error(f"   Item data: {item}")
```

---

## References

- **Logging Guidelines**: `backend/LOGGING_GUIDELINES.md`
- **Security Best Practices**: Never commit `.env`, always validate environment variables
- **Python Style**: Follow PEP 8
- **Error Handling**: Be specific, be helpful, be thorough

---

**Last Updated:** 2026-01-17  
**Version:** 1.0
