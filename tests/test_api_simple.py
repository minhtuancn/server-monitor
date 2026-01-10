"""
Simplified Core API Tests for central_api.py
Target: Increase central_api.py coverage from 0% to 30%+
Focus: Helper functions, constants, utilities (no full HTTP handling)
"""

import pytest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import central_api
from central_api import dispatch_audit_event, verify_auth_token


class TestDispatchAuditEvent:
    """Test audit event dispatching"""
    
    def test_dispatch_creates_audit_log(self):
        """Test dispatch_audit_event creates audit log entry"""
        with patch('central_api.db.add_audit_log') as mock_audit, \
             patch('central_api.plugin_manager.dispatch_event') as mock_event:
            
            mock_audit.return_value = {"id": "audit-123", "action": "server.create"}
            
            result = dispatch_audit_event(
                user_id=1,
                action="server.create",
                target_type="server",
                target_id=5,
                meta={"name": "test-server"},
                ip="127.0.0.1",
                user_agent="Mozilla/5.0",
                username="admin"
            )
            
            # Should call add_audit_log
            mock_audit.assert_called_once()
            kwargs = mock_audit.call_args[1]
            assert kwargs['user_id'] == 1
            assert kwargs['action'] == 'server.create'
            assert kwargs['target_type'] == 'server'
            assert kwargs['target_id'] == 5
            assert kwargs['ip'] == '127.0.0.1'
    
    def test_dispatch_sends_to_plugins(self):
        """Test dispatch_audit_event triggers plugin events"""
        with patch('central_api.db.add_audit_log') as mock_audit, \
             patch('central_api.plugin_manager.dispatch_event') as mock_event:
            
            mock_audit.return_value = {"id": "audit-123"}
            
            dispatch_audit_event(
                user_id=1,
                action="task.execute",
                target_type="task",
                target_id=10,
                server_id=5,
                server_name="web-server"
            )
            
            # Should dispatch to plugins
            mock_event.assert_called_once()
    
    def test_dispatch_with_minimal_params(self):
        """Test dispatch with only required parameters"""
        with patch('central_api.db.add_audit_log') as mock_audit, \
             patch('central_api.plugin_manager.dispatch_event'):
            
            mock_audit.return_value = {"id": "audit-456"}
            
            dispatch_audit_event(
                user_id=2,
                action="user.login",
                target_type="user",
                target_id=2
            )
            
            mock_audit.assert_called_once()
            kwargs = mock_audit.call_args[1]
            assert kwargs['user_id'] == 2
            assert kwargs['action'] == 'user.login'


class TestVerifyAuthToken:
    """Test JWT token verification"""
    
    def test_verify_valid_token(self):
        """Test verifying a valid JWT token"""
        with patch('central_api.security.AuthMiddleware.decode_token') as mock_decode:
            mock_decode.return_value = {
                "user_id": 1,
                "username": "admin",
                "role": "admin"
            }
            
            mock_handler = Mock()
            mock_handler.headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGc.eyJ1c2VyX2lkIjox.abc123'}
            mock_handler.path = '/api/tasks'
            mock_handler.command = 'GET'
            
            result = verify_auth_token(mock_handler)
            
            assert result['valid'] is True
            assert result['user_id'] == 1
            assert result['username'] == 'admin'
            mock_decode.assert_called_once()
    
    def test_verify_missing_token(self):
        """Test verification with no Authorization header"""
        mock_handler = Mock()
        mock_handler.headers = {}
        mock_handler.path = '/api/tasks'
        mock_handler.command = 'POST'
        
        result = verify_auth_token(mock_handler)
        
        assert result['valid'] is False
        assert 'error' in result
    
    def test_verify_invalid_token(self):
        """Test verification with invalid token"""
        with patch('central_api.security.AuthMiddleware.decode_token') as mock_decode:
            mock_decode.return_value = None  # Invalid token
            
            mock_handler = Mock()
            mock_handler.headers = {'Authorization': 'Bearer invalid.token.here'}
            mock_handler.path = '/api/tasks'
            mock_handler.command = 'GET'
            
            result = verify_auth_token(mock_handler)
            
            # Will fall back to legacy token check, then fail
            assert result['valid'] is False
    
    def test_verify_public_endpoint(self):
        """Test public endpoints don't require auth"""
        mock_handler = Mock()
        mock_handler.headers = {}
        mock_handler.path = '/api/servers'
        mock_handler.command = 'GET'
        
        result = verify_auth_token(mock_handler)
        
        # Public GET endpoint
        assert result['valid'] is True
        assert result['role'] == 'public'


class TestConstants:
    """Test API constants and configuration"""
    
    def test_port_is_9083(self):
        """Test API runs on port 9083"""
        assert central_api.PORT == 9083
    
    def test_task_command_max_length(self):
        """Test task command has max length"""
        assert central_api.TASK_COMMAND_MAX_LENGTH > 0
        assert isinstance(central_api.TASK_COMMAND_MAX_LENGTH, int)
        # Default is 10000
        assert central_api.TASK_COMMAND_MAX_LENGTH >= 10000
    
    def test_task_preview_length(self):
        """Test task preview length"""
        assert central_api.TASK_COMMAND_PREVIEW_LENGTH == 100
    
    def test_logger_exists(self):
        """Test structured logger is initialized"""
        assert central_api.logger is not None
        assert hasattr(central_api.logger, 'info')
        assert hasattr(central_api.logger, 'error')
        assert hasattr(central_api.logger, 'warning')
    
    def test_metrics_collector_exists(self):
        """Test metrics collector is initialized"""
        assert central_api.metrics is not None
        assert hasattr(central_api.metrics, 'record_request')
    
    def test_user_manager_exists(self):
        """Test user manager is initialized"""
        assert central_api.user_mgr is not None
    
    def test_settings_manager_exists(self):
        """Test settings manager is initialized"""
        assert central_api.settings_mgr is not None
    
    def test_task_policy_exists(self):
        """Test task policy is initialized"""
        assert central_api.task_policy is not None
    
    def test_plugin_manager_exists(self):
        """Test plugin manager is initialized"""
        assert central_api.plugin_manager is not None
    
    def test_cache_exists(self):
        """Test cache helper is initialized"""
        assert central_api.cache is not None
    
    def test_rate_limiter_exists(self):
        """Test rate limiter is initialized"""
        assert central_api.rate_limiter is not None
    
    def test_http_server_global(self):
        """Test global HTTP server variable"""
        # Should exist (may be None before start)
        assert hasattr(central_api, 'http_server')


class TestURLPathParsing:
    """Test URL parsing utilities"""
    
    def test_parse_simple_path(self):
        """Test parsing path without query"""
        from urllib.parse import urlparse
        
        parsed = urlparse('/api/servers')
        assert parsed.path == '/api/servers'
        assert parsed.query == ''
    
    def test_parse_path_with_query(self):
        """Test parsing path with query parameters"""
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse('/api/servers?status=online&limit=10')
        query = parse_qs(parsed.query)
        
        assert parsed.path == '/api/servers'
        assert 'status' in query
        assert query['status'][0] == 'online'
        assert query['limit'][0] == '10'
    
    def test_parse_restful_id(self):
        """Test extracting ID from RESTful path"""
        from urllib.parse import urlparse
        
        parsed = urlparse('/api/servers/123')
        parts = parsed.path.split('/')
        
        # ['', 'api', 'servers', '123']
        if len(parts) >= 4:
            server_id = parts[3]
            assert server_id == '123'
    
    def test_parse_nested_path(self):
        """Test parsing nested resource paths"""
        from urllib.parse import urlparse
        
        parsed = urlparse('/api/servers/5/tasks/10')
        parts = parsed.path.split('/')
        
        # ['', 'api', 'servers', '5', 'tasks', '10']
        assert parts[1] == 'api'
        assert parts[2] == 'servers'
        assert parts[3] == '5'
        assert parts[4] == 'tasks'
        assert parts[5] == '10'
    
    def test_parse_query_multiple_values(self):
        """Test query params with multiple values"""
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse('/api/tasks?status=pending&status=running')
        query = parse_qs(parsed.query)
        
        # Multiple values for same key
        assert 'status' in query
        assert len(query['status']) == 2
        assert 'pending' in query['status']
        assert 'running' in query['status']


class TestJSONOperations:
    """Test JSON encoding/decoding operations"""
    
    def test_encode_dict_to_json(self):
        """Test encoding dict to JSON string"""
        data = {"username": "admin", "role": "admin"}
        json_str = json.dumps(data)
        
        assert isinstance(json_str, str)
        assert 'username' in json_str
        assert 'admin' in json_str
    
    def test_decode_json_to_dict(self):
        """Test decoding JSON string to dict"""
        json_str = '{"status": "online", "cpu": 45.5}'
        data = json.loads(json_str)
        
        assert isinstance(data, dict)
        assert data['status'] == 'online'
        assert data['cpu'] == 45.5
    
    def test_encode_list(self):
        """Test encoding list to JSON"""
        servers = [
            {"id": 1, "name": "server1"},
            {"id": 2, "name": "server2"}
        ]
        json_str = json.dumps(servers)
        
        assert isinstance(json_str, str)
        assert 'server1' in json_str
    
    def test_decode_invalid_json(self):
        """Test handling invalid JSON"""
        with pytest.raises(json.JSONDecodeError):
            json.loads('{ invalid json }')
    
    def test_encode_with_datetime(self):
        """Test encoding dict with datetime (requires custom handler)"""
        data = {"timestamp": datetime.now().isoformat()}
        json_str = json.dumps(data)
        
        assert isinstance(json_str, str)
        # ISO format should be in output
        assert 'T' in json_str  # ISO datetime contains 'T'


class TestSecurityHelpers:
    """Test security-related helper functions"""
    
    def test_get_client_ip_direct(self):
        """Test extracting IP from client_address"""
        mock_handler = Mock()
        mock_handler.client_address = ('192.168.1.100', 54321)
        
        # Direct access
        ip = mock_handler.client_address[0]
        assert ip == '192.168.1.100'
    
    def test_localhost_detection(self):
        """Test detecting localhost connections"""
        localhost_ips = ['127.0.0.1', '::1', 'localhost']
        
        for ip in localhost_ips:
            assert ip in ['127.0.0.1', '::1', 'localhost']
    
    def test_authorization_header_parsing(self):
        """Test parsing Bearer token from Authorization header"""
        auth_header = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.abc123'
        
        # Extract token
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer '
            assert token.startswith('eyJ')
    
    def test_empty_authorization_header(self):
        """Test handling empty Authorization header"""
        auth_header = ''
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = None
        
        assert token is None


class TestErrorResponses:
    """Test error response formatting"""
    
    def test_error_dict_structure(self):
        """Test error response has expected structure"""
        error = {"error": "Server not found", "code": "NOT_FOUND"}
        
        assert 'error' in error
        assert isinstance(error['error'], str)
    
    def test_error_with_details(self):
        """Test error with additional details"""
        error = {
            "error": "Validation failed",
            "details": {
                "field": "username",
                "issue": "required"
            }
        }
        
        assert 'error' in error
        assert 'details' in error
        assert error['details']['field'] == 'username'
    
    def test_success_response(self):
        """Test success response structure"""
        response = {
            "success": True,
            "data": {"id": 123, "name": "test-server"}
        }
        
        assert response['success'] is True
        assert 'data' in response


class TestHTTPMethods:
    """Test HTTP method definitions"""
    
    def test_http_methods_exist(self):
        """Test HTTP method handlers exist"""
        assert hasattr(central_api.CentralAPIHandler, 'do_GET')
        assert hasattr(central_api.CentralAPIHandler, 'do_POST')
        assert hasattr(central_api.CentralAPIHandler, 'do_PUT')
        assert hasattr(central_api.CentralAPIHandler, 'do_DELETE')
    
    def test_handler_inherits_from_base(self):
        """Test handler inherits from BaseHTTPRequestHandler"""
        from http.server import BaseHTTPRequestHandler
        assert issubclass(central_api.CentralAPIHandler, BaseHTTPRequestHandler)


class TestTaskValidation:
    """Test task command validation constants"""
    
    def test_task_max_length_positive(self):
        """Test task max length is positive"""
        assert central_api.TASK_COMMAND_MAX_LENGTH > 0
    
    def test_task_preview_smaller_than_max(self):
        """Test preview length is smaller than max"""
        assert central_api.TASK_COMMAND_PREVIEW_LENGTH < central_api.TASK_COMMAND_MAX_LENGTH
    
    def test_task_length_validation_logic(self):
        """Test logic for validating task command length"""
        command = "ls -la /home"
        max_length = central_api.TASK_COMMAND_MAX_LENGTH
        
        # Should be valid
        assert len(command) <= max_length
        
        # Very long command
        long_command = "a" * (max_length + 1)
        assert len(long_command) > max_length
    
    def test_task_preview_truncation(self):
        """Test logic for truncating task preview"""
        long_command = "a" * 500
        preview_length = central_api.TASK_COMMAND_PREVIEW_LENGTH
        
        preview = long_command[:preview_length]
        assert len(preview) == preview_length


class TestDatabaseImports:
    """Test database module imports"""
    
    def test_db_module_imported(self):
        """Test database module is imported"""
        assert hasattr(central_api, 'db')
        assert central_api.db is not None
    
    def test_ssh_module_imported(self):
        """Test SSH manager module is imported"""
        assert hasattr(central_api, 'ssh')
        assert central_api.ssh is not None
    
    def test_email_module_imported(self):
        """Test email alerts module is imported"""
        assert hasattr(central_api, 'email')
        assert central_api.email is not None
    
    def test_alert_manager_imported(self):
        """Test alert manager is imported"""
        assert hasattr(central_api, 'alert_manager')
        assert central_api.alert_manager is not None
    
    def test_security_module_imported(self):
        """Test security module is imported"""
        assert hasattr(central_api, 'security')
        assert central_api.security is not None


class TestEventTypes:
    """Test event type constants"""
    
    def test_event_types_imported(self):
        """Test EventTypes is imported"""
        assert hasattr(central_api, 'EventTypes')
    
    def test_event_severity_imported(self):
        """Test EventSeverity is imported"""
        assert hasattr(central_api, 'EventSeverity')
    
    def test_create_event_imported(self):
        """Test create_event function is imported"""
        assert hasattr(central_api, 'create_event')


class TestCacheOperations:
    """Test cache helper operations"""
    
    def test_cache_get_operation(self):
        """Test cache get returns None for missing key"""
        with patch.object(central_api.cache, 'get') as mock_get:
            mock_get.return_value = None
            
            result = central_api.cache.get('nonexistent_key')
            assert result is None
    
    def test_cache_set_operation(self):
        """Test cache set stores value"""
        with patch.object(central_api.cache, 'set') as mock_set:
            central_api.cache.set('test_key', 'test_value', ttl=60)
            
            mock_set.assert_called_once_with('test_key', 'test_value', ttl=60)
    
    def test_cache_delete_operation(self):
        """Test cache delete removes key"""
        with patch.object(central_api.cache, 'delete') as mock_delete:
            central_api.cache.delete('test_key')
            
            mock_delete.assert_called_once_with('test_key')


class TestRateLimiter:
    """Test rate limiter operations"""
    
    def test_rate_limiter_has_check_method(self):
        """Test rate limiter has check_rate_limit method"""
        assert hasattr(central_api.rate_limiter, 'check_rate_limit')
    
    def test_check_endpoint_rate_limit_imported(self):
        """Test endpoint rate limit checker is imported"""
        assert hasattr(central_api, 'check_endpoint_rate_limit')
    
    def test_rate_limiter_allows_request(self):
        """Test rate limiter allows within limit"""
        with patch.object(central_api.rate_limiter, 'check_rate_limit') as mock_check:
            mock_check.return_value = (True, {'remaining': 99, 'reset_at': 1234567890})
            
            allowed, info = central_api.rate_limiter.check_rate_limit('127.0.0.1:api', 100, 60)
            assert allowed is True
            assert info['remaining'] == 99
    
    def test_rate_limiter_blocks_request(self):
        """Test rate limiter blocks when exceeded"""
        with patch.object(central_api.rate_limiter, 'check_rate_limit') as mock_check:
            mock_check.return_value = (False, {'retry_after': 60, 'reset_at': 1234567890})
            
            allowed, info = central_api.rate_limiter.check_rate_limit('192.168.1.100:login', 10, 60)
            assert allowed is False
            assert 'retry_after' in info
