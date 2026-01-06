#!/usr/bin/env python3

"""
Web Terminal Backend for SSH Sessions
Provides WebSocket-based terminal access to remote servers
"""

import asyncio
import websockets
import json
import paramiko
import threading
import sys
import os
import select

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db

PORT = 9084  # WebSocket terminal port

class SSHTerminalSession:
    """
    Manages an SSH terminal session with WebSocket streaming
    """
    
    def __init__(self, server_id, websocket):
        self.server_id = server_id
        self.websocket = websocket
        self.ssh_client = None
        self.channel = None
        self.running = False
        
    async def connect(self):
        """Establish SSH connection to server"""
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
            
            if server.get('ssh_key_path'):
                key_path = os.path.expanduser(server['ssh_key_path'])
                if os.path.exists(key_path):
                    connect_kwargs['key_filename'] = key_path
            elif server.get('ssh_password'):
                connect_kwargs['password'] = server['ssh_password']
            else:
                await self.send_error("No SSH credentials configured")
                return False
            
            self.ssh_client.connect(**connect_kwargs)
            
            # Create interactive shell channel
            self.channel = self.ssh_client.invoke_shell(
                term='xterm-256color',
                width=120,
                height=30
            )
            
            self.running = True
            
            # Send success message
            await self.send_message({
                'type': 'connected',
                'message': f'Connected to {server["name"]} ({server["host"]})'
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
    
    async def resize_terminal(self, cols, rows):
        """Resize terminal"""
        if self.channel:
            try:
                self.channel.resize_pty(width=cols, height=rows)
            except:
                pass
    
    def close(self):
        """Close SSH connection"""
        self.running = False
        
        if self.channel:
            try:
                self.channel.close()
            except:
                pass
        
        if self.ssh_client:
            try:
                self.ssh_client.close()
            except:
                pass

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
        
        # Create terminal session
        session_id = f"{server_id}_{auth_result['user_id']}"
        session = SSHTerminalSession(server_id, websocket)
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
        pass
    
    except Exception as e:
        print(f"Terminal error: {e}")
    
    finally:
        # Cleanup
        if session:
            session.close()
        
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
