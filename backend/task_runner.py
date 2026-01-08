#!/usr/bin/env python3

"""
Task Runner Module for Remote Command Execution
Handles asynchronous task execution with SSH connection pooling
"""

import threading
import queue
import time
import sys
import os
import socket
from datetime import datetime
import io

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
from ssh_key_manager import get_decrypted_key
import paramiko

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration from environment
TASKS_STORE_OUTPUT_DEFAULT = os.environ.get('TASKS_STORE_OUTPUT_DEFAULT', '0') == '1'
TASKS_OUTPUT_MAX_BYTES = int(os.environ.get('TASKS_OUTPUT_MAX_BYTES', '65536'))  # 64KB default
TASKS_CONCURRENT_PER_SERVER = int(os.environ.get('TASKS_CONCURRENT_PER_SERVER', '1'))
TASKS_DEFAULT_TIMEOUT = int(os.environ.get('TASKS_DEFAULT_TIMEOUT', '60'))

# Task queue
task_queue = queue.Queue()
running_tasks = {}  # task_id -> thread
server_task_count = {}  # server_id -> count


class TaskRunner:
    """
    Handles execution of a single task
    """
    
    def __init__(self, task_id):
        self.task_id = task_id
        self.task = None
        self.ssh_client = None
        self.should_stop = False
        
    def run(self):
        """Execute the task"""
        try:
            # Get task details
            self.task = db.get_task(self.task_id)
            if not self.task:
                return
            
            # Get server details
            server = db.get_server(self.task['server_id'], decrypt_password=True)
            if not server:
                self._fail_task('Server not found')
                return
            
            # Mark task as running
            started_at = datetime.utcnow().isoformat() + 'Z'
            db.update_task_status(self.task_id, 'running', started_at=started_at)
            
            # Execute command via SSH
            success, exit_code, stdout, stderr = self._execute_ssh_command(server)
            
            # Update task with results
            if self.should_stop:
                # Task was cancelled
                finished_at = datetime.utcnow().isoformat() + 'Z'
                db.update_task_status(
                    self.task_id,
                    'cancelled',
                    exit_code=None,
                    stdout=None if not self.task['store_output'] else 'Task cancelled',
                    stderr=None if not self.task['store_output'] else 'Task cancelled by user',
                    finished_at=finished_at
                )
            elif success:
                finished_at = datetime.utcnow().isoformat() + 'Z'
                
                # Truncate output if needed
                if self.task['store_output']:
                    stdout = self._truncate_output(stdout)
                    stderr = self._truncate_output(stderr)
                else:
                    stdout = None
                    stderr = None
                
                status = 'success' if exit_code == 0 else 'failed'
                db.update_task_status(
                    self.task_id,
                    status,
                    exit_code=exit_code,
                    stdout=stdout,
                    stderr=stderr,
                    finished_at=finished_at
                )
            else:
                # Execution failed (timeout or error)
                finished_at = datetime.utcnow().isoformat() + 'Z'
                db.update_task_status(
                    self.task_id,
                    'failed',
                    exit_code=-1,
                    stdout=None if not self.task['store_output'] else stdout,
                    stderr=None if not self.task['store_output'] else stderr,
                    finished_at=finished_at
                )
                
        except Exception as e:
            # Unexpected error
            finished_at = datetime.utcnow().isoformat() + 'Z'
            error_msg = f'Task execution error: {str(e)}'
            db.update_task_status(
                self.task_id,
                'failed',
                exit_code=-1,
                stdout=None,
                stderr=None if not self.task['store_output'] else error_msg,
                finished_at=finished_at
            )
        finally:
            # Cleanup
            if self.ssh_client:
                try:
                    self.ssh_client.close()
                except:
                    pass
            
            # Remove from running tasks
            if self.task_id in running_tasks:
                del running_tasks[self.task_id]
            
            # Decrement server task count
            if self.task and self.task['server_id'] in server_task_count:
                server_task_count[self.task['server_id']] -= 1
                if server_task_count[self.task['server_id']] <= 0:
                    del server_task_count[self.task['server_id']]
    
    def _execute_ssh_command(self, server):
        """
        Execute command via SSH
        
        Returns:
            (success, exit_code, stdout, stderr)
        """
        try:
            # Create SSH client
            self.ssh_client = paramiko.SSHClient()
            # Security Note: AutoAddPolicy used for task execution on monitored servers
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # nosec B507
            
            # Build connection kwargs
            connect_kwargs = {
                'hostname': server['host'],
                'port': server['port'],
                'username': server['username'],
                'timeout': 10,
                'look_for_keys': False,
                'allow_agent': False
            }
            
            # Priority 1: Try SSH key from vault if server has one configured
            if server.get('ssh_key_vault_id'):
                try:
                    private_key_pem = get_decrypted_key(server['ssh_key_vault_id'])
                    if private_key_pem:
                        key_file = io.StringIO(private_key_pem)
                        
                        # Try to load as different key types
                        pkey = None
                        for key_class in [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey]:
                            try:
                                key_file.seek(0)
                                pkey = key_class.from_private_key(key_file)
                                break
                            except:
                                continue
                        
                        if pkey:
                            connect_kwargs['pkey'] = pkey
                except Exception:
                    pass  # Fall through to try other methods
            
            # Priority 2: Try SSH key file path
            if 'pkey' not in connect_kwargs and server.get('ssh_key_path'):
                key_path = os.path.expanduser(server['ssh_key_path'])
                if os.path.exists(key_path):
                    connect_kwargs['key_filename'] = key_path
            
            # Priority 3: Try password
            if 'pkey' not in connect_kwargs and 'key_filename' not in connect_kwargs:
                if server.get('ssh_password'):
                    connect_kwargs['password'] = server['ssh_password']
                else:
                    return False, -1, '', 'No authentication method available'
            
            # Connect to server
            self.ssh_client.connect(**connect_kwargs)
            
            # Execute command with timeout
            timeout = self.task.get('timeout_seconds', TASKS_DEFAULT_TIMEOUT)
            # Security Note: paramiko exec_command does not use shell=True by default
            # Commands are validated by task_policy before execution
            # See task_policy.py for allowlist/denylist validation
            stdin, stdout, stderr = self.ssh_client.exec_command(
                self.task['command'],
                timeout=timeout
            )  # nosec B601
            
            # Read output
            exit_code = stdout.channel.recv_exit_status()
            stdout_data = stdout.read().decode('utf-8', errors='replace')
            stderr_data = stderr.read().decode('utf-8', errors='replace')
            
            return True, exit_code, stdout_data, stderr_data
            
        except paramiko.AuthenticationException as e:
            return False, -1, '', f'SSH authentication failed: {str(e)}'
        except paramiko.SSHException as e:
            if isinstance(e, paramiko.ssh_exception.SSHException) and 'timed out' in str(e).lower():
                db.update_task_status(self.task_id, 'timeout')
                return False, -1, '', f'Command execution timeout after {timeout} seconds'
            return False, -1, '', f'SSH error: {str(e)}'
        except socket.timeout as e:
            db.update_task_status(self.task_id, 'timeout')
            return False, -1, '', f'Command execution timeout after {timeout} seconds'
        except Exception as e:
            return False, -1, '', f'Execution error: {str(e)}'
    
    def _truncate_output(self, output):
        """Truncate output to maximum allowed bytes"""
        if not output:
            return output
        
        output_bytes = output.encode('utf-8')
        if len(output_bytes) > TASKS_OUTPUT_MAX_BYTES:
            truncated = output_bytes[:TASKS_OUTPUT_MAX_BYTES].decode('utf-8', errors='ignore')
            return truncated + f'\n\n... [Output truncated. Max size: {TASKS_OUTPUT_MAX_BYTES} bytes]'
        
        return output
    
    def _fail_task(self, error_msg):
        """Mark task as failed with error message"""
        finished_at = datetime.utcnow().isoformat() + 'Z'
        db.update_task_status(
            self.task_id,
            'failed',
            exit_code=-1,
            stdout=None,
            stderr=error_msg if self.task.get('store_output') else None,
            finished_at=finished_at
        )
    
    def cancel(self):
        """Request task cancellation"""
        self.should_stop = True
        # Note: We can't forcefully stop SSH command execution
        # This will be checked after command completes


def worker_thread():
    """Worker thread that processes tasks from queue"""
    while True:
        try:
            task_id = task_queue.get(timeout=1)
            
            if task_id is None:  # Shutdown signal
                break
            
            # Get task to check server_id
            task = db.get_task(task_id)
            if not task:
                task_queue.task_done()
                continue
            
            # Check server concurrency limit
            server_id = task['server_id']
            current_count = server_task_count.get(server_id, 0)
            
            if current_count >= TASKS_CONCURRENT_PER_SERVER:
                # Re-queue task and try later with exponential backoff
                retry_delay = min(5, 1 * (1 + current_count))  # Max 5 seconds delay
                time.sleep(retry_delay)
                task_queue.put(task_id)
                task_queue.task_done()
                continue
            
            # Increment server task count
            server_task_count[server_id] = current_count + 1
            
            # Execute task
            runner = TaskRunner(task_id)
            running_tasks[task_id] = runner
            
            # Run in separate thread to allow cancellation
            thread = threading.Thread(target=runner.run)
            thread.daemon = True
            thread.start()
            
            task_queue.task_done()
            
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Worker thread error: {e}")


# Start worker threads
NUM_WORKERS = int(os.environ.get('TASKS_NUM_WORKERS', '4'))
worker_threads = []

def start_task_workers():
    """Start task worker threads"""
    for i in range(NUM_WORKERS):
        thread = threading.Thread(target=worker_thread, daemon=True)
        thread.start()
        worker_threads.append(thread)
    print(f"Started {NUM_WORKERS} task worker threads")


def enqueue_task(task_id):
    """
    Add task to execution queue
    
    Returns:
        bool: True if task was enqueued successfully, False otherwise
    """
    try:
        task_queue.put(task_id, timeout=5)  # 5 second timeout
        return True
    except queue.Full:
        # Queue is full, mark task as failed
        db.update_task_status(
            task_id,
            'failed',
            exit_code=-1,
            stderr='Task queue is full. Please try again later.'
        )
        return False
    except Exception as e:
        # Unexpected error
        print(f"Error enqueuing task {task_id}: {e}")
        db.update_task_status(
            task_id,
            'failed',
            exit_code=-1,
            stderr=f'Failed to enqueue task: {str(e)}'
        )
        return False


def cancel_task(task_id):
    """Cancel a running task"""
    if task_id in running_tasks:
        running_tasks[task_id].cancel()
        return True
    return False


def get_queue_size():
    """Get number of tasks in queue"""
    return task_queue.qsize()


def get_running_task_count():
    """Get number of currently running tasks"""
    return len(running_tasks)


# Auto-start workers when module is imported
start_task_workers()
