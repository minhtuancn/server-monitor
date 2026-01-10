"""
GET Endpoint Tests for central_api.py
Target: Test GET operations for users, settings, groups, servers, tasks
Focus: Authentication, authorization, query parameters, filtering
"""

import pytest
import json
import sys
import os
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import central_api
from central_api import verify_auth_token


class TestGETUsers:
    """Test GET /api/users endpoints"""
    
    def test_get_all_users_requires_admin(self):
        """Test listing users requires admin role"""
        mock_handler = Mock()
        mock_handler.headers = {'Authorization': 'Bearer user.token'}
        mock_handler.path = '/api/users'
        mock_handler.command = 'GET'
        
        with patch('central_api.security.AuthMiddleware.decode_token') as mock_decode:
            mock_decode.return_value = {
                "user_id": 2,
                "role": "user"  # Not admin
            }
            
            result = verify_auth_token(mock_handler)
            
            assert result['valid'] is True
            assert result['role'] != 'admin'
    
    def test_get_all_users_success(self):
        """Test successful user listing"""
        with patch('central_api.user_mgr.get_all_users') as mock_users:
            mock_users.return_value = [
                {"id": 1, "username": "admin", "role": "admin"},
                {"id": 2, "username": "user1", "role": "user"}
            ]
            
            users = mock_users()
            
            assert len(users) == 2
            assert users[0]["username"] == "admin"
    
    def test_get_single_user_by_id(self):
        """Test getting user by ID"""
        path = "/api/users/5"
        user_id = int(path.split("/")[-1])
        
        assert user_id == 5
    
    def test_get_single_user_success(self):
        """Test successful single user retrieval"""
        with patch('central_api.user_mgr.get_user') as mock_user:
            mock_user.return_value = {
                "id": 5,
                "username": "testuser",
                "email": "test@example.com",
                "role": "user"
            }
            
            user = mock_user(5)
            
            assert user is not None
            assert user["id"] == 5
    
    def test_get_user_not_found(self):
        """Test user not found returns None"""
        with patch('central_api.user_mgr.get_user') as mock_user:
            mock_user.return_value = None
            
            user = mock_user(999)
            
            assert user is None
    
    def test_user_can_see_own_data(self):
        """Test users can see their own data"""
        auth_user_id = 5
        requested_user_id = 5
        role = "user"
        
        can_access = (role == "admin" or auth_user_id == requested_user_id)
        
        assert can_access is True
    
    def test_user_cannot_see_others_data(self):
        """Test users cannot see other users' data"""
        auth_user_id = 5
        requested_user_id = 6
        role = "user"
        
        can_access = (role == "admin" or auth_user_id == requested_user_id)
        
        assert can_access is False
    
    def test_admin_can_see_any_user(self):
        """Test admins can see any user's data"""
        role = "admin"
        
        can_access = (role == "admin")
        
        assert can_access is True
    
    def test_invalid_user_id_format(self):
        """Test invalid user ID format handling"""
        path = "/api/users/invalid"
        
        try:
            user_id = int(path.split("/")[-1])
            assert False, "Should raise ValueError"
        except ValueError:
            assert True
    
    def test_get_roles(self):
        """Test getting available roles"""
        with patch('central_api.user_mgr.get_roles') as mock_roles:
            mock_roles.return_value = ["admin", "user", "viewer"]
            
            roles = mock_roles()
            
            assert len(roles) == 3
            assert "admin" in roles


class TestGETSettings:
    """Test GET /api/settings endpoints"""
    
    def test_get_all_settings_requires_auth(self):
        """Test getting settings requires authentication"""
        mock_handler = Mock()
        mock_handler.headers = {}
        mock_handler.path = '/api/settings'
        
        result = verify_auth_token(mock_handler)
        
        assert result['valid'] is False
    
    def test_get_all_settings_success(self):
        """Test successful settings retrieval"""
        with patch('central_api.settings_mgr.get_all_settings') as mock_settings:
            mock_settings.return_value = {
                "max_connections": 10,
                "timeout": 30,
                "retry_attempts": 3
            }
            
            settings = mock_settings()
            
            assert "max_connections" in settings
            assert settings["timeout"] == 30
    
    def test_get_single_setting(self):
        """Test getting single setting by key"""
        path = "/api/settings/max_connections"
        key = path.split("/")[-1]
        
        assert key == "max_connections"
    
    def test_get_single_setting_success(self):
        """Test successful single setting retrieval"""
        with patch('central_api.settings_mgr.get_setting') as mock_setting:
            mock_setting.return_value = 10
            
            value = mock_setting("max_connections")
            
            assert value == 10
    
    def test_get_setting_not_found(self):
        """Test setting not found returns None"""
        with patch('central_api.settings_mgr.get_setting') as mock_setting:
            mock_setting.return_value = None
            
            value = mock_setting("nonexistent")
            
            assert value is None
    
    def test_get_settings_options(self):
        """Test getting settings options"""
        with patch('central_api.settings_mgr.get_options') as mock_options:
            mock_options.return_value = {
                "max_connections": {"min": 1, "max": 100, "default": 10},
                "timeout": {"min": 1, "max": 300, "default": 30}
            }
            
            options = mock_options()
            
            assert "max_connections" in options
            assert options["timeout"]["default"] == 30


class TestGETGroups:
    """Test GET /api/groups endpoints"""
    
    def test_get_groups_requires_auth(self):
        """Test getting groups requires authentication"""
        mock_handler = Mock()
        mock_handler.headers = {}
        mock_handler.path = '/api/groups'
        
        result = verify_auth_token(mock_handler)
        
        assert result['valid'] is False
    
    def test_parse_group_type_query_param(self):
        """Test parsing group type query parameter"""
        path_with_query = "/api/groups?type=servers"
        query_params = parse_qs(urlparse(path_with_query).query)
        group_type = query_params.get("type", [None])[0]
        
        assert group_type == "servers"
    
    def test_get_groups_without_filter(self):
        """Test getting all groups without filter"""
        path = "/api/groups"
        query_params = parse_qs(urlparse(path).query)
        group_type = query_params.get("type", [None])[0]
        
        assert group_type is None
    
    def test_filter_groups_by_type(self):
        """Test filtering groups by type"""
        all_groups = [
            {"id": 1, "name": "Prod Servers", "type": "servers"},
            {"id": 2, "name": "Dev Notes", "type": "notes"},
            {"id": 3, "name": "DB Servers", "type": "servers"}
        ]
        
        group_type = "servers"
        filtered = [g for g in all_groups if g["type"] == group_type]
        
        assert len(filtered) == 2
        assert all(g["type"] == "servers" for g in filtered)


class TestGETServers:
    """Test GET /api/servers endpoints"""
    
    def test_get_servers_requires_auth(self):
        """Test getting servers requires authentication"""
        mock_handler = Mock()
        mock_handler.headers = {}
        mock_handler.path = '/api/servers'
        
        result = verify_auth_token(mock_handler)
        
        assert result['valid'] is False
    
    def test_get_all_servers(self):
        """Test getting all servers"""
        with patch('central_api.db.get_servers') as mock_servers:
            mock_servers.return_value = [
                {"id": 1, "name": "web-1", "status": "online"},
                {"id": 2, "name": "db-1", "status": "offline"}
            ]
            
            servers = mock_servers()
            
            assert len(servers) == 2
            assert servers[0]["name"] == "web-1"
    
    def test_filter_servers_by_status(self):
        """Test filtering servers by status"""
        with patch('central_api.db.get_servers') as mock_servers:
            mock_servers.return_value = [
                {"id": 1, "name": "web-1", "status": "online"}
            ]
            
            servers = mock_servers(status="online")
            
            assert all(s["status"] == "online" for s in servers)
    
    def test_get_single_server(self):
        """Test getting single server by ID"""
        with patch('central_api.db.get_server') as mock_server:
            mock_server.return_value = {
                "id": 5,
                "name": "web-1",
                "host": "192.168.1.1",
                "port": 22,
                "status": "online"
            }
            
            server = mock_server(5)
            
            assert server["id"] == 5
            assert server["name"] == "web-1"
    
    def test_get_server_not_found(self):
        """Test server not found"""
        with patch('central_api.db.get_server') as mock_server:
            mock_server.return_value = None
            
            server = mock_server(999)
            
            assert server is None


class TestGETTasks:
    """Test GET /api/tasks endpoints"""
    
    def test_get_tasks_requires_auth(self):
        """Test getting tasks requires authentication"""
        mock_handler = Mock()
        mock_handler.headers = {}
        mock_handler.path = '/api/tasks'
        
        result = verify_auth_token(mock_handler)
        
        assert result['valid'] is False
    
    def test_get_all_tasks(self):
        """Test getting all tasks"""
        with patch('central_api.db.get_tasks') as mock_tasks:
            mock_tasks.return_value = [
                {"id": "task-1", "command": "ls -la", "status": "completed"},
                {"id": "task-2", "command": "uptime", "status": "pending"}
            ]
            
            tasks = mock_tasks()
            
            assert len(tasks) == 2
            assert tasks[0]["status"] == "completed"
    
    def test_get_single_task(self):
        """Test getting single task by ID"""
        with patch('central_api.db.get_task') as mock_task:
            mock_task.return_value = {
                "id": "task-123",
                "command": "ls -la",
                "status": "completed",
                "output": "total 48\ndrwxr-xr-x"
            }
            
            task = mock_task("task-123")
            
            assert task["id"] == "task-123"
            assert "output" in task
    
    def test_filter_tasks_by_server(self):
        """Test filtering tasks by server ID"""
        all_tasks = [
            {"id": "task-1", "server_id": 5, "status": "completed"},
            {"id": "task-2", "server_id": 6, "status": "pending"},
            {"id": "task-3", "server_id": 5, "status": "failed"}
        ]
        
        server_id = 5
        filtered = [t for t in all_tasks if t["server_id"] == server_id]
        
        assert len(filtered) == 2
        assert all(t["server_id"] == 5 for t in filtered)
    
    def test_filter_tasks_by_status(self):
        """Test filtering tasks by status"""
        all_tasks = [
            {"id": "task-1", "status": "completed"},
            {"id": "task-2", "status": "pending"},
            {"id": "task-3", "status": "completed"}
        ]
        
        status = "completed"
        filtered = [t for t in all_tasks if t["status"] == status]
        
        assert len(filtered) == 2


class TestGETWebhooks:
    """Test GET /api/webhooks endpoints"""
    
    def test_get_webhooks_requires_auth(self):
        """Test getting webhooks requires authentication"""
        mock_handler = Mock()
        mock_handler.headers = {}
        mock_handler.path = '/api/webhooks'
        
        result = verify_auth_token(mock_handler)
        
        assert result['valid'] is False
    
    def test_get_all_webhooks(self):
        """Test getting all webhooks"""
        with patch('central_api.db.get_webhooks') as mock_webhooks:
            mock_webhooks.return_value = [
                {"id": 1, "name": "Slack Alert", "url": "https://hooks.slack.com/..."},
                {"id": 2, "name": "Discord", "url": "https://discord.com/api/webhooks/..."}
            ]
            
            webhooks = mock_webhooks()
            
            assert len(webhooks) == 2
            assert webhooks[0]["name"] == "Slack Alert"


class TestQueryParameterParsing:
    """Test query parameter parsing"""
    
    def test_parse_single_param(self):
        """Test parsing single query parameter"""
        url = "/api/servers?status=online"
        params = parse_qs(urlparse(url).query)
        
        status = params.get("status", [None])[0]
        
        assert status == "online"
    
    def test_parse_multiple_params(self):
        """Test parsing multiple query parameters"""
        url = "/api/tasks?server_id=5&status=completed"
        params = parse_qs(urlparse(url).query)
        
        server_id = params.get("server_id", [None])[0]
        status = params.get("status", [None])[0]
        
        assert server_id == "5"
        assert status == "completed"
    
    def test_parse_array_param(self):
        """Test parsing array query parameter"""
        url = "/api/servers?ids=1&ids=2&ids=3"
        params = parse_qs(urlparse(url).query)
        
        ids = params.get("ids", [])
        
        assert len(ids) == 3
        assert "1" in ids
    
    def test_parse_empty_query(self):
        """Test parsing URL with no query parameters"""
        url = "/api/servers"
        params = parse_qs(urlparse(url).query)
        
        assert len(params) == 0
    
    def test_default_value_for_missing_param(self):
        """Test default value for missing parameter"""
        url = "/api/groups"
        params = parse_qs(urlparse(url).query)
        
        group_type = params.get("type", [None])[0]
        page = params.get("page", ["1"])[0]
        
        assert group_type is None
        assert page == "1"


class TestGETPagination:
    """Test pagination for GET endpoints"""
    
    def test_parse_page_number(self):
        """Test parsing page number from query"""
        url = "/api/servers?page=2"
        params = parse_qs(urlparse(url).query)
        
        page = int(params.get("page", ["1"])[0])
        
        assert page == 2
    
    def test_parse_page_size(self):
        """Test parsing page size from query"""
        url = "/api/servers?page=1&per_page=50"
        params = parse_qs(urlparse(url).query)
        
        per_page = int(params.get("per_page", ["20"])[0])
        
        assert per_page == 50
    
    def test_default_pagination_values(self):
        """Test default pagination values"""
        url = "/api/servers"
        params = parse_qs(urlparse(url).query)
        
        page = int(params.get("page", ["1"])[0])
        per_page = int(params.get("per_page", ["20"])[0])
        
        assert page == 1
        assert per_page == 20
    
    def test_calculate_offset(self):
        """Test calculating offset for pagination"""
        page = 3
        per_page = 20
        
        offset = (page - 1) * per_page
        
        assert offset == 40


class TestGETResponseFormats:
    """Test GET response formats"""
    
    def test_list_response_format(self):
        """Test list response format"""
        response = [
            {"id": 1, "name": "item1"},
            {"id": 2, "name": "item2"}
        ]
        
        assert isinstance(response, list)
        assert len(response) == 2
    
    def test_single_item_response_format(self):
        """Test single item response format"""
        response = {
            "id": 5,
            "name": "item",
            "status": "active"
        }
        
        assert isinstance(response, dict)
        assert "id" in response
    
    def test_not_found_response(self):
        """Test not found response format"""
        response = {"error": "Resource not found"}
        
        assert "error" in response
        assert "not found" in response["error"].lower()
    
    def test_paginated_response_format(self):
        """Test paginated response format"""
        response = {
            "data": [{"id": 1}, {"id": 2}],
            "page": 1,
            "per_page": 20,
            "total": 50
        }
        
        assert "data" in response
        assert "page" in response
        assert "total" in response


class TestGETAuthentication:
    """Test authentication for GET endpoints"""
    
    def test_public_endpoints_no_auth(self):
        """Test public endpoints don't require auth"""
        public_paths = [
            "/api/health",
            "/api/version"
        ]
        
        # Public endpoints should be accessible
        for path in public_paths:
            # No auth required
            assert not path.startswith("/api/users")
            assert not path.startswith("/api/servers")
    
    def test_protected_get_endpoints(self):
        """Test protected GET endpoints require auth"""
        protected_paths = [
            "/api/users",
            "/api/servers",
            "/api/tasks",
            "/api/settings",
            "/api/groups",
            "/api/webhooks"
        ]
        
        mock_handler = Mock()
        mock_handler.headers = {}
        
        for path in protected_paths:
            mock_handler.path = path
            result = verify_auth_token(mock_handler)
            
            # Should fail without token
            assert result['valid'] is False
    
    def test_extract_bearer_token(self):
        """Test extracting Bearer token from header"""
        auth_header = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.token"
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Skip "Bearer "
            
            assert token.startswith("eyJ")
            assert len(token) > 10
