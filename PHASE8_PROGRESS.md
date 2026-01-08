# Phase 8 Implementation Progress

**Date**: 2026-01-08  
**Branch**: `copilot/add-plugin-system-and-optimizations`  
**Status**: PR1 Complete, PR2 Database Layer Complete

## Overview

Phase 8 transforms the server monitor into an extensible platform with:
1. Plugin system for extensibility
2. Webhooks for external integrations
3. Performance optimizations for 100→500+ servers

## Completed Work

### PR1: Core Plugin Framework ✅ COMPLETE

**Files Created:**
- `backend/event_model.py` - Unified event schema
- `backend/plugin_system.py` - Plugin manager and interface
- `backend/plugins/webhook.py` - Example webhook plugin
- `backend/plugins/README.md` - Plugin development guide
- `docs/modules/PLUGINS.md` - Comprehensive plugin documentation
- `tests/test_plugin_system.py` - 19 passing tests
- `tests/test_plugin_integration.py` - End-to-end integration test

**Files Modified:**
- `backend/central_api.py` - Integrated plugin system
  - Added imports for plugin_system and event_model
  - Created `dispatch_audit_event()` helper function
  - Added plugin startup in main() with context
  - Added plugin shutdown in graceful_shutdown()
  - Converted one audit log call to use dispatch_audit_event()
- `.env.example` - Added plugin configuration section

**Key Features Implemented:**
1. **Event Model** (`event_model.py`)
   - Unified `Event` dataclass for all system events
   - Standard event types (EventTypes class)
   - Severity levels (EventSeverity class)
   - Conversion from audit_logs for backward compatibility
   - Helper function `create_event()`

2. **Plugin System** (`plugin_system.py`)
   - `PluginInterface` base class with lifecycle hooks
   - `PluginManager` with allowlist-based loading
   - Fail-safe execution (plugin errors don't crash core)
   - Event routing to specific handlers
   - Structured logging with service tags
   - Environment-based configuration

3. **Webhook Plugin** (`plugins/webhook.py`)
   - HMAC-SHA256 signature generation
   - Event type filtering
   - Retry logic with exponential backoff
   - Timeout configuration
   - Comprehensive error handling

4. **Integration**
   - Plugin manager initialized at startup
   - Plugins notified of startup/shutdown
   - Event dispatching via `dispatch_audit_event()` helper
   - Works alongside existing audit logging

### PR2: Webhooks Database Layer ✅ COMPLETE

**Files Modified:**
- `backend/database.py` - Added webhooks schema and CRUD

**Database Schema:**
1. **webhooks table**
   - id (TEXT PRIMARY KEY)
   - name, url, secret
   - enabled (INTEGER)
   - event_types (TEXT/JSON)
   - retry_max, timeout
   - created_by, created_at, updated_at, last_triggered_at
   - Index on enabled

2. **webhook_deliveries table** (audit trail)
   - id (TEXT PRIMARY KEY)
   - webhook_id, event_id, event_type
   - status, status_code, response_body, error
   - attempt, delivered_at
   - Indexes on webhook_id and delivered_at

**CRUD Functions:**
- `create_webhook()` - Create new webhook
- `get_webhooks(enabled_only=False)` - List webhooks
- `get_webhook(webhook_id)` - Get single webhook
- `update_webhook()` - Update webhook fields
- `delete_webhook()` - Delete webhook
- `update_webhook_last_triggered()` - Update timestamp
- `log_webhook_delivery()` - Log delivery attempt
- `get_webhook_deliveries()` - Get delivery logs

**Tested and Validated:**
- Database initialization successful
- CRUD operations working
- JSON parsing for event_types
- Boolean conversion for enabled flag

## Remaining Work

### PR2: Webhooks API Endpoints (HIGH PRIORITY)

**Add to `backend/central_api.py`:**

1. **GET /api/webhooks** - List all webhooks (admin only)
   ```python
   # In do_GET(), add endpoint
   elif path == '/api/webhooks':
       # Check admin auth
       # Call db.get_webhooks()
       # Return JSON list
   ```

2. **POST /api/webhooks** - Create webhook (admin only)
   ```python
   # In do_POST(), add endpoint
   elif path == '/api/webhooks':
       # Check admin auth
       # Parse JSON body
       # Validate URL (prevent SSRF)
       # Call db.create_webhook()
       # Log audit event
       # Return webhook_id
   ```

3. **GET /api/webhooks/{id}** - Get single webhook (admin only)
   ```python
   elif path.startswith('/api/webhooks/') and '/' in path[14:]:
       webhook_id = path.split('/')[-1]
       # Call db.get_webhook(webhook_id)
       # Return webhook or 404
   ```

4. **PUT /api/webhooks/{id}** - Update webhook (admin only)
   ```python
   # In do_PUT(), add endpoint
   elif path.startswith('/api/webhooks/'):
       webhook_id = path.split('/')[-1]
       # Parse JSON body
       # Call db.update_webhook()
       # Log audit event
   ```

5. **DELETE /api/webhooks/{id}** - Delete webhook (admin only)
   ```python
   # In do_DELETE(), add endpoint  
   elif path.startswith('/api/webhooks/'):
       webhook_id = path.split('/')[-1]
       # Call db.delete_webhook()
       # Log audit event
   ```

6. **POST /api/webhooks/{id}/test** - Test webhook (admin only)
   ```python
   # Send test event to webhook
   # Use webhook plugin or manual HTTP request
   # Return delivery result
   ```

7. **GET /api/webhooks/{id}/deliveries** - Get delivery logs (admin only)
   ```python
   # Call db.get_webhook_deliveries(webhook_id)
   # Support pagination (limit, offset)
   # Return delivery log list
   ```

**Security Considerations:**
- All endpoints require admin authentication
- Validate URLs to prevent SSRF attacks:
  ```python
  from urllib.parse import urlparse
  parsed = urlparse(url)
  if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
      return {'error': 'Internal URLs not allowed'}
  if parsed.scheme not in ['http', 'https']:
      return {'error': 'Only HTTP/HTTPS allowed'}
  ```
- Sanitize webhook secrets in responses
- Rate limit webhook creation (e.g., 10 per hour)

### PR2: Webhook Dispatcher Integration

**Create `backend/webhook_dispatcher.py`:**
```python
"""
Webhook Dispatcher - Manages webhook delivery
Integrates with plugin system and database
"""

import database as db
import urllib.request
import urllib.error
import hmac
import hashlib
import json
from observability import StructuredLogger
from event_model import Event

logger = StructuredLogger('webhook_dispatcher')

def dispatch_to_webhooks(event: Event):
    """
    Dispatch event to all enabled webhooks
    
    This is called by the plugin system event dispatcher
    or can be called directly for specific events.
    """
    webhooks = db.get_webhooks(enabled_only=True)
    
    for webhook in webhooks:
        # Check if webhook is interested in this event type
        if webhook['event_types']:
            if event.event_type not in webhook['event_types']:
                continue  # Skip this webhook
        
        # Deliver webhook
        try:
            _deliver_webhook(webhook, event)
        except Exception as e:
            logger.error('Webhook delivery error',
                        webhook_id=webhook['id'],
                        event_id=event.event_id,
                        error=str(e))

def _deliver_webhook(webhook, event):
    """Deliver event to a single webhook with retries"""
    payload = event.to_json()
    payload_bytes = payload.encode('utf-8')
    
    # Calculate HMAC signature
    signature = None
    if webhook.get('secret'):
        signature = hmac.new(
            webhook['secret'].encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
    
    # Build request
    headers = {
        'Content-Type': 'application/json',
        'X-SM-Event-Id': event.event_id,
        'X-SM-Event-Type': event.event_type,
        'User-Agent': 'ServerMonitor-Webhook/2.3.0'
    }
    
    if signature:
        headers['X-SM-Signature'] = f'sha256={signature}'
    
    req = urllib.request.Request(
        webhook['url'],
        data=payload_bytes,
        headers=headers,
        method='POST'
    )
    
    retry_max = webhook.get('retry_max', 3)
    timeout = webhook.get('timeout', 10)
    
    # Retry loop
    for attempt in range(1, retry_max + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status_code = response.getcode()
                response_body = response.read().decode('utf-8', errors='ignore')
                
                # Log successful delivery
                db.log_webhook_delivery(
                    webhook_id=webhook['id'],
                    event_id=event.event_id,
                    event_type=event.event_type,
                    status='success',
                    status_code=status_code,
                    response_body=response_body[:1000],  # Truncate
                    attempt=attempt
                )
                
                # Update last triggered
                db.update_webhook_last_triggered(webhook['id'])
                
                logger.info('Webhook delivered',
                           webhook_id=webhook['id'],
                           event_id=event.event_id,
                           status_code=status_code)
                return  # Success
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='ignore')[:1000]
            
            # Log failed delivery
            db.log_webhook_delivery(
                webhook_id=webhook['id'],
                event_id=event.event_id,
                event_type=event.event_type,
                status='failed' if attempt == retry_max else 'retrying',
                status_code=e.code,
                error=f'HTTP {e.code}: {error_body}',
                attempt=attempt
            )
            
            # Don't retry 4xx errors
            if 400 <= e.code < 500:
                logger.warning('Webhook delivery failed (client error)',
                              webhook_id=webhook['id'],
                              status_code=e.code)
                return
            
        except Exception as e:
            # Log error
            db.log_webhook_delivery(
                webhook_id=webhook['id'],
                event_id=event.event_id,
                event_type=event.event_type,
                status='failed' if attempt == retry_max else 'retrying',
                error=str(e),
                attempt=attempt
            )
        
        # Exponential backoff
        if attempt < retry_max:
            import time
            time.sleep(2 ** (attempt - 1))
    
    logger.error('Webhook delivery failed after retries',
                webhook_id=webhook['id'],
                event_id=event.event_id,
                attempts=retry_max)
```

**Integrate dispatcher:**
1. Import in `central_api.py`: `from webhook_dispatcher import dispatch_to_webhooks`
2. Call in `dispatch_audit_event()` after `plugin_manager.dispatch_event(event)`:
   ```python
   # Also dispatch to managed webhooks (from DB)
   dispatch_to_webhooks(event)
   ```

### PR2: Documentation

**Create `docs/modules/WEBHOOKS.md`:**
- Webhook overview and use cases
- Configuration via UI/API
- HMAC signature verification examples
- Event types reference
- Security best practices
- Troubleshooting guide

**Update `docs/openapi.yaml`:**
Add webhook endpoints with full schemas:
```yaml
/api/webhooks:
  get:
    summary: List webhooks
    tags: [Webhooks]
    security: [bearerAuth: []]
    responses:
      200:
        description: List of webhooks
        content:
          application/json:
            schema:
              type: object
              properties:
                webhooks:
                  type: array
                  items:
                    $ref: '#/components/schemas/Webhook'
  
  post:
    summary: Create webhook
    tags: [Webhooks]
    security: [bearerAuth: []]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [name, url]
            properties:
              name:
                type: string
              url:
                type: string
                format: uri
              secret:
                type: string
              enabled:
                type: boolean
              event_types:
                type: array
                items:
                  type: string
    responses:
      201:
        description: Webhook created

# Add Webhook schema to components
components:
  schemas:
    Webhook:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        url:
          type: string
        enabled:
          type: boolean
        event_types:
          type: array
          items:
            type: string
        retry_max:
          type: integer
        timeout:
          type: integer
        created_at:
          type: string
        updated_at:
          type: string
        last_triggered_at:
          type: string
```

### PR2: Testing

**Create `tests/test_webhooks.py`:**
```python
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import database as db
from event_model import Event, EventTypes

class TestWebhooks(unittest.TestCase):
    def setUp(self):
        # Use test database
        db.DB_PATH = ':memory:'
        db.init_database()
    
    def test_create_webhook(self):
        result = db.create_webhook(
            name='Test Webhook',
            url='https://example.com/hook',
            secret='secret',
            event_types=['task.finished'],
            created_by=1
        )
        self.assertTrue(result['success'])
        self.assertIn('webhook_id', result)
    
    def test_get_webhooks(self):
        db.create_webhook('Hook 1', 'https://example.com/1', created_by=1)
        db.create_webhook('Hook 2', 'https://example.com/2', created_by=1)
        
        webhooks = db.get_webhooks()
        self.assertEqual(len(webhooks), 2)
    
    def test_update_webhook(self):
        result = db.create_webhook('Test', 'https://example.com', created_by=1)
        webhook_id = result['webhook_id']
        
        update_result = db.update_webhook(webhook_id, name='Updated')
        self.assertTrue(update_result['success'])
        
        webhook = db.get_webhook(webhook_id)
        self.assertEqual(webhook['name'], 'Updated')
    
    def test_delete_webhook(self):
        result = db.create_webhook('Test', 'https://example.com', created_by=1)
        webhook_id = result['webhook_id']
        
        delete_result = db.delete_webhook(webhook_id)
        self.assertTrue(delete_result['success'])
        
        webhook = db.get_webhook(webhook_id)
        self.assertIsNone(webhook)
    
    def test_log_webhook_delivery(self):
        result = db.create_webhook('Test', 'https://example.com', created_by=1)
        webhook_id = result['webhook_id']
        
        log_result = db.log_webhook_delivery(
            webhook_id=webhook_id,
            event_id='event-123',
            event_type='task.finished',
            status='success',
            status_code=200
        )
        self.assertTrue(log_result['success'])
        
        deliveries = db.get_webhook_deliveries(webhook_id)
        self.assertEqual(len(deliveries), 1)
        self.assertEqual(deliveries[0]['status'], 'success')

if __name__ == '__main__':
    unittest.main()
```

### PR3: UI Integrations Page

**Frontend Work (Next.js):**
1. Create `frontend-next/src/app/(dashboard)/settings/integrations/page.tsx`
2. Add webhook management component
3. Implement CRUD operations via API proxy
4. Add test webhook button
5. Display delivery logs

**Key Features:**
- List webhooks in table
- Create webhook modal/form
- Edit webhook inline or modal
- Delete confirmation
- Enable/disable toggle
- Test webhook button (sends test event)
- View recent deliveries
- Event type multi-select
- HMAC secret generator

### PR4: Performance Optimizations

**Caching:**
1. Add simple in-memory cache to `central_api.py`:
```python
from time import time

cache = {}

def get_cached(key, ttl_seconds, fetch_func):
    """Simple cache helper"""
    if key in cache:
        value, expires = cache[key]
        if time() < expires:
            return value
    
    value = fetch_func()
    cache[key] = (value, time() + ttl_seconds)
    return value

# Use in endpoints:
stats = get_cached('stats_overview', 30, lambda: db.get_server_stats())
```

2. Cache these endpoints:
   - `/api/stats/overview` (30s TTL)
   - `/api/servers` (10s TTL)
   - `/api/activity/recent` (15s TTL)

**Database Indexes (already added):**
- `idx_tasks_server_id`
- `idx_tasks_status`
- `idx_tasks_created_at`
- `idx_audit_logs` (may need to add)

**Rate Limiting:**
Add to heavy endpoints:
```python
from collections import defaultdict
from time import time

rate_limits = defaultdict(list)

def check_rate_limit(key, max_requests, window_seconds):
    """Simple rate limiting"""
    now = time()
    requests = rate_limits[key]
    
    # Remove old requests
    requests[:] = [t for t in requests if now - t < window_seconds]
    
    if len(requests) >= max_requests:
        return False
    
    requests.append(now)
    return True

# Use in endpoints:
if not check_rate_limit(f'inventory:{server_id}', 10, 60):
    return {'error': 'Rate limit exceeded'}
```

### PR5: Documentation Updates

**Update `ARCHITECTURE.md`:**
- Add event pipeline diagram
- Document plugin system architecture
- Explain webhook flow

**Update `SECURITY.md`:**
- HMAC signature security
- Webhook SSRF protection
- Secret management for webhooks
- Plugin security model

**Update `CHANGELOG.md`:**
Create v2.3.0 entry with all Phase 8 features

## Testing Checklist

- [ ] Unit tests pass (19 existing + new webhook tests)
- [ ] Integration test passes
- [ ] Database migrations work on existing DB
- [ ] Plugin system loads correctly
- [ ] Webhook CRUD operations work
- [ ] Webhook delivery works (with mock server)
- [ ] HMAC signatures verify correctly
- [ ] Rate limiting works
- [ ] Caching improves performance
- [ ] UI displays webhooks correctly
- [ ] Admin-only endpoints enforced
- [ ] SSRF protection works
- [ ] Error handling is robust

## Deployment Notes

1. **Environment Variables:**
   ```bash
   # Enable plugins
   PLUGINS_ENABLED=true
   PLUGINS_ALLOWLIST=webhook
   
   # Or use managed webhooks (via DB)
   # No plugin config needed - webhooks configured via UI/API
   ```

2. **Database Migration:**
   - Schema changes are non-breaking
   - New tables created automatically on startup
   - Existing data unaffected

3. **Backward Compatibility:**
   - All changes are opt-in
   - Works without plugins enabled
   - Existing audit logging continues to work
   - No breaking API changes

## Known Issues / TODOs

1. **Performance:**
   - Cache implementation is basic (in-memory only)
   - Consider Redis for production deployments
   - No cache invalidation strategy yet

2. **Webhooks:**
   - No webhook retry queue (retries are synchronous)
   - Consider async delivery with queue
   - No webhook signature verification endpoint

3. **UI:**
   - Webhook UI not yet implemented
   - Need delivery log visualization
   - Missing webhook test functionality

4. **Testing:**
   - Need more integration tests
   - Load testing for 500+ servers
   - Webhook delivery testing with mock server

## Next Steps

1. Complete PR2 by adding webhook API endpoints
2. Create webhook dispatcher integration
3. Add comprehensive tests
4. Update OpenAPI spec
5. Create WEBHOOKS.md documentation
6. Implement UI (PR3)
7. Add performance optimizations (PR4)
8. Update architecture documentation (PR5)
9. Final testing and validation
10. Merge to main
