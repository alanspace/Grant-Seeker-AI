"""Tests for utility functions."""
import pytest
import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))

from adk_agent_v2 import get_current_date, normalize_value, clean_json_string


def test_get_current_date():
    """Test getting current date returns tuple of strings."""
    human_date, iso_date = get_current_date()
    
    # Check types
    assert isinstance(human_date, str)
    assert isinstance(iso_date, str)
    
    # Check format patterns
    assert len(iso_date) == 10  # YYYY-MM-DD
    assert iso_date.count('-') == 2
    
    # Verify it's today's date
    today = datetime.now()
    assert iso_date == today.strftime("%Y-%m-%d")
    assert today.strftime("%B") in human_date  # Month name present


def test_normalize_value_with_none():
    """Test normalize_value with None."""
    result = normalize_value(None, "default")
    assert result == "default"


def test_normalize_value_with_empty_string():
    """Test normalize_value with empty string."""
    result = normalize_value("", "default")
    assert result == "default"


def test_normalize_value_with_whitespace():
    """Test normalize_value with whitespace-only string."""
    result = normalize_value("   ", "default")
    assert result == "default"


def test_normalize_value_with_valid_string():
    """Test normalize_value with valid string."""
    result = normalize_value("Valid Value", "default")
    assert result == "Valid Value"


def test_normalize_value_with_string_and_spaces():
    """Test normalize_value preserves strings with content and spaces."""
    result = normalize_value("  Valid Value  ", "default")
    assert result == "  Valid Value  "


def test_clean_json_string_with_markdown():
    """Test cleaning JSON string with markdown code blocks."""
    json_with_markdown = '```json\n{"key": "value"}\n```'
    result = clean_json_string(json_with_markdown)
    assert result == '{"key": "value"}'


def test_clean_json_string_without_markdown():
    """Test cleaning JSON string without markdown."""
    clean_json = '{"key": "value"}'
    result = clean_json_string(clean_json)
    assert result == '{"key": "value"}'


def test_clean_json_string_with_only_backticks():
    """Test cleaning JSON string with only backticks."""
    json_with_backticks = '```{"key": "value"}```'
    result = clean_json_string(json_with_backticks)
    assert result == '{"key": "value"}'


def test_clean_json_string_multiple_blocks():
    """Test cleaning JSON with multiple markdown blocks."""
    json_str = '```json\n```\n{"data": "test"}\n```'
    result = clean_json_string(json_str)
    assert '```' not in result
    assert 'json' not in result
    assert '{"data": "test"}' in result


def test_clean_json_string_strips_whitespace():
    """Test that clean_json_string strips leading/trailing whitespace."""
    json_str = '  \n```json\n{"key": "value"}\n```  \n'
    result = clean_json_string(json_str)
    assert result == '{"key": "value"}'
    assert not result.startswith(' ')
    assert not result.endswith(' ')
