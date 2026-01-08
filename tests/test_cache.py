#!/usr/bin/env python3

"""
Unit tests for cache_helper module
"""

import unittest
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from cache_helper import SimpleCache, get_cache


class TestSimpleCache(unittest.TestCase):
    """Test cases for SimpleCache"""
    
    def setUp(self):
        """Set up test cache"""
        self.cache = SimpleCache()
    
    def test_get_nonexistent_key(self):
        """Test getting a non-existent key returns None"""
        result = self.cache.get('nonexistent')
        self.assertIsNone(result)
    
    def test_set_and_get(self):
        """Test setting and getting a value"""
        self.cache.set('test_key', 'test_value', ttl=10)
        result = self.cache.get('test_key')
        self.assertEqual(result, 'test_value')
    
    def test_ttl_expiration(self):
        """Test that values expire after TTL"""
        self.cache.set('expire_key', 'expire_value', ttl=1)
        
        # Should exist immediately
        result = self.cache.get('expire_key')
        self.assertEqual(result, 'expire_value')
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired now
        result = self.cache.get('expire_key')
        self.assertIsNone(result)
    
    def test_delete(self):
        """Test deleting a key"""
        self.cache.set('delete_key', 'delete_value', ttl=10)
        self.assertEqual(self.cache.get('delete_key'), 'delete_value')
        
        self.cache.delete('delete_key')
        self.assertIsNone(self.cache.get('delete_key'))
    
    def test_clear(self):
        """Test clearing all cache entries"""
        self.cache.set('key1', 'value1', ttl=10)
        self.cache.set('key2', 'value2', ttl=10)
        
        self.cache.clear()
        
        self.assertIsNone(self.cache.get('key1'))
        self.assertIsNone(self.cache.get('key2'))
    
    def test_stats_tracking(self):
        """Test cache statistics tracking"""
        # Set some values
        self.cache.set('stats_key1', 'value1', ttl=10)
        self.cache.set('stats_key2', 'value2', ttl=10)
        
        # Generate hits and misses
        self.cache.get('stats_key1')  # hit
        self.cache.get('stats_key1')  # hit
        self.cache.get('nonexistent')  # miss
        
        stats = self.cache.get_stats()
        
        self.assertEqual(stats['hits'], 2)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['total_requests'], 3)
        self.assertEqual(stats['entries'], 2)
        self.assertAlmostEqual(stats['hit_rate_percent'], 66.67, places=1)
    
    def test_get_or_compute_cache_hit(self):
        """Test get_or_compute with cache hit"""
        # Set value
        self.cache.set('compute_key', 'cached_value', ttl=10)
        
        # Should return cached value without calling compute_fn
        compute_called = []
        
        def compute_fn():
            compute_called.append(True)
            return 'computed_value'
        
        result = self.cache.get_or_compute('compute_key', compute_fn, ttl=10)
        
        self.assertEqual(result, 'cached_value')
        self.assertEqual(len(compute_called), 0)  # Should not be called
    
    def test_get_or_compute_cache_miss(self):
        """Test get_or_compute with cache miss"""
        compute_called = []
        
        def compute_fn():
            compute_called.append(True)
            return 'computed_value'
        
        result = self.cache.get_or_compute('new_key', compute_fn, ttl=10)
        
        self.assertEqual(result, 'computed_value')
        self.assertEqual(len(compute_called), 1)  # Should be called once
        
        # Verify it's now cached
        result2 = self.cache.get('new_key')
        self.assertEqual(result2, 'computed_value')
    
    def test_complex_data_types(self):
        """Test caching complex data types"""
        test_data = {
            'list': [1, 2, 3],
            'dict': {'a': 1, 'b': 2},
            'nested': {'list': [{'x': 1}]}
        }
        
        self.cache.set('complex_key', test_data, ttl=10)
        result = self.cache.get('complex_key')
        
        self.assertEqual(result, test_data)
        self.assertEqual(result['list'], [1, 2, 3])
        self.assertEqual(result['dict']['a'], 1)
    
    def test_sanitize_key(self):
        """Test key sanitization for metrics"""
        # Keys with IDs should be sanitized
        key1 = '/api/servers/123/inventory'
        sanitized1 = self.cache._sanitize_key(key1)
        self.assertEqual(sanitized1, 'api/servers/inventory')
        
        # Keys without IDs should remain
        key2 = '/api/stats/overview'
        sanitized2 = self.cache._sanitize_key(key2)
        self.assertEqual(sanitized2, 'api/stats/overview')


class TestCacheSingleton(unittest.TestCase):
    """Test cache singleton pattern"""
    
    def test_get_cache_singleton(self):
        """Test that get_cache returns the same instance"""
        cache1 = get_cache()
        cache2 = get_cache()
        
        self.assertIs(cache1, cache2)
        
        # Set value in cache1
        cache1.set('singleton_test', 'value', ttl=10)
        
        # Should be accessible from cache2
        result = cache2.get('singleton_test')
        self.assertEqual(result, 'value')


if __name__ == '__main__':
    unittest.main()
