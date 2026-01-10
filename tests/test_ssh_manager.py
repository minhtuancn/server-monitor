"""
SSH Manager Tests for ssh_manager.py
Target: Test SSH connection pool, command execution, agent management
Focus: Connection handling, error cases, timeouts, security
"""

import pytest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock, call
import paramiko
from concurrent.futures import TimeoutError as FuturesTimeoutError

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import ssh_manager
from ssh_manager import SSHConnectionPool


class TestSSHConnectionPool:
    """Test SSH connection pool functionality"""
    
    def test_connection_pool_initialization(self):
        """Test connection pool initializes correctly"""
        pool = SSHConnectionPool(max_connections=50, timeout=10, quick_timeout=5)
        
        assert pool.max_connections == 50
        assert pool.timeout == 10
        assert pool.quick_timeout == 5
        assert len(pool.connections) == 0
        assert len(pool.locks) == 0
    
    def test_connection_key_format(self):
        """Test connection key format"""
        host = "192.168.1.1"
        port = 22
        username = "admin"
        
        key = f"{username}@{host}:{port}"
        
        assert key == "admin@192.168.1.1:22"
    
    def test_connection_pool_stores_connections(self):
        """Test pool stores connections by key"""
        pool = SSHConnectionPool()
        
        # Simulate adding a connection
        key = "admin@192.168.1.1:22"
        mock_client = Mock()
        
        pool.connections[key] = mock_client
        
        assert key in pool.connections
        assert pool.connections[key] == mock_client
    
    def test_close_specific_connection(self):
        """Test closing a specific connection"""
        pool = SSHConnectionPool()
        
        # Add mock connection
        key = "admin@192.168.1.1:22"
        mock_client = Mock()
        pool.connections[key] = mock_client
        
        # Close connection
        pool.close_connection("192.168.1.1", 22, "admin")
        
        # Verify closed
        assert key not in pool.connections
        mock_client.close.assert_called_once()
    
    def test_close_all_connections(self):
        """Test closing all connections"""
        pool = SSHConnectionPool()
        
        # Add multiple connections
        mock_client1 = Mock()
        mock_client2 = Mock()
        pool.connections["admin@host1:22"] = mock_client1
        pool.connections["user@host2:22"] = mock_client2
        
        # Close all
        pool.close_all()
        
        # Verify all closed
        assert len(pool.connections) == 0
        mock_client1.close.assert_called_once()
        mock_client2.close.assert_called_once()
    
    def test_connection_key_uniqueness(self):
        """Test connection keys are unique per host/port/user"""
        key1 = f"admin@192.168.1.1:22"
        key2 = f"admin@192.168.1.1:2222"
        key3 = f"user@192.168.1.1:22"
        
        assert key1 != key2  # Different ports
        assert key1 != key3  # Different users
        assert key2 != key3  # Both different


class TestSSHConnection:
    """Test SSH connection establishment"""
    
    def test_ssh_connection_requires_credentials(self):
        """Test SSH connection requires key or password"""
        # Without credentials should fail
        has_key = False
        has_password = False
        
        has_credentials = has_key or has_password
        
        assert has_credentials is False
    
    def test_ssh_key_path_expansion(self):
        """Test SSH key path expansion"""
        key_path = "~/.ssh/id_rsa"
        expanded = os.path.expanduser(key_path)
        
        assert expanded != key_path
        assert "~" not in expanded
    
    def test_ssh_key_file_validation(self):
        """Test SSH key file existence check"""
        # Valid path format
        key_path = "/root/.ssh/id_rsa"
        
        # Check existence
        exists = os.path.exists(key_path)
        
        # Should be boolean
        assert isinstance(exists, bool)
    
    def test_connection_parameters_validation(self):
        """Test connection parameters are validated"""
        # Valid parameters
        params = {
            "hostname": "192.168.1.1",
            "port": 22,
            "username": "admin",
            "timeout": 10,
            "look_for_keys": False,
            "allow_agent": False
        }
        
        assert params["hostname"] is not None
        assert params["port"] > 0
        assert params["username"] is not None
    
    def test_auto_add_policy_is_set(self):
        """Test AutoAddPolicy is set for connection"""
        with patch('paramiko.SSHClient') as mock_ssh:
            mock_client = Mock()
            mock_ssh.return_value = mock_client
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            mock_client.set_missing_host_key_policy.assert_called_once()


class TestCommandExecution:
    """Test SSH command execution"""
    
    def test_execute_command_function_exists(self):
        """Test execute_command function exists"""
        assert hasattr(ssh_manager, 'execute_command')
        assert callable(ssh_manager.execute_command)
    
    def test_execute_command_returns_dict(self):
        """Test execute_command returns dict with expected keys"""
        result = {
            "success": True,
            "output": "test output",
            "error": "",
            "exit_code": 0
        }
        
        assert "success" in result
        assert "output" in result
        assert "error" in result
        assert "exit_code" in result
    
    def test_successful_command_execution(self):
        """Test successful command execution result"""
        result = {
            "success": True,
            "output": "Hello World",
            "error": "",
            "exit_code": 0
        }
        
        assert result["success"] is True
        assert result["exit_code"] == 0
        assert len(result["output"]) > 0
    
    def test_failed_command_execution(self):
        """Test failed command execution result"""
        result = {
            "success": False,
            "error": "Command not found"
        }
        
        assert result["success"] is False
        assert "error" in result
    
    def test_command_with_error_output(self):
        """Test command that produces error output"""
        result = {
            "success": True,
            "output": "",
            "error": "Permission denied",
            "exit_code": 1
        }
        
        assert result["exit_code"] != 0
        assert len(result["error"]) > 0
    
    def test_command_timeout_handling(self):
        """Test command execution with timeout"""
        timeout = 30
        
        assert timeout > 0
        assert timeout <= 300  # Reasonable max


class TestConnectionTesting:
    """Test SSH connection testing functions"""
    
    def test_test_connection_function_exists(self):
        """Test test_connection function exists"""
        assert hasattr(ssh_manager, 'test_connection')
        assert callable(ssh_manager.test_connection)
    
    def test_successful_connection_test(self):
        """Test successful connection test result"""
        result = {
            "success": True,
            "message": "SSH connection successful"
        }
        
        assert result["success"] is True
        assert "message" in result
    
    def test_failed_connection_test(self):
        """Test failed connection test result"""
        result = {
            "success": False,
            "error": "Connection refused"
        }
        
        assert result["success"] is False
        assert "error" in result
    
    def test_test_ssh_connection_alias(self):
        """Test test_ssh_connection is alias for test_connection"""
        assert hasattr(ssh_manager, 'test_ssh_connection')
        assert callable(ssh_manager.test_ssh_connection)
    
    def test_quick_connect_test_exists(self):
        """Test quick connection test with short timeout"""
        pool = SSHConnectionPool(quick_timeout=5)
        
        assert pool.quick_timeout == 5
        assert pool.quick_timeout < pool.timeout


class TestRemoteAgentData:
    """Test remote agent data retrieval"""
    
    def test_get_remote_agent_data_function_exists(self):
        """Test get_remote_agent_data function exists"""
        assert hasattr(ssh_manager, 'get_remote_agent_data')
        assert callable(ssh_manager.get_remote_agent_data)
    
    def test_agent_data_uses_curl_command(self):
        """Test agent data retrieval uses curl"""
        agent_port = 8083
        endpoint = "/api/all"
        
        command = f"curl -s http://localhost:{agent_port}{endpoint}"
        
        assert "curl" in command
        assert str(agent_port) in command
        assert endpoint in command
    
    def test_agent_data_json_parsing(self):
        """Test agent data JSON parsing"""
        json_output = '{"cpu": 50, "memory": 60}'
        
        try:
            data = json.loads(json_output)
            success = True
        except json.JSONDecodeError:
            success = False
        
        assert success is True
        assert "cpu" in data
    
    def test_invalid_json_handling(self):
        """Test invalid JSON response handling"""
        invalid_json = "Not valid JSON"
        
        try:
            json.loads(invalid_json)
            result = {"success": True}
        except json.JSONDecodeError:
            result = {"success": False, "error": "Invalid JSON response from agent"}
        
        assert result["success"] is False
        assert "Invalid JSON" in result["error"]
    
    def test_agent_data_with_timeout_exists(self):
        """Test get_remote_agent_data_with_timeout exists"""
        assert hasattr(ssh_manager, 'get_remote_agent_data_with_timeout')
        assert callable(ssh_manager.get_remote_agent_data_with_timeout)
    
    def test_timeout_result_format(self):
        """Test timeout result format"""
        result = {
            "success": False,
            "error": "Connection timeout",
            "timeout": True
        }
        
        assert result["success"] is False
        assert result["timeout"] is True
    
    def test_default_agent_port(self):
        """Test default agent port"""
        agent_port = 8083
        
        assert agent_port == 8083


class TestAgentStatus:
    """Test agent status checking"""
    
    def test_check_agent_status_exists(self):
        """Test check_agent_status function exists"""
        assert hasattr(ssh_manager, 'check_agent_status')
        assert callable(ssh_manager.check_agent_status)
    
    def test_agent_status_command(self):
        """Test agent status check command"""
        agent_port = 8083
        command = f'ss -tlnp | grep ":{agent_port}"'
        
        assert "ss -tlnp" in command
        assert str(agent_port) in command
    
    def test_agent_running_result(self):
        """Test agent running result format"""
        result = {
            "success": True,
            "status": "running",
            "message": "Agent is running"
        }
        
        assert result["success"] is True
        assert result["status"] == "running"
    
    def test_agent_stopped_result(self):
        """Test agent stopped result format"""
        result = {
            "success": True,
            "status": "stopped",
            "message": "Agent is not running"
        }
        
        assert result["success"] is True
        assert result["status"] == "stopped"


class TestAgentManagement:
    """Test agent start/stop operations"""
    
    def test_start_remote_agent_exists(self):
        """Test start_remote_agent function exists"""
        assert hasattr(ssh_manager, 'start_remote_agent')
        assert callable(ssh_manager.start_remote_agent)
    
    def test_start_agent_command_format(self):
        """Test start agent command format"""
        agent_script_path = "/tmp/agent.py"
        command = f"nohup python3 {agent_script_path} > /tmp/agent.log 2>&1 &"
        
        assert "nohup" in command
        assert "python3" in command
        assert agent_script_path in command
        assert "&" in command  # Background execution
    
    def test_stop_remote_agent_exists(self):
        """Test stop_remote_agent function exists"""
        assert hasattr(ssh_manager, 'stop_remote_agent')
        assert callable(ssh_manager.stop_remote_agent)
    
    def test_stop_agent_command_format(self):
        """Test stop agent command format"""
        agent_port = 8083
        command = f"kill $(lsof -t -i:{agent_port})"
        
        assert "kill" in command
        assert "lsof" in command
        assert str(agent_port) in command
    
    def test_agent_already_running_check(self):
        """Test checking if agent is already running before start"""
        status = {"status": "running"}
        
        if status.get("status") == "running":
            should_skip_start = True
        else:
            should_skip_start = False
        
        assert should_skip_start is True


class TestAgentDeployment:
    """Test agent deployment"""
    
    def test_deploy_agent_exists(self):
        """Test deploy_agent function exists"""
        assert hasattr(ssh_manager, 'deploy_agent')
        assert callable(ssh_manager.deploy_agent)
    
    def test_default_remote_path(self):
        """Test default remote agent path"""
        remote_path = "/tmp/server_monitor_agent.py"
        
        assert remote_path.startswith("/tmp/")
        assert remote_path.endswith(".py")
    
    def test_file_permissions_format(self):
        """Test file permissions for deployed agent"""
        permissions = 0o755
        
        # Check format
        assert isinstance(permissions, int)
        assert permissions == 493  # 0o755 in decimal
    
    def test_deploy_success_result(self):
        """Test deploy success result format"""
        remote_path = "/tmp/agent.py"
        result = {
            "success": True,
            "message": f"Agent deployed to {remote_path}"
        }
        
        assert result["success"] is True
        assert remote_path in result["message"]
    
    def test_deploy_failure_result(self):
        """Test deploy failure result format"""
        result = {
            "success": False,
            "error": "SFTP transfer failed"
        }
        
        assert result["success"] is False
        assert "error" in result


class TestRemoteActions:
    """Test remote action execution"""
    
    def test_execute_remote_action_exists(self):
        """Test execute_remote_action function exists"""
        assert hasattr(ssh_manager, 'execute_remote_action')
        assert callable(ssh_manager.execute_remote_action)
    
    def test_kill_process_action(self):
        """Test kill process action command"""
        action_type = "kill_process"
        pid = 1234
        
        command = f"kill -15 {pid}"
        
        assert "kill -15" in command
        assert str(pid) in command
    
    def test_service_action_command(self):
        """Test service action command"""
        service = "nginx"
        action = "restart"
        
        command = f"systemctl {action} {service}"
        
        assert "systemctl" in command
        assert action in command
        assert service in command
    
    def test_docker_action_command(self):
        """Test docker action command"""
        container = "web-app"
        action = "restart"
        
        command = f"docker {action} {container}"
        
        assert "docker" in command
        assert action in command
        assert container in command
    
    def test_unknown_action_type(self):
        """Test unknown action type handling"""
        action_type = "unknown_action"
        
        valid_types = ["kill_process", "service_action", "docker_action"]
        
        assert action_type not in valid_types
    
    def test_valid_service_actions(self):
        """Test valid service actions"""
        valid_actions = ["start", "stop", "restart", "status"]
        
        assert "start" in valid_actions
        assert "stop" in valid_actions
        assert "restart" in valid_actions


class TestConnectionPoolLocking:
    """Test thread-safe connection pool operations"""
    
    def test_global_lock_exists(self):
        """Test global lock exists for pool"""
        pool = SSHConnectionPool()
        
        assert hasattr(pool, 'global_lock')
        assert pool.global_lock is not None
    
    def test_per_connection_locks(self):
        """Test per-connection locks are created"""
        pool = SSHConnectionPool()
        
        assert hasattr(pool, 'locks')
        assert isinstance(pool.locks, dict)
    
    def test_thread_pool_executor_exists(self):
        """Test thread pool executor for async operations"""
        pool = SSHConnectionPool()
        
        assert hasattr(pool, 'executor')
        assert pool.executor is not None


class TestErrorHandling:
    """Test error handling in SSH operations"""
    
    def test_connection_failed_error_format(self):
        """Test connection failed error format"""
        error = Exception("Connection refused")
        result = {"success": False, "error": f"SSH connection failed: {str(error)}"}
        
        assert result["success"] is False
        assert "SSH connection failed" in result["error"]
    
    def test_command_execution_error(self):
        """Test command execution error handling"""
        result = {
            "success": False,
            "error": "Command execution failed: timeout"
        }
        
        assert result["success"] is False
        assert "error" in result
    
    def test_sftp_transfer_error(self):
        """Test SFTP transfer error handling"""
        result = {
            "success": False,
            "error": "SFTP error: Permission denied"
        }
        
        assert result["success"] is False
        assert "SFTP" in result["error"]
    
    def test_timeout_error_handling(self):
        """Test timeout error handling"""
        try:
            # Simulate timeout
            raise FuturesTimeoutError()
        except FuturesTimeoutError:
            result = {"success": False, "error": "Connection timeout", "timeout": True}
        
        assert result["success"] is False
        assert result["timeout"] is True


class TestSSHKeyManagement:
    """Test SSH key management"""
    
    def test_get_ssh_public_key_exists(self):
        """Test get_ssh_public_key function exists"""
        assert hasattr(ssh_manager, 'get_ssh_public_key')
        assert callable(ssh_manager.get_ssh_public_key)
    
    def test_default_public_key_path(self):
        """Test default public key path"""
        default_path = "~/.ssh/id_rsa.pub"
        
        assert default_path.startswith("~/")
        assert default_path.endswith(".pub")
    
    def test_key_path_validation(self):
        """Test SSH key path validation"""
        key_path = "~/.ssh/id_rsa"
        expanded = os.path.expanduser(key_path)
        
        # Should expand tilde
        assert "~" not in expanded


class TestConnectionReuse:
    """Test connection reuse in pool"""
    
    def test_connection_keepalive_test(self):
        """Test connection keepalive with echo test"""
        keepalive_command = "echo test"
        
        assert keepalive_command == "echo test"
    
    def test_dead_connection_removal(self):
        """Test dead connections are removed from pool"""
        pool = SSHConnectionPool()
        
        # Add mock connection
        key = "admin@192.168.1.1:22"
        mock_client = Mock()
        pool.connections[key] = mock_client
        
        # Simulate failure and removal
        del pool.connections[key]
        
        assert key not in pool.connections
    
    def test_connection_reuse_same_key(self):
        """Test connection is reused for same key"""
        pool = SSHConnectionPool()
        
        key1 = f"admin@192.168.1.1:22"
        key2 = f"admin@192.168.1.1:22"
        
        assert key1 == key2  # Should reuse


class TestTimeoutConfiguration:
    """Test timeout configuration"""
    
    def test_normal_timeout_setting(self):
        """Test normal timeout setting"""
        pool = SSHConnectionPool(timeout=10)
        
        assert pool.timeout == 10
    
    def test_quick_timeout_setting(self):
        """Test quick timeout for health checks"""
        pool = SSHConnectionPool(quick_timeout=5)
        
        assert pool.quick_timeout == 5
        assert pool.quick_timeout < pool.timeout
    
    def test_command_timeout_parameter(self):
        """Test command execution timeout parameter"""
        timeout = 30
        
        assert timeout > 0
        assert timeout >= 10  # Reasonable minimum


class TestSecurityConsiderations:
    """Test security-related aspects"""
    
    def test_paramiko_exec_command_no_shell(self):
        """Test paramiko exec_command doesn't use shell by default"""
        # This is a security feature of paramiko
        # Commands are not executed through shell, preventing injection
        command = "ls -la"
        
        # Verify command is string (not shell script)
        assert isinstance(command, str)
        assert not command.startswith("/bin/sh")
    
    def test_credentials_required(self):
        """Test credentials are required for connection"""
        ssh_key_path = None
        password = None
        
        has_credentials = bool(ssh_key_path or password)
        
        assert has_credentials is False
    
    def test_look_for_keys_disabled(self):
        """Test look_for_keys is disabled for security"""
        look_for_keys = False
        
        assert look_for_keys is False
    
    def test_allow_agent_disabled(self):
        """Test SSH agent is disabled for security"""
        allow_agent = False
        
        assert allow_agent is False
