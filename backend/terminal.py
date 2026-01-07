#!/usr/bin/env python3

"""
Web Terminal Backend for SSH Sessions
Provides WebSocket-based terminal access to remote servers with:
- SSH Key Vault integration
- Session tracking and audit logging
- Proper resource cleanup
- Multiple concurrent sessions support
"""

import asyncio
import websockets
import json
import paramiko
import threading
import sys
import os
import select
import io
import tempfile
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
from ssh_key_manager import get_decrypted_key

PORT = 9084  # WebSocket terminal port

# Session timeout (idle timeout in seconds)
SESSION_IDLE_TIMEOUT = 1800  # 30 minutes

class SSHTerminalSession:
    """
    Manages an SSH terminal session with WebSocket streaming
    
    Features:
    - SSH key vault integration
    - Session tracking in database
    - Audit logging
    - Automatic cleanup
    - Idle timeout detection
    """
    
    def __init__(self, server_id, websocket, user_id=None, ssh_key_id=None, session_id=None):
        self.server_id = server_id
        self.websocket = websocket
        self.user_id = user_id
        self.ssh_key_id = ssh_key_id
        self.session_id = session_id
        self.ssh_client = None
        self.channel = None
        self.running = False
        self.last_activity = time.time()
        self._cleanup_done = False
        
    async def connect(self):
        """Establish SSH connection to server with SSH key vault support"""
        try:
            # Get server details from database
            server = db.get_server(self.server_id, decrypt_password=True)
            
            if not server:
                await self.send_error("Server not found")
                return False
            
            # Create SSH client
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to server
            connect_kwargs = {
                'hostname': server['host'],
                'port': server['port'],
                'username': server['username'],
                'timeout': 10,
                'look_for_keys': False,
                'allow_agent': False
            }
            
            # Priority 1: Use SSH key from vault if provided
            if self.ssh_key_id:
                try:
                    private_key_pem = get_decrypted_key(self.ssh_key_id)
                    if private_key_pem:
                        # Write key to temporary file (secure, in-memory if possible)
                        # Paramiko requires either a file path or a key object
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
                        else:
                            await self.send_error("Failed to load SSH key from vault")
                            return False
                    else:
                        await self.send_error("Failed to decrypt SSH key")
                        return False
                except Exception as e:
                    await self.send_error(f"Error loading SSH key: {str(e)}")
                    return False
            
            # Priority 2: Use SSH key file path from server config
            elif server.get('ssh_key_path'):
                key_path = os.path.expanduser(server['ssh_key_path'])
                if os.path.exists(key_path):
                    connect_kwargs['key_filename'] = key_path
                else:
                    await self.send_error(f"SSH key file not found: {key_path}")
                    return False
            
            # Priority 3: Use password
            elif server.get('ssh_password'):
                connect_kwargs['password'] = server['ssh_password']
            
            else:
                await self.send_error("No SSH credentials configured")
                return False
            
            # Attempt connection
            self.ssh_client.connect(**connect_kwargs)
            
            # Create interactive shell channel
            self.channel = self.ssh_client.invoke_shell(
                term='xterm-256color',
                width=120,
                height=30
            )
            
            self.running = True
            self.last_activity = time.time()
            
            # Send success message
            await self.send_message({
                'type': 'connected',
                'message': f'Connected to {server["name"]} ({server["host"]})',
                'session_id': self.session_id
            })
            
            return True
        
        except Exception as e:
            await self.send_error(f"Connection failed: {str(e)}")
            return False
    
    async def send_message(self, data):
        """Send message to WebSocket client"""
        try:
            await self.websocket.send(json.dumps(data))
        except:
            pass
    
    async def send_error(self, message):
        """Send error message"""
        await self.send_message({'type': 'error', 'message': message})
    
    async def send_output(self, data):
        """Send terminal output"""
        await self.send_message({'type': 'output', 'data': data})
    
    async def handle_input(self, data):
        """Send input to SSH channel"""
        if self.channel and self.running:
            try:
                self.channel.send(data)
            except:
                self.running = False
    
    async def read_output(self):
        """Read output from SSH channel"""
        loop = asyncio.get_event_loop()
        
        while self.running:
            try:
                # Check if channel has data
                if self.channel and self.channel.recv_ready():
                    data = self.channel.recv(4096).decode('utf-8', errors='ignore')
                    await self.send_output(data)
                else:
                    # Small delay to prevent CPU spinning
                    await asyncio.sleep(0.01)
                
                # Check if channel is still open
                if self.channel and self.channel.exit_status_ready():
                    self.running = False
                    await self.send_message({'type': 'disconnected', 'message': 'SSH session ended'})
            
            except Exception as e:
                self.running = False
                await self.send_error(f"Read error: {str(e)}")
                break
    
    async def handle_input(self, data):
        """Send input to SSH channel and update activity"""
        if self.channel and self.running:
            try:
                self.channel.send(data)
                self.last_activity = time.time()
                # Update activity in database
                if self.session_id:
                    db.update_terminal_session_activity(self.session_id)
            except:
                self.running = False
    
    def check_idle_timeout(self):
        """Check if session has exceeded idle timeout"""
        if SESSION_IDLE_TIMEOUT > 0:
            idle_time = time.time() - self.last_activity
            if idle_time > SESSION_IDLE_TIMEOUT:
                return True
        return False
    
    async def resize_terminal(self, cols, rows):
        """Resize terminal"""
        if self.channel:
            try:
                self.channel.resize_pty(width=cols, height=rows)
            except:
                pass
    
    def close(self):
        """Close SSH connection and cleanup resources"""
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        self.running = False
        
        try:
            # Close SSH channel
            if self.channel:
                self.channel.close()
                self.channel = None
        except:
            pass
        
        try:
            # Close SSH client
            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
        except:
            pass
        
        # Update session in database
        if self.session_id:
            status = 'timeout' if self.check_idle_timeout() else 'closed'
            db.end_terminal_session(self.session_id, status=status)

# Active sessions
active_sessions = {}

async def handle_terminal(websocket, path):
    """Handle WebSocket terminal connection"""
    session = None
    session_id = None
    
    try:
        # First message should be authentication + server ID
        init_message = await websocket.recv()
        init_data = json.loads(init_message)
        
        # Verify authentication token
        token = init_data.get('token')
        server_id = init_data.get('server_id')
        
        if not token or not server_id:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Token and server_id required'
            }))
            return
        
        # Verify session
        auth_result = db.verify_session(token)
        
        if not auth_result.get('valid'):
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Invalid authentication token'
            }))
            return
        
        try:
            server_id = int(server_id)
        except ValueError:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Invalid server_id'
            }))
            return
        
        # Get user ID from auth result
        user_id = auth_result.get('user_id')
        role = auth_result.get('role', 'user')
        
        # Check RBAC - only admin and operator can use terminal
        if role not in ['admin', 'operator']:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Access denied. Admin or operator role required for terminal access'
            }))
            return
        
        # Get optional SSH key ID from vault
        ssh_key_id = init_data.get('ssh_key_id')
        
        # Create session in database
        session_result = db.create_terminal_session(
            server_id=server_id,
            user_id=user_id,
            ssh_key_id=ssh_key_id
        )
        
        if not session_result.get('success'):
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Failed to create session: {session_result.get("error")}'
            }))
            return
        
        session_id = session_result['session_id']
        
        # Create audit log for terminal access
        server = db.get_server(server_id)
        db.add_audit_log(
            user_id=user_id,
            action='terminal.open',
            target_type='server',
            target_id=str(server_id),
            meta={
                'server_name': server.get('name') if server else 'Unknown',
                'server_host': server.get('host') if server else 'Unknown',
                'ssh_key_id': ssh_key_id,
                'session_id': session_id
            }
        )
        
        # Create terminal session
        session = SSHTerminalSession(
            server_id=server_id,
            websocket=websocket,
            user_id=user_id,
            ssh_key_id=ssh_key_id,
            session_id=session_id
        )
        active_sessions[session_id] = session
        
        # Connect to server
        if not await session.connect():
            return
        
        # Start output reader
        output_task = asyncio.create_task(session.read_output())
        
        # Handle incoming messages
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get('type')
                
                if msg_type == 'input':
                    # User input
                    await session.handle_input(data.get('data', ''))
                
                elif msg_type == 'resize':
                    # Terminal resize
                    cols = data.get('cols', 80)
                    rows = data.get('rows', 24)
                    await session.resize_terminal(cols, rows)
                
                elif msg_type == 'close':
                    # Client requested close
                    break
            
            except json.JSONDecodeError:
                pass
        
        # Cancel output task
        output_task.cancel()
    
    except websockets.exceptions.ConnectionClosed:
        print(f"WebSocket connection closed for session {session_id}")
    
    except Exception as e:
        print(f"Terminal error: {e}")
    
    finally:
        # Cleanup
        if session:
            session.close()
            
            # Add audit log for terminal close
            if session.user_id:
                db.add_audit_log(
                    user_id=session.user_id,
                    action='terminal.close',
                    target_type='server',
                    target_id=str(session.server_id),
                    meta={
                        'session_id': session.session_id,
                        'duration_seconds': int(time.time() - session.last_activity) if session.last_activity else 0
                    }
                )
        
        if session_id and session_id in active_sessions:
            del active_sessions[session_id]

async def main():
    """Start WebSocket server"""
    # Initialize database
    db.init_database()
    
    print(f'╔══════════════════════════════════════════════════════════╗')
    print(f'║  Web Terminal Server                                     ║')
    print(f'╚══════════════════════════════════════════════════════════╝')
    print(f'\n🖥️  WebSocket server running on ws://0.0.0.0:{PORT}')
    print(f'🔒 Authentication required')
    print(f'\n📝 Protocol:')
    print(f'   1. Connect to ws://server:{PORT}')
    print(f'   2. Send: {{"token": "...", "server_id": 123}}')
    print(f'   3. Send: {{"type": "input", "data": "command\\n"}}')
    print(f'   4. Receive: {{"type": "output", "data": "..."}}')
    print(f'\n✨ Press Ctrl+C to stop')
    
    async with websockets.serve(handle_terminal, '0.0.0.0', PORT):
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n\n👋 Shutting down terminal server...')
