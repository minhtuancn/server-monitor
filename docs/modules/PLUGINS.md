# Plugin System - Server Monitor

**Version:** 2.3.0  
**Status:** Production Ready  
**Last Updated:** 2026-01-08

---

## Overview

The Server Monitor Plugin System provides a safe, extensible mechanism for customizing and extending the monitoring platform without modifying core code. Plugins can respond to system events, integrate with external services, and implement custom behaviors.

## Architecture

### Design Principles

1. **Security by Default**: Allowlist-based loading prevents unauthorized code execution
2. **Fail-Safe**: Plugin errors are isolated and logged, but never crash the core system
3. **Event-Driven**: Plugins respond to standardized events across the system
4. **Minimal Overhead**: In-process execution for performance
5. **Backward Compatible**: Core functionality works without any plugins

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Core Application                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │Central API │  │Task Runner │  │ Terminal   │            │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘            │
│        │                │                │                    │
│        └────────────────┴────────────────┘                   │
│                         ▼                                     │
│             ┌────────────────────────┐                       │
│             │   Event Model          │                       │
│             │  (Unified Schema)      │                       │
│             └──────────┬─────────────┘                       │
│                        ▼                                      │
│             ┌────────────────────────┐                       │
│             │   Plugin Manager       │                       │
│             │  - Allowlist Loader    │                       │
│             │  - Event Dispatcher    │                       │
│             │  - Error Isolation     │                       │
│             └──────────┬─────────────┘                       │
│                        ▼                                      │
│    ┌──────────────────┬──────────────────┬────────────┐     │
│    ▼                  ▼                  ▼            ▼      │
│ ┌────────┐      ┌─────────┐      ┌──────────┐  ┌────────┐ │
│ │Webhook │      │  Slack  │      │ Custom 1 │  │Custom N│ │
│ │Plugin  │      │ Plugin  │      │  Plugin  │  │Plugin  │ │
│ └────────┘      └─────────┘      └──────────┘  └────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Event Model

All events use a unified schema defined in `event_model.py`:

### Event Structure

```python
{
    "event_id": "uuid-v4",              # Unique event identifier
    "event_type": "task.finished",      # Standardized event type
    "timestamp": "2026-01-08T01:00:00Z",# ISO 8601 UTC timestamp
    "user_id": 1,                       # User who triggered event
    "username": "admin",                # Username (enriched)
    "server_id": 5,                     # Related server ID
    "server_name": "web-01",            # Server name (enriched)
    "target_type": "task",              # Resource type
    "target_id": "task-123",            # Resource identifier
    "action": "task_finished",          # Legacy audit action
    "meta": {                           # Event-specific metadata
        "exit_code": 0,
        "duration": 5.2,
        "command": "uptime"
    },
    "ip": "192.168.1.100",             # Client IP address
    "user_agent": "Mozilla/5.0...",    # Client user agent
    "severity": "info"                 # info, warning, error, critical
}
```

### Standard Event Types

| Category | Event Type | Description |
|----------|-----------|-------------|
| **Server** | `server.created` | New server added |
| | `server.updated` | Server configuration changed |
| | `server.deleted` | Server removed |
| | `server.status_changed` | Server status changed |
| **Task** | `task.created` | Remote task created |
| | `task.started` | Task execution started |
| | `task.finished` | Task completed successfully |
| | `task.failed` | Task execution failed |
| | `task.cancelled` | Task cancelled by user |
| **Terminal** | `terminal.connect` | SSH terminal session opened |
| | `terminal.disconnect` | SSH terminal session closed |
| | `terminal.command` | Command executed in terminal |
| **Inventory** | `inventory.collected` | System inventory collected |
| | `inventory.updated` | Inventory data updated |
| **Alert** | `alert.triggered` | System alert triggered |
| | `alert.resolved` | Alert condition resolved |
| **Audit** | `audit.export` | Audit logs exported |
| | `audit.cleanup` | Old audit logs cleaned up |

See `backend/event_model.py` for the complete list.

## Plugin Interface

### Base Class

All plugins inherit from `PluginInterface`:

```python
from plugin_system import PluginInterface
from event_model import Event

class MyPlugin(PluginInterface):
    def __init__(self, config=None):
        super().__init__(config)
        # Initialize plugin with config
        
    # Implement optional hook methods below
```

### Lifecycle Hooks

```python
def on_startup(self, ctx: Dict[str, Any]) -> None:
    """Called when server starts"""
    pass

def on_shutdown(self) -> None:
    """Called when server shuts down"""
    pass
```

### Event Hooks

```python
def on_event(self, event: Event) -> None:
    """Called for every system event (catch-all)"""
    pass

def on_audit_log(self, event: Event) -> None:
    """Called when audit log is created"""
    pass

def on_task_created(self, event: Event) -> None:
    """Called when task is created"""
    pass

def on_task_finished(self, event: Event) -> None:
    """Called when task finishes (success or failure)"""
    pass

def on_inventory_collected(self, event: Event) -> None:
    """Called when inventory is collected"""
    pass

def on_alert(self, event: Event) -> None:
    """Called when alert is triggered"""
    pass

def on_server_status_changed(self, event: Event) -> None:
    """Called when server status changes"""
    pass
```

## Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `PLUGINS_ENABLED` | Yes | Enable plugin system | `true` or `false` |
| `PLUGINS_ALLOWLIST` | Yes | Comma-separated plugin names | `webhook,slack` |
| `PLUGIN_<NAME>_CONFIG` | No | Plugin-specific config (JSON) | See below |

### Example Configuration

```bash
# Enable plugin system
export PLUGINS_ENABLED=true

# Load webhook and slack plugins
export PLUGINS_ALLOWLIST=webhook,slack

# Configure webhook plugin
export PLUGIN_WEBHOOK_CONFIG='{
  "url": "https://example.com/webhook",
  "secret": "your-webhook-secret",
  "event_types": ["task.finished", "alert.triggered"],
  "timeout": 10,
  "retry_max": 3
}'

# Configure slack plugin
export PLUGIN_SLACK_CONFIG='{
  "webhook_url": "https://hooks.slack.com/services/...",
  "channel": "#monitoring",
  "username": "ServerMonitor"
}'
```

## Writing Plugins

### Step 1: Create Plugin File

Create `backend/plugins/my_plugin.py`:

```python
#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugin_system import PluginInterface
from event_model import Event, EventTypes
from observability import StructuredLogger

logger = StructuredLogger('plugin:my_plugin')

class MyPlugin(PluginInterface):
    """Custom plugin description"""
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # Parse configuration
        self.api_key = self.config.get('api_key')
        self.endpoint = self.config.get('endpoint', 'https://api.example.com')
        
        # Validate required config
        if not self.api_key:
            logger.warning('MyPlugin: No API key configured, plugin disabled')
            self.enabled = False
        
        if self.enabled:
            logger.info('MyPlugin initialized', endpoint=self.endpoint)
    
    def on_startup(self, ctx):
        logger.info('MyPlugin started')
    
    def on_task_finished(self, event):
        """Process completed tasks"""
        exit_code = event.meta.get('exit_code')
        server_name = event.server_name
        
        logger.info('Task completed',
                   server=server_name,
                   exit_code=exit_code)
        
        # Your custom logic here
        if exit_code != 0:
            self._send_alert(event)
    
    def _send_alert(self, event):
        """Send alert to external API"""
        try:
            # Implementation here
            pass
        except Exception as e:
            logger.error('Failed to send alert', error=str(e))
```

### Step 2: Add to Allowlist

```bash
export PLUGINS_ALLOWLIST=webhook,my_plugin
export PLUGIN_MY_PLUGIN_CONFIG='{"api_key":"secret","endpoint":"https://api.example.com"}'
```

### Step 3: Test Plugin

1. Start the server with plugin enabled
2. Trigger events (create tasks, etc.)
3. Check logs for plugin activity:
   ```bash
   grep "plugin:my_plugin" data/logs/central_api.log
   ```

## Example: Webhook Plugin

The built-in webhook plugin demonstrates best practices:

### Features

- ✅ HMAC-SHA256 signature for security
- ✅ Event type filtering
- ✅ Automatic retries with exponential backoff
- ✅ Timeout configuration
- ✅ Comprehensive error handling
- ✅ Structured logging

### Configuration

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

### Webhook Request Format

```http
POST /webhook HTTP/1.1
Host: example.com
Content-Type: application/json
X-SM-Event-Id: uuid-v4
X-SM-Event-Type: task.finished
X-SM-Signature: sha256=abc123...
User-Agent: ServerMonitor-Webhook/1.0

{
  "event_id": "...",
  "event_type": "task.finished",
  ...
}
```

### Verifying Webhook Signature

```python
import hmac
import hashlib

def verify_signature(payload_body, signature, secret):
    """Verify HMAC-SHA256 signature"""
    expected = hmac.new(
        secret.encode('utf-8'),
        payload_body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # signature format: "sha256=<hex>"
    received = signature.replace('sha256=', '')
    return hmac.compare_digest(expected, received)
```

## Security Considerations

### Allowlist Enforcement

- Only plugins explicitly listed in `PLUGINS_ALLOWLIST` are loaded
- Plugin files must exist in `backend/plugins/` directory
- No dynamic loading from external sources

### Error Isolation

- Plugin errors are caught and logged
- Failures don't affect core system operation
- Each plugin runs in try-except blocks

### Network Security

When making external requests:

1. **Validate URLs**: Prevent SSRF attacks
   ```python
   from urllib.parse import urlparse
   parsed = urlparse(url)
   if parsed.hostname in ['localhost', '127.0.0.1']:
       raise ValueError('Internal URLs not allowed')
   ```

2. **Use Timeouts**: Prevent hanging requests
   ```python
   urllib.request.urlopen(req, timeout=10)
   ```

3. **Limit Retries**: Prevent infinite loops
   ```python
   max_retries = 3
   ```

### Secrets Management

- Never log secrets or sensitive data
- Use environment variables for configuration
- Redact sensitive data in logs:
  ```python
  def _safe_config(self):
      safe = self.config.copy()
      if 'secret' in safe:
          safe['secret'] = '***REDACTED***'
      return safe
  ```

### Input Validation

- Validate all event data before processing
- Sanitize data before sending to external systems
- Check data types and ranges

## Performance

### Optimization Tips

1. **Keep Hooks Fast**: Event handlers should complete quickly
   ```python
   # Good: Quick operations
   def on_event(self, event):
       self.event_count += 1
   
   # Bad: Slow operations
   def on_event(self, event):
       time.sleep(5)  # Blocks event processing!
   ```

2. **Use Background Processing**: For slow operations, use threads/queues
   ```python
   import queue
   import threading
   
   class MyPlugin(PluginInterface):
       def __init__(self, config=None):
           super().__init__(config)
           self.queue = queue.Queue()
           self.worker = threading.Thread(target=self._worker)
           self.worker.daemon = True
           self.worker.start()
       
       def on_event(self, event):
           self.queue.put(event)  # Non-blocking
       
       def _worker(self):
           while True:
               event = self.queue.get()
               self._process_slow(event)
   ```

3. **Filter Events Early**: Only process relevant events
   ```python
   def on_event(self, event):
       if event.event_type not in self.watched_types:
           return  # Skip early
       # Process event
   ```

4. **Batch Operations**: Accumulate events and process in batches
   ```python
   def __init__(self, config=None):
       super().__init__(config)
       self.batch = []
       self.batch_size = 100
   
   def on_event(self, event):
       self.batch.append(event)
       if len(self.batch) >= self.batch_size:
           self._flush_batch()
   ```

## Monitoring & Debugging

### Logging

Use structured logging for consistency:

```python
from observability import StructuredLogger

logger = StructuredLogger('plugin:my_plugin')

# Info level
logger.info('Event processed', event_type=event.event_type, count=123)

# Warning level
logger.warning('Configuration missing', key='api_key')

# Error level
logger.error('Failed to process event', error=str(e), event_id=event.event_id)
```

### Log Format

Logs use JSON format with consistent fields:

```json
{
  "timestamp": "2026-01-08T01:00:00.123Z",
  "level": "INFO",
  "service": "plugin:my_plugin",
  "message": "Event processed",
  "event_type": "task.finished",
  "count": 123
}
```

### Checking Plugin Status

View loaded plugins in startup logs:

```bash
grep "Plugin loaded" data/logs/central_api.log
```

Check for plugin errors:

```bash
grep "Plugin error" data/logs/central_api.log
```

## Testing

### Unit Testing

Test plugins in isolation:

```python
import unittest
from my_plugin import MyPlugin
from event_model import Event, EventTypes

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.config = {'api_key': 'test'}
        self.plugin = MyPlugin(self.config)
    
    def test_task_finished(self):
        event = Event(
            event_type=EventTypes.TASK_FINISHED,
            server_name='test-server',
            meta={'exit_code': 0}
        )
        # Should not raise exception
        self.plugin.on_task_finished(event)
```

### Integration Testing

Test with the running system:

1. Enable plugin with test configuration
2. Trigger events via API
3. Verify plugin behavior in logs
4. Check external systems receive data

## Troubleshooting

### Plugin Not Loading

**Symptom**: Plugin not in startup logs

**Solutions**:
1. Check `PLUGINS_ENABLED=true`
2. Verify plugin in `PLUGINS_ALLOWLIST`
3. Check file exists: `ls backend/plugins/my_plugin.py`
4. Check for syntax errors in plugin file
5. Review logs: `grep "plugin" data/logs/central_api.log`

### Plugin Not Receiving Events

**Symptom**: No log output from plugin

**Solutions**:
1. Check `plugin.enabled` is `True`
2. Verify hook methods are implemented correctly
3. Check event type filtering
4. Add debug logging to confirm plugin is active

### Plugin Errors

**Symptom**: Errors in logs

**Solutions**:
1. Check error message and traceback
2. Verify configuration is valid JSON
3. Check required dependencies are installed
4. Test plugin in isolation
5. Add more error handling

## Migration Guide

### From Manual Integrations

If you have custom notification code:

**Before** (hardcoded in core):
```python
# In central_api.py
import requests
requests.post('https://my-webhook.com', json=data)
```

**After** (as plugin):
```python
# In backend/plugins/my_integration.py
class MyIntegration(PluginInterface):
    def on_event(self, event):
        requests.post(self.config['url'], json=event.to_dict())
```

**Benefits**:
- No core code changes
- Easier to maintain
- Can be enabled/disabled
- Isolated error handling

## Advanced Topics

### State Persistence

For state that should survive restarts, use files or database:

```python
import json
from pathlib import Path

class StatefulPlugin(PluginInterface):
    def __init__(self, config=None):
        super().__init__(config)
        self.state_file = Path('data/plugin_state.json')
        self.load_state()
    
    def load_state(self):
        if self.state_file.exists():
            with open(self.state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {}
    
    def save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f)
    
    def on_event(self, event):
        self.state[event.event_id] = event.timestamp
        self.save_state()
```

### Custom Event Sources

Plugins can also generate events:

```python
from event_model import create_event, EventTypes
from plugin_system import dispatch_event

class EventGeneratorPlugin(PluginInterface):
    def on_startup(self, ctx):
        # Generate custom event
        event = create_event(
            event_type='custom.plugin_started',
            meta={'plugin': 'my_plugin'}
        )
        dispatch_event(event)
```

## API Reference

See inline documentation in:
- `backend/plugin_system.py` - Plugin manager and interface
- `backend/event_model.py` - Event data structures
- `backend/plugins/webhook.py` - Example implementation

## Support

- **Documentation**: `backend/plugins/README.md`
- **Examples**: `backend/plugins/webhook.py`
- **Issues**: GitHub issue tracker
- **Logs**: `data/logs/central_api.log`
