#!/usr/bin/env python3

"""
Pytest configuration and fixtures for server-monitor tests
Handles test setup, teardown, and common test utilities
"""

import sys
import os
import pytest
import requests

# Set CI environment to disable rate limiting for tests
os.environ['CI'] = 'true'

# Add backend directory to path so we can import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import after setting CI env var so security.py reads the flag
from rate_limiter import get_rate_limiter
import security

# Test configuration
BASE_URL = os.getenv('TEST_BASE_URL', 'http://localhost:9083')


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """
    Reset rate limiter and security IP blocks before each test
    
    This fixture runs automatically before each test to ensure
    that rate limiting and IP blocks from previous tests don't
    affect the current test. Tests that legitimately need to
    test rate limiting behavior can use the @pytest.mark.no_reset
    marker to disable auto-reset.
    
    Note: Rate limiting is effectively disabled when CI=true env var
    is set (which it is for testing), but we still reset the counters
    for cleanliness.
    """
    # Always use local reset since it's more reliable
    _local_reset_rate_limiter()
    
    yield
    
    # Cleanup after test (optional, for consistency)
    _local_reset_rate_limiter()


def _local_reset_rate_limiter():
    """
    Reset rate limiter locally (fallback if API server not running)
    """
    # Reset global rate limiter state
    rate_limiter = get_rate_limiter()
    if hasattr(rate_limiter, 'clear_all'):
        rate_limiter.clear_all()
    
    # Reset security rate limiting and IP blocks
    # These are used by security.RateLimiter
    if hasattr(security, 'clear_rate_limit_state'):
        try:
            security.clear_rate_limit_state()
        except:
            # Fallback for older versions
            security.login_attempts.clear()
            security.blocked_ips.clear()
            if hasattr(security, 'request_counts'):
                security.request_counts.clear()
    else:
        # Fallback for older versions
        security.login_attempts.clear()
        security.blocked_ips.clear()
        if hasattr(security, 'request_counts'):
            security.request_counts.clear()


@pytest.fixture
def rate_limiter_with_state():
    """
    Get rate limiter without resetting (for rate limit tests)
    
    Use this fixture when you want to test rate limiting behavior
    and need to preserve state across requests.
    
    Example:
        def test_rate_limiting(rate_limiter_with_state):
            # Rate limiter state is preserved for this test
            pass
    """
    return get_rate_limiter()


@pytest.fixture(scope="session")
def test_base_url():
    """Get the base URL for API tests"""
    return os.getenv('TEST_BASE_URL', 'http://localhost:9083')


@pytest.fixture(scope="session")
def test_credentials():
    """Get test user credentials"""
    return {
        'username': os.getenv('TEST_USER', 'admin'),
        'password': os.getenv('TEST_PASS', 'admin123')
    }
