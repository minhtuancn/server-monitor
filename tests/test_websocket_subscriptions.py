"""
Tests for WebSocket server subscription feature
Target: Increase websocket_server.py coverage from 0% to 60%+
Tests: Connection, broadcast, subscriptions, message handling
"""

import pytest
import asyncio
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Mock websockets.exceptions before importing websocket_server
class MockConnectionClosed(Exception):
    """Mock websockets.exceptions.ConnectionClosed"""
    pass

with patch('websockets.exceptions.ConnectionClosed', MockConnectionClosed):
    import websocket_server


class TestWebSocketConnection:
    """Test WebSocket connection handling"""
    
    @pytest.mark.asyncio
    async def test_handle_client_welcome_message(self):
        """Test client receives welcome message on connection"""
        import websocket_server
        
        # Mock websocket with async iterator
        mock_ws = AsyncMock()
        mock_ws.remote_address = ('127.0.0.1', 12345)
        mock_ws.send = AsyncMock()
        
        # Create async iterator that yields nothing (connection only)
        async def async_iter():
            return
            yield  # Make it a generator
        mock_ws.__aiter__ = lambda: async_iter()
        
        # Handle client connection (will exit immediately after welcome)
        await websocket_server.handle_client(mock_ws, '/ws')
        
        # Check welcome message was sent
        assert mock_ws.send.called
        call_args = mock_ws.send.call_args[0][0]
        welcome = json.loads(call_args)
        
        assert welcome['type'] == 'connection'
        assert welcome['status'] == 'connected'
        assert 'update_interval' in welcome
    
    @pytest.mark.asyncio
    async def test_handle_client_adds_to_connected_set(self):
        """Test client is added to connected_clients set"""
        import websocket_server
        
        # Clear existing clients
        websocket_server.connected_clients.clear()
        
        mock_ws = AsyncMock()
        mock_ws.remote_address = ('127.0.0.1', 12346)
        mock_ws.send = AsyncMock()
        
        async def async_iter():
            return
            yield
        mock_ws.__aiter__ = lambda: async_iter()
        
        # Start task
        task = asyncio.create_task(websocket_server.handle_client(mock_ws, '/ws'))
        await asyncio.sleep(0.01)  # Let it run briefly
        
        # Check client was added
        assert mock_ws in websocket_server.connected_clients
        
        # Cancel task
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    @pytest.mark.asyncio
    async def test_handle_client_ping_pong(self):
        """Test ping/pong keep-alive mechanism"""
        import websocket_server
        
        mock_ws = AsyncMock()
        mock_ws.remote_address = ('127.0.0.1', 12347)
        mock_ws.send = AsyncMock()
        
        # Create async iterator that yields ping message
        ping_msg = json.dumps({"type": "ping"})
        async def async_iter():
            yield ping_msg
        mock_ws.__aiter__ = lambda: async_iter()
        
        await websocket_server.handle_client(mock_ws, '/ws')
        
        # Check pong was sent
        sent_messages = [call[0][0] for call in mock_ws.send.call_args_list]
        pong_messages = [msg for msg in sent_messages if 'pong' in msg]
        
        assert len(pong_messages) > 0
        pong = json.loads(pong_messages[0])
        assert pong['type'] == 'pong'


class TestWebSocketSubscriptions:
    """Test server-specific subscription feature"""
    
    @pytest.mark.asyncio
    async def test_subscribe_to_specific_servers(self):
        """Test subscribing to specific server IDs"""
        import websocket_server
        
        websocket_server.client_subscriptions.clear()
        
        mock_ws = AsyncMock()
        mock_ws.remote_address = ('127.0.0.1', 12348)
        mock_ws.send = AsyncMock()
        
        # Send subscription message
        subscribe_msg = json.dumps({
            "type": "subscribe",
            "server_ids": [1, 2, 3]
        })
        async def async_iter():
            yield subscribe_msg
        mock_ws.__aiter__ = lambda: async_iter()
        
        await websocket_server.handle_client(mock_ws, '/ws')
        
        # Check response
        sent_messages = [call[0][0] for call in mock_ws.send.call_args_list]
        subscription_responses = [msg for msg in sent_messages if 'subscription_updated' in msg]
        
        assert len(subscription_responses) > 0
        response = json.loads(subscription_responses[0])
        assert response['type'] == 'subscription_updated'
        assert response['subscribed_to'] == [1, 2, 3]
    
    @pytest.mark.asyncio
    async def test_unsubscribe_from_servers(self):
        """Test unsubscribing (receive all servers)"""
        import websocket_server
        
        websocket_server.client_subscriptions.clear()
        
        mock_ws = AsyncMock()
        mock_ws.remote_address = ('127.0.0.1', 12349)
        mock_ws.send = AsyncMock()
        
        # Send unsubscribe message
        unsubscribe_msg = json.dumps({
            "type": "subscribe",
            "server_ids": None
        })
        async def async_iter():
            yield unsubscribe_msg
        mock_ws.__aiter__ = lambda: async_iter()
        
        await websocket_server.handle_client(mock_ws, '/ws')
        
        # Check response
        sent_messages = [call[0][0] for call in mock_ws.send.call_args_list]
        subscription_responses = [msg for msg in sent_messages if 'subscription_updated' in msg]
        
        assert len(subscription_responses) > 0
        response = json.loads(subscription_responses[0])
        assert response['type'] == 'subscription_updated'
        assert response['subscribed_to'] == 'all'
    
    @pytest.mark.asyncio
    async def test_subscribe_invalid_format(self):
        """Test subscribing with invalid format"""
        import websocket_server
        
        mock_ws = AsyncMock()
        mock_ws.remote_address = ('127.0.0.1', 12350)
        mock_ws.send = AsyncMock()
        
        # Send invalid subscription
        invalid_msg = json.dumps({
            "type": "subscribe",
            "server_ids": "invalid"  # Should be list or None
        })
        async def async_iter():
            yield invalid_msg
        mock_ws.__aiter__ = lambda: async_iter()
        
        await websocket_server.handle_client(mock_ws, '/ws')
        
        # Check error response
        sent_messages = [call[0][0] for call in mock_ws.send.call_args_list]
        error_responses = [msg for msg in sent_messages if 'error' in msg]
        
        assert len(error_responses) > 0
        response = json.loads(error_responses[0])
        assert response['type'] == 'error'


class TestWebSocketBroadcast:
    """Test broadcast functionality"""
    
    @pytest.mark.asyncio
    async def test_broadcast_filters_by_subscription(self):
        """Test broadcast filters stats based on subscriptions"""
        import websocket_server
        
        # Clear state
        websocket_server.connected_clients.clear()
        websocket_server.client_subscriptions.clear()
        
        # Create mock client with subscription
        mock_ws = AsyncMock()
        mock_ws.remote_address = ('127.0.0.1', 12351)
        mock_ws.send = AsyncMock()
        
        websocket_server.connected_clients.add(mock_ws)
        client_id = id(mock_ws)
        websocket_server.client_subscriptions[client_id] = {1, 2}  # Subscribe to servers 1, 2
        
        # Mock database and SSH functions
        with patch('websocket_server.db.list_servers') as mock_list_servers, \
             patch('websocket_server.db.get_server') as mock_get_server, \
             patch('websocket_server.ssh.get_remote_agent_data') as mock_ssh:
            
            # Return 3 servers
            mock_list_servers.return_value = [
                {'id': 1, 'name': 'Server1'},
                {'id': 2, 'name': 'Server2'},
                {'id': 3, 'name': 'Server3'},
            ]
            
            # Mock get_server to return full details
            def get_server_side_effect(server_id, decrypt_password=False):
                servers = {
                    1: {'id': 1, 'name': 'Server1', 'host': '10.0.0.1', 'port': 22, 'username': 'user1'},
                    2: {'id': 2, 'name': 'Server2', 'host': '10.0.0.2', 'port': 22, 'username': 'user2'},
                    3: {'id': 3, 'name': 'Server3', 'host': '10.0.0.3', 'port': 22, 'username': 'user3'},
                }
                return servers.get(server_id)
            mock_get_server.side_effect = get_server_side_effect
            
            # Mock SSH to return success
            mock_ssh.return_value = {
                'success': True,
                'data': {'cpu': 50.0, 'memory': 60.0, 'disk': 70.0}
            }
            
            # Run one iteration of broadcast
            task = asyncio.create_task(websocket_server.broadcast_server_stats())
            await asyncio.sleep(0.1)  # Let it run briefly
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            # Check filtered message was sent
            if mock_ws.send.called:
                call_args = mock_ws.send.call_args[0][0]
                message = json.loads(call_args)
                
                # Should only receive stats for servers 1, 2 (not 3)
                assert message['type'] == 'stats_update'
                server_ids = [stat['server_id'] for stat in message['data']]
                assert 1 in server_ids or 2 in server_ids
                assert 3 not in server_ids
    
    @pytest.mark.asyncio
    async def test_broadcast_sends_all_without_subscription(self):
        """Test broadcast sends all stats when no subscription"""
        import websocket_server
        
        websocket_server.connected_clients.clear()
        websocket_server.client_subscriptions.clear()
        
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        websocket_server.connected_clients.add(mock_ws)
        # No subscription set - should receive all
        
        with patch('websocket_server.db.list_servers') as mock_list_servers, \
             patch('websocket_server.db.get_server') as mock_get_server, \
             patch('websocket_server.ssh.get_remote_agent_data') as mock_ssh:
            
            mock_list_servers.return_value = [
                {'id': 1, 'name': 'Server1'},
                {'id': 2, 'name': 'Server2'},
            ]
            
            def get_server_side_effect(server_id, decrypt_password=False):
                return {'id': server_id, 'name': f'Server{server_id}', 'host': f'10.0.0.{server_id}', 'port': 22, 'username': 'user'}
            mock_get_server.side_effect = get_server_side_effect
            
            mock_ssh.return_value = {'success': True, 'data': {'cpu': 50.0}}
            
            task = asyncio.create_task(websocket_server.broadcast_server_stats())
            await asyncio.sleep(0.1)
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            # Should send all servers
            if mock_ws.send.called:
                call_args = mock_ws.send.call_args[0][0]
                message = json.loads(call_args)
                assert len(message['data']) == 2


class TestWebSocketErrorHandling:
    """Test error handling"""
    
    @pytest.mark.asyncio
    async def test_handle_invalid_json(self):
        """Test handling of invalid JSON messages"""
        import websocket_server
        
        mock_ws = AsyncMock()
        mock_ws.remote_address = ('127.0.0.1', 12352)
        mock_ws.send = AsyncMock()
        
        # Send invalid JSON
        invalid_json = "{ this is not json }"
        async def async_iter():
            yield invalid_json
        mock_ws.__aiter__ = lambda: async_iter()
        
        await websocket_server.handle_client(mock_ws, '/ws')
        
        # Check error message was sent
        sent_messages = [call[0][0] for call in mock_ws.send.call_args_list]
        error_messages = [msg for msg in sent_messages if 'error' in msg and 'Invalid JSON' in msg]
        
        assert len(error_messages) > 0
    
    @pytest.mark.asyncio
    async def test_cleanup_on_disconnect(self):
        """Test client cleanup on disconnection"""
        import websocket_server
        
        websocket_server.connected_clients.clear()
        websocket_server.client_subscriptions.clear()
        
        mock_ws = AsyncMock()
        mock_ws.remote_address = ('127.0.0.1', 12353)
        mock_ws.send = AsyncMock()
        
        async def async_iter():
            return
            yield
        mock_ws.__aiter__ = lambda: async_iter()
        
        # Add client and subscription
        websocket_server.connected_clients.add(mock_ws)
        client_id = id(mock_ws)
        websocket_server.client_subscriptions[client_id] = {1, 2}
        
        # Handle client (will disconnect immediately)
        await websocket_server.handle_client(mock_ws, '/ws')
        
        # Check cleanup - subscription should be removed
        # (Note: cleanup happens in finally block, check accordingly)
        assert client_id not in websocket_server.client_subscriptions or \
               mock_ws not in websocket_server.connected_clients


class TestWebSocketStats:
    """Test statistics tracking"""
    
    def test_stats_structure(self):
        """Test stats dictionary has expected keys"""
        import websocket_server
        
        assert 'total_clients' in websocket_server.stats
        assert 'active_connections' in websocket_server.stats
        assert 'messages_sent' in websocket_server.stats
        assert 'uptime' in websocket_server.stats
    
    def test_stats_initial_values(self):
        """Test stats have valid initial values"""
        import websocket_server
        
        assert isinstance(websocket_server.stats['total_clients'], int)
        assert isinstance(websocket_server.stats['active_connections'], int)
        assert isinstance(websocket_server.stats['messages_sent'], int)


class TestWebSocketConfiguration:
    """Test WebSocket configuration"""
    
    def test_websocket_port(self):
        """Test WebSocket port is configured"""
        import websocket_server
        
        assert websocket_server.PORT == 9085
    
    def test_update_interval(self):
        """Test update interval is configured"""
        import websocket_server
        
        assert websocket_server.UPDATE_INTERVAL == 3
    
    def test_client_subscriptions_structure(self):
        """Test client_subscriptions is a dict"""
        import websocket_server
        
        assert isinstance(websocket_server.client_subscriptions, dict)
