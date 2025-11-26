"""Unit tests for custom exceptions."""
import pytest
from backend.exceptions import (
    GrantSeekerError,
    GrantSearchError,
    GrantExtractionError,
    LeadParsingError
)


def test_grant_seeker_error():
    """Test base GrantSeekerError."""
    error = GrantSeekerError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_grant_search_error():
    """Test GrantSearchError inheritance."""
    error = GrantSearchError("Search failed")
    assert str(error) == "Search failed"
    assert isinstance(error, GrantSeekerError)


def test_grant_extraction_error():
    """Test GrantExtractionError inheritance."""
    error = GrantExtractionError("Extraction failed")
    assert str(error) == "Extraction failed"
    assert isinstance(error, GrantSeekerError)


def test_lead_parsing_error():
    """Test LeadParsingError inheritance."""
    error = LeadParsingError("Parsing failed")
    assert str(error) == "Parsing failed"
    assert isinstance(error, GrantSeekerError)
