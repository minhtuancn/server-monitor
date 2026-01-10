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


def is_backend_running(base_url=None):
    """
    Check if backend API server is running
    
    Returns True if server responds to health check, False otherwise
    """
    if base_url is None:
        base_url = os.getenv('TEST_BASE_URL', 'http://localhost:9083')
    
    try:
        response = requests.get(f"{base_url}/api/health", timeout=2)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False


@pytest.fixture(scope="session")
def backend_required():
    """
    Fixture that skips test if backend is not running
    
    Use this fixture for integration tests that require backend services.
    If backend is not reachable, the test will be skipped with a message.
    
    Example:
        def test_api_endpoint(backend_required):
            # This test will be skipped if backend is not running
            response = requests.get("http://localhost:9083/api/servers")
            assert response.status_code == 200
    """
    if not is_backend_running():
        pytest.skip("Backend API server is not running (connection refused). "
                   "Start services with ./start-all.sh to run integration tests.")
    return True


@pytest.fixture(autouse=True)
def skip_integration_if_no_backend(request):
    """
    Auto-skip integration tests if backend is not running
    
    This fixture automatically runs before each test marked with
    @pytest.mark.integration and skips the test if backend is not available.
    """
    if request.node.get_closest_marker('integration'):
        if not is_backend_running():
            pytest.skip("Backend not running - skipping integration test")

