#!/usr/bin/env python3

"""
WebSocket Server for Real-time Monitoring Updates
Broadcasts server metrics to all connected clients
"""

import asyncio
import websockets
import json
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
import ssh_manager as ssh

PORT = 9085  # WebSocket port for monitoring updates
UPDATE_INTERVAL = 3  # Update every 3 seconds

# Store connected clients
connected_clients = set()

# Statistics for monitoring
stats = {
    'total_clients': 0,
    'active_connections': 0,
    'messages_sent': 0,
    'uptime': datetime.now()
}

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
    
    # Add client to connected set
    connected_clients.add(websocket)
    stats['total_clients'] += 1
    stats['active_connections'] = len(connected_clients)
    
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
                    server_ids = data.get('server_ids', [])
                    # Store subscription preferences (future feature)
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
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Client disconnected: {client_id}")
    except Exception as e:
        print(f"Error with client {client_id}: {e}")
    finally:
        # Remove client from connected set
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        stats['active_connections'] = len(connected_clients)
        print(f"Active connections: {stats['active_connections']}")


async def stats_reporter():
    """
    Periodically report server statistics
    """
    while True:
        await asyncio.sleep(60)  # Report every minute
        
        uptime = datetime.now() - stats['uptime']
        hours = uptime.total_seconds() / 3600
        
        print(f"\n=== WebSocket Server Stats ===")
        print(f"Uptime: {hours:.2f} hours")
        print(f"Total clients connected: {stats['total_clients']}")
        print(f"Active connections: {stats['active_connections']}")
        print(f"Messages sent: {stats['messages_sent']}")
        print(f"===============================\n")


async def main():
    """
    Start WebSocket server
    """
    print(f"\n{'='*60}")
    print(f"  WebSocket Monitoring Server v1.0")
    print(f"{'='*60}")
    print(f"  Port: {PORT}")
    print(f"  Update Interval: {UPDATE_INTERVAL}s")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Initialize database
    db.init_database()
    print("Database initialized")
    
    # Start WebSocket server
    async with websockets.serve(handle_client, "0.0.0.0", PORT):
        print(f"WebSocket server listening on ws://0.0.0.0:{PORT}")
        print("Waiting for clients to connect...\n")
        
        # Run broadcast and stats reporter concurrently
        await asyncio.gather(
            broadcast_server_stats(),
            stats_reporter()
        )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nShutting down WebSocket server...")
        print("Goodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
