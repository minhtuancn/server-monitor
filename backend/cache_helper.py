#!/usr/bin/env python3

"""
Simple in-memory cache with TTL support
Provides thread-safe caching for frequently accessed data
"""

import time
import threading
from typing import Any, Optional, Callable
from dataclasses import dataclass

try:
    from observability import get_metrics_collector

    metrics = get_metrics_collector()
except:
    metrics = None


@dataclass
class CacheEntry:
    """Represents a cached value with expiration"""

    value: Any
    expires_at: float


class SimpleCache:
    """
    Thread-safe in-memory cache with TTL

    Features:
    - Thread-safe operations
    - Per-key TTL
    - Automatic expiration
    - Metrics tracking (hits/misses)
    """

    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._misses += 1
                self._track_metric("cache_misses", key)
                return None

            # Check if expired
            if time.time() > entry.expires_at:
                # Remove expired entry
                del self._cache[key]
                self._misses += 1
                self._track_metric("cache_misses", key)
                return None

            # Cache hit
            self._hits += 1
            self._track_metric("cache_hits", key)
            return entry.value

    def _track_metric(self, metric_name: str, key: str):
        """Track cache metrics if metrics collector is available"""
        if metrics and hasattr(metrics, "increment"):
            try:
                metrics.increment(metric_name, labels={"key": self._sanitize_key(key)})
            except:
                pass

    def set(self, key: str, value: Any, ttl: int):
        """
        Set value in cache with TTL

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        with self._lock:
            expires_at = time.time() + ttl
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    def delete(self, key: str):
        """
        Delete key from cache

        Args:
            key: Cache key
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0

            return {
                "hits": self._hits,
                "misses": self._misses,
                "total_requests": total,
                "hit_rate_percent": round(hit_rate, 2),
                "entries": len(self._cache),
            }

    def _sanitize_key(self, key: str) -> str:
        """Sanitize cache key for metrics label"""
        # Remove dynamic parts like IDs for better metric aggregation
        parts = key.split("/")
        sanitized = []
        for part in parts:
            # Keep only non-numeric parts
            if part and not part.isdigit():
                sanitized.append(part)
        return "/".join(sanitized) if sanitized else "unknown"

    def get_or_compute(self, key: str, compute_fn: Callable[[], Any], ttl: int) -> Any:
        """
        Get value from cache, or compute and cache it

        Args:
            key: Cache key
            compute_fn: Function to compute value if not cached
            ttl: Time to live in seconds

        Returns:
            Cached or computed value
        """
        # Try to get from cache
        value = self.get(key)
        if value is not None:
            return value

        # Compute value
        value = compute_fn()

        # Cache it
        self.set(key, value, ttl)

        return value


# Global cache instance
_global_cache: Optional[SimpleCache] = None
_cache_lock = threading.Lock()


def get_cache() -> SimpleCache:
    """
    Get global cache instance (singleton)

    Returns:
        SimpleCache instance
    """
    global _global_cache

    if _global_cache is None:
        with _cache_lock:
            if _global_cache is None:
                _global_cache = SimpleCache()

    return _global_cache
