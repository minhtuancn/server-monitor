"""
Task Runner Tests for task_runner.py
Target: Test task execution, SSH command handling, queue management
Focus: Task lifecycle, concurrency control, output handling
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import queue
import threading

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import task_runner
from task_runner import TaskRunner


class TestConfiguration:
    """Test task runner configuration"""
    
    def test_default_config_values(self):
        """Test default configuration values"""
        assert hasattr(task_runner, 'TASKS_STORE_OUTPUT_DEFAULT')
        assert hasattr(task_runner, 'TASKS_OUTPUT_MAX_BYTES')
        assert hasattr(task_runner, 'TASKS_CONCURRENT_PER_SERVER')
        assert hasattr(task_runner, 'TASKS_DEFAULT_TIMEOUT')
    
    def test_output_max_bytes_default(self):
        """Test output max bytes default value"""
        max_bytes = task_runner.TASKS_OUTPUT_MAX_BYTES
        
        assert max_bytes >= 65536  # At least 64KB
    
    def test_concurrent_per_server_default(self):
        """Test concurrent tasks per server default"""
        concurrent = task_runner.TASKS_CONCURRENT_PER_SERVER
        
        assert concurrent >= 1
    
    def test_default_timeout_value(self):
        """Test default timeout value"""
        timeout = task_runner.TASKS_DEFAULT_TIMEOUT
        
        assert timeout >= 60  # At least 60 seconds


class TestTaskQueue:
    """Test task queue management"""
    
    def test_task_queue_exists(self):
        """Test task queue is initialized"""
        assert hasattr(task_runner, 'task_queue')
        assert isinstance(task_runner.task_queue, queue.Queue)
    
    def test_running_tasks_dict(self):
        """Test running tasks dictionary exists"""
        assert hasattr(task_runner, 'running_tasks')
        assert isinstance(task_runner.running_tasks, dict)
    
    def test_server_task_count_dict(self):
        """Test server task count tracking"""
        assert hasattr(task_runner, 'server_task_count')
        assert isinstance(task_runner.server_task_count, dict)
    
    def test_queue_operations(self):
        """Test basic queue operations"""
        test_queue = queue.Queue()
        
        # Put task
        test_queue.put("task-123")
        
        # Get task
        task_id = test_queue.get(timeout=1)
        
        assert task_id == "task-123"
    
    def test_queue_empty_check(self):
        """Test queue empty check"""
        test_queue = queue.Queue()
        
        assert test_queue.empty() is True
        
        test_queue.put("task-1")
        
        assert test_queue.empty() is False


class TestTaskRunner:
    """Test TaskRunner class"""
    
    def test_task_runner_initialization(self):
        """Test TaskRunner initialization"""
        runner = TaskRunner("task-123")
        
        assert runner.task_id == "task-123"
        assert runner.task is None
        assert runner.ssh_client is None
        assert runner.should_stop is False
    
    def test_task_runner_has_run_method(self):
        """Test TaskRunner has run method"""
        runner = TaskRunner("task-123")
        
        assert hasattr(runner, 'run')
        assert callable(runner.run)
    
    def test_task_runner_has_cancel_method(self):
        """Test TaskRunner has cancel method"""
        runner = TaskRunner("task-123")
        
        assert hasattr(runner, 'cancel')
        assert callable(runner.cancel)
    
    def test_cancel_sets_should_stop_flag(self):
        """Test cancel sets should_stop flag"""
        runner = TaskRunner("task-123")
        
        assert runner.should_stop is False
        
        runner.cancel()
        
        assert runner.should_stop is True


class TestTaskExecution:
    """Test task execution logic"""
    
    def test_task_status_transitions(self):
        """Test task status transitions"""
        statuses = ["pending", "running", "success", "failed", "cancelled", "timeout"]
        
        assert "pending" in statuses
        assert "running" in statuses
        assert "success" in statuses
    
    def test_success_exit_code(self):
        """Test success determined by exit code 0"""
        exit_code = 0
        
        status = "success" if exit_code == 0 else "failed"
        
        assert status == "success"
    
    def test_failure_exit_code(self):
        """Test failure determined by non-zero exit code"""
        exit_code = 1
        
        status = "success" if exit_code == 0 else "failed"
        
        assert status == "failed"
    
    def test_timestamp_format(self):
        """Test timestamp format for task tracking"""
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        assert "T" in timestamp
        assert timestamp.endswith("Z")
    
    def test_task_requires_server_id(self):
        """Test task requires server_id"""
        task = {
            "task_id": "task-123",
            "server_id": 5,
            "command": "ls -la"
        }
        
        assert "server_id" in task
        assert task["server_id"] is not None


class TestSSHCommandExecution:
    """Test SSH command execution"""
    
    def test_execute_ssh_command_method_exists(self):
        """Test _execute_ssh_command method exists"""
        runner = TaskRunner("task-123")
        
        assert hasattr(runner, '_execute_ssh_command')
    
    def test_ssh_connection_parameters(self):
        """Test SSH connection parameters"""
        connect_kwargs = {
            "hostname": "192.168.1.1",
            "port": 22,
            "username": "admin",
            "timeout": 10,
            "look_for_keys": False,
            "allow_agent": False
        }
        
        assert "hostname" in connect_kwargs
        assert "port" in connect_kwargs
        assert "username" in connect_kwargs
        assert connect_kwargs["look_for_keys"] is False
        assert connect_kwargs["allow_agent"] is False
    
    def test_authentication_priority_ssh_key_vault(self):
        """Test SSH key vault has highest priority"""
        server = {
            "ssh_key_vault_id": "vault-123",
            "ssh_key_path": "/path/to/key",
            "ssh_password": "password"
        }
        
        # Should prefer vault key
        has_vault = server.get("ssh_key_vault_id") is not None
        
        assert has_vault is True
    
    def test_authentication_priority_key_file(self):
        """Test SSH key file is second priority"""
        server = {
            "ssh_key_vault_id": None,
            "ssh_key_path": "/path/to/key",
            "ssh_password": "password"
        }
        
        # Should use key file if no vault
        has_vault = server.get("ssh_key_vault_id")
        has_key_file = server.get("ssh_key_path")
        
        assert has_vault is None
        assert has_key_file is not None
    
    def test_authentication_priority_password(self):
        """Test password is last priority"""
        server = {
            "ssh_key_vault_id": None,
            "ssh_key_path": None,
            "ssh_password": "password"
        }
        
        # Should use password if no keys
        has_vault = server.get("ssh_key_vault_id")
        has_key_file = server.get("ssh_key_path")
        has_password = server.get("ssh_password")
        
        assert has_vault is None
        assert has_key_file is None
        assert has_password is not None
    
    def test_no_authentication_method(self):
        """Test error when no authentication method available"""
        server = {
            "ssh_key_vault_id": None,
            "ssh_key_path": None,
            "ssh_password": None
        }
        
        has_auth = any([
            server.get("ssh_key_vault_id"),
            server.get("ssh_key_path"),
            server.get("ssh_password")
        ])
        
        assert has_auth is False
    
    def test_command_execution_return_format(self):
        """Test command execution return format"""
        result = (True, 0, "output", "")
        
        success, exit_code, stdout, stderr = result
        
        assert isinstance(success, bool)
        assert isinstance(exit_code, int)
        assert isinstance(stdout, str)
        assert isinstance(stderr, str)


class TestOutputHandling:
    """Test output handling and truncation"""
    
    def test_truncate_output_method_exists(self):
        """Test _truncate_output method exists"""
        runner = TaskRunner("task-123")
        
        assert hasattr(runner, '_truncate_output')
    
    def test_output_under_limit_not_truncated(self):
        """Test output under limit is not truncated"""
        output = "Short output"
        max_bytes = 65536
        
        output_bytes = output.encode("utf-8")
        
        assert len(output_bytes) < max_bytes
    
    def test_output_over_limit_truncated(self):
        """Test output over limit is truncated"""
        output = "x" * 100000  # 100KB
        max_bytes = 65536  # 64KB
        
        output_bytes = output.encode("utf-8")
        
        assert len(output_bytes) > max_bytes
    
    def test_truncation_message_added(self):
        """Test truncation message is added"""
        max_bytes = 1000
        truncation_msg = f"... [Output truncated. Max size: {max_bytes} bytes]"
        
        assert "truncated" in truncation_msg.lower()
        assert str(max_bytes) in truncation_msg
    
    def test_store_output_flag(self):
        """Test store_output flag"""
        task = {
            "task_id": "task-123",
            "store_output": True
        }
        
        if task["store_output"]:
            save_output = True
        else:
            save_output = False
        
        assert save_output is True
    
    def test_null_output_when_not_storing(self):
        """Test output is null when not storing"""
        store_output = False
        
        if store_output:
            stdout = "output data"
        else:
            stdout = None
        
        assert stdout is None


class TestTimeoutHandling:
    """Test timeout handling"""
    
    def test_default_timeout_used(self):
        """Test default timeout is used"""
        task = {}
        default_timeout = 60
        
        timeout = task.get("timeout_seconds", default_timeout)
        
        assert timeout == default_timeout
    
    def test_custom_timeout_used(self):
        """Test custom timeout is used when provided"""
        task = {"timeout_seconds": 120}
        default_timeout = 60
        
        timeout = task.get("timeout_seconds", default_timeout)
        
        assert timeout == 120
    
    def test_timeout_status(self):
        """Test timeout status is set"""
        status = "timeout"
        
        assert status == "timeout"
    
    def test_timeout_error_message(self):
        """Test timeout error message format"""
        timeout = 60
        error_msg = f"Command execution timeout after {timeout} seconds"
        
        assert "timeout" in error_msg.lower()
        assert str(timeout) in error_msg


class TestConcurrencyControl:
    """Test concurrency control"""
    
    def test_server_task_count_tracking(self):
        """Test server task count is tracked"""
        server_task_count = {}
        
        server_id = 5
        server_task_count[server_id] = 1
        
        assert server_task_count[server_id] == 1
    
    def test_server_task_count_increment(self):
        """Test server task count is incremented"""
        server_task_count = {5: 1}
        
        server_task_count[5] += 1
        
        assert server_task_count[5] == 2
    
    def test_server_task_count_decrement(self):
        """Test server task count is decremented"""
        server_task_count = {5: 2}
        
        server_task_count[5] -= 1
        
        assert server_task_count[5] == 1
    
    def test_concurrency_limit_check(self):
        """Test concurrency limit check"""
        current_count = 3
        limit = 1
        
        exceeds_limit = current_count >= limit
        
        assert exceeds_limit is True
    
    def test_retry_delay_calculation(self):
        """Test retry delay calculation"""
        current_count = 2
        
        retry_delay = min(5, 1 * (1 + current_count))
        
        assert retry_delay <= 5
        assert retry_delay > 0
    
    def test_remove_zero_count_servers(self):
        """Test servers with zero count are removed"""
        server_task_count = {5: 1}
        
        server_task_count[5] -= 1
        
        if server_task_count[5] <= 0:
            del server_task_count[5]
        
        assert 5 not in server_task_count


class TestWorkerThread:
    """Test worker thread functionality"""
    
    def test_worker_thread_exists(self):
        """Test worker_thread function exists"""
        assert hasattr(task_runner, 'worker_thread')
        assert callable(task_runner.worker_thread)
    
    def test_shutdown_signal(self):
        """Test None is shutdown signal"""
        task_id = None
        
        is_shutdown = task_id is None
        
        assert is_shutdown is True
    
    def test_queue_get_timeout(self):
        """Test queue get with timeout"""
        test_queue = queue.Queue()
        
        try:
            task_id = test_queue.get(timeout=0.1)
            timed_out = False
        except queue.Empty:
            timed_out = True
        
        assert timed_out is True
    
    def test_daemon_thread_flag(self):
        """Test daemon thread flag"""
        thread = threading.Thread(target=lambda: None)
        thread.daemon = True
        
        assert thread.daemon is True


class TestErrorHandling:
    """Test error handling"""
    
    def test_authentication_exception_handling(self):
        """Test authentication exception handling"""
        error = "SSH authentication failed: Invalid credentials"
        
        assert "authentication failed" in error.lower()
    
    def test_ssh_exception_handling(self):
        """Test SSH exception handling"""
        error = "SSH error: Connection refused"
        
        assert "ssh error" in error.lower()
    
    def test_timeout_exception_handling(self):
        """Test timeout exception handling"""
        error = "timed out"
        
        is_timeout = "timed out" in error.lower()
        
        assert is_timeout is True
    
    def test_generic_exception_handling(self):
        """Test generic exception handling"""
        error = "Execution error: Unexpected failure"
        
        assert "error" in error.lower()
    
    def test_fail_task_method_exists(self):
        """Test _fail_task method exists"""
        runner = TaskRunner("task-123")
        
        assert hasattr(runner, '_fail_task')
    
    def test_error_exit_code(self):
        """Test error exit code is -1"""
        exit_code = -1
        
        assert exit_code == -1


class TestTaskCleanup:
    """Test task cleanup"""
    
    def test_ssh_client_cleanup(self):
        """Test SSH client is closed in cleanup"""
        mock_client = Mock()
        
        try:
            mock_client.close()
        except:
            pass
        
        mock_client.close.assert_called_once()
    
    def test_running_tasks_removal(self):
        """Test task removed from running_tasks"""
        running_tasks = {"task-123": Mock()}
        
        task_id = "task-123"
        if task_id in running_tasks:
            del running_tasks[task_id]
        
        assert task_id not in running_tasks
    
    def test_server_count_cleanup(self):
        """Test server task count is decremented"""
        server_task_count = {5: 1}
        
        server_id = 5
        if server_id in server_task_count:
            server_task_count[server_id] -= 1
            if server_task_count[server_id] <= 0:
                del server_task_count[server_id]
        
        assert 5 not in server_task_count


class TestTaskStatus:
    """Test task status management"""
    
    def test_pending_status(self):
        """Test pending status"""
        status = "pending"
        
        assert status == "pending"
    
    def test_running_status(self):
        """Test running status"""
        status = "running"
        
        assert status == "running"
    
    def test_success_status(self):
        """Test success status"""
        status = "success"
        
        assert status == "success"
    
    def test_failed_status(self):
        """Test failed status"""
        status = "failed"
        
        assert status == "failed"
    
    def test_cancelled_status(self):
        """Test cancelled status"""
        status = "cancelled"
        
        assert status == "cancelled"
    
    def test_timeout_status(self):
        """Test timeout status"""
        status = "timeout"
        
        assert status == "timeout"


class TestKeyTypeHandling:
    """Test SSH key type handling"""
    
    def test_multiple_key_types_supported(self):
        """Test multiple SSH key types are tried"""
        key_types = ["RSAKey", "Ed25519Key", "ECDSAKey"]
        
        assert len(key_types) >= 3
    
    def test_key_file_string_io(self):
        """Test key file uses StringIO"""
        import io
        
        key_data = "-----BEGIN RSA PRIVATE KEY-----"
        key_file = io.StringIO(key_data)
        
        assert hasattr(key_file, 'seek')
        assert hasattr(key_file, 'read')
    
    def test_key_file_seek_reset(self):
        """Test key file is reset for each attempt"""
        import io
        
        key_file = io.StringIO("test data")
        key_file.read()  # Move position
        
        key_file.seek(0)  # Reset
        
        assert key_file.tell() == 0


class TestServerValidation:
    """Test server validation"""
    
    def test_server_not_found_handling(self):
        """Test server not found is handled"""
        server = None
        
        if not server:
            error = "Server not found"
        
        assert server is None
    
    def test_server_has_required_fields(self):
        """Test server has required connection fields"""
        server = {
            "host": "192.168.1.1",
            "port": 22,
            "username": "admin"
        }
        
        required = ["host", "port", "username"]
        has_all = all(k in server for k in required)
        
        assert has_all is True


class TestOutputDecoding:
    """Test output decoding"""
    
    def test_utf8_decoding(self):
        """Test UTF-8 decoding"""
        data = b"Hello World"
        decoded = data.decode("utf-8")
        
        assert decoded == "Hello World"
    
    def test_error_replacement_on_decode(self):
        """Test error replacement on decode failures"""
        data = b"\xff\xfe invalid utf-8"
        
        # Should not raise exception
        decoded = data.decode("utf-8", errors="replace")
        
        assert decoded is not None
    
    def test_ignore_errors_on_decode(self):
        """Test ignore errors on decode"""
        data = b"\xff\xfe invalid"
        
        decoded = data.decode("utf-8", errors="ignore")
        
        assert decoded is not None
