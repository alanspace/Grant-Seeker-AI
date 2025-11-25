"""Utility functions for Grant Seeker application."""
from datetime import datetime


def get_current_date() -> tuple[str, str]:
    """Get current date in human-readable and ISO format.
    
    Returns:
        Tuple of (human_readable_date, iso_date)
    """
    now = datetime.now()
    return (
        now.strftime("%B %d, %Y"),
        now.strftime("%Y-%m-%d")
    )


def normalize_value(value: str | None, default: str) -> str:
    """Convert empty strings, None, or whitespace-only strings to default value.
    
    Args:
        value: The value to normalize
        default: Default value to use if value is empty
        
    Returns:
        Normalized value or default
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return default
    return value


def clean_json_string(json_str: str) -> str:
    """Remove markdown code blocks from JSON string.
    
    Args:
        json_str: JSON string potentially wrapped in markdown
        
    Returns:
        Cleaned JSON string
    """
    return json_str.replace("```json", "").replace("```", "").strip()
