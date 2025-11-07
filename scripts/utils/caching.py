"""
Caching utilities for expensive operations.

This module provides:
- LRU caches for frequently accessed data
- Disk-based caching for API responses
- Cache invalidation and management
- Persistent caches across runs
"""

import json
import pickle
import hashlib
import time
from typing import Any, Optional, Callable, Dict
from pathlib import Path
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class DiskCache:
    """
    Disk-based cache for expensive operations.

    Example:
        >>> cache = DiskCache(cache_dir='cache/')
        >>> @cache.cached(ttl=3600)
        ... def expensive_function(arg):
        ...     return compute_result(arg)
    """

    def __init__(self, cache_dir: str = '.cache', max_size_mb: int = 1000):
        """
        Initialize disk cache.

        Args:
            cache_dir: Directory to store cache files
            max_size_mb: Maximum cache size in megabytes
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_mb = max_size_mb

        # Metadata file to track cache entries
        self.metadata_file = self.cache_dir / '_metadata.json'
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_metadata(self):
        """Save cache metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def _get_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function name and arguments."""
        # Create a hashable representation
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get path for cache file."""
        return self.cache_dir / f"{cache_key}.pkl"

    def get(self, func_name: str, args: tuple, kwargs: dict, ttl: Optional[int] = None) -> Optional[Any]:
        """
        Get cached value if available and not expired.

        Args:
            func_name: Function name
            args: Function arguments
            kwargs: Function keyword arguments
            ttl: Time-to-live in seconds (None = no expiration)

        Returns:
            Cached value or None if not found/expired
        """
        cache_key = self._get_cache_key(func_name, args, kwargs)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        # Check TTL if specified
        if ttl is not None:
            metadata = self.metadata.get(cache_key, {})
            cache_time = metadata.get('timestamp', 0)
            if time.time() - cache_time > ttl:
                logger.debug(f"Cache expired for {func_name}")
                return None

        # Load cached value
        try:
            with open(cache_path, 'rb') as f:
                value = pickle.load(f)
            logger.debug(f"Cache hit for {func_name}")
            return value
        except (IOError, pickle.PickleError) as e:
            logger.warning(f"Failed to load cache for {func_name}: {e}")
            return None

    def set(self, func_name: str, args: tuple, kwargs: dict, value: Any):
        """
        Store value in cache.

        Args:
            func_name: Function name
            args: Function arguments
            kwargs: Function keyword arguments
            value: Value to cache
        """
        cache_key = self._get_cache_key(func_name, args, kwargs)
        cache_path = self._get_cache_path(cache_key)

        # Save value
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)

            # Update metadata
            self.metadata[cache_key] = {
                'func': func_name,
                'timestamp': time.time(),
                'size': cache_path.stat().st_size
            }
            self._save_metadata()

            logger.debug(f"Cached result for {func_name}")

            # Check cache size and clean if needed
            self._check_size()
        except (IOError, pickle.PickleError) as e:
            logger.warning(f"Failed to cache result for {func_name}: {e}")

    def _check_size(self):
        """Check cache size and clean old entries if needed."""
        total_size = sum(entry.get('size', 0) for entry in self.metadata.values())
        max_size_bytes = self.max_size_mb * 1024 * 1024

        if total_size > max_size_bytes:
            logger.info(f"Cache size ({total_size / 1024 / 1024:.1f} MB) exceeds limit, cleaning...")
            self.clean_oldest(keep_size_mb=self.max_size_mb * 0.8)

    def clean_oldest(self, keep_size_mb: Optional[int] = None):
        """
        Remove oldest cache entries.

        Args:
            keep_size_mb: Target size to reduce to (None = remove all old entries)
        """
        if not self.metadata:
            return

        # Sort by timestamp (oldest first)
        sorted_entries = sorted(
            self.metadata.items(),
            key=lambda x: x[1].get('timestamp', 0)
        )

        total_size = 0
        keep_entries = {}

        # Keep newest entries up to target size
        for cache_key, metadata in reversed(sorted_entries):
            entry_size = metadata.get('size', 0)

            if keep_size_mb is None:
                # Remove all old entries
                cache_path = self._get_cache_path(cache_key)
                if cache_path.exists():
                    cache_path.unlink()
            elif total_size + entry_size <= keep_size_mb * 1024 * 1024:
                keep_entries[cache_key] = metadata
                total_size += entry_size
            else:
                # Remove this entry
                cache_path = self._get_cache_path(cache_key)
                if cache_path.exists():
                    cache_path.unlink()

        if keep_size_mb is not None:
            self.metadata = keep_entries
            self._save_metadata()
            logger.info(f"Cleaned cache to {total_size / 1024 / 1024:.1f} MB")
        else:
            self.metadata = {}
            self._save_metadata()
            logger.info("Cleared all cache entries")

    def clear(self):
        """Clear entire cache."""
        self.clean_oldest(keep_size_mb=None)

    def cached(self, ttl: Optional[int] = None):
        """
        Decorator to cache function results.

        Args:
            ttl: Time-to-live in seconds (None = no expiration)

        Example:
            >>> cache = DiskCache()
            >>> @cache.cached(ttl=3600)
            ... def expensive_func(x):
            ...     return x ** 2
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Try to get from cache
                cached_value = self.get(func.__name__, args, kwargs, ttl)
                if cached_value is not None:
                    return cached_value

                # Compute value
                value = func(*args, **kwargs)

                # Store in cache
                self.set(func.__name__, args, kwargs, value)

                return value

            return wrapper
        return decorator


class MemoryCache:
    """
    Simple in-memory LRU cache.

    Example:
        >>> cache = MemoryCache(max_size=100)
        >>> cache.set('key', 'value')
        >>> cache.get('key')
        'value'
    """

    def __init__(self, max_size: int = 128):
        """
        Initialize memory cache.

        Args:
            max_size: Maximum number of entries
        """
        self.max_size = max_size
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None

    def set(self, key: str, value: Any):
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
            del self.cache[oldest_key]
            del self.access_times[oldest_key]

        self.cache[key] = value
        self.access_times[key] = time.time()

    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.access_times.clear()

    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self.cache


def memoize(func: Callable) -> Callable:
    """
    Simple memoization decorator using in-memory cache.

    Args:
        func: Function to memoize

    Returns:
        Wrapped function with caching

    Example:
        >>> @memoize
        ... def fibonacci(n):
        ...     if n < 2:
        ...         return n
        ...     return fibonacci(n-1) + fibonacci(n-2)
    """
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from arguments
        key = str(args) + str(sorted(kwargs.items()))

        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    wrapper.cache = cache
    wrapper.clear_cache = lambda: cache.clear()

    return wrapper


# Global cache instances
_disk_cache = None
_memory_cache = None


def get_disk_cache(cache_dir: str = '.cache', max_size_mb: int = 1000) -> DiskCache:
    """
    Get global disk cache instance.

    Args:
        cache_dir: Cache directory
        max_size_mb: Maximum cache size in MB

    Returns:
        DiskCache instance
    """
    global _disk_cache
    if _disk_cache is None:
        _disk_cache = DiskCache(cache_dir, max_size_mb)
    return _disk_cache


def get_memory_cache(max_size: int = 128) -> MemoryCache:
    """
    Get global memory cache instance.

    Args:
        max_size: Maximum number of entries

    Returns:
        MemoryCache instance
    """
    global _memory_cache
    if _memory_cache is None:
        _memory_cache = MemoryCache(max_size)
    return _memory_cache


# Export public API
__all__ = [
    'DiskCache',
    'MemoryCache',
    'memoize',
    'get_disk_cache',
    'get_memory_cache',
]
