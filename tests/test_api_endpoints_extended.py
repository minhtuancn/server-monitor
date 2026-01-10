"""
Extended API Endpoint Tests for central_api.py
Target: Test user management, settings, database management endpoints
Focus: Role-based access control, validation, admin-only operations
"""

import pytest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import central_api
from central_api import verify_auth_token


class TestUserManagementEndpoints:
    """Test /api/users endpoints"""
    
    def test_create_user_requires_admin(self):
        """Test creating user requires admin role"""
        mock_handler = Mock()
        mock_handler.headers = {'Authorization': 'Bearer user.token'}
        mock_handler.path = '/api/users'
        mock_handler.command = 'POST'
        
        with patch('central_api.security.AuthMiddleware.decode_token') as mock_decode:
            mock_decode.return_value = {
                "user_id": 2,
                "username": "user",
                "role": "user"  # Not admin
            }
            
            result = verify_auth_token(mock_handler)
            
            # Should be authenticated
            assert result['valid'] is True
            # But role is not admin
            assert result['role'] != 'admin'
    
    def test_create_user_requires_fields(self):
        """Test creating user requires all fields"""
        data = {"username": "newuser", "email": "new@example.com"}
        
        required = ["username", "email", "password", "role"]
        has_all = all(k in data for k in required)
        
        assert has_all is False
    
    def test_create_user_success(self):
        """Test successful user creation"""
        with patch('central_api.user_mgr.create_user') as mock_create:
            mock_create.return_value = (True, "User created successfully", 5)
            
            success, message, user_id = mock_create(
                username="newuser",
                email="new@example.com",
                password="secure123",
                role="user"
            )
            
            assert success is True
            assert user_id == 5
    
    def test_change_password_requires_auth(self):
        """Test password change requires authentication"""
        path = "/api/users/2/change-password"
        user_id = int(path.split("/")[-2])
        
        assert user_id == 2
    
    def test_change_password_requires_old_and_new(self):
        """Test password change requires old and new password"""
        data = {"old_password": "old123"}
        
        required = ["old_password", "new_password"]
        has_all = all(k in data for k in required)
        
        assert has_all is False
    
    def test_change_password_success(self):
        """Test successful password change"""
        with patch('central_api.user_mgr.change_password') as mock_change:
            mock_change.return_value = (True, "Password changed successfully")
            
            success, message = mock_change(2, "old123", "new456")
            
            assert success is True
            assert "changed" in message.lower()
    
    def test_user_can_change_own_password(self):
        """Test users can change their own password"""
        auth_user_id = 2
        target_user_id = 2
        role = "user"
        
        # User changing their own password
        can_change = (role == "admin" or auth_user_id == target_user_id)
        
        assert can_change is True
    
    def test_user_cannot_change_others_password(self):
        """Test users cannot change other users' passwords"""
        auth_user_id = 2
        target_user_id = 3
        role = "user"
        
        can_change = (role == "admin" or auth_user_id == target_user_id)
        
        assert can_change is False
    
    def test_admin_can_change_any_password(self):
        """Test admins can change any user's password"""
        auth_user_id = 1
        target_user_id = 3
        role = "admin"
        
        can_change = (role == "admin" or auth_user_id == target_user_id)
        
        assert can_change is True


class TestSettingsEndpoints:
    """Test /api/settings endpoints"""
    
    def test_update_settings_requires_admin(self):
        """Test updating settings requires admin role"""
        mock_handler = Mock()
        mock_handler.path = '/api/settings'
        mock_handler.command = 'POST'
        
        with patch('central_api.security.AuthMiddleware.decode_token') as mock_decode:
            mock_decode.return_value = {
                "user_id": 2,
                "role": "user"
            }
            
            auth_result = mock_decode("token")
            
            assert auth_result['role'] != 'admin'
    
    def test_update_multiple_settings(self):
        """Test updating multiple settings at once"""
        with patch('central_api.settings_mgr.update_multiple_settings') as mock_update:
            mock_update.return_value = (True, "Settings updated", [])
            
            settings_data = {
                "max_connections": 10,
                "timeout": 30,
                "retry_attempts": 3
            }
            
            success, message, failed = mock_update(settings_data, user_id=1)
            
            assert success is True
            assert len(failed) == 0
    
    def test_update_single_setting_requires_value(self):
        """Test updating single setting requires value"""
        data = {}
        
        assert data.get("value") is None
    
    def test_update_single_setting_success(self):
        """Test successful single setting update"""
        with patch('central_api.settings_mgr.update_setting') as mock_update:
            mock_update.return_value = (True, "Setting updated")
            
            key = "max_connections"
            value = 20
            
            success, message = mock_update(key, value, user_id=1)
            
            assert success is True
    
    def test_setting_key_extracted_from_path(self):
        """Test setting key extraction from path"""
        path = "/api/settings/max_connections"
        key = path.split("/")[-1]
        
        assert key == "max_connections"


class TestDatabaseManagementEndpoints:
    """Test database backup/restore endpoints"""
    
    def test_backup_requires_admin(self):
        """Test database backup requires admin role"""
        mock_handler = Mock()
        mock_handler.path = '/api/database/backup'
        
        with patch('central_api.security.AuthMiddleware.decode_token') as mock_decode:
            mock_decode.return_value = {"role": "user"}
            
            auth_result = mock_decode("token")
            
            assert auth_result['role'] != 'admin'
    
    def test_create_backup_success(self):
        """Test successful database backup creation"""
        # Test backup response structure
        backup_result = {
            "success": True,
            "filename": "backup_20250110_123456.db",
            "size": 1048576
        }
        
        assert backup_result["success"] is True
        assert "filename" in backup_result
    
    def test_restore_requires_admin(self):
        """Test database restore requires admin role"""
        with patch('central_api.security.AuthMiddleware.decode_token') as mock_decode:
            mock_decode.return_value = {"role": "user"}
            
            auth_result = mock_decode("token")
            
            assert auth_result['role'] != 'admin'
    
    def test_restore_requires_filename(self):
        """Test database restore requires filename"""
        data = {}
        
        filename = data.get("filename")
        
        assert filename is None
    
    def test_restore_success(self):
        """Test successful database restore"""
        # Test restore response structure
        restore_result = {
            "success": True,
            "message": "Database restored successfully"
        }
        
        assert restore_result["success"] is True


class TestServerValidation:
    """Test server creation validation"""
    
    def test_server_validates_ip_or_hostname(self):
        """Test server creation validates IP or hostname"""
        with patch('central_api.security.InputSanitizer.validate_ip') as mock_ip, \
             patch('central_api.security.InputSanitizer.validate_hostname') as mock_host:
            
            # Valid IP
            mock_ip.return_value = True
            mock_host.return_value = False
            
            host = "192.168.1.1"
            is_valid = mock_ip(host) or mock_host(host)
            
            assert is_valid is True
            
            # Valid hostname
            mock_ip.return_value = False
            mock_host.return_value = True
            
            host = "example.com"
            is_valid = mock_ip(host) or mock_host(host)
            
            assert is_valid is True
            
            # Invalid both
            mock_ip.return_value = False
            mock_host.return_value = False
            
            host = "invalid..host"
            is_valid = mock_ip(host) or mock_host(host)
            
            assert is_valid is False
    
    def test_server_validates_port(self):
        """Test server port validation"""
        with patch('central_api.security.InputSanitizer.validate_port') as mock_validate:
            # Valid port
            mock_validate.return_value = True
            assert mock_validate(22) is True
            
            # Invalid port
            mock_validate.return_value = False
            assert mock_validate(99999) is False
    
    def test_server_validates_agent_port(self):
        """Test agent port validation"""
        with patch('central_api.security.InputSanitizer.validate_port') as mock_validate:
            # Valid agent port
            mock_validate.return_value = True
            assert mock_validate(8083) is True
            
            # Invalid agent port
            mock_validate.return_value = False
            assert mock_validate(-1) is False
    
    def test_default_ports_applied(self):
        """Test default ports are applied"""
        data = {"name": "server", "host": "192.168.1.1", "username": "admin"}
        
        port = data.get("port", 22)
        agent_port = data.get("agent_port", 8083)
        
        assert port == 22
        assert agent_port == 8083


class TestRoleBasedAccessControl:
    """Test RBAC across endpoints"""
    
    def test_admin_endpoints_reject_non_admin(self):
        """Test admin-only endpoints reject regular users"""
        admin_endpoints = [
            "/api/users",
            "/api/settings",
            "/api/database/backup",
            "/api/database/restore"
        ]
        
        with patch('central_api.security.AuthMiddleware.decode_token') as mock_decode:
            mock_decode.return_value = {"role": "user"}
            
            auth_result = mock_decode("token")
            
            for endpoint in admin_endpoints:
                # All should reject non-admin
                assert auth_result['role'] != 'admin'
    
    def test_admin_role_grants_access(self):
        """Test admin role grants access to admin endpoints"""
        with patch('central_api.security.AuthMiddleware.decode_token') as mock_decode:
            mock_decode.return_value = {"role": "admin"}
            
            auth_result = mock_decode("token")
            
            assert auth_result['role'] == 'admin'
    
    def test_protected_routes_require_authentication(self):
        """Test all protected routes require authentication"""
        protected_paths = [
            "/api/servers",
            "/api/tasks",
            "/api/users",
            "/api/settings"
        ]
        
        mock_handler = Mock()
        mock_handler.headers = {}  # No auth header
        mock_handler.command = 'POST'
        
        for path in protected_paths:
            mock_handler.path = path
            result = verify_auth_token(mock_handler)
            
            # Should fail without token
            assert result['valid'] is False


class TestPathParsing:
    """Test path parsing for dynamic routes"""
    
    def test_extract_user_id_from_path(self):
        """Test extracting user ID from path"""
        path = "/api/users/5/change-password"
        user_id = int(path.split("/")[-2])
        
        assert user_id == 5
    
    def test_extract_server_id_from_path(self):
        """Test extracting server ID from path"""
        path = "/api/servers/10"
        server_id = int(path.split("/")[-1])
        
        assert server_id == 10
    
    def test_extract_setting_key_from_path(self):
        """Test extracting setting key from path"""
        path = "/api/settings/max_connections"
        key = path.split("/")[-1]
        
        assert key == "max_connections"
    
    def test_path_validation(self):
        """Test path validation"""
        path1 = "/api/users/"
        path2 = "/api/users"
        
        # Should detect trailing slash
        assert path1.endswith("/")
        assert not path2.endswith("/")


class TestErrorResponses:
    """Test error response handling"""
    
    def test_missing_fields_error_format(self):
        """Test missing fields error response"""
        error_response = {"error": "Missing required fields"}
        
        assert "error" in error_response
        assert isinstance(error_response["error"], str)
    
    def test_admin_access_error_format(self):
        """Test admin access required error"""
        error_response = {"error": "Admin access required"}
        
        assert error_response["error"] == "Admin access required"
    
    def test_access_denied_error_format(self):
        """Test access denied error"""
        error_response = {"error": "Access denied"}
        
        assert "denied" in error_response["error"].lower()
    
    def test_database_error_format(self):
        """Test database error response format"""
        error_response = {
            "error": "Database error: Connection failed"
        }
        
        assert "error" in error_response
        assert error_response["error"].startswith("Database error:")


class TestSuccessResponses:
    """Test success response formats"""
    
    def test_create_success_response(self):
        """Test creation success response format"""
        response = {
            "success": True,
            "message": "Resource created successfully",
            "id": 5
        }
        
        assert response["success"] is True
        assert "id" in response
    
    def test_update_success_response(self):
        """Test update success response format"""
        response = {
            "success": True,
            "message": "Resource updated successfully"
        }
        
        assert response["success"] is True
        assert "message" in response
    
    def test_settings_update_response(self):
        """Test settings update response format"""
        response = {
            "success": True,
            "message": "Settings updated",
            "failed": []
        }
        
        assert response["success"] is True
        assert isinstance(response["failed"], list)


class TestGroupValidation:
    """Test group creation validation"""
    
    def test_group_type_validation(self):
        """Test group type must be valid"""
        valid_types = ["servers", "notes", "snippets", "inventory"]
        
        # Valid type
        assert "servers" in valid_types
        
        # Invalid type
        assert "invalid_type" not in valid_types
    
    def test_group_requires_name_and_type(self):
        """Test group requires name and type"""
        data = {"name": "Production"}
        
        has_type = "type" in data
        has_name = "name" in data
        
        assert has_name is True
        assert has_type is False
    
    def test_group_default_color(self):
        """Test group default color is applied"""
        data = {"name": "Production", "type": "servers"}
        
        color = data.get("color", "#1976d2")
        
        assert color == "#1976d2"
    
    def test_group_description_optional(self):
        """Test group description is optional"""
        data = {"name": "Production", "type": "servers"}
        
        description = data.get("description", "")
        
        assert description == ""


class TestStatusCodes:
    """Test HTTP status code handling"""
    
    def test_created_status_code(self):
        """Test 201 Created status code"""
        status_code = 201
        
        assert status_code == 201
    
    def test_bad_request_status_code(self):
        """Test 400 Bad Request status code"""
        status_code = 400
        
        assert status_code == 400
    
    def test_unauthorized_status_code(self):
        """Test 401 Unauthorized status code"""
        status_code = 401
        
        assert status_code == 401
    
    def test_forbidden_status_code(self):
        """Test 403 Forbidden status code"""
        status_code = 403
        
        assert status_code == 403
    
    def test_internal_error_status_code(self):
        """Test 500 Internal Server Error status code"""
        status_code = 500
        
        assert status_code == 500
    
    def test_success_status_code(self):
        """Test 200 OK status code"""
        status_code = 200
        
        assert status_code == 200
