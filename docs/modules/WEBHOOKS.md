# Webhooks Management

**Version:** 2.3.0  
**Last Updated:** 2026-01-08

---

## Overview

The Webhooks Management feature allows administrators to configure HTTP callbacks that are triggered when specific events occur in the Server Monitor system. This enables integration with external systems, notification services, and custom automation workflows.

### Key Features

- **Managed Configuration**: Configure webhooks through UI or API (no ENV variables needed)
- **Event Filtering**: Subscribe to specific event types or all events
- **HMAC Signing**: Secure webhook deliveries with SHA256 HMAC signatures
- **Delivery Logs**: Track all webhook delivery attempts with status and errors
- **Retry Logic**: Automatic retry with exponential backoff on failures
- **SSRF Protection**: Built-in security to prevent internal network access
- **Test Functionality**: Send test events to verify webhook configuration

---

## Use Cases

### 1. External Notification Systems
Send events to external platforms like Slack, Discord, PagerDuty, or custom notification services.

```json
{
  "name": "Slack Notifications",
  "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "event_types": ["alert.triggered", "server.status_changed", "task.failed"]
}
```

### 2. CI/CD Pipeline Integration
Trigger builds or deployments when servers are updated or tasks complete.

```json
{
  "name": "CI/CD Trigger",
  "url": "https://ci.example.com/webhooks/server-monitor",
  "event_types": ["server.updated", "task.finished"]
}
```

### 3. Audit Log Forwarding
Forward audit events to external SIEM or logging systems.

```json
{
  "name": "SIEM Forwarder",
  "url": "https://siem.example.com/api/events",
  "event_types": ["user.login", "settings.updated", "webhook.created"]
}
```

### 4. Custom Automation
Build custom automation workflows triggered by server monitor events.

```json
{
  "name": "Custom Automation",
  "url": "https://automation.example.com/webhook",
  "secret": "your-secret-key"
}
```

---

## Configuration

### Via API

#### Create Webhook

```bash
curl -X POST https://your-server:9083/api/webhooks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Webhook",
    "url": "https://example.com/webhook",
    "secret": "my-secret-key",
    "enabled": true,
    "event_types": ["task.finished", "server.created"],
    "retry_max": 3,
    "timeout": 10
  }'
```

**Response:**
```json
{
  "success": true,
  "webhook_id": "webhook-uuid-here"
}
```

#### List Webhooks

```bash
curl -X GET https://your-server:9083/api/webhooks \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "webhooks": [
    {
      "id": "webhook-uuid",
      "name": "My Webhook",
      "url": "https://example.com/webhook",
      "secret": "***REDACTED***",
      "enabled": 1,
      "event_types": ["task.finished", "server.created"],
      "retry_max": 3,
      "timeout": 10,
      "created_at": "2026-01-08T01:00:00Z",
      "updated_at": "2026-01-08T01:00:00Z",
      "last_triggered_at": null
    }
  ]
}
```

#### Update Webhook

```bash
curl -X PUT https://your-server:9083/api/webhooks/WEBHOOK_ID \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false,
    "retry_max": 5
  }'
```

#### Delete Webhook

```bash
curl -X DELETE https://your-server:9083/api/webhooks/WEBHOOK_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Test Webhook

```bash
curl -X POST https://your-server:9083/api/webhooks/WEBHOOK_ID/test \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get Delivery Logs

```bash
curl -X GET "https://your-server:9083/api/webhooks/WEBHOOK_ID/deliveries?limit=50&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "deliveries": [
    {
      "id": "delivery-uuid",
      "webhook_id": "webhook-uuid",
      "event_id": "event-uuid",
      "event_type": "task.finished",
      "status": "success",
      "status_code": 200,
      "response_body": "OK",
      "error": null,
      "attempt": 1,
      "delivered_at": "2026-01-08T01:05:00Z"
    }
  ],
  "count": 1,
  "limit": 50,
  "offset": 0
}
```

### Via UI

1. Navigate to **Settings → Integrations → Webhooks**
2. Click **Add Webhook**
3. Fill in webhook details:
   - Name: Descriptive name for the webhook
   - URL: Target endpoint URL
   - Secret: Optional HMAC secret for signature verification
   - Event Types: Select specific events or leave empty for all events
   - Retry Max: Number of retry attempts (default: 3)
   - Timeout: Request timeout in seconds (default: 10)
4. Click **Save**
5. Use **Test** button to verify configuration

---

## Webhook Payload

When an event occurs, Server Monitor sends an HTTP POST request to the configured webhook URL with the following structure:

### Headers

```
Content-Type: application/json
X-SM-Event-Id: event-uuid
X-SM-Event-Type: task.finished
X-SM-Signature: sha256=HMAC_SIGNATURE
User-Agent: ServerMonitor-Webhook/2.3.0
```

### Body

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "task.finished",
  "timestamp": "2026-01-08T01:00:00.000Z",
  "user_id": 1,
  "username": "admin",
  "server_id": 5,
  "server_name": "web-01",
  "target_type": "task",
  "target_id": "task-123",
  "action": "task_finished",
  "meta": {
    "task_id": "task-123",
    "command": "df -h",
    "exit_code": 0,
    "output": "..."
  },
  "ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "severity": "info"
}
```

---

## HMAC Signature Verification

If a webhook secret is configured, Server Monitor includes an HMAC-SHA256 signature in the `X-SM-Signature` header.

### Verification Example (Python)

```python
import hmac
import hashlib
import json

def verify_webhook(request_body, signature_header, secret):
    """
    Verify webhook signature
    
    Args:
        request_body: Raw request body (bytes)
        signature_header: Value of X-SM-Signature header
        secret: Webhook secret (string)
    
    Returns:
        bool: True if signature is valid
    """
    # Extract signature from header
    if not signature_header.startswith('sha256='):
        return False
    
    received_signature = signature_header[7:]  # Remove 'sha256=' prefix
    
    # Calculate expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        request_body,
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures (constant-time comparison)
    return hmac.compare_digest(expected_signature, received_signature)

# Usage in Flask
from flask import Flask, request

app = Flask(__name__)
WEBHOOK_SECRET = 'your-secret-key'

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-SM-Signature', '')
    
    if not verify_webhook(request.data, signature, WEBHOOK_SECRET):
        return 'Invalid signature', 401
    
    event = request.json
    print(f"Received event: {event['event_type']}")
    
    return 'OK', 200
```

### Verification Example (Node.js)

```javascript
const crypto = require('crypto');
const express = require('express');

const app = express();
const WEBHOOK_SECRET = 'your-secret-key';

app.use(express.json());

function verifyWebhook(body, signature, secret) {
  if (!signature.startsWith('sha256=')) {
    return false;
  }
  
  const receivedSignature = signature.substring(7);
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(JSON.stringify(body))
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(receivedSignature),
    Buffer.from(expectedSignature)
  );
}

app.post('/webhook', (req, res) => {
  const signature = req.headers['x-sm-signature'] || '';
  
  if (!verifyWebhook(req.body, signature, WEBHOOK_SECRET)) {
    return res.status(401).send('Invalid signature');
  }
  
  const event = req.body;
  console.log(`Received event: ${event.event_type}`);
  
  res.send('OK');
});

app.listen(3000);
```

---

## Event Types Reference

### Server Events
- `server.created` - New server added
- `server.updated` - Server configuration changed
- `server.deleted` - Server removed
- `server.status_changed` - Server status changed

### Task Events
- `task.created` - Task scheduled
- `task.started` - Task execution started
- `task.finished` - Task completed successfully
- `task.failed` - Task execution failed
- `task.cancelled` - Task cancelled by user

### Terminal Events
- `terminal.connect` - Terminal session started
- `terminal.disconnect` - Terminal session ended
- `terminal.command` - Command executed in terminal

### User Events
- `user.login` - User logged in
- `user.logout` - User logged out
- `user.created` - New user created
- `user.updated` - User profile updated
- `user.deleted` - User deleted

### Webhook Events
- `webhook.created` - Webhook created
- `webhook.updated` - Webhook updated
- `webhook.deleted` - Webhook deleted
- `webhook.test` - Test webhook delivery

### Other Events
- `alert.triggered` - Alert condition met
- `alert.resolved` - Alert condition resolved
- `settings.updated` - System settings changed
- `inventory.collected` - Inventory data collected
- `ssh_key.created` - SSH key added
- `ssh_key.deleted` - SSH key removed

---

## Security

### SSRF Protection

Server Monitor includes built-in SSRF (Server-Side Request Forgery) protection to prevent webhooks from targeting internal resources:

**Blocked URLs:**
- `localhost`, `127.0.0.1`, `0.0.0.0`
- IPv6 localhost (`::1`)
- Private IP ranges:
  - `10.0.0.0/8`
  - `172.16.0.0/12`
  - `192.168.0.0/16`
- Link-local addresses
- Internal domain patterns (`.local`, `.internal`, `.lan`)
- Non-HTTP schemes (`file://`, `gopher://`, `ftp://`)

**Allowed URLs:**
- Public `http://` and `https://` URLs only

### Best Practices

1. **Use HTTPS**: Always use HTTPS URLs for production webhooks
2. **Configure Secrets**: Enable HMAC signing for all webhooks
3. **Verify Signatures**: Always verify HMAC signatures on the receiving end
4. **Limit Event Types**: Subscribe only to events you need
5. **Monitor Deliveries**: Check delivery logs for failures
6. **Rotate Secrets**: Periodically update webhook secrets
7. **Rate Limiting**: Implement rate limiting on webhook receivers
8. **Validate Payload**: Validate event payload structure and types

### Secret Management

- Secrets are stored encrypted in the database
- Secrets are never exposed in API responses (shown as `***REDACTED***`)
- Secrets can only be set during creation or update
- To change a secret, provide a new value in the update request
- To remove signing, set secret to empty string

---

## Troubleshooting

### Webhook Not Firing

**Check:**
1. Webhook is enabled (`enabled: true`)
2. Event type filter includes the event (or is empty for all events)
3. Webhook URL is reachable from server
4. No SSRF protection blocking the URL
5. Check delivery logs for error details

### Signature Verification Fails

**Common Issues:**
1. **Secret Mismatch**: Ensure webhook secret matches verification secret
2. **Body Modification**: Don't modify request body before verification
3. **Encoding Issues**: Use raw bytes for signature calculation
4. **Header Case**: Header names might be lowercase (`x-sm-signature`)

### High Failure Rate

**Solutions:**
1. Increase `timeout` value (default: 10 seconds)
2. Increase `retry_max` value (default: 3)
3. Check webhook endpoint performance
4. Verify network connectivity
5. Check for rate limiting on receiver side

### Delivery Delays

**Causes:**
- Webhook endpoint slow to respond
- Multiple retries due to failures
- High system load

**Solutions:**
- Optimize webhook endpoint performance
- Return response quickly (process async if needed)
- Monitor system resources

---

## Performance Considerations

### Webhook Delivery

- Webhooks are delivered synchronously within the request that triggers the event
- Failed deliveries retry with exponential backoff (1s, 2s, 4s)
- Maximum retry attempts: configurable (default: 3)
- Timeout per attempt: configurable (default: 10 seconds)

### Best Practices

1. **Receiver Performance**: Webhook receivers should respond quickly (< 1 second)
2. **Async Processing**: Process webhook payload asynchronously after responding
3. **Limit Event Types**: Only subscribe to events you need
4. **Monitor Load**: Check delivery logs for patterns
5. **Use Queues**: For high-volume scenarios, consider using a message queue on the receiver side

---

## API Reference

See [OpenAPI Documentation](/docs/openapi.yaml) for complete API specification.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/webhooks` | List all webhooks |
| POST | `/api/webhooks` | Create webhook |
| GET | `/api/webhooks/{id}` | Get webhook details |
| PUT | `/api/webhooks/{id}` | Update webhook |
| DELETE | `/api/webhooks/{id}` | Delete webhook |
| POST | `/api/webhooks/{id}/test` | Test webhook delivery |
| GET | `/api/webhooks/{id}/deliveries` | Get delivery logs |

All endpoints require admin authentication.

---

## Changelog

### Version 2.3.0 (2026-01-08)
- Initial release of managed webhooks feature
- CRUD API endpoints
- UI for webhook management
- Delivery logging and monitoring
- HMAC signing support
- SSRF protection
- Test functionality

---

## Support

For issues or questions:
1. Check delivery logs in UI
2. Review troubleshooting section above
3. Check system logs for detailed error messages
4. Create an issue on GitHub

---

## Related Documentation

- [Plugin System](/docs/modules/PLUGINS.md)
- [Event Model](/backend/event_model.py)
- [Audit Logs](/docs/modules/AUDIT.md)
- [Security Guide](/SECURITY.md)
