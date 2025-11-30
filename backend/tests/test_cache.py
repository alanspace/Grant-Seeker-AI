"""Tests for CacheService."""
import pytest
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from adk_agent import CacheService


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create a temporary cache directory."""
    cache_dir = tmp_path / "test_cache"
    return cache_dir


@pytest.fixture
def cache_service(temp_cache_dir):
    """Create a CacheService instance with temp directory."""
    return CacheService(cache_dir=str(temp_cache_dir), ttl_hours=24)


def test_cache_initialization(cache_service, temp_cache_dir):
    """Test cache service initializes correctly."""
    assert cache_service.cache_dir.exists()
    assert cache_service.cache_dir == Path(temp_cache_dir)
    assert cache_service.ttl == timedelta(hours=24)


def test_cache_set_and_get(cache_service):
    """Test setting and getting cached data."""
    test_key = "test_key"
    test_data = {"name": "Test Grant", "amount": "$10,000"}
    
    # Set cache
    cache_service.set(test_key, test_data)
    
    # Get cache
    cached_data = cache_service.get(test_key)
    
    assert cached_data is not None
    assert cached_data == test_data


def test_cache_miss(cache_service):
    """Test cache miss returns None."""
    result = cache_service.get("nonexistent_key")
    assert result is None


def test_cache_expiration(temp_cache_dir):
    """Test cache expiration after TTL."""
    # Create cache with very short TTL (0.001 hours = 3.6 seconds)
    cache_service = CacheService(cache_dir=str(temp_cache_dir), ttl_hours=0.001)
    
    test_key = "expire_test"
    test_data = {"test": "data"}
    
    # Set cache
    cache_service.set(test_key, test_data)
    
    # Should be cached immediately
    assert cache_service.get(test_key) == test_data
    
    # Wait for expiration
    time.sleep(4)
    
    # Should be expired and return None
    assert cache_service.get(test_key) is None


def test_cache_key_hashing(cache_service):
    """Test that cache keys are properly hashed."""
    test_key = "search:grants chicago:5"
    test_data = {"results": []}
    
    cache_service.set(test_key, test_data)
    
    # Check that file is created with MD5 hash
    cache_files = list(cache_service.cache_dir.glob("*.json"))
    assert len(cache_files) == 1
    assert cache_files[0].name.endswith(".json")
    assert len(cache_files[0].stem) == 32  # MD5 hash length


def test_cache_clear(cache_service):
    """Test clearing all cache files."""
    # Add multiple cache entries
    cache_service.set("key1", {"data": 1})
    cache_service.set("key2", {"data": 2})
    cache_service.set("key3", {"data": 3})
    
    # Verify files exist
    assert len(list(cache_service.cache_dir.glob("*.json"))) == 3
    
    # Clear cache
    count = cache_service.clear()
    
    assert count == 3
    assert len(list(cache_service.cache_dir.glob("*.json"))) == 0


def test_cache_corrupted_file(cache_service, temp_cache_dir):
    """Test handling of corrupted cache file."""
    # Create a corrupted cache file
    cache_key = cache_service._get_cache_key("corrupted")
    cache_path = cache_service._get_cache_path(cache_key)
    
    with open(cache_path, 'w') as f:
        f.write("invalid json content{{{")
    
    # Should return None and delete corrupted file
    result = cache_service.get("corrupted")
    assert result is None
    assert not cache_path.exists()


def test_cache_with_special_characters(cache_service):
    """Test cache with special characters in key."""
    test_key = "https://example.com/grant?id=123&type=community"
    test_data = {"url": test_key, "title": "Test Grant"}
    
    cache_service.set(test_key, test_data)
    cached_data = cache_service.get(test_key)
    
    assert cached_data == test_data
