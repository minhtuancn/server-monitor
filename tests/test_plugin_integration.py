#!/usr/bin/env python3

"""
Test plugin system integration
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Set plugin environment
# Use a mock URL that won't make actual network calls in CI
# The webhook plugin should handle connection errors gracefully
os.environ['PLUGINS_ENABLED'] = 'true'
os.environ['PLUGINS_ALLOWLIST'] = 'webhook'
# Use localhost URL to avoid network calls - the plugin should handle failures gracefully
os.environ['PLUGIN_WEBHOOK_CONFIG'] = '{"url":"http://localhost:19999/webhook","timeout":1}'

from plugin_system import get_plugin_manager
from event_model import Event, EventTypes, create_event, EventSeverity

def test_plugin_integration():
    """Test plugin system integration"""
    print("Testing plugin system integration...")
    
    # Get plugin manager
    manager = get_plugin_manager()
    print(f"✓ Plugin manager initialized")
    print(f"  - Enabled: {manager.enabled}")
    print(f"  - Allowlist: {manager.allowlist}")
    print(f"  - Plugins loaded: {list(manager.plugins.keys())}")
    
    # Test startup
    manager.startup({'test': 'startup'})
    print(f"✓ Plugin startup notification sent")
    
    # Test event dispatch
    event = create_event(
        event_type=EventTypes.TASK_FINISHED,
        user_id=1,
        username='admin',
        server_id=5,
        server_name='web-01',
        target_type='task',
        target_id='task-123',
        meta={'exit_code': 0, 'command': 'uptime'},
        severity=EventSeverity.INFO
    )
    
    print(f"✓ Created event: {event.event_type}")
    
    manager.dispatch_event(event)
    print(f"✓ Event dispatched to plugins")
    
    # Test shutdown
    manager.shutdown()
    print(f"✓ Plugin shutdown notification sent")
    
    print("\n✅ All plugin integration tests passed!")

if __name__ == '__main__':
    test_plugin_integration()
