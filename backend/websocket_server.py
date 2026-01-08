#!/usr/bin/env python3

"""
WebSocket Server for Real-time Monitoring Updates
Broadcasts server metrics to all connected clients
"""

import asyncio
import json
import os
import signal
import sys
from datetime import datetime

import websockets

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db  # noqa: E402
import ssh_manager as ssh  # noqa: E402
from observability import StructuredLogger, get_metrics_collector  # noqa: E402

PORT = 9085  # WebSocket port for monitoring updates
UPDATE_INTERVAL = 3  # Update every 3 seconds

# Store connected clients
connected_clients = set()

# Initialize structured logger
logger = StructuredLogger('websocket_monitor')
metrics = get_metrics_collector()

# Statistics for monitoring
stats = {
    'total_clients': 0,
    'active_connections': 0,
    'messages_sent': 0,
    'uptime': datetime.now()
}

# Global server for graceful shutdown
ws_server = None


async def broadcast_server_stats():
    """
    Fetch stats from all servers and broadcast to all clients
    """
    while True:
        try:
            # Get all servers from database
            servers = db.list_servers()

            if not servers:
                await asyncio.sleep(UPDATE_INTERVAL)
                continue

            # Collect stats from all servers
            all_stats = []

            for server in servers:
                server_id = server['id']

                # Skip if no clients are connected
                if not connected_clients:
                    continue

                try:
                    # Get server with decrypted password
                    server_detail = db.get_server(server_id, decrypt_password=True)
                    if not server_detail:
                        continue

                    # Get remote stats via SSH
                    result = ssh.get_remote_agent_data(
                        host=server_detail['host'],
                        port=server_detail['port'],
                        username=server_detail['username'],
                        key_path=server_detail.get('ssh_key_path'),
                        password=server_detail.get('ssh_password'),
                        agent_port=server_detail.get('agent_port', 8083)
                    )

                    if result['success']:
                        # Add server ID and update status
                        data = result['data']
                        data['server_id'] = server_id
                        data['server_name'] = server_detail['name']
                        data['status'] = 'online'
                        data['timestamp'] = datetime.now().isoformat()

                        all_stats.append(data)

                        # Update server status in database
                        db.update_server_status(server_id, 'online')

                    else:
                        # Server is offline or agent not responding
                        all_stats.append({
                            'server_id': server_id,
                            'server_name': server_detail['name'],
                            'status': 'offline',
                            'error': result.get('error', 'Connection failed'),
                            'timestamp': datetime.now().isoformat()
                        })

                        # Update server status in database
                        db.update_server_status(server_id, 'offline')

                except Exception as e:
                    print(f"Error fetching stats for server {server_id}: {e}")
                    all_stats.append({
                        'server_id': server_id,
                        'server_name': server.get('name', 'Unknown'),
                        'status': 'error',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })

            # Broadcast to all connected clients
            if connected_clients and all_stats:
                message = json.dumps({
                    'type': 'stats_update',
                    'data': all_stats,
                    'timestamp': datetime.now().isoformat()
                })

                # Send to all clients
                disconnected = set()
                for client in connected_clients:
                    try:
                        await client.send(message)
                        stats['messages_sent'] += 1
                    except websockets.exceptions.ConnectionClosed:
                        disconnected.add(client)
                    except Exception as e:
                        print(f"Error sending to client: {e}")
                        disconnected.add(client)

                # Remove disconnected clients
                connected_clients.difference_update(disconnected)
                stats['active_connections'] = len(connected_clients)

        except Exception as e:
            print(f"Error in broadcast loop: {e}")

        # Wait before next update
        await asyncio.sleep(UPDATE_INTERVAL)


async def handle_client(websocket, path):
    """
    Handle individual WebSocket client connection
    """
    client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"

    logger.info('WebSocket monitoring client connected',
                client_id=client_id,
                path=path)

    # Add client to connected set
    connected_clients.add(websocket)
    stats['total_clients'] += 1
    stats['active_connections'] = len(connected_clients)

    # Update metrics
    metrics.websocket_connections = len(connected_clients)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Client connected: {client_id}")
    print(f"Active connections: {stats['active_connections']}")

    try:
        # Send welcome message
        welcome_msg = json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'Connected to monitoring WebSocket server',
            'update_interval': UPDATE_INTERVAL,
            'timestamp': datetime.now().isoformat()
        })
        await websocket.send(welcome_msg)

        # Listen for messages from client
        async for message in websocket:
            try:
                data = json.loads(message)

                # Handle ping/pong for keep-alive
                if data.get('type') == 'ping':
                    pong_msg = json.dumps({
                        'type': 'pong',
                        'timestamp': datetime.now().isoformat()
                    })
                    await websocket.send(pong_msg)

                # Handle request for immediate update
                elif data.get('type') == 'request_update':
                    # This will be handled by the broadcast loop
                    pass

                # Handle server subscription (future feature)
                elif data.get('type') == 'subscribe':
                    # TODO: Implement server-specific subscriptions
                    # This will allow clients to subscribe to updates from specific servers only
                    # Expected format: {'type': 'subscribe', 'server_ids': [1, 2, 3]}
                    pass

            except json.JSONDecodeError:
                error_msg = json.dumps({
                    'type': 'error',
                    'message': 'Invalid JSON message',
                    'timestamp': datetime.now().isoformat()
                })
                await websocket.send(error_msg)
            except Exception as e:
                print(f"Error processing client message: {e}")

    except websockets.exceptions.ConnectionClosed:
        logger.info('WebSocket monitoring client disconnected',
                    client_id=client_id)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Client disconnected: {client_id}")
    except Exception as e:
        logger.error('WebSocket monitoring client error',
                     client_id=client_id,
                     error=str(e))
        print(f"Error with client {client_id}: {e}")
    finally:
        # Remove client from connected set
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        stats['active_connections'] = len(connected_clients)

        # Update metrics
        metrics.websocket_connections = len(connected_clients)

        logger.info('WebSocket monitoring client cleanup complete',
                    client_id=client_id,
                    active_connections=len(connected_clients))
        print(f"Active connections: {stats['active_connections']}")


async def stats_reporter():
    """
    Periodically report server statistics
    """
    while True:
        await asyncio.sleep(60)  # Report every minute

        uptime = datetime.now() - stats['uptime']
        hours = uptime.total_seconds() / 3600

        print("\n=== WebSocket Server Stats ===")
        print(f"Uptime: {hours:.2f} hours")
        print(f"Total clients connected: {stats['total_clients']}")
        print(f"Active connections: {stats['active_connections']}")
        print(f"Messages sent: {stats['messages_sent']}")
        print("===============================\n")


async def main():
    """
    Start WebSocket server
    """
    # Initialize database
    db.init_database()

    logger.info('Starting WebSocket Monitoring Server',
                port=PORT,
                update_interval_seconds=UPDATE_INTERVAL,
                version='Phase 6')

    print(f"\n{'='*60}")
    print("  WebSocket Monitoring Server v1.0")
    print(f"{'='*60}")
    print(f"  Port: {PORT}")
    print(f"  Update Interval: {UPDATE_INTERVAL}s")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    print("Database initialized")

    # Start WebSocket server
    # Bind address is configurable via WEBSOCKET_BIND_HOST env var (defaults to 0.0.0.0)
    # Security: Use firewall rules to restrict access as needed
    bind_host = os.getenv('WEBSOCKET_BIND_HOST', '0.0.0.0')
    async with websockets.serve(handle_client, bind_host, PORT):  # nosec B104 - bind address is configurable for production use
        print(f"WebSocket server listening on ws://{bind_host}:{PORT}")
        print("Waiting for clients to connect...\n")

        # Run broadcast and stats reporter concurrently
        await asyncio.gather(
            broadcast_server_stats(),
            stats_reporter()
        )


def graceful_shutdown():
    """
    Handle graceful shutdown on SIGTERM/SIGINT
    - Close all WebSocket connections
    - Close SSH connections
    - Flush logs
    """
    logger.info('Received shutdown signal, shutting down gracefully')
    print('\n\n🛑 Shutting down WebSocket monitoring server gracefully...')

    try:
        # Close all connected clients
        logger.info(f'Closing {len(connected_clients)} active WebSocket connections')
        for client in list(connected_clients):
            try:
                asyncio.create_task(client.close())
            except Exception as e:
                logger.error('Error closing WebSocket client', error=str(e))

        connected_clients.clear()

        # Close SSH connections
        try:
            ssh.ssh_pool.close_all()
        except Exception as e:
            logger.error('Failed to close SSH connections', error=str(e))

        logger.info('WebSocket monitoring server shutdown complete')
        print('✓ WebSocket monitoring server shutdown complete')

    except Exception as e:
        logger.error('Error during graceful shutdown', error=str(e))
        print(f'⚠️  Error during shutdown: {e}')


if __name__ == '__main__':
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
    except Exception as e:
        logger.error('WebSocket monitoring server fatal error', error=str(e))
        print(f"Fatal error: {e}")
        sys.exit(1)
