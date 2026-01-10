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
import uuid
import signal

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
from ssh_key_manager import get_decrypted_key
from observability import StructuredLogger, get_metrics_collector

PORT = 9084  # WebSocket terminal port

# Session timeout (idle timeout in seconds)
SESSION_IDLE_TIMEOUT = int(os.environ.get("TERMINAL_IDLE_TIMEOUT_SECONDS", "1800"))  # 30 minutes default

# Initialize structured logger
logger = StructuredLogger("terminal")
metrics = get_metrics_collector()

# Global server for graceful shutdown
ws_server = None


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
                logger.error(
                    "Terminal connection failed - server not found",
                    session_id=self.session_id,
                    server_id=self.server_id,
                    user_id=self.user_id,
                )
                await self.send_error("Server not found")
                return False

            logger.info(
                "Establishing terminal SSH connection",
                session_id=self.session_id,
                server_id=self.server_id,
                server_name=server.get("name"),
                user_id=self.user_id,
                ssh_key_id=self.ssh_key_id,
            )

            # Create SSH client
            self.ssh_client = paramiko.SSHClient()
            # Security Note: AutoAddPolicy used for web terminal access to monitored servers
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # nosec B507

            # Connect to server
            connect_kwargs = {
                "hostname": server["host"],
                "port": server["port"],
                "username": server["username"],
                "timeout": 10,
                "look_for_keys": False,
                "allow_agent": False,
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
                            connect_kwargs["pkey"] = pkey
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
            elif server.get("ssh_key_path"):
                key_path = os.path.expanduser(server["ssh_key_path"])
                if os.path.exists(key_path):
                    connect_kwargs["key_filename"] = key_path
                else:
                    await self.send_error(f"SSH key file not found: {key_path}")
                    return False

            # Priority 3: Use password
            elif server.get("ssh_password"):
                connect_kwargs["password"] = server["ssh_password"]

            else:
                await self.send_error("No SSH credentials configured")
                return False

            # Attempt connection
            self.ssh_client.connect(**connect_kwargs)

            # Create interactive shell channel
            self.channel = self.ssh_client.invoke_shell(term="xterm-256color", width=120, height=30)

            self.running = True
            self.last_activity = time.time()

            # Add audit log
            if self.user_id:
                db.add_audit_log(
                    user_id=self.user_id,
                    action="terminal.connect",
                    target_type="server",
                    target_id=str(self.server_id),
                    meta={"session_id": self.session_id, "ssh_key_id": self.ssh_key_id, "hostname": server["host"]},
                )

            logger.info(
                "Terminal SSH connection established",
                session_id=self.session_id,
                server_id=self.server_id,
                server_name=server.get("name"),
                user_id=self.user_id,
            )

            # Update metrics
            metrics.terminal_sessions += 1

            # Send success message
            await self.send_message(
                {
                    "type": "connected",
                    "message": f'Connected to {server["name"]} ({server["host"]})',
                    "session_id": self.session_id,
                }
            )

            return True

        except paramiko.AuthenticationException:
            logger.warning(
                "Terminal authentication failed",
                session_id=self.session_id,
                server_id=self.server_id,
                user_id=self.user_id,
            )
            await self.send_error("Authentication failed")
            return False
        except Exception as e:
            logger.error(
                "Terminal connection error",
                session_id=self.session_id,
                server_id=self.server_id,
                user_id=self.user_id,
                error=str(e),
            )
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
        await self.send_message({"type": "error", "message": message})

    async def send_output(self, data):
        """Send terminal output"""
        await self.send_message({"type": "output", "data": data})

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
                    data = self.channel.recv(4096).decode("utf-8", errors="ignore")
                    await self.send_output(data)
                else:
                    # Small delay to prevent CPU spinning
                    await asyncio.sleep(0.01)

                # Check if channel is still open
                if self.channel and self.channel.exit_status_ready():
                    self.running = False
                    await self.send_message({"type": "disconnected", "message": "SSH session ended"})

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
                logger.info(
                    "Terminal session idle timeout",
                    session_id=self.session_id,
                    server_id=self.server_id,
                    user_id=self.user_id,
                    idle_seconds=int(idle_time),
                )
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

        duration_seconds = int(time.time() - self.last_activity) if hasattr(self, "last_activity") else 0
        is_timeout = self.check_idle_timeout()

        logger.info(
            "Closing terminal session",
            session_id=self.session_id,
            server_id=self.server_id,
            user_id=self.user_id,
            duration_seconds=duration_seconds,
            reason="timeout" if is_timeout else "closed",
        )

        # Update metrics
        if metrics.terminal_sessions > 0:
            metrics.terminal_sessions -= 1

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
            status = "timeout" if is_timeout else "closed"
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
        token = init_data.get("token")
        server_id = init_data.get("server_id")

        if not token or not server_id:
            logger.warning(
                "Terminal connection missing credentials",
                remote_host=websocket.remote_address[0] if websocket.remote_address else "unknown",
            )
            await websocket.send(json.dumps({"type": "error", "message": "Token and server_id required"}))
            return

        # Verify session
        auth_result = db.verify_session(token)

        if not auth_result.get("valid"):
            logger.warning(
                "Terminal connection invalid token",
                remote_host=websocket.remote_address[0] if websocket.remote_address else "unknown",
            )
            await websocket.send(json.dumps({"type": "error", "message": "Invalid authentication token"}))
            return

        try:
            server_id = int(server_id)
        except ValueError:
            logger.warning(
                "Terminal connection invalid server_id",
                server_id=server_id,
                remote_host=websocket.remote_address[0] if websocket.remote_address else "unknown",
            )
            await websocket.send(json.dumps({"type": "error", "message": "Invalid server_id"}))
            return

        # Get user ID from auth result
        user_id = auth_result.get("user_id")
        role = auth_result.get("role", "user")

        # Check RBAC - only admin and operator can use terminal
        if role not in ["admin", "operator"]:
            await websocket.send(
                json.dumps(
                    {"type": "error", "message": "Access denied. Admin or operator role required for terminal access"}
                )
            )
            return

        # Get optional SSH key ID from vault
        ssh_key_id = init_data.get("ssh_key_id")

        # Create session in database
        session_result = db.create_terminal_session(server_id=server_id, user_id=user_id, ssh_key_id=ssh_key_id)

        if not session_result.get("success"):
            await websocket.send(
                json.dumps({"type": "error", "message": f'Failed to create session: {session_result.get("error")}'})
            )
            return

        session_id = session_result["session_id"]

        # Create audit log for terminal access
        server = db.get_server(server_id)
        db.add_audit_log(
            user_id=user_id,
            action="terminal.open",
            target_type="server",
            target_id=str(server_id),
            meta={
                "server_name": server.get("name") if server else "Unknown",
                "server_host": server.get("host") if server else "Unknown",
                "ssh_key_id": ssh_key_id,
                "session_id": session_id,
            },
        )

        # Create terminal session
        session = SSHTerminalSession(
            server_id=server_id, websocket=websocket, user_id=user_id, ssh_key_id=ssh_key_id, session_id=session_id
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
                msg_type = data.get("type")

                if msg_type == "input":
                    # User input
                    await session.handle_input(data.get("data", ""))

                elif msg_type == "resize":
                    # Terminal resize
                    cols = data.get("cols", 80)
                    rows = data.get("rows", 24)
                    await session.resize_terminal(cols, rows)

                elif msg_type == "close":
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
                    action="terminal.close",
                    target_type="server",
                    target_id=str(session.server_id),
                    meta={
                        "session_id": session.session_id,
                        "duration_seconds": int(time.time() - session.last_activity) if session.last_activity else 0,
                    },
                )

        if session_id and session_id in active_sessions:
            del active_sessions[session_id]


async def main():
    """Start WebSocket server"""
    global ws_server

    # Initialize database
    db.init_database()

    logger.info(
        "Starting Terminal WebSocket Server", port=PORT, idle_timeout_seconds=SESSION_IDLE_TIMEOUT, version="Phase 6"
    )

    print(f"╔══════════════════════════════════════════════════════════╗")
    print(f"║  Web Terminal Server                                     ║")
    print(f"╚══════════════════════════════════════════════════════════╝")
    print(f"\n🖥️  WebSocket server running on ws://0.0.0.0:{PORT}")
    print(f"🔒 Authentication required")
    print(f"⏱️  Idle timeout: {SESSION_IDLE_TIMEOUT} seconds")
    print(f"\n📝 Protocol:")
    print(f"   1. Connect to ws://server:{PORT}")
    print(f'   2. Send: {{"token": "...", "server_id": 123}}')
    print(f'   3. Send: {{"type": "input", "data": "command\\n"}}')
    print(f'   4. Receive: {{"type": "output", "data": "..."}}')
    print(f"\n✨ Press Ctrl+C to stop")

    # Security: Binding to 0.0.0.0 exposes the service to all network interfaces
    # This is intentional for production use where the service needs to be accessible
    # from other machines. Use firewall rules to restrict access in production.
    ws_server = await websockets.serve(handle_terminal, "0.0.0.0", PORT)  # nosec B104
    await asyncio.Future()  # Run forever


def graceful_shutdown():
    """
    Handle graceful shutdown on SIGTERM/SIGINT
    - Close all active terminal sessions
    - Mark sessions as interrupted in database
    - Close WebSocket server
    """
    logger.info("Received shutdown signal, shutting down gracefully")
    print(f"\n\n🛑 Shutting down terminal server gracefully...")

    try:
        # Close all active sessions
        logger.info(f"Closing {len(active_sessions)} active terminal sessions")
        for session_id, session in list(active_sessions.items()):
            try:
                # Mark as interrupted in database
                db.end_terminal_session(session_id, status="interrupted")
                # Close SSH connection
                session.close()
                logger.info(f"Closed terminal session {session_id}")
            except Exception as e:
                logger.error(f"Error closing session {session_id}", error=str(e))

        active_sessions.clear()

        # Close WebSocket server
        if ws_server:
            logger.info("Closing WebSocket server")
            ws_server.close()

        logger.info("Terminal server shutdown complete")
        print("✓ Terminal server shutdown complete")

    except Exception as e:
        logger.error("Error during graceful shutdown", error=str(e))
        print(f"⚠️  Error during shutdown: {e}")


if __name__ == "__main__":
    # Setup signal handlers
    def signal_handler(signum, frame):
        graceful_shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        graceful_shutdown()
