"""Unit tests for utility functions."""
import pytest
from backend.utils.helpers import normalize_value, clean_json_string, get_current_date


def test_normalize_value_with_none():
    """Test normalize_value with None."""
    result = normalize_value(None, "default")
    assert result == "default"


def test_normalize_value_with_empty_string():
    """Test normalize_value with empty string."""
    result = normalize_value("", "default")
    assert result == "default"


def test_normalize_value_with_whitespace():
    """Test normalize_value with whitespace."""
    result = normalize_value("   ", "default")
    assert result == "default"


def test_normalize_value_with_valid_string():
    """Test normalize_value with valid string."""
    result = normalize_value("valid value", "default")
    assert result == "valid value"


def test_clean_json_string_with_markdown():
    """Test clean_json_string with markdown code blocks."""
    input_str = '```json\n{"key": "value"}\n```'
    result = clean_json_string(input_str)
    assert result == '{"key": "value"}'


def test_clean_json_string_without_markdown():
    """Test clean_json_string without markdown."""
    input_str = '{"key": "value"}'
    result = clean_json_string(input_str)
    assert result == '{"key": "value"}'


def test_get_current_date():
    """Test get_current_date returns tuple."""
    human_date, iso_date = get_current_date()
    
    assert isinstance(human_date, str)
    assert isinstance(iso_date, str)
    assert len(iso_date) == 10  # YYYY-MM-DD format
    assert "-" in iso_date
