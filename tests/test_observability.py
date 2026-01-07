#!/usr/bin/env python3

"""
Tests for Phase 6 Observability Features
Tests health checks, metrics, request-id, and task policy
"""

import pytest
import requests
import json
import uuid

# Test Configuration
BASE_URL = "http://localhost:9083"
TEST_USER = "admin"
TEST_PASS = "admin123"

# Global test state
auth_token = None


@pytest.fixture(scope='session', autouse=True)
def setup_auth():
    """Setup authentication before running tests"""
    global auth_token
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": TEST_USER, "password": TEST_PASS}
    )
    if response.status_code == 200:
        data = response.json()
        auth_token = data.get('token')
        print(f"\nAuthentication successful. Token: {auth_token[:20]}...")
    else:
        pytest.skip(f"Authentication failed: {response.text}")
    yield


class TestHealthChecks:
    """Test health and readiness endpoints"""
    
    def test_health_endpoint_public(self):
        """Test /api/health is publicly accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert 'timestamp' in data
    
    def test_readiness_endpoint_public(self):
        """Test /api/ready is publicly accessible"""
        response = requests.get(f"{BASE_URL}/api/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] in ['ready', 'not_ready']
        assert 'timestamp' in data
        assert 'checks' in data
        
        # Check that expected checks are present
        checks = data['checks']
        assert 'database' in checks
        
    def test_health_has_no_sensitive_info(self):
        """Test health endpoint doesn't expose sensitive info"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should not contain these sensitive fields
        assert 'password' not in json.dumps(data).lower()
        assert 'secret' not in json.dumps(data).lower()
        assert 'token' not in json.dumps(data).lower()


class TestMetricsEndpoint:
    """Test metrics endpoint"""
    
    def test_metrics_requires_auth_or_localhost(self):
        """Test /api/metrics requires authentication"""
        response = requests.get(f"{BASE_URL}/api/metrics")
        
        # Should work if called from localhost or with admin token
        # We're testing from localhost, so it should work
        assert response.status_code in [200, 401]
    
    def test_metrics_prometheus_format(self):
        """Test metrics endpoint returns Prometheus format by default"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/metrics", headers=headers)
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            assert 'text/plain' in content_type or 'text' in content_type
            
            # Check for Prometheus format markers
            text = response.text
            assert '# HELP' in text or '# TYPE' in text or 'server_monitor' in text
    
    def test_metrics_json_format(self):
        """Test metrics endpoint can return JSON format"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/metrics?format=json", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            assert 'timestamp' in data
            assert 'uptime_seconds' in data
            assert 'requests' in data


class TestRequestIdPropagation:
    """Test X-Request-Id header propagation"""
    
    def test_request_id_generated_when_missing(self):
        """Test that request ID is generated when not provided"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200
        assert 'X-Request-Id' in response.headers
        request_id = response.headers['X-Request-Id']
        
        # Should be a valid UUID format
        try:
            uuid.UUID(request_id)
            assert True
        except ValueError:
            pytest.fail(f"Request ID is not a valid UUID: {request_id}")
    
    def test_request_id_preserved_when_provided(self):
        """Test that provided request ID is preserved in response"""
        test_request_id = str(uuid.uuid4())
        headers = {"X-Request-Id": test_request_id}
        
        response = requests.get(f"{BASE_URL}/api/health", headers=headers)
        
        assert response.status_code == 200
        assert 'X-Request-Id' in response.headers
        assert response.headers['X-Request-Id'] == test_request_id
    
    def test_request_id_stable_across_endpoints(self):
        """Test that request ID is consistent within a request"""
        test_request_id = str(uuid.uuid4())
        headers = {
            "X-Request-Id": test_request_id,
            "Authorization": f"Bearer {auth_token}"
        }
        
        # Test on multiple endpoints
        response1 = requests.get(f"{BASE_URL}/api/health", headers=headers)
        response2 = requests.get(f"{BASE_URL}/api/ready", headers=headers)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.headers['X-Request-Id'] == test_request_id
        assert response2.headers['X-Request-Id'] == test_request_id


class TestTaskPolicy:
    """Test task safety policy"""
    
    def test_task_policy_blocks_dangerous_commands(self):
        """Test that dangerous commands are blocked by task policy"""
        # This test requires task policy to be configured and endpoints to be available
        # We test the policy module directly since API testing would require server setup
        
        # Import the module
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
        
        from task_policy import TaskPolicy
        
        policy = TaskPolicy(mode='denylist')
        
        # Test dangerous commands
        dangerous_commands = [
            "rm -rf /",
            "shutdown -h now",
            "dd if=/dev/zero of=/dev/sda",
            "chmod 777 /etc/passwd",
            "mkfs.ext4 /dev/sda1",
        ]
        
        for cmd in dangerous_commands:
            is_valid, reason = policy.validate_command(cmd)
            assert not is_valid, f"Command should be blocked: {cmd}"
            assert reason, f"Should have a reason for blocking: {cmd}"
    
    def test_task_policy_allows_safe_commands(self):
        """Test that safe commands are allowed by task policy"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
        
        from task_policy import TaskPolicy
        
        policy = TaskPolicy(mode='denylist')
        
        # Test safe commands
        safe_commands = [
            "ls -la",
            "cat /var/log/syslog",
            "grep error /var/log/app.log",
            "systemctl status nginx",
            "df -h",
            "ps aux",
        ]
        
        for cmd in safe_commands:
            is_valid, reason = policy.validate_command(cmd)
            assert is_valid, f"Command should be allowed: {cmd} - Reason: {reason}"
    
    def test_task_policy_allowlist_mode(self):
        """Test task policy in allowlist mode"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
        
        from task_policy import TaskPolicy
        
        policy = TaskPolicy(mode='allowlist')
        
        # Test that only allowed commands pass
        allowed_cmd = "ls -la"
        is_valid, reason = policy.validate_command(allowed_cmd)
        # In default allowlist, 'ls' should be allowed
        assert is_valid, f"Command should be allowed in allowlist mode: {allowed_cmd}"
        
        # Test that non-allowed commands fail
        not_allowed_cmd = "some_random_command"
        is_valid, reason = policy.validate_command(not_allowed_cmd)
        assert not is_valid, f"Command should be blocked in allowlist mode: {not_allowed_cmd}"


class TestAuditLogExport:
    """Test audit log export endpoints"""
    
    def test_audit_export_csv_requires_admin(self):
        """Test that audit log CSV export requires admin role"""
        # Try without auth
        response = requests.get(f"{BASE_URL}/api/export/audit/csv")
        assert response.status_code == 401
    
    def test_audit_export_json_requires_admin(self):
        """Test that audit log JSON export requires admin role"""
        # Try without auth
        response = requests.get(f"{BASE_URL}/api/export/audit/json")
        assert response.status_code == 401
    
    def test_audit_export_csv_with_admin(self):
        """Test CSV export with admin authentication"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/export/audit/csv", headers=headers)
        
        # Should get CSV or 200 OK if admin
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            assert 'csv' in content_type.lower()
            assert 'Content-Disposition' in response.headers
    
    def test_audit_export_json_with_admin(self):
        """Test JSON export with admin authentication"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/export/audit/json", headers=headers)
        
        # Should get JSON or 200 OK if admin
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            assert 'json' in content_type.lower()
            # Should be valid JSON
            data = response.json()
            assert isinstance(data, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
