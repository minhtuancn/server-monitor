#!/usr/bin/env python3

"""
Rate limiting helper for API endpoints
Provides token bucket-based rate limiting per key (user, server, etc.)
"""

import time
import threading
from typing import Dict, Tuple
from dataclasses import dataclass
from observability import StructuredLogger

logger = StructuredLogger('rate_limiter')


@dataclass
class RateLimitBucket:
    """Token bucket for rate limiting"""
    tokens: float
    last_update: float


class RateLimiter:
    """
    Token bucket rate limiter
    
    Features:
    - Per-key rate limiting
    - Token bucket algorithm
    - Thread-safe
    - Configurable limits per endpoint
    """
    
    def __init__(self):
        self._buckets: Dict[str, RateLimitBucket] = {}
        self._lock = threading.RLock()
    
    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 60
    ) -> Tuple[bool, dict]:
        """
        Check if request is within rate limit
        
        Args:
            key: Rate limit key (e.g., "user:123", "server:456")
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (allowed: bool, info: dict)
            info contains: remaining, reset_at, limit
        """
        with self._lock:
            now = time.time()
            
            # Get or create bucket
            if key not in self._buckets:
                self._buckets[key] = RateLimitBucket(
                    tokens=float(max_requests),
                    last_update=now
                )
            
            bucket = self._buckets[key]
            
            # Calculate tokens to add based on elapsed time
            elapsed = now - bucket.last_update
            tokens_to_add = elapsed * (max_requests / window_seconds)
            
            # Update bucket
            bucket.tokens = min(max_requests, bucket.tokens + tokens_to_add)
            bucket.last_update = now
            
            # Check if request is allowed
            if bucket.tokens >= 1.0:
                bucket.tokens -= 1.0
                allowed = True
            else:
                allowed = False
            
            # Calculate when bucket will have tokens again
            if bucket.tokens < max_requests:
                seconds_per_token = window_seconds / max_requests
                seconds_until_token = (1.0 - bucket.tokens) * seconds_per_token
                reset_at = now + seconds_until_token
            else:
                reset_at = now
            
            info = {
                'allowed': allowed,
                'remaining': int(bucket.tokens),
                'limit': max_requests,
                'reset_at': int(reset_at),
                'retry_after': int(reset_at - now) if not allowed else 0
            }
            
            if not allowed:
                logger.warning('Rate limit exceeded',
                             key=key,
                             limit=max_requests,
                             window=window_seconds,
                             retry_after=info['retry_after'])
            
            return allowed, info
    
    def reset(self, key: str):
        """
        Reset rate limit for a key
        
        Args:
            key: Rate limit key
        """
        with self._lock:
            if key in self._buckets:
                del self._buckets[key]
    
    def clear_all(self):
        """Clear all rate limit buckets"""
        with self._lock:
            self._buckets.clear()
    
    def cleanup_old_buckets(self, max_age_seconds: int = 3600):
        """
        Remove buckets that haven't been used recently
        
        Args:
            max_age_seconds: Maximum age of bucket before cleanup
        """
        with self._lock:
            now = time.time()
            keys_to_remove = []
            
            for key, bucket in self._buckets.items():
                if now - bucket.last_update > max_age_seconds:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._buckets[key]
            
            if keys_to_remove:
                logger.debug(f'Cleaned up {len(keys_to_remove)} old rate limit buckets')


# Global rate limiter instance
_global_rate_limiter: RateLimiter = None
_limiter_lock = threading.Lock()


def get_rate_limiter() -> RateLimiter:
    """
    Get global rate limiter instance (singleton)
    
    Returns:
        RateLimiter instance
    """
    global _global_rate_limiter
    
    if _global_rate_limiter is None:
        with _limiter_lock:
            if _global_rate_limiter is None:
                _global_rate_limiter = RateLimiter()
    
    return _global_rate_limiter


# Predefined rate limit configurations
RATE_LIMITS = {
    'inventory_refresh': {
        'max_requests': 10,
        'window_seconds': 60,
        'key_prefix': 'inventory:server'
    },
    'task_create': {
        'max_requests': 20,
        'window_seconds': 60,
        'key_prefix': 'task:user'
    },
    'webhook_test': {
        'max_requests': 10,
        'window_seconds': 60,
        'key_prefix': 'webhook:user'
    }
}


def check_endpoint_rate_limit(endpoint: str, identifier: str) -> Tuple[bool, dict]:
    """
    Convenience function to check rate limit for predefined endpoints
    
    Args:
        endpoint: Endpoint name (e.g., 'inventory_refresh', 'task_create')
        identifier: Unique identifier (e.g., server_id, user_id)
        
    Returns:
        Tuple of (allowed: bool, info: dict)
    """
    if endpoint not in RATE_LIMITS:
        # No rate limit configured for this endpoint
        return True, {'allowed': True, 'remaining': 999, 'limit': 999}
    
    config = RATE_LIMITS[endpoint]
    key = f"{config['key_prefix']}:{identifier}"
    
    limiter = get_rate_limiter()
    return limiter.check_rate_limit(
        key=key,
        max_requests=config['max_requests'],
        window_seconds=config['window_seconds']
    )
