"""Caching service for Grant Seeker application."""
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class CacheService:
    """Simple file-based cache for search results and page content."""
    
    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        """Initialize cache service.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live for cache entries in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        logger.info(f"Cache initialized at {self.cache_dir} with TTL={ttl_hours}h")
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache filename from key.
        
        Args:
            key: Cache key (e.g., search query or URL)
            
        Returns:
            MD5 hash of the key
        """
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get full path for cache file.
        
        Args:
            cache_key: Hashed cache key
            
        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, key: str) -> Optional[dict]:
        """Retrieve data from cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            logger.debug(f"Cache miss: {key}")
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check expiration
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            if datetime.now() - cached_at > self.ttl:
                logger.debug(f"Cache expired: {key}")
                cache_path.unlink()  # Delete expired cache
                return None
            
            logger.info(f"Cache hit: {key}")
            return cache_data['data']
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Invalid cache file: {cache_path}, error: {e}")
            cache_path.unlink()  # Delete corrupted cache
            return None
    
    def set(self, key: str, data: dict) -> None:
        """Store data in cache.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'key': key,
            'data': data
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Cached: {key}")
        except Exception as e:
            logger.error(f"Failed to cache {key}: {e}")
    
    def clear(self) -> int:
        """Clear all cache files.
        
        Returns:
            Number of files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        logger.info(f"Cleared {count} cache files")
        return count
    
    def clear_expired(self) -> int:
        """Clear only expired cache files.
        
        Returns:
            Number of files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cached_at = datetime.fromisoformat(cache_data['cached_at'])
                if datetime.now() - cached_at > self.ttl:
                    cache_file.unlink()
                    count += 1
            except Exception:
                # Delete corrupted files
                cache_file.unlink()
                count += 1
        
        logger.info(f"Cleared {count} expired cache files")
        return count
