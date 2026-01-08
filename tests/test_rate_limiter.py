#!/usr/bin/env python3

"""
Unit tests for rate_limiter module
"""

import unittest
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from rate_limiter import RateLimiter, get_rate_limiter, check_endpoint_rate_limit, RATE_LIMITS


class TestRateLimiter(unittest.TestCase):
    """Test cases for RateLimiter"""
    
    def setUp(self):
        """Set up test rate limiter"""
        self.limiter = RateLimiter()
    
    def test_allow_within_limit(self):
        """Test that requests within limit are allowed"""
        allowed, info = self.limiter.check_rate_limit('test:user1', max_requests=5, window_seconds=60)
        
        self.assertTrue(allowed)
        self.assertTrue(info['allowed'])
        self.assertEqual(info['limit'], 5)
        self.assertEqual(info['remaining'], 4)  # One token consumed
    
    def test_block_when_exceeded(self):
        """Test that requests are blocked when limit exceeded"""
        key = 'test:user2'
        max_requests = 3
        
        # Make requests up to limit
        for i in range(max_requests):
            allowed, info = self.limiter.check_rate_limit(key, max_requests=max_requests, window_seconds=60)
            self.assertTrue(allowed, f"Request {i+1} should be allowed")
        
        # Next request should be blocked
        allowed, info = self.limiter.check_rate_limit(key, max_requests=max_requests, window_seconds=60)
        
        self.assertFalse(allowed)
        self.assertFalse(info['allowed'])
        self.assertEqual(info['remaining'], 0)
        self.assertGreater(info['retry_after'], 0)
    
    def test_token_bucket_refill(self):
        """Test that tokens refill over time"""
        key = 'test:user3'
        max_requests = 10
        window_seconds = 1  # 1 second window for fast test
        
        # Consume all tokens
        for _ in range(max_requests):
            allowed, info = self.limiter.check_rate_limit(key, max_requests=max_requests, window_seconds=window_seconds)
            self.assertTrue(allowed)
        
        # Should be blocked now
        allowed, info = self.limiter.check_rate_limit(key, max_requests=max_requests, window_seconds=window_seconds)
        self.assertFalse(allowed)
        
        # Wait for tokens to refill
        time.sleep(0.2)  # 20% of window = 2 tokens
        
        # Should have tokens now
        allowed, info = self.limiter.check_rate_limit(key, max_requests=max_requests, window_seconds=window_seconds)
        self.assertTrue(allowed)
    
    def test_different_keys_independent(self):
        """Test that different keys have independent limits"""
        max_requests = 3
        
        # User1 consumes all tokens
        for _ in range(max_requests):
            allowed, info = self.limiter.check_rate_limit('test:user_a', max_requests=max_requests, window_seconds=60)
            self.assertTrue(allowed)
        
        # User1 should be blocked
        allowed, info = self.limiter.check_rate_limit('test:user_a', max_requests=max_requests, window_seconds=60)
        self.assertFalse(allowed)
        
        # User2 should still have tokens
        allowed, info = self.limiter.check_rate_limit('test:user_b', max_requests=max_requests, window_seconds=60)
        self.assertTrue(allowed)
    
    def test_reset(self):
        """Test resetting rate limit for a key"""
        key = 'test:user4'
        max_requests = 2
        
        # Consume all tokens
        for _ in range(max_requests):
            self.limiter.check_rate_limit(key, max_requests=max_requests, window_seconds=60)
        
        # Should be blocked
        allowed, info = self.limiter.check_rate_limit(key, max_requests=max_requests, window_seconds=60)
        self.assertFalse(allowed)
        
        # Reset
        self.limiter.reset(key)
        
        # Should be allowed again
        allowed, info = self.limiter.check_rate_limit(key, max_requests=max_requests, window_seconds=60)
        self.assertTrue(allowed)
    
    def test_clear_all(self):
        """Test clearing all rate limits"""
        # Set up limits for multiple keys
        self.limiter.check_rate_limit('test:user5', max_requests=5, window_seconds=60)
        self.limiter.check_rate_limit('test:user6', max_requests=5, window_seconds=60)
        
        # Clear all
        self.limiter.clear_all()
        
        # Both should have fresh limits
        allowed1, info1 = self.limiter.check_rate_limit('test:user5', max_requests=5, window_seconds=60)
        allowed2, info2 = self.limiter.check_rate_limit('test:user6', max_requests=5, window_seconds=60)
        
        self.assertTrue(allowed1)
        self.assertTrue(allowed2)
        self.assertEqual(info1['remaining'], 4)
        self.assertEqual(info2['remaining'], 4)
    
    def test_cleanup_old_buckets(self):
        """Test cleanup of old buckets"""
        # Create some buckets
        self.limiter.check_rate_limit('test:old1', max_requests=5, window_seconds=60)
        self.limiter.check_rate_limit('test:old2', max_requests=5, window_seconds=60)
        
        # Manually set last_update to old time
        for bucket in self.limiter._buckets.values():
            bucket.last_update = time.time() - 7200  # 2 hours ago
        
        # Clean up buckets older than 1 hour
        self.limiter.cleanup_old_buckets(max_age_seconds=3600)
        
        # Buckets should be removed
        self.assertEqual(len(self.limiter._buckets), 0)
    
    def test_rate_info_structure(self):
        """Test that rate info has correct structure"""
        allowed, info = self.limiter.check_rate_limit('test:user7', max_requests=10, window_seconds=60)
        
        self.assertIn('allowed', info)
        self.assertIn('remaining', info)
        self.assertIn('limit', info)
        self.assertIn('reset_at', info)
        self.assertIn('retry_after', info)
        
        self.assertEqual(info['limit'], 10)
        self.assertIsInstance(info['remaining'], int)
        self.assertIsInstance(info['reset_at'], int)
        self.assertIsInstance(info['retry_after'], int)


class TestRateLimiterSingleton(unittest.TestCase):
    """Test rate limiter singleton pattern"""
    
    def test_get_rate_limiter_singleton(self):
        """Test that get_rate_limiter returns the same instance"""
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()
        
        self.assertIs(limiter1, limiter2)


class TestEndpointRateLimits(unittest.TestCase):
    """Test endpoint-specific rate limits"""
    
    def setUp(self):
        """Set up and clear rate limiter"""
        self.limiter = get_rate_limiter()
        self.limiter.clear_all()
    
    def test_inventory_refresh_rate_limit(self):
        """Test inventory refresh rate limit"""
        self.assertIn('inventory_refresh', RATE_LIMITS)
        config = RATE_LIMITS['inventory_refresh']
        
        self.assertEqual(config['max_requests'], 10)
        self.assertEqual(config['window_seconds'], 60)
        self.assertEqual(config['key_prefix'], 'inventory:server')
    
    def test_task_create_rate_limit(self):
        """Test task create rate limit"""
        self.assertIn('task_create', RATE_LIMITS)
        config = RATE_LIMITS['task_create']
        
        self.assertEqual(config['max_requests'], 20)
        self.assertEqual(config['window_seconds'], 60)
        self.assertEqual(config['key_prefix'], 'task:user')
    
    def test_webhook_test_rate_limit(self):
        """Test webhook test rate limit"""
        self.assertIn('webhook_test', RATE_LIMITS)
        config = RATE_LIMITS['webhook_test']
        
        self.assertEqual(config['max_requests'], 10)
        self.assertEqual(config['window_seconds'], 60)
        self.assertEqual(config['key_prefix'], 'webhook:user')
    
    def test_check_endpoint_rate_limit_allowed(self):
        """Test check_endpoint_rate_limit allows requests within limit"""
        allowed, info = check_endpoint_rate_limit('inventory_refresh', 'server123')
        
        self.assertTrue(allowed)
        self.assertEqual(info['limit'], 10)
    
    def test_check_endpoint_rate_limit_blocked(self):
        """Test check_endpoint_rate_limit blocks after limit"""
        server_id = 'server456'
        
        # Make 10 requests (the limit)
        for _ in range(10):
            allowed, info = check_endpoint_rate_limit('inventory_refresh', server_id)
            self.assertTrue(allowed)
        
        # 11th request should be blocked
        allowed, info = check_endpoint_rate_limit('inventory_refresh', server_id)
        self.assertFalse(allowed)
    
    def test_check_endpoint_rate_limit_unknown_endpoint(self):
        """Test unknown endpoint has no rate limit"""
        allowed, info = check_endpoint_rate_limit('unknown_endpoint', 'id123')
        
        # Should always be allowed for unknown endpoints
        self.assertTrue(allowed)
        self.assertEqual(info['limit'], 999)


if __name__ == '__main__':
    unittest.main()
