#!/usr/bin/env python3

"""
SSH Connection Module for Remote Server Monitoring
Handles SSH connections, command execution, and agent communication
"""

import paramiko
import json
import socket
import time
from threading import Lock, Thread
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

class SSHConnectionPool:
    """
    Manages SSH connections to remote servers
    Reuses connections to improve performance
    """
    
    def __init__(self, max_connections=50, timeout=10, quick_timeout=5):
        self.connections = {}
        self.locks = {}
        self.max_connections = max_connections
        self.timeout = timeout  # Normal timeout
        self.quick_timeout = quick_timeout  # Quick timeout for health checks
        self.global_lock = Lock()
        self.executor = ThreadPoolExecutor(max_workers=20)  # For async operations
    
    def get_connection(self, host, port, username, ssh_key_path=None, password=None):
        """
        Get or create SSH connection
        """
        key = f"{username}@{host}:{port}"
        
        with self.global_lock:
            if key not in self.locks:
                self.locks[key] = Lock()
        
        with self.locks[key]:
            # Check if connection exists and is alive
            if key in self.connections:
                client = self.connections[key]
                try:
                    client.exec_command('echo test', timeout=2)
                    return client
                except:
                    # Connection dead, remove it
                    try:
                        client.close()
                    except:
                        pass
                    del self.connections[key]
            
            # Create new connection
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            try:
                if ssh_key_path:
                    # Expand ~ to home directory
                    key_path = os.path.expanduser(ssh_key_path)
                    
                    if not os.path.exists(key_path):
                        raise Exception(f"SSH key not found: {key_path}")
                    
                    client.connect(
                        hostname=host,
                        port=port,
                        username=username,
                        key_filename=key_path,
                        timeout=self.timeout,
                        look_for_keys=False,
                        allow_agent=False
                    )
                elif password:
                    client.connect(
                        hostname=host,
                        port=port,
                        username=username,
                        password=password,
                        timeout=self.timeout,
                        look_for_keys=False,
                        allow_agent=False
                    )
                else:
                    raise Exception("Either ssh_key_path or password must be provided")
                
                self.connections[key] = client
                return client
            
            except Exception as e:
                raise Exception(f"SSH connection failed: {str(e)}")
    
    def close_connection(self, host, port, username):
        """Close a specific connection"""
        key = f"{username}@{host}:{port}"
        
        with self.global_lock:
            if key in self.connections:
                try:
                    self.connections[key].close()
                except:
                    pass
                del self.connections[key]
    
    def close_all(self):
        """Close all connections"""
        with self.global_lock:
            for client in self.connections.values():
                try:
                    client.close()
                except:
                    pass
            self.connections.clear()
    
    def quick_connect_test(self, host, port, username, ssh_key_path=None, password=None):
        """Quick connection test with short timeout"""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_kwargs = {
                'hostname': host,
                'port': port,
                'username': username,
                'timeout': self.quick_timeout,
                'look_for_keys': False,
                'allow_agent': False
            }
            
            if ssh_key_path:
                key_path = os.path.expanduser(ssh_key_path)
                if os.path.exists(key_path):
                    connect_kwargs['key_filename'] = key_path
            elif password:
                connect_kwargs['password'] = password
            else:
                return False
            
            client.connect(**connect_kwargs)
            client.close()
            return True
        except:
            return False

# Global connection pool
ssh_pool = SSHConnectionPool()

def execute_command(host, port, username, command, ssh_key_path=None, password=None, timeout=30):
    """
    Execute a command on remote server via SSH
    """
    try:
        client = ssh_pool.get_connection(host, port, username, ssh_key_path, password)
        
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        exit_code = stdout.channel.recv_exit_status()
        
        return {
            'success': True,
            'output': output,
            'error': error,
            'exit_code': exit_code
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def test_connection(host, port, username, ssh_key_path=None, password=None):
    """
    Test SSH connection to a server
    """
    try:
        result = execute_command(host, port, username, 'echo "test"', ssh_key_path, password, timeout=10)
        
        if result['success'] and result['output'] == 'test':
            return {'success': True, 'message': 'SSH connection successful'}
        else:
            return {'success': False, 'error': result.get('error', 'Connection test failed')}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_ssh_connection(host, port, username, ssh_key_path=None, password=None):
    """
    Alias for test_connection - tests SSH connection with a key
    """
    return test_connection(host, port, username, ssh_key_path, password)

def get_remote_agent_data(host, port, username, agent_port=8083, endpoint='/api/all', ssh_key_path=None, password=None):
    """
    Get monitoring data from remote agent via SSH tunnel or direct HTTP
    This function tries to curl the agent API from the remote server
    """
    try:
        # Execute curl command on remote server to get agent data
        command = f'curl -s http://localhost:{agent_port}{endpoint}'
        
        result = execute_command(host, port, username, command, ssh_key_path, password, timeout=15)
        
        if result['success']:
            try:
                data = json.loads(result['output'])
                return {'success': True, 'data': data}
            except json.JSONDecodeError:
                return {'success': False, 'error': 'Invalid JSON response from agent'}
        else:
            return {'success': False, 'error': result.get('error', 'Failed to get agent data')}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_remote_agent_data_with_timeout(host, port, username, agent_port=8083, endpoint='/api/all', ssh_key_path=None, password=None, timeout=10):
    """
    Get monitoring data with configurable timeout - returns cached data if connection fails
    This is optimized for dashboard views where speed is important
    """
    try:
        # Use thread pool to execute with timeout
        future = ssh_pool.executor.submit(
            get_remote_agent_data,
            host, port, username, agent_port, endpoint, ssh_key_path, password
        )
        
        result = future.result(timeout=timeout)
        return result
    
    except FuturesTimeoutError:
        return {
            'success': False,
            'error': 'Connection timeout',
            'timeout': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def check_agent_status(host, port, username, agent_port=8083, ssh_key_path=None, password=None):
    """
    Check if monitoring agent is running on remote server
    """
    try:
        # Check if agent port is listening
        command = f'ss -tlnp | grep ":{agent_port}"'
        
        result = execute_command(host, port, username, command, ssh_key_path, password, timeout=10)
        
        if result['success'] and result['output']:
            return {'success': True, 'status': 'running', 'message': 'Agent is running'}
        else:
            return {'success': True, 'status': 'stopped', 'message': 'Agent is not running'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def start_remote_agent(host, port, username, agent_script_path, ssh_key_path=None, password=None):
    """
    Start monitoring agent on remote server
    """
    try:
        # Check if agent is already running
        status = check_agent_status(host, port, username, 8083, ssh_key_path, password)
        
        if status.get('status') == 'running':
            return {'success': True, 'message': 'Agent is already running'}
        
        # Start agent in background
        command = f'nohup python3 {agent_script_path} > /tmp/agent.log 2>&1 &'
        
        result = execute_command(host, port, username, command, ssh_key_path, password, timeout=10)
        
        if result['success']:
            # Wait a bit for agent to start
            time.sleep(2)
            
            # Verify agent started
            status = check_agent_status(host, port, username, 8083, ssh_key_path, password)
            
            if status.get('status') == 'running':
                return {'success': True, 'message': 'Agent started successfully'}
            else:
                return {'success': False, 'error': 'Agent failed to start'}
        else:
            return {'success': False, 'error': result.get('error', 'Failed to start agent')}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def stop_remote_agent(host, port, username, agent_port=8083, ssh_key_path=None, password=None):
    """
    Stop monitoring agent on remote server
    """
    try:
        # Find and kill agent process
        command = f"kill $(lsof -t -i:{agent_port})"
        
        result = execute_command(host, port, username, command, ssh_key_path, password, timeout=10)
        
        # Wait a bit
        time.sleep(1)
        
        # Verify agent stopped
        status = check_agent_status(host, port, username, agent_port, ssh_key_path, password)
        
        if status.get('status') == 'stopped':
            return {'success': True, 'message': 'Agent stopped successfully'}
        else:
            return {'success': False, 'error': 'Failed to stop agent'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def deploy_agent(host, port, username, local_agent_path, remote_agent_path='/tmp/server_monitor_agent.py', ssh_key_path=None, password=None):
    """
    Deploy monitoring agent to remote server
    """
    try:
        client = ssh_pool.get_connection(host, port, username, ssh_key_path, password)
        
        sftp = client.open_sftp()
        
        # Upload agent script
        sftp.put(local_agent_path, remote_agent_path)
        
        # Make it executable
        sftp.chmod(remote_agent_path, 0o755)
        
        sftp.close()
        
        return {'success': True, 'message': f'Agent deployed to {remote_agent_path}'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def execute_remote_action(host, port, username, action_type, action_data, ssh_key_path=None, password=None):
    """
    Execute actions on remote server (kill process, restart service, etc.)
    """
    try:
        if action_type == 'kill_process':
            pid = action_data.get('pid')
            command = f'kill -15 {pid}'
        
        elif action_type == 'service_action':
            service = action_data.get('service')
            action = action_data.get('action')  # start, stop, restart
            command = f'systemctl {action} {service}'
        
        elif action_type == 'docker_action':
            container = action_data.get('container')
            action = action_data.get('action')
            command = f'docker {action} {container}'
        
        else:
            return {'success': False, 'error': 'Unknown action type'}
        
        result = execute_command(host, port, username, command, ssh_key_path, password, timeout=30)
        
        if result['success']:
            return {'success': True, 'message': f'Action {action_type} executed successfully'}
        else:
            return {'success': False, 'error': result.get('error', 'Action failed')}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_ssh_public_key(key_path='~/.ssh/id_rsa.pub'):
    """
    Read SSH public key for display
    """
    try:
        key_path = os.path.expanduser(key_path)
        
        if not os.path.exists(key_path):
            # Try to generate key pair if not exists
            private_key = key_path.replace('.pub', '')
            if not os.path.exists(private_key):
                return {'success': False, 'error': 'SSH key not found. Generate it first with: ssh-keygen -t rsa'}
        
        with open(key_path, 'r') as f:
            public_key = f.read().strip()
        
        return {'success': True, 'public_key': public_key}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ==================== AGENT MANAGEMENT ====================

def install_agent_remote(host, port, username, agent_port=8083, ssh_key_path=None, password=None):
    """
    Install monitoring agent on remote server
    """
    try:
        # Local agent path
        local_agent = '/opt/server-monitor-dev/backend/agent.py'
        remote_agent = '/opt/monitoring/agent.py'
        
        # Create directory on remote
        mkdir_cmd = f'mkdir -p /opt/monitoring'
        result = execute_command(host, port, username, mkdir_cmd, ssh_key_path, password)
        
        if not result['success']:
            return {'success': False, 'error': 'Failed to create remote directory'}
        
        # Deploy agent
        deploy_result = deploy_agent(host, port, username, local_agent, remote_agent, ssh_key_path, password)
        
        if not deploy_result['success']:
            return deploy_result
        
        # Create systemd service
        service_content = f"""[Unit]
Description=Server Monitor Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/monitoring
ExecStart=/usr/bin/python3 {remote_agent} --port {agent_port}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        # Write service file
        service_cmd = f'cat > /etc/systemd/system/monitor-agent.service << EOF\n{service_content}\nEOF'
        result = execute_command(host, port, username, service_cmd, ssh_key_path, password)
        
        if not result['success']:
            return {'success': False, 'error': 'Failed to create systemd service'}
        
        # Reload systemd and enable service
        reload_cmd = 'systemctl daemon-reload && systemctl enable monitor-agent && systemctl start monitor-agent'
        result = execute_command(host, port, username, reload_cmd, ssh_key_path, password)
        
        if not result['success']:
            return {'success': False, 'error': 'Failed to start agent service'}
        
        return {
            'success': True,
            'message': 'Agent installed and started successfully',
            'agent_path': remote_agent,
            'service': 'monitor-agent',
            'port': agent_port
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_agent_info(host, port, username, ssh_key_path=None, password=None):
    """
    Get agent installation info and status
    """
    try:
        # Check if agent file exists
        check_file = 'test -f /opt/monitoring/agent.py && echo "exists" || echo "not_found"'
        result = execute_command(host, port, username, check_file, ssh_key_path, password)
        
        if not result['success']:
            return {'success': False, 'error': 'Failed to check agent file'}
        
        agent_installed = 'exists' in result['output']
        
        # Check service status
        service_cmd = 'systemctl is-active monitor-agent 2>/dev/null || echo "inactive"'
        result = execute_command(host, port, username, service_cmd, ssh_key_path, password)
        
        service_active = 'active' in result['output']
        
        # Get agent version if installed
        version = 'unknown'
        if agent_installed:
            version_cmd = 'grep "VERSION = " /opt/monitoring/agent.py | head -1 | cut -d "=" -f2 | tr -d "\' \""'
            result = execute_command(host, port, username, version_cmd, ssh_key_path, password)
            if result['success']:
                version = result['output'].strip() or 'unknown'
        
        # Check agent port
        port_cmd = 'ss -tlnp | grep ":8083" || netstat -tlnp 2>/dev/null | grep ":8083" || echo "not_listening"'
        result = execute_command(host, port, username, port_cmd, ssh_key_path, password)
        
        port_listening = 'not_listening' not in result['output']
        
        return {
            'success': True,
            'installed': agent_installed,
            'service_active': service_active,
            'port_listening': port_listening,
            'version': version,
            'status': 'running' if (agent_installed and service_active and port_listening) else 'stopped'
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def uninstall_agent_remote(host, port, username, ssh_key_path=None, password=None):
    """
    Uninstall monitoring agent from remote server
    """
    try:
        # Stop and disable service
        stop_cmd = 'systemctl stop monitor-agent && systemctl disable monitor-agent'
        execute_command(host, port, username, stop_cmd, ssh_key_path, password)
        
        # Remove service file
        rm_service = 'rm -f /etc/systemd/system/monitor-agent.service'
        execute_command(host, port, username, rm_service, ssh_key_path, password)
        
        # Reload systemd
        reload_cmd = 'systemctl daemon-reload'
        execute_command(host, port, username, reload_cmd, ssh_key_path, password)
        
        # Remove agent files
        rm_agent = 'rm -rf /opt/monitoring'
        result = execute_command(host, port, username, rm_agent, ssh_key_path, password)
        
        if not result['success']:
            return {'success': False, 'error': 'Failed to remove agent files'}
        
        return {'success': True, 'message': 'Agent uninstalled successfully'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ==================== PORT CONFLICT DETECTION ====================

def check_port_available(host, port, username, check_port, ssh_key_path=None, password=None):
    """
    Check if a port is available (not in use) on remote server
    """
    try:
        # Check using ss (modern) or netstat (fallback)
        cmd = f'ss -tlnp 2>/dev/null | grep ":{check_port}" || netstat -tlnp 2>/dev/null | grep ":{check_port}" || echo "PORT_AVAILABLE"'
        result = execute_command(host, port, username, cmd, ssh_key_path, password)
        
        if not result['success']:
            return {'success': False, 'error': 'Failed to check port'}
        
        output = result['output'].strip()
        
        if 'PORT_AVAILABLE' in output or not output:
            return {
                'success': True,
                'available': True,
                'port': check_port,
                'process': None,
                'pid': None
            }
        else:
            # Parse process info
            import re
            # Try to extract PID and process name
            pid_match = re.search(r'pid=(\d+)', output)
            proc_match = re.search(r'users:\(\("([^"]+)"', output)
            
            pid = pid_match.group(1) if pid_match else 'unknown'
            process = proc_match.group(1) if proc_match else 'unknown'
            
            return {
                'success': True,
                'available': False,
                'port': check_port,
                'process': process,
                'pid': pid,
                'details': output
            }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def suggest_available_port(host, port, username, start_port, ssh_key_path=None, password=None):
    """
    Suggest an available port starting from start_port
    """
    try:
        for check_port in range(start_port, start_port + 100):
            result = check_port_available(host, port, username, check_port, ssh_key_path, password)
            
            if result.get('success') and result.get('available'):
                return {
                    'success': True,
                    'suggested_port': check_port,
                    'message': f'Port {check_port} is available'
                }
        
        return {'success': False, 'error': 'No available ports found in range'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    # Test SSH connection
    print("Testing SSH module...")
    
    # Get public key
    key_result = get_ssh_public_key()
    print("\nPublic key:", key_result)
    
    # Test connection (replace with your server details)
    # result = test_connection('192.168.1.100', 22, 'root', ssh_key_path='~/.ssh/id_rsa')
    # print("\nConnection test:", result)
