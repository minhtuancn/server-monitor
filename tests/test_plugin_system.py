#!/usr/bin/env python3

"""
Tests for Plugin System and Event Model
"""

import unittest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from event_model import Event, EventTypes, EventSeverity, create_event
from plugin_system import PluginInterface, PluginManager, get_plugin_manager


class TestEventModel(unittest.TestCase):
    """Test event model functionality"""
    
    def test_event_creation(self):
        """Test creating an event"""
        event = Event(
            event_type=EventTypes.TASK_FINISHED,
            user_id=1,
            username='admin',
            server_id=5,
            server_name='web-01',
            target_type='task',
            target_id='task-123',
            meta={'exit_code': 0}
        )
        
        self.assertEqual(event.event_type, EventTypes.TASK_FINISHED)
        self.assertEqual(event.user_id, 1)
        self.assertEqual(event.username, 'admin')
        self.assertEqual(event.server_name, 'web-01')
        self.assertEqual(event.meta['exit_code'], 0)
        self.assertIsNotNone(event.event_id)
        self.assertIsNotNone(event.timestamp)
    
    def test_event_to_dict(self):
        """Test converting event to dict"""
        event = Event(
            event_type=EventTypes.SERVER_CREATED,
            user_id=1,
            target_type='server',
            target_id='5'
        )
        
        data = event.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['event_type'], EventTypes.SERVER_CREATED)
        self.assertEqual(data['user_id'], 1)
        self.assertIn('event_id', data)
        self.assertIn('timestamp', data)
    
    def test_event_to_json(self):
        """Test converting event to JSON"""
        event = Event(
            event_type=EventTypes.ALERT_TRIGGERED,
            severity=EventSeverity.CRITICAL,
            meta={'threshold': 90}
        )
        
        json_str = event.to_json()
        self.assertIsInstance(json_str, str)
        
        # Parse back to verify
        data = json.loads(json_str)
        self.assertEqual(data['event_type'], EventTypes.ALERT_TRIGGERED)
        self.assertEqual(data['severity'], EventSeverity.CRITICAL)
        self.assertEqual(data['meta']['threshold'], 90)
    
    def test_event_from_audit_log(self):
        """Test creating event from audit log"""
        audit_log = {
            'id': 'log-123',
            'action': 'terminal.connect',
            'created_at': '2026-01-08T01:00:00Z',
            'user_id': 1,
            'target_type': 'server',
            'target_id': '5',
            'meta_json': '{"session_id": "sess-123"}',
            'ip': '192.168.1.100',
            'user_agent': 'Mozilla/5.0'
        }
        
        event = Event.from_audit_log(audit_log)
        self.assertEqual(event.event_id, 'log-123')
        self.assertEqual(event.event_type, 'terminal.connect')
        self.assertEqual(event.user_id, 1)
        self.assertEqual(event.meta['session_id'], 'sess-123')
        self.assertEqual(event.ip, '192.168.1.100')
    
    def test_create_event_helper(self):
        """Test create_event helper function"""
        event = create_event(
            event_type=EventTypes.TASK_CREATED,
            user_id=1,
            server_id=5,
            target_type='task',
            target_id='task-456',
            meta={'command': 'uptime'},
            severity=EventSeverity.INFO
        )
        
        self.assertEqual(event.event_type, EventTypes.TASK_CREATED)
        self.assertEqual(event.user_id, 1)
        self.assertEqual(event.server_id, 5)
        self.assertEqual(event.action, 'task_created')  # Auto-generated
        self.assertEqual(event.severity, EventSeverity.INFO)


class TestPluginInterface(unittest.TestCase):
    """Test plugin interface base class"""
    
    def test_plugin_creation(self):
        """Test creating a plugin instance"""
        config = {'setting': 'value'}
        plugin = PluginInterface(config)
        
        self.assertEqual(plugin.config, config)
        self.assertTrue(plugin.enabled)
        self.assertEqual(plugin.name, 'PluginInterface')
    
    def test_plugin_hooks_are_optional(self):
        """Test that all hook methods are optional"""
        plugin = PluginInterface()
        event = Event(event_type='test.event')
        
        # Should not raise exceptions
        plugin.on_startup({})
        plugin.on_shutdown()
        plugin.on_event(event)
        plugin.on_audit_log(event)
        plugin.on_task_created(event)
        plugin.on_task_finished(event)
        plugin.on_inventory_collected(event)
        plugin.on_alert(event)
        plugin.on_server_status_changed(event)


class MockPlugin(PluginInterface):
    """Mock plugin for testing"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.events_received = []
        self.startup_called = False
        self.shutdown_called = False
    
    def on_startup(self, ctx):
        self.startup_called = True
    
    def on_shutdown(self):
        self.shutdown_called = True
    
    def on_event(self, event):
        self.events_received.append(event)


class TestPluginManager(unittest.TestCase):
    """Test plugin manager functionality"""
    
    def setUp(self):
        """Reset environment before each test"""
        # Clear environment
        for key in list(os.environ.keys()):
            if key.startswith('PLUGIN'):
                del os.environ[key]
    
    def test_plugin_system_disabled_by_default(self):
        """Test plugin system is disabled by default"""
        manager = PluginManager()
        self.assertFalse(manager.enabled)
    
    @patch.dict(os.environ, {'PLUGINS_ENABLED': 'true', 'PLUGINS_ALLOWLIST': 'test_plugin'})
    def test_plugin_system_enabled(self):
        """Test enabling plugin system"""
        manager = PluginManager()
        self.assertTrue(manager.enabled)
        self.assertIn('test_plugin', manager.allowlist)
    
    @patch.dict(os.environ, {'PLUGINS_ENABLED': 'true', 'PLUGINS_ALLOWLIST': 'plugin1,plugin2,plugin3'})
    def test_allowlist_parsing(self):
        """Test parsing allowlist from environment"""
        manager = PluginManager()
        self.assertEqual(manager.allowlist, ['plugin1', 'plugin2', 'plugin3'])
    
    @patch.dict(os.environ, {'PLUGINS_ENABLED': 'true', 'PLUGINS_ALLOWLIST': ''})
    def test_empty_allowlist(self):
        """Test handling empty allowlist"""
        manager = PluginManager()
        self.assertEqual(manager.allowlist, [])
    
    def test_event_dispatch_when_disabled(self):
        """Test event dispatch does nothing when disabled"""
        manager = PluginManager()
        event = Event(event_type='test.event')
        
        # Should not raise exception
        manager.dispatch_event(event)
    
    @patch.dict(os.environ, {'PLUGINS_ENABLED': 'true'})
    def test_plugin_error_isolation(self):
        """Test that plugin errors don't crash the system"""
        manager = PluginManager()
        
        # Create a plugin that raises an error
        class BrokenPlugin(PluginInterface):
            def on_event(self, event):
                raise ValueError("Plugin error!")
        
        manager.plugins['broken'] = BrokenPlugin()
        event = Event(event_type='test.event')
        
        # Should not raise exception (error is caught and logged)
        manager.dispatch_event(event)
    
    @patch.dict(os.environ, {'PLUGINS_ENABLED': 'true'})
    def test_event_routing(self):
        """Test event routing to plugin hooks"""
        manager = PluginManager()
        mock_plugin = MockPlugin()
        manager.plugins['mock'] = mock_plugin
        
        # Dispatch different event types
        events = [
            Event(event_type=EventTypes.TASK_CREATED),
            Event(event_type=EventTypes.TASK_FINISHED),
            Event(event_type=EventTypes.ALERT_TRIGGERED),
        ]
        
        for event in events:
            manager.dispatch_event(event)
        
        # Verify plugin received events
        self.assertEqual(len(mock_plugin.events_received), 3)
    
    @patch.dict(os.environ, {'PLUGINS_ENABLED': 'true'})
    def test_disabled_plugin_not_called(self):
        """Test that disabled plugins don't receive events"""
        manager = PluginManager()
        mock_plugin = MockPlugin()
        mock_plugin.enabled = False
        manager.plugins['mock'] = mock_plugin
        
        event = Event(event_type='test.event')
        manager.dispatch_event(event)
        
        # Plugin should not receive event
        self.assertEqual(len(mock_plugin.events_received), 0)
    
    @patch.dict(os.environ, {'PLUGINS_ENABLED': 'true'})
    def test_startup_notification(self):
        """Test plugin startup notification"""
        manager = PluginManager()
        mock_plugin = MockPlugin()
        manager.plugins['mock'] = mock_plugin
        
        ctx = {'server': 'test'}
        manager.startup(ctx)
        
        self.assertTrue(mock_plugin.startup_called)
    
    @patch.dict(os.environ, {'PLUGINS_ENABLED': 'true'})
    def test_shutdown_notification(self):
        """Test plugin shutdown notification"""
        manager = PluginManager()
        mock_plugin = MockPlugin()
        manager.plugins['mock'] = mock_plugin
        
        manager.shutdown()
        
        self.assertTrue(mock_plugin.shutdown_called)


class TestEventTypes(unittest.TestCase):
    """Test event type constants"""
    
    def test_event_types_defined(self):
        """Test that standard event types are defined"""
        self.assertEqual(EventTypes.SERVER_CREATED, 'server.created')
        self.assertEqual(EventTypes.TASK_FINISHED, 'task.finished')
        self.assertEqual(EventTypes.TERMINAL_CONNECT, 'terminal.connect')
        self.assertEqual(EventTypes.ALERT_TRIGGERED, 'alert.triggered')
        self.assertEqual(EventTypes.INVENTORY_COLLECTED, 'inventory.collected')
    
    def test_severity_levels(self):
        """Test severity level constants"""
        self.assertEqual(EventSeverity.INFO, 'info')
        self.assertEqual(EventSeverity.WARNING, 'warning')
        self.assertEqual(EventSeverity.ERROR, 'error')
        self.assertEqual(EventSeverity.CRITICAL, 'critical')


if __name__ == '__main__':
    unittest.main()
