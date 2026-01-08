# Server Monitor Plugins

This directory contains plugins for the Server Monitor system. Plugins extend the functionality of the system without modifying core code.

## Overview

The plugin system allows you to:
- Send events to external integrations (webhooks, Slack, custom APIs)
- Collect custom inventory data
- Implement custom task policies
- Create custom exporters
- React to system events

## Security

**The plugin system uses an allowlist approach for security:**
- Plugins must be explicitly enabled via `PLUGINS_ENABLED=true`
- Only plugins in `PLUGINS_ALLOWLIST` are loaded
- Plugin errors are isolated and don't crash the core system
- All plugins run in the same process (for simplicity and performance)

## Configuration

### Enable Plugin System

```bash
export PLUGINS_ENABLED=true
export PLUGINS_ALLOWLIST=webhook,slack  # Comma-separated list
```

### Plugin-Specific Configuration

Each plugin can have its own configuration via environment variables:

```bash
export PLUGIN_<NAME>_CONFIG='{"key":"value"}'  # JSON format
```

Example for webhook plugin:
```bash
export PLUGIN_WEBHOOK_CONFIG='{"url":"https://example.com/webhook","secret":"mysecret"}'
```

## Writing a Plugin

### 1. Create Plugin File

Create a Python file in `backend/plugins/` (e.g., `my_plugin.py`)

### 2. Implement PluginInterface

```python
from plugin_system import PluginInterface
from event_model import Event
from observability import StructuredLogger

logger = StructuredLogger('plugin:my_plugin')

class MyPlugin(PluginInterface):
    """My custom plugin"""
    
    def __init__(self, config=None):
        super().__init__(config)
        # Initialize your plugin
        self.my_setting = self.config.get('my_setting', 'default')
        logger.info('MyPlugin initialized', setting=self.my_setting)
    
    def on_startup(self, ctx):
        """Called when server starts"""
        logger.info('MyPlugin started')
    
    def on_event(self, event):
        """Called for every event"""
        logger.info('Event received', event_type=event.event_type)
    
    def on_task_finished(self, event):
        """Called when a task finishes"""
        logger.info('Task finished', 
                   task_id=event.target_id,
                   exit_code=event.meta.get('exit_code'))
```

### 3. Add to Allowlist

```bash
export PLUGINS_ALLOWLIST=webhook,my_plugin
```

## Plugin Interface

All plugins must inherit from `PluginInterface` and can implement these optional methods:

### Lifecycle Hooks

- **`on_startup(ctx)`** - Called when the server starts
- **`on_shutdown()`** - Called when the server shuts down

### Event Hooks

- **`on_event(event)`** - Called for every event (catch-all)
- **`on_audit_log(event)`** - Called for audit log events
- **`on_task_created(event)`** - Called when a task is created
- **`on_task_finished(event)`** - Called when a task finishes
- **`on_inventory_collected(event)`** - Called when inventory is collected
- **`on_alert(event)`** - Called when an alert is triggered
- **`on_server_status_changed(event)`** - Called when server status changes

## Event Model

Events have a standardized structure:

```python
{
    "event_id": "uuid",
    "event_type": "task.finished",
    "timestamp": "2026-01-08T01:00:00Z",
    "user_id": 1,
    "username": "admin",
    "server_id": 5,
    "server_name": "web-01",
    "target_type": "task",
    "target_id": "task-123",
    "action": "task_finished",
    "meta": {
        "exit_code": 0,
        "duration": 5.2,
        "command": "uptime"
    },
    "ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "severity": "info"
}
```

## Event Types

Common event types (see `event_model.py` for full list):

### Server Events
- `server.created`
- `server.updated`
- `server.deleted`
- `server.status_changed`

### Task Events
- `task.created`
- `task.started`
- `task.finished`
- `task.failed`
- `task.cancelled`

### Terminal Events
- `terminal.connect`
- `terminal.disconnect`
- `terminal.command`

### Inventory Events
- `inventory.collected`
- `inventory.updated`

### Alert Events
- `alert.triggered`
- `alert.resolved`

## Example Plugins

### Webhook Plugin

The built-in webhook plugin demonstrates event dispatching to external URLs:

```bash
export PLUGINS_ENABLED=true
export PLUGINS_ALLOWLIST=webhook
export PLUGIN_WEBHOOK_CONFIG='{
  "url": "https://example.com/webhook",
  "secret": "your-webhook-secret",
  "event_types": ["task.finished", "alert.triggered"],
  "timeout": 10,
  "retry_max": 3
}'
```

Features:
- HMAC-SHA256 signature (`X-SM-Signature` header)
- Event type filtering
- Automatic retries with exponential backoff
- Timeout configuration

## Best Practices

1. **Error Handling**: Always wrap your code in try-except blocks. Plugin errors should never crash the system.

2. **Logging**: Use `StructuredLogger` with service name `plugin:<name>` for consistent logging:
   ```python
   logger = StructuredLogger('plugin:my_plugin')
   ```

3. **Configuration**: Use the `config` dict passed to `__init__()`. Validate required settings.

4. **Performance**: Keep event handlers fast. For long-running operations, use background threads or queues.

5. **Testing**: Test your plugin in isolation before adding to production allowlist.

6. **Security**: 
   - Never log sensitive data (passwords, tokens)
   - Validate all external inputs
   - Be careful with network requests (SSRF protection)

## Troubleshooting

### Plugin Not Loading

1. Check plugin is in allowlist:
   ```bash
   echo $PLUGINS_ALLOWLIST
   ```

2. Check plugin system is enabled:
   ```bash
   echo $PLUGINS_ENABLED
   ```

3. Check plugin file exists:
   ```bash
   ls -la backend/plugins/
   ```

4. Check logs for errors:
   ```bash
   grep "plugin" logs/central_api.log
   ```

### Plugin Not Receiving Events

1. Verify plugin is loaded (check startup logs)
2. Check plugin's `enabled` property is `True`
3. Ensure you're implementing the correct hook methods
4. Check event type filtering in your plugin

## Advanced Topics

### Background Processing

For long-running operations, use threads or queues:

```python
import threading
import queue

class MyPlugin(PluginInterface):
    def __init__(self, config=None):
        super().__init__(config)
        self.event_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()
    
    def on_event(self, event):
        self.event_queue.put(event)  # Non-blocking
    
    def _worker(self):
        while True:
            event = self.event_queue.get()
            # Process event in background
            self._process_event(event)
```

### External Dependencies

Plugins can import external libraries, but ensure they're installed:

```python
try:
    import requests
except ImportError:
    logger.error('requests library required for this plugin')
    raise
```

### State Management

Plugins can maintain state across events:

```python
class MyPlugin(PluginInterface):
    def __init__(self, config=None):
        super().__init__(config)
        self.event_count = 0
        self.last_alert_time = None
    
    def on_event(self, event):
        self.event_count += 1
        if self.event_count % 100 == 0:
            logger.info('Processed events', count=self.event_count)
```

## Support

For questions or issues:
1. Check logs for error messages
2. Review the webhook plugin example
3. See the main documentation in `docs/modules/PLUGINS.md`
4. Open an issue on GitHub
