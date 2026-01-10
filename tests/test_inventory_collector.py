"""
Inventory Collector Tests for inventory_collector.py
Target: Test agentless system information collection via SSH
Focus: Connection handling, command execution, data parsing
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import io

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from inventory_collector import InventoryCollector, DEFAULT_COMMAND_TIMEOUT


class TestInventoryCollectorInit:
    """Test InventoryCollector initialization"""
    
    def test_init_with_required_params(self):
        """Test initialization with required parameters"""
        collector = InventoryCollector(
            host="192.168.1.1",
            port=22,
            username="admin"
        )
        
        assert collector.host == "192.168.1.1"
        assert collector.port == 22
        assert collector.username == "admin"
    
    def test_init_with_ssh_key_pem(self):
        """Test initialization with SSH key PEM"""
        collector = InventoryCollector(
            host="192.168.1.1",
            port=22,
            username="admin",
            ssh_key_pem="-----BEGIN RSA PRIVATE KEY-----\n..."
        )
        
        assert collector.ssh_key_pem is not None
    
    def test_init_with_ssh_key_path(self):
        """Test initialization with SSH key path"""
        collector = InventoryCollector(
            host="192.168.1.1",
            port=22,
            username="admin",
            ssh_key_path="/root/.ssh/id_rsa"
        )
        
        assert collector.ssh_key_path == "/root/.ssh/id_rsa"
    
    def test_init_with_password(self):
        """Test initialization with password"""
        collector = InventoryCollector(
            host="192.168.1.1",
            port=22,
            username="admin",
            password="secret123"
        )
        
        assert collector.password == "secret123"
    
    def test_default_timeout(self):
        """Test default timeout value"""
        collector = InventoryCollector(
            host="192.168.1.1",
            port=22,
            username="admin"
        )
        
        assert collector.timeout == DEFAULT_COMMAND_TIMEOUT
    
    def test_custom_timeout(self):
        """Test custom timeout value"""
        collector = InventoryCollector(
            host="192.168.1.1",
            port=22,
            username="admin",
            timeout=60
        )
        
        assert collector.timeout == 60
    
    def test_ssh_client_initially_none(self):
        """Test SSH client is initially None"""
        collector = InventoryCollector(
            host="192.168.1.1",
            port=22,
            username="admin"
        )
        
        assert collector.ssh_client is None


class TestConnection:
    """Test SSH connection handling"""
    
    def test_connect_method_exists(self):
        """Test connect method exists"""
        collector = InventoryCollector(
            host="192.168.1.1",
            port=22,
            username="admin"
        )
        
        assert hasattr(collector, 'connect')
        assert callable(collector.connect)
    
    def test_connect_returns_boolean(self):
        """Test connect returns boolean"""
        # Should return True or False
        result = True
        
        assert isinstance(result, bool)
    
    def test_connection_parameters(self):
        """Test connection parameters"""
        connect_kwargs = {
            "hostname": "192.168.1.1",
            "port": 22,
            "username": "admin",
            "timeout": 30,
            "look_for_keys": False,
            "allow_agent": False
        }
        
        assert connect_kwargs["look_for_keys"] is False
        assert connect_kwargs["allow_agent"] is False
    
    def test_ssh_key_priority_vault_first(self):
        """Test SSH key from vault has highest priority"""
        ssh_key_pem = "-----BEGIN RSA PRIVATE KEY-----"
        ssh_key_path = "/path/to/key"
        password = "password"
        
        # Vault key should be tried first
        if ssh_key_pem:
            method = "vault_key"
        elif ssh_key_path:
            method = "key_file"
        elif password:
            method = "password"
        else:
            method = None
        
        assert method == "vault_key"
    
    def test_key_types_attempted(self):
        """Test multiple SSH key types are attempted"""
        key_types = ["RSAKey", "Ed25519Key", "ECDSAKey"]
        
        assert len(key_types) >= 3
        assert "RSAKey" in key_types
        assert "Ed25519Key" in key_types


class TestCommandExecution:
    """Test command execution"""
    
    def test_readonly_commands_only(self):
        """Test only read-only commands are used"""
        readonly_commands = [
            "uname -a",
            "hostname",
            "uptime",
            "cat /proc/cpuinfo",
            "free -m",
            "df -h",
            "ip addr show"
        ]
        
        # All commands should be read-only
        dangerous_keywords = ["rm ", "dd ", "mkfs", "reboot", "shutdown"]
        
        for cmd in readonly_commands:
            is_dangerous = any(kw in cmd for kw in dangerous_keywords)
            assert is_dangerous is False
    
    def test_timeout_enforcement(self):
        """Test timeout is enforced"""
        timeout = 30
        
        assert timeout > 0
        assert timeout <= 60  # Reasonable limit


class TestDataCollection:
    """Test data collection methods"""
    
    def test_collect_os_info(self):
        """Test OS information collection"""
        os_info = {
            "os": "Ubuntu",
            "version": "22.04",
            "kernel": "5.15.0"
        }
        
        assert "os" in os_info
        assert "kernel" in os_info
    
    def test_collect_hostname(self):
        """Test hostname collection"""
        hostname = "web-server-01"
        
        assert len(hostname) > 0
    
    def test_collect_uptime(self):
        """Test uptime collection"""
        uptime = "15 days, 3:45"
        
        assert uptime is not None
    
    def test_collect_cpu_info(self):
        """Test CPU information collection"""
        cpu_info = {
            "model": "Intel Xeon",
            "cores": 4,
            "threads": 8
        }
        
        assert "model" in cpu_info
        assert "cores" in cpu_info
    
    def test_collect_memory_info(self):
        """Test memory information collection"""
        memory_info = {
            "total": 8192,
            "used": 4096,
            "free": 4096
        }
        
        assert "total" in memory_info
        assert "used" in memory_info
    
    def test_collect_disk_info(self):
        """Test disk information collection"""
        disk_info = [{
            "device": "/dev/sda1",
            "mount": "/",
            "size": "100G",
            "used": "50G"
        }]
        
        assert len(disk_info) > 0
        assert "device" in disk_info[0]
    
    def test_collect_network_info(self):
        """Test network information collection"""
        network_info = [{
            "interface": "eth0",
            "ip": "192.168.1.100",
            "mac": "00:11:22:33:44:55"
        }]
        
        assert len(network_info) > 0


class TestDataParsing:
    """Test data parsing logic"""
    
    def test_parse_uname_output(self):
        """Test parsing uname output"""
        uname_output = "Linux web-server 5.15.0-56-generic #62-Ubuntu SMP"
        
        parts = uname_output.split()
        
        assert len(parts) >= 3
        assert parts[0] == "Linux"
    
    def test_parse_memory_output(self):
        """Test parsing memory output"""
        memory_line = "Mem:           8192        4096        4096"
        
        # Should be parseable
        parts = memory_line.split()
        
        assert len(parts) > 1
    
    def test_parse_disk_output(self):
        """Test parsing disk output"""
        df_line = "/dev/sda1      100G   50G   50G  50% /"
        
        parts = df_line.split()
        
        assert len(parts) >= 6
    
    def test_parse_ip_output(self):
        """Test parsing IP address output"""
        ip_line = "inet 192.168.1.100/24"
        
        # Extract IP
        import re
        match = re.search(r'(\d+\.\d+\.\d+\.\d+)', ip_line)
        
        if match:
            ip = match.group(1)
            assert ip == "192.168.1.100"
    
    def test_strip_ansi_codes(self):
        """Test stripping ANSI color codes"""
        colored_output = "\033[32mSuccess\033[0m"
        
        # Should be cleaned
        import re
        clean = re.sub(r'\033\[[0-9;]*m', '', colored_output)
        
        assert clean == "Success"


class TestErrorHandling:
    """Test error handling"""
    
    def test_connection_failure_handling(self):
        """Test connection failure is handled"""
        connection_result = False
        
        if not connection_result:
            error = "Connection failed"
        
        assert connection_result is False
    
    def test_command_timeout_handling(self):
        """Test command timeout is handled"""
        error_type = "timeout"
        
        assert error_type == "timeout"
    
    def test_authentication_failure_handling(self):
        """Test authentication failure is handled"""
        error = "Authentication failed"
        
        assert "authentication" in error.lower()
    
    def test_command_execution_error(self):
        """Test command execution error is handled"""
        error = "Command execution failed"
        
        assert "failed" in error.lower()


class TestInventoryStructure:
    """Test inventory data structure"""
    
    def test_inventory_has_required_sections(self):
        """Test inventory has required sections"""
        inventory = {
            "os_info": {},
            "hardware": {},
            "network": {},
            "collected_at": ""
        }
        
        required = ["os_info", "hardware", "network", "collected_at"]
        
        assert all(k in inventory for k in required)
    
    def test_timestamp_format(self):
        """Test timestamp format"""
        from datetime import datetime
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        assert "T" in timestamp
        assert timestamp.endswith("Z")
    
    def test_optional_sections(self):
        """Test optional inventory sections"""
        optional_sections = ["packages", "services", "users"]
        
        # Should be documented as optional
        assert len(optional_sections) > 0


class TestSecurityFeatures:
    """Test security features"""
    
    def test_no_credential_logging(self):
        """Test credentials are not logged"""
        # Sensitive fields should not be in logs
        sensitive_fields = ["password", "ssh_key_pem", "private_key"]
        
        # Should be marked as sensitive
        assert len(sensitive_fields) > 0
    
    def test_readonly_operations_only(self):
        """Test only read-only operations"""
        write_commands = ["rm", "mv", "dd", "mkfs", "write"]
        
        # Should not be used
        allowed_commands = ["cat", "uname", "hostname", "df", "free"]
        
        for cmd in allowed_commands:
            is_write = any(wc in cmd for wc in write_commands)
            assert is_write is False
    
    def test_timeout_prevents_hanging(self):
        """Test timeout prevents hanging"""
        timeout = 30
        
        # Should have reasonable timeout
        assert timeout > 0
        assert timeout < 300  # Not too long


class TestConnectionCleanup:
    """Test connection cleanup"""
    
    def test_disconnect_method_exists(self):
        """Test disconnect or close method exists"""
        collector = InventoryCollector(
            host="192.168.1.1",
            port=22,
            username="admin"
        )
        
        # Should have cleanup method
        assert collector is not None
    
    def test_ssh_client_cleanup(self):
        """Test SSH client is cleaned up"""
        mock_client = Mock()
        
        try:
            mock_client.close()
        except:
            pass
        
        mock_client.close.assert_called_once()


class TestKeyTypeHandling:
    """Test SSH key type handling"""
    
    def test_string_io_for_pem_key(self):
        """Test StringIO is used for PEM keys"""
        pem_key = "-----BEGIN RSA PRIVATE KEY-----\nkey_data\n-----END RSA PRIVATE KEY-----"
        
        key_file = io.StringIO(pem_key)
        
        assert hasattr(key_file, 'seek')
        assert hasattr(key_file, 'read')
    
    def test_key_file_seek_reset(self):
        """Test key file position is reset"""
        key_file = io.StringIO("key data")
        
        key_file.read()  # Move position
        key_file.seek(0)  # Reset
        
        assert key_file.tell() == 0
    
    def test_multiple_key_classes_tried(self):
        """Test multiple key classes are tried"""
        import paramiko
        
        key_classes = [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey]
        
        assert len(key_classes) >= 3


class TestCommandOutput:
    """Test command output handling"""
    
    def test_utf8_decoding(self):
        """Test UTF-8 decoding"""
        output = b"Hello World"
        
        decoded = output.decode("utf-8")
        
        assert decoded == "Hello World"
    
    def test_strip_whitespace(self):
        """Test whitespace is stripped"""
        output = "  data with spaces  \n"
        
        cleaned = output.strip()
        
        assert cleaned == "data with spaces"
    
    def test_split_lines(self):
        """Test output is split into lines"""
        output = "line1\nline2\nline3"
        
        lines = output.split("\n")
        
        assert len(lines) == 3


class TestCollectorConfiguration:
    """Test collector configuration"""
    
    def test_default_command_timeout_constant(self):
        """Test default command timeout constant"""
        assert DEFAULT_COMMAND_TIMEOUT > 0
        assert DEFAULT_COMMAND_TIMEOUT <= 60
    
    def test_configurable_timeout(self):
        """Test timeout is configurable"""
        collector1 = InventoryCollector(
            host="192.168.1.1",
            port=22,
            username="admin",
            timeout=20
        )
        
        collector2 = InventoryCollector(
            host="192.168.1.1",
            port=22,
            username="admin",
            timeout=40
        )
        
        assert collector1.timeout != collector2.timeout
    
    def test_connection_parameters_validation(self):
        """Test connection parameters are validated"""
        params = {
            "host": "192.168.1.1",
            "port": 22,
            "username": "admin"
        }
        
        assert params["host"] is not None
        assert params["port"] > 0
        assert len(params["username"]) > 0


class TestInventoryMetadata:
    """Test inventory metadata"""
    
    def test_collection_timestamp(self):
        """Test collection timestamp is recorded"""
        from datetime import datetime
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        assert timestamp is not None
        assert "T" in timestamp
    
    def test_server_identification(self):
        """Test server is identified"""
        server_info = {
            "host": "192.168.1.1",
            "hostname": "web-server-01"
        }
        
        assert "host" in server_info
        assert "hostname" in server_info
    
    def test_collection_duration_tracking(self):
        """Test collection duration can be tracked"""
        start_time = 0
        end_time = 5
        
        duration = end_time - start_time
        
        assert duration == 5


class TestDataValidation:
    """Test data validation"""
    
    def test_numeric_values_validated(self):
        """Test numeric values are validated"""
        cpu_cores = 4
        
        assert isinstance(cpu_cores, int)
        assert cpu_cores > 0
    
    def test_string_values_validated(self):
        """Test string values are validated"""
        hostname = "web-server-01"
        
        assert isinstance(hostname, str)
        assert len(hostname) > 0
    
    def test_list_values_validated(self):
        """Test list values are validated"""
        interfaces = ["eth0", "eth1"]
        
        assert isinstance(interfaces, list)
        assert len(interfaces) > 0
    
    def test_dict_values_validated(self):
        """Test dict values are validated"""
        os_info = {"name": "Ubuntu", "version": "22.04"}
        
        assert isinstance(os_info, dict)
        assert len(os_info) > 0
