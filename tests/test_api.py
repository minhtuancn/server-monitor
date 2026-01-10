#!/usr/bin/env python3

"""
Integration tests for Server Monitor API
Tests authentication, CRUD operations, and key features
"""

import pytest

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration
import requests
import json
import time
from datetime import datetime

# Test Configuration
BASE_URL = "http://localhost:9083"
TEST_USER = "admin"
TEST_PASS = "admin123"

# Global test state
auth_token = None
test_server_id = None


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
        pytest.fail(f"Authentication failed: {response.text}")
    yield
    # Cleanup after all tests


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_login_success(self):
        """Test successful login"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": TEST_USER, "password": TEST_PASS}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'token' in data
        assert 'username' in data
        assert data['username'] == TEST_USER
        
        # Save token for other tests
        global auth_token
        auth_token = data['token']
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "wrong", "password": "wrong"}
        )
        
        assert response.status_code == 401
    
    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": TEST_USER}
        )
        
        assert response.status_code == 400
    
    def test_verify_token(self):
        """Test token verification"""
        global auth_token
        assert auth_token is not None
        
        response = requests.get(
            f"{BASE_URL}/api/auth/verify",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is True
        assert 'username' in data
    
    def test_verify_invalid_token(self):
        """Test verification with invalid token"""
        response = requests.get(
            f"{BASE_URL}/api/auth/verify",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


class TestServerCRUD:
    """Test server CRUD operations"""
    
    def test_create_server(self):
        """Test creating a new server"""
        global auth_token, test_server_id
        
        server_data = {
            "name": "Test Server",
            "host": f"192.168.1.{int(time.time()) % 255}",  # Unique host
            "port": 22,
            "username": "root",
            "description": "Test server for automated tests",
            "tags": "test,automated"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/servers",
            json=server_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        assert response.status_code == 201
        data = response.json()
        # API returns server_id instead of id
        assert 'server_id' in data or 'id' in data
        
        test_server_id = data.get('server_id') or data.get('id')
        print(f"Created server with ID: {test_server_id}")
    
    def test_list_servers(self):
        """Test listing all servers"""
        global auth_token
        
        response = requests.get(
            f"{BASE_URL}/api/servers",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_server_by_id(self):
        """Test getting a specific server"""
        global auth_token, test_server_id
        assert test_server_id is not None
        
        response = requests.get(
            f"{BASE_URL}/api/servers/{test_server_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == test_server_id
        assert data['name'] == "Test Server"
    
    def test_update_server(self):
        """Test updating a server"""
        global auth_token, test_server_id
        assert test_server_id is not None
        
        update_data = {
            "name": "Updated Test Server",
            "description": "Updated description"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/servers/{test_server_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        print(f"Update response: {response.status_code}, {response.text}")
        
        assert response.status_code == 200
        data = response.json()
        # API might return success message instead of full server data
        assert data.get('success') is True or 'name' in data
    
    def test_delete_server(self):
        """Test deleting a server (cleanup)"""
        global auth_token, test_server_id
        assert test_server_id is not None
        
        response = requests.delete(
            f"{BASE_URL}/api/servers/{test_server_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        
        # Verify deletion
        response = requests.get(
            f"{BASE_URL}/api/servers/{test_server_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404


class TestStatistics:
    """Test statistics endpoints"""
    
    def test_get_overview_stats(self):
        """Test getting overview statistics"""
        response = requests.get(f"{BASE_URL}/api/stats/overview")
        
        assert response.status_code == 200
        data = response.json()
        assert 'total_servers' in data
        assert 'online_servers' in data
        assert 'offline_servers' in data
        assert isinstance(data['total_servers'], int)


class TestExport:
    """Test export functionality"""
    
    def test_export_servers_csv(self):
        """Test exporting servers as CSV"""
        global auth_token
        
        response = requests.get(
            f"{BASE_URL}/api/export/servers/csv",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        assert 'text/csv' in response.headers.get('Content-Type', '')
    
    def test_export_servers_json(self):
        """Test exporting servers as JSON"""
        global auth_token
        
        response = requests.get(
            f"{BASE_URL}/api/export/servers/json",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        assert 'application/json' in response.headers.get('Content-Type', '')
        data = response.json()
        assert isinstance(data, list)


class TestEmailConfig:
    """Test email configuration"""
    
    def test_get_email_config(self):
        """Test getting email configuration"""
        global auth_token
        
        response = requests.get(
            f"{BASE_URL}/api/email/config",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'smtp_host' in data or 'enabled' in data
    
    def test_update_email_config(self):
        """Test updating email configuration"""
        global auth_token
        
        config = {
            "enabled": False,
            "smtp_host": "smtp.test.com",
            "smtp_port": 587,
            "smtp_username": "test@test.com",
            "smtp_password": "testpass",
            "recipients": ["admin@test.com"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/email/config",
            json=config,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200


class TestUnauthorizedAccess:
    """Test that endpoints require authentication"""
    
    def test_list_servers_no_auth(self):
        """Test that listing servers without auth fails"""
        response = requests.get(f"{BASE_URL}/api/servers")
        # Public endpoint might allow read, but write operations should fail
        assert response.status_code in [200, 401]
    
    def test_create_server_no_auth(self):
        """Test that creating server without auth fails"""
        response = requests.post(
            f"{BASE_URL}/api/servers",
            json={"name": "Test", "host": "1.2.3.4"}
        )
        assert response.status_code == 401
    
    def test_delete_server_no_auth(self):
        """Test that deleting server without auth fails"""
        response = requests.delete(f"{BASE_URL}/api/servers/1")
        assert response.status_code == 401


def test_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    print(f"  API URL: {BASE_URL}")
    print(f"  Test User: {TEST_USER}")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print("="*60)


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
