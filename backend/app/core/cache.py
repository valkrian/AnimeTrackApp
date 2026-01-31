"""
In-memory cache system for storing API responses with TTL support.
Provides thread-safe operations for concurrent access with automatic cleanup.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from threading import Lock
from typing import Dict, Optional, Any, Set
from contextlib import asynccontextmanager

from app.core.config import settings
from app.models.anime import CacheEntry, SeasonalAnimeResponse

# Configure logging
logger = logging.getLogger(__name__)


class InMemoryCache:
    """
    Thread-safe in-memory cache with TTL support and automatic cleanup.
    Uses dictionary-based storage with timestamp tracking for expiration.
    """
    
    def __init__(self, default_ttl_minutes: int = None):
        """
        Initialize the cache with optional TTL override.
        
        Args:
            default_ttl_minutes: Override default TTL from settings
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._default_ttl_minutes = default_ttl_minutes or settings.CACHE_TTL_MINUTES
        self._cleanup_task: Optional[asyncio.Task] = None
        self._cleanup_interval = 300  # 5 minutes cleanup interval
        
        logger.info(f"Initialized cache with {self._default_ttl_minutes} minute TTL")
    
    def _generate_cache_key(self, endpoint: str, params: Dict[str, Any] = None) -> str:
        """
        Generate a cache key from endpoint and parameters.
        
        Args:
            endpoint: API endpoint
            params: Optional parameters dictionary
            
        Returns:
            String cache key
        """
        if params:
            # Sort params for consistent key generation
            param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            return f"{endpoint}?{param_str}"
        return endpoint
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """
        Check if a cache entry has expired.
        
        Args:
            entry: Cache entry to check
            
        Returns:
            True if expired, False otherwise
        """
        return entry.is_expired()
    
    def _cleanup_expired_entries(self) -> int:
        """
        Remove expired entries from cache.
        Thread-safe operation that cleans up expired entries.
        
        Returns:
            Number of entries removed
        """
        removed_count = 0
        
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() 
                if self._is_expired(entry)
            ]
            
            for key in expired_keys:
                del self._cache[key]
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} expired cache entries")
        
        return removed_count
    
    async def _periodic_cleanup(self):
        """
        Periodic cleanup task that runs in the background.
        Removes expired entries at regular intervals.
        """
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                self._cleanup_expired_entries()
            except asyncio.CancelledError:
                logger.info("Cache cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error during cache cleanup: {e}")
    
    def start_cleanup_task(self):
        """Start the background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
            logger.info("Started cache cleanup task")
    
    def stop_cleanup_task(self):
        """Stop the background cleanup task."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            logger.info("Stopped cache cleanup task")
    
    def get(self, key: str) -> Optional[SeasonalAnimeResponse]:
        """
        Retrieve data from cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data if found and not expired, None otherwise
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                logger.debug(f"Cache miss for key: {key}")
                return None
            
            if self._is_expired(entry):
                # Remove expired entry
                del self._cache[key]
                logger.debug(f"Cache expired for key: {key}")
                return None
            
            logger.debug(f"Cache hit for key: {key}, TTL: {entry.time_to_live()}s")
            return entry.data
    
    def set(self, key: str, data: SeasonalAnimeResponse, ttl_minutes: Optional[int] = None) -> None:
        """
        Store data in cache with TTL.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl_minutes: Optional TTL override
        """
        ttl = ttl_minutes or self._default_ttl_minutes
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=ttl)
        
        entry = CacheEntry(
            data=data,
            timestamp=now,
            expires_at=expires_at,
            cache_key=key
        )
        
        with self._lock:
            self._cache[key] = entry
        
        logger.debug(f"Cached data for key: {key}, expires at: {expires_at}")
    
    def delete(self, key: str) -> bool:
        """
        Remove specific entry from cache.
        
        Args:
            key: Cache key to remove
            
        Returns:
            True if entry was removed, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Deleted cache entry: {key}")
                return True
            return False
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of entries cleared
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
        
        logger.info(f"Cleared {count} cache entries")
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_entries = len(self._cache)
            expired_entries = sum(
                1 for entry in self._cache.values() 
                if self._is_expired(entry)
            )
            active_entries = total_entries - expired_entries
        
        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "default_ttl_minutes": self._default_ttl_minutes,
            "cleanup_interval_seconds": self._cleanup_interval
        }
    
    def get_cache_keys(self) -> Set[str]:
        """
        Get all cache keys (including expired ones).
        
        Returns:
            Set of cache keys
        """
        with self._lock:
            return set(self._cache.keys())
    
    @asynccontextmanager
    async def cache_context(self):
        """
        Async context manager for cache lifecycle management.
        Starts cleanup task on enter, stops on exit.
        """
        try:
            self.start_cleanup_task()
            yield self
        finally:
            self.stop_cleanup_task()


# Global cache instance
cache = InMemoryCache()


def get_cache() -> InMemoryCache:
    """
    Get cache instance.
    Useful for dependency injection in FastAPI.
    """
    return cache


# Cache utility functions for common operations
async def get_seasonal_anime_cache(year: Optional[int] = None, season: Optional[str] = None) -> Optional[SeasonalAnimeResponse]:
    """
    Get seasonal anime data from cache.
    
    Args:
        year: Optional year parameter
        season: Optional season parameter
        
    Returns:
        Cached seasonal anime data if available
    """
    if year and season:
        key = f"seasonal_anime_{year}_{season.lower()}"
    else:
        key = "seasonal_anime_current"
    
    return cache.get(key)


async def set_seasonal_anime_cache(data: SeasonalAnimeResponse, year: Optional[int] = None, season: Optional[str] = None) -> None:
    """
    Store seasonal anime data in cache.
    
    Args:
        data: Seasonal anime data to cache
        year: Optional year parameter
        season: Optional season parameter
    """
    if year and season:
        key = f"seasonal_anime_{year}_{season.lower()}"
    else:
        key = "seasonal_anime_current"
    
    cache.set(key, data)