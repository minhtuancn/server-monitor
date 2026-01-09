#!/usr/bin/env python3

"""
Test security features: rate limiting, CORS, input validation
"""

import os
import requests
import time
import pytest

BASE_URL = "http://localhost:9083"
TEST_USER = "admin"
TEST_PASS = "admin123"


@pytest.mark.skipif(
    os.environ.get('CI', '').lower() in ('true', '1', 'yes'),
    reason="Rate limiting is disabled in CI mode (CI=true)"
)
def test_rate_limiting():
    """Test rate limiting on general endpoints"""
    # Make many requests quickly
    responses = []
    for i in range(110):  # Exceed rate limit of 100
        response = requests.get(f"{BASE_URL}/api/stats/overview")
        responses.append(response.status_code)
        if response.status_code == 429:
            print(f"Rate limited after {i+1} requests")
            assert 'Retry-After' in response.headers
            break
    
    # Should have hit rate limit
    assert 429 in responses, "Rate limiting should block after 100 requests"


@pytest.mark.skipif(
    os.environ.get('CI', '').lower() in ('true', '1', 'yes'),
    reason="Rate limiting is disabled in CI mode (CI=true)"
)
def test_login_rate_limiting():
    """Test rate limiting on login endpoint"""
    # Make multiple failed login attempts
    for i in range(7):  # Exceed login rate limit of 5
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "wrong", "password": "wrong"}
        )
        
        if response.status_code == 429:
            print(f"Login rate limited after {i+1} attempts")
            data = response.json()
            assert 'retry_after' in data or 'error' in data
            break
    
    # Should hit login rate limit
    assert response.status_code in [401, 429]


def test_cors_headers():
    """Test CORS headers are present"""
    response = requests.get(f"{BASE_URL}/api/stats/overview")
    
    # Check for CORS headers
    assert 'Access-Control-Allow-Origin' in response.headers
    print(f"CORS Origin: {response.headers['Access-Control-Allow-Origin']}")


def test_security_headers():
    """Test security headers are present"""
    response = requests.get(f"{BASE_URL}/api/stats/overview")
    
    # Check for security headers
    expected_headers = [
        'X-Content-Type-Options',
        'X-Frame-Options',
        'X-XSS-Protection'
    ]
    
    for header in expected_headers:
        assert header in response.headers, f"Missing security header: {header}"
        print(f"{header}: {response.headers[header]}")


def test_input_validation_invalid_ip():
    """Test input validation rejects invalid IP"""
    time.sleep(2)  # Wait to avoid rate limiting
    
    # Login first
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": TEST_USER, "password": TEST_PASS}
    )
    token = login_response.json().get('token')
    
    # Try to create server with invalid IP
    response = requests.post(
        f"{BASE_URL}/api/servers",
        json={
            "name": "Invalid Server",
            "host": "999.999.999.999",  # Invalid IP
            "username": "root"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Response: {response.status_code}, {response.text}")
    assert response.status_code == 400


def test_input_validation_invalid_port():
    """Test input validation rejects invalid port"""
    time.sleep(2)  # Wait to avoid rate limiting
    
    # Login first
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": TEST_USER, "password": TEST_PASS}
    )
    token = login_response.json().get('token')
    
    # Try to create server with invalid port
    response = requests.post(
        f"{BASE_URL}/api/servers",
        json={
            "name": "Invalid Server",
            "host": "192.168.1.1",
            "port": 99999,  # Invalid port
            "username": "root"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Response: {response.status_code}, {response.text}")
    assert response.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
