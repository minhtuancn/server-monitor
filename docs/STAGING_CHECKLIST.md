# Server Monitor v2.2.0 - Staging Validation Checklist

**Version:** 2.2.0  
**Date:** January 2026  
**Purpose:** Pre-release validation for production deployment

---

## 📋 Overview

This checklist validates the Server Monitor v2.2.0 release in a staging environment before production deployment. All items must pass before releasing to production.

---

## 🎯 Pre-Validation Setup

### Environment Requirements

- [ ] Fresh Linux server (Ubuntu 22.04+ or equivalent)
- [ ] Minimum 2GB RAM, 2 CPU cores
- [ ] Python 3.11+, Node.js 20+ available
- [ ] Network access to monitored servers
- [ ] Domain/subdomain configured (if testing production URLs)

### Test Data Preparation

- [ ] Prepare 2-3 test servers for monitoring
- [ ] Create test SSH keys
- [ ] Prepare test user accounts
- [ ] Note baseline metrics for comparison

---

## 1️⃣ Fresh Installation Validation

### 1.1 One-Command Installation

```bash
# Install v2.2.0 using installer script
curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash -s -- --ref v2.2.0
```

**Validation Checklist:**

- [ ] Installer completes without errors
- [ ] All dependencies installed (Python, Node.js, system packages)
- [ ] Service user `server-monitor` created
- [ ] Directories created with correct permissions:
  - [ ] `/opt/server-monitor` (application)
  - [ ] `/etc/server-monitor` (configuration)
  - [ ] `/var/lib/server-monitor` (database)
  - [ ] `/var/log/server-monitor` (logs)
- [ ] Database initialized successfully (`servers.db` exists)
- [ ] Configuration file created at `/etc/server-monitor/config.env`
- [ ] Secrets generated (JWT_SECRET, ENCRYPTION_KEY, KEY_VAULT_MASTER_KEY)
- [ ] Systemd services created and enabled:
  - [ ] `server-monitor-api.service`
  - [ ] `server-monitor-ws.service`
  - [ ] `server-monitor-terminal.service`
  - [ ] `server-monitor-frontend.service`
- [ ] All services started and running

### 1.2 Service Status Verification

```bash
# Check all services
sudo systemctl status server-monitor-api
sudo systemctl status server-monitor-ws
sudo systemctl status server-monitor-terminal
sudo systemctl status server-monitor-frontend

# Check if services are enabled for auto-start
sudo systemctl is-enabled server-monitor-api
sudo systemctl is-enabled server-monitor-ws
sudo systemctl is-enabled server-monitor-terminal
sudo systemctl is-enabled server-monitor-frontend
```

**Validation Checklist:**

- [ ] All 4 services show `active (running)` status
- [ ] All 4 services enabled for auto-start on boot
- [ ] No error messages in service status output
- [ ] Services listening on expected ports:
  - [ ] Port 9083 (Central API)
  - [ ] Port 9085 (Monitoring WebSocket)
  - [ ] Port 9084 (Terminal WebSocket)
  - [ ] Port 9081 (Frontend)

### 1.3 Initial Access Validation

```bash
# Run smoke test
cd /opt/server-monitor
sudo -u server-monitor ./scripts/smoke.sh --verbose
```

**Validation Checklist:**

- [ ] Smoke test passes with 0 failures
- [ ] Frontend accessible at `http://SERVER_IP:9081`
- [ ] Login page loads without errors
- [ ] Default admin account works (check installer output)
- [ ] Dashboard loads after login
- [ ] No console errors in browser dev tools

---

## 2️⃣ Upgrade from v2.1.0 → v2.2.0

### 2.1 Pre-Upgrade State Capture

**On existing v2.1.0 installation:**

```bash
# Backup current state
sudo systemctl stop server-monitor-*
sudo cp /var/lib/server-monitor/servers.db /tmp/pre-upgrade-backup.db
sudo sqlite3 /var/lib/server-monitor/servers.db "SELECT COUNT(*) FROM servers;" > /tmp/server-count.txt
sudo sqlite3 /var/lib/server-monitor/servers.db "SELECT COUNT(*) FROM audit_logs;" > /tmp/audit-count.txt
sudo systemctl start server-monitor-*
```

**Record:**
- [ ] Number of servers: ___________
- [ ] Number of audit logs: ___________
- [ ] Database file size: ___________
- [ ] Configuration backed up

### 2.2 Perform Upgrade

```bash
# Run update using smctl
sudo /opt/server-monitor/scripts/smctl update v2.2.0
```

**Validation Checklist:**

- [ ] Update script completes without errors
- [ ] Services restarted automatically
- [ ] New version deployed (`/opt/server-monitor/VERSION`)
- [ ] Database migration (if any) completed
- [ ] Configuration preserved
- [ ] Secrets unchanged

### 2.3 Post-Upgrade Verification

```bash
# Verify data integrity
sudo sqlite3 /var/lib/server-monitor/servers.db "SELECT COUNT(*) FROM servers;"
sudo sqlite3 /var/lib/server-monitor/servers.db "SELECT COUNT(*) FROM audit_logs;"

# Check new features
curl http://localhost:9083/api/health
curl http://localhost:9083/api/ready
curl http://localhost:9083/api/metrics
```

**Validation Checklist:**

- [ ] All services running after upgrade
- [ ] Server count matches pre-upgrade
- [ ] Audit log count >= pre-upgrade (new entries added)
- [ ] No data loss detected
- [ ] Existing SSH keys accessible
- [ ] Existing user accounts intact
- [ ] Historical metrics preserved
- [ ] New v2.2.0 endpoints responding:
  - [ ] `/api/health` returns 200
  - [ ] `/api/ready` returns 200
  - [ ] `/api/metrics` returns metrics
- [ ] Swagger UI updated at `/docs`
- [ ] OpenAPI spec available at `/api/openapi.yaml`

---

## 3️⃣ Rollback Testing

### 3.1 Prepare for Rollback

```bash
# Create rollback point
sudo /opt/server-monitor/scripts/smctl backup
```

**Record:**
- [ ] Backup created at: ___________
- [ ] Backup size: ___________

### 3.2 Perform Rollback

```bash
# Rollback to v2.1.0
sudo /opt/server-monitor/scripts/rollback.sh v2.1.0
```

**Validation Checklist:**

- [ ] Rollback script completes without errors
- [ ] Services restarted with v2.1.0 code
- [ ] Database intact (no corruption)
- [ ] All servers still accessible
- [ ] Login still works
- [ ] Dashboard functional

### 3.3 Re-Upgrade to v2.2.0

```bash
# Upgrade again to v2.2.0 for continued testing
sudo /opt/server-monitor/scripts/smctl update v2.2.0
```

**Validation Checklist:**

- [ ] Second upgrade succeeds
- [ ] Services running normally
- [ ] Data preserved through rollback cycle

---

## 4️⃣ Database Integrity & Performance

### 4.1 Database Health Check

```bash
# Check database integrity
sudo sqlite3 /var/lib/server-monitor/servers.db "PRAGMA integrity_check;"

# Check database size and table counts
sudo sqlite3 /var/lib/server-monitor/servers.db ".dbinfo"
```

**Validation Checklist:**

- [ ] Integrity check returns "ok"
- [ ] No corruption detected
- [ ] All tables present
- [ ] Indexes intact
- [ ] No orphaned records

### 4.2 Concurrent Access Testing

```bash
# Simulate concurrent reads/writes
for i in {1..10}; do
  curl -s http://localhost:9083/api/servers &
done
wait
```

**Validation Checklist:**

- [ ] No database lock errors
- [ ] All requests complete successfully
- [ ] Response times acceptable (<500ms)
- [ ] No connection pool exhaustion

---

## 5️⃣ Service Validation (Systemd)

### 5.1 Service Restart Testing

```bash
# Test individual service restarts
sudo systemctl restart server-monitor-api
sleep 2
sudo systemctl status server-monitor-api

sudo systemctl restart server-monitor-ws
sleep 2
sudo systemctl status server-monitor-ws

sudo systemctl restart server-monitor-terminal
sleep 2
sudo systemctl status server-monitor-terminal

sudo systemctl restart server-monitor-frontend
sleep 2
sudo systemctl status server-monitor-frontend
```

**Validation Checklist:**

- [ ] Each service restarts cleanly
- [ ] No error messages in journal logs
- [ ] Services return to active state within 5 seconds
- [ ] Dependent services not affected

### 5.2 Full System Restart

```bash
# Stop all services
sudo systemctl stop server-monitor-*

# Start all services
sudo systemctl start server-monitor-*

# Wait and check
sleep 5
sudo systemctl status server-monitor-*
```

**Validation Checklist:**

- [ ] All services start successfully
- [ ] Correct startup order maintained
- [ ] No race conditions
- [ ] Frontend connects to API
- [ ] WebSocket services available

### 5.3 Boot Persistence

```bash
# Reboot server
sudo reboot

# After reboot, check auto-start
sudo systemctl status server-monitor-*
```

**Validation Checklist:**

- [ ] All services auto-start on boot
- [ ] Services operational within 30 seconds
- [ ] No manual intervention required

---

## 6️⃣ New v2.2.0 Features Validation

### 6.1 Observability Endpoints

**Test Health Endpoint:**
```bash
curl -i http://localhost:9083/api/health
```

**Expected:**
- [ ] HTTP 200 status
- [ ] Response body: `{"status": "ok", "timestamp": "..."}`
- [ ] Response time < 100ms

**Test Readiness Endpoint:**
```bash
curl -i http://localhost:9083/api/ready
```

**Expected:**
- [ ] HTTP 200 status
- [ ] Response includes database check: `{"status": "ready", "checks": {...}}`
- [ ] All checks pass

**Test Metrics Endpoint (Prometheus format):**
```bash
curl http://localhost:9083/api/metrics
```

**Expected:**
- [ ] Returns Prometheus text format
- [ ] Includes `uptime_seconds`
- [ ] Includes request counts
- [ ] Includes latency metrics
- [ ] Includes WebSocket connection count

**Test Metrics Endpoint (JSON format):**
```bash
curl http://localhost:9083/api/metrics?format=json
```

**Expected:**
- [ ] Returns JSON format
- [ ] Same metrics as Prometheus format
- [ ] Valid JSON structure

### 6.2 Audit Export Endpoints

**Login as admin first:**
```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:9083/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"YOUR_ADMIN_PASSWORD"}' | jq -r '.token')
```

**Test CSV Export:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:9083/api/export/audit/csv > /tmp/audit.csv
```

**Expected:**
- [ ] HTTP 200 status
- [ ] Valid CSV format
- [ ] Contains audit log entries
- [ ] CSV injection characters escaped
- [ ] Headers present

**Test JSON Export:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:9083/api/export/audit/json > /tmp/audit.json
```

**Expected:**
- [ ] HTTP 200 status
- [ ] Valid JSON format
- [ ] Contains audit log entries
- [ ] Sensitive data sanitized

### 6.3 Task Recovery & Graceful Shutdown

**Create a long-running task:**
```bash
# Through the UI, create a task that runs "sleep 300"
```

**Test Graceful Shutdown:**
```bash
# Send SIGTERM to API service
sudo systemctl restart server-monitor-api

# Check task status
curl http://localhost:9083/api/tasks
```

**Expected:**
- [ ] Service shuts down gracefully (no kill -9)
- [ ] Running task marked as "interrupted"
- [ ] Audit log entry created
- [ ] No orphaned processes
- [ ] Service restarts cleanly

**Test Task Recovery:**
```bash
# Simulate crashed service (kill -9)
sudo pkill -9 -f "central_api"

# Wait 2 minutes for staleness
sleep 120

# Restart service
sudo systemctl start server-monitor-api

# Check logs
sudo journalctl -u server-monitor-api -n 50
```

**Expected:**
- [ ] Startup log shows recovery statistics
- [ ] Stale tasks detected and recovered
- [ ] Tasks marked as "interrupted"
- [ ] Recovery audit log entries created

### 6.4 Audit Cleanup

**Test Startup Cleanup:**
```bash
# Check logs on service start
sudo journalctl -u server-monitor-api -b | grep -i "audit cleanup"
```

**Expected:**
- [ ] Cleanup runs on startup
- [ ] Logs show number of records cleaned
- [ ] No errors during cleanup
- [ ] Database not locked

**Test Scheduled Cleanup:**
```bash
# Wait for scheduled cleanup (check interval in config)
# Default: 24 hours, can configure shorter for testing
```

**Expected:**
- [ ] Cleanup runs periodically
- [ ] Old records deleted per retention policy
- [ ] Performance not impacted

### 6.5 Structured Logging

**Check Log Format:**
```bash
# API logs
sudo journalctl -u server-monitor-api -n 10 -o cat

# WebSocket logs
sudo journalctl -u server-monitor-ws -n 10 -o cat

# Terminal logs
sudo journalctl -u server-monitor-terminal -n 10 -o cat
```

**Expected:**
- [ ] All logs in JSON format
- [ ] Consistent structure across services
- [ ] Contains: timestamp, level, service, message
- [ ] Request-ID present in API logs
- [ ] Sensitive data redacted (passwords, tokens)

---

## 7️⃣ API Documentation Validation

### 7.1 Swagger UI

**Access Swagger UI:**
```bash
# Browser: http://localhost:9083/docs
```

**Validation:**
- [ ] Swagger UI loads successfully
- [ ] All endpoints documented
- [ ] Try It Out feature works
- [ ] Request/response examples present
- [ ] Authentication flow functional
- [ ] New v2.2.0 endpoints listed:
  - [ ] `/api/health`
  - [ ] `/api/ready`
  - [ ] `/api/metrics`
  - [ ] `/api/export/audit/csv`
  - [ ] `/api/export/audit/json`

### 7.2 OpenAPI Specification

**Download OpenAPI Spec:**
```bash
curl http://localhost:9083/api/openapi.yaml > /tmp/openapi.yaml
```

**Validation:**
- [ ] Valid YAML format
- [ ] OpenAPI 3.0.3 compliant
- [ ] Contains all endpoints
- [ ] Security schemes defined
- [ ] Schema definitions complete
- [ ] Examples provided

---

## 8️⃣ Security Validation

### 8.1 Startup Secret Validation

**Test with weak secrets (should fail):**
```bash
# Edit config to use placeholder secrets
sudo sed -i 's/JWT_SECRET=.*/JWT_SECRET=change_me_in_production/' /etc/server-monitor/config.env

# Restart service
sudo systemctl restart server-monitor-api

# Check status
sudo systemctl status server-monitor-api
```

**Expected:**
- [ ] Service fails to start
- [ ] Error logged about weak secret
- [ ] Exit code 1

**Restore proper secrets:**
```bash
# Restore original config
sudo systemctl restart server-monitor-api
```

### 8.2 Task Safety Policy

**Test dangerous command blocking:**
```bash
# Attempt to run dangerous command through UI
# Try: "rm -rf /"
```

**Expected:**
- [ ] Command blocked
- [ ] Error message shown
- [ ] Audit log entry created
- [ ] Task not executed

**Test allowed commands:**
```bash
# Run safe command through UI
# Try: "ls -la"
```

**Expected:**
- [ ] Command executes successfully
- [ ] Output returned
- [ ] Audit log entry created

---

## 9️⃣ Integration Testing

### 9.1 End-to-End User Flow

**Complete User Journey:**

1. **Login**
   - [ ] Login page loads
   - [ ] Valid credentials accepted
   - [ ] Invalid credentials rejected
   - [ ] Session cookie set (HttpOnly)

2. **Add Server**
   - [ ] Add server form works
   - [ ] SSH connection test succeeds
   - [ ] Server appears in list
   - [ ] Metrics collected

3. **Monitor Server**
   - [ ] Dashboard shows server
   - [ ] Real-time metrics update via WebSocket
   - [ ] Charts render correctly
   - [ ] No memory leaks (check over 5 minutes)

4. **Use Web Terminal**
   - [ ] Terminal connects via WebSocket
   - [ ] Commands execute correctly
   - [ ] Output displays properly
   - [ ] Session tracked in audit log
   - [ ] Session closes cleanly

5. **Create Task**
   - [ ] Task form submits
   - [ ] Task executes asynchronously
   - [ ] Output captured
   - [ ] Status updates correctly
   - [ ] Completion logged

6. **View Audit Logs**
   - [ ] Audit log page loads
   - [ ] Filters work
   - [ ] Export to CSV works
   - [ ] Export to JSON works

7. **Logout**
   - [ ] Logout successful
   - [ ] Session invalidated
   - [ ] Cookie cleared
   - [ ] Redirect to login

### 9.2 Multi-User Concurrency

**Simulate Multiple Users:**
```bash
# Open 3-5 browser sessions
# Perform various operations simultaneously
```

**Expected:**
- [ ] No race conditions
- [ ] No database locks
- [ ] All operations complete
- [ ] Correct data isolation

---

## 🔟 Performance & Load Testing

### 10.1 API Response Times

**Measure Key Endpoints:**
```bash
# Health check
time curl http://localhost:9083/api/health

# Stats
time curl http://localhost:9083/api/stats/overview

# Server list
time curl http://localhost:9083/api/servers
```

**Expected:**
- [ ] Health: < 50ms
- [ ] Stats: < 200ms
- [ ] Server list: < 300ms

### 10.2 WebSocket Stability

**Long-Running Connection:**
```bash
# Keep WebSocket connection open for 10 minutes
# Monitor for disconnects or memory leaks
```

**Expected:**
- [ ] Connection stable
- [ ] No disconnects
- [ ] Memory usage stable
- [ ] CPU usage reasonable

---

## 1️⃣1️⃣ Smoke Test (Automated)

### 11.1 Run Standard Smoke Test

```bash
cd /opt/server-monitor
sudo -u server-monitor ./scripts/smoke.sh --verbose
```

**Expected:**
- [ ] All tests pass
- [ ] Exit code 0
- [ ] No warnings
- [ ] Summary shows 0 failures

### 11.2 Run Staging Smoke Test

```bash
# Test against staging URL
./scripts/smoke.sh --base-url http://staging.example.com --api-url http://staging.example.com
```

**Expected:**
- [ ] Tests pass against remote staging
- [ ] Public endpoints accessible
- [ ] Private endpoints return 401 (as expected)

### 11.3 Run Authenticated Smoke Test

```bash
# Set credentials as environment variables (safer than command-line args)
export SMOKE_USER="admin"
export SMOKE_PASS="YOUR_PASSWORD"

# Test with admin credentials
./scripts/smoke.sh --auth-user "$SMOKE_USER" --auth-pass "$SMOKE_PASS" --verbose

# Clear credentials from environment
unset SMOKE_USER SMOKE_PASS
```

**Expected:**
- [ ] Authenticated tests pass
- [ ] Protected endpoints accessible
- [ ] Token validation works

---

## 1️⃣2️⃣ Documentation Review

### 12.1 Verify Documentation

- [ ] README.md updated to v2.2.0
- [ ] CHANGELOG.md includes v2.2.0 entry
- [ ] RELEASE_NOTES_v2.2.0.md complete
- [ ] POST-PRODUCTION.md accurate
- [ ] DEPLOYMENT.md accurate
- [ ] API docs (Swagger) updated
- [ ] All links work
- [ ] Screenshots up-to-date (if any)

### 12.2 Installation Documentation

**Follow Installation Docs:**
- [ ] One-command install instructions accurate
- [ ] Manual install instructions accurate
- [ ] Configuration examples valid
- [ ] Troubleshooting guide helpful
- [ ] Upgrade guide clear

---

## ✅ Sign-Off Checklist

### Pre-Production Approval

**Technical Lead Sign-Off:**
- [ ] All validation tests passed
- [ ] No critical bugs found
- [ ] Performance acceptable
- [ ] Security validated
- [ ] Documentation complete

**QA Sign-Off:**
- [ ] End-to-end testing complete
- [ ] Edge cases tested
- [ ] Rollback tested
- [ ] Upgrade path validated

**DevOps Sign-Off:**
- [ ] Installation tested
- [ ] Service management validated
- [ ] Monitoring ready
- [ ] Backup/restore verified

**Security Sign-Off:**
- [ ] Security features validated
- [ ] Secrets management correct
- [ ] Audit logging working
- [ ] Task policy enforced

---

## 📊 Test Results Summary

**Date Tested:** ___________  
**Tested By:** ___________  
**Environment:** ___________

**Overall Result:**
- [ ] ✅ PASS - Ready for production
- [ ] ⚠️ PASS WITH ISSUES - Minor issues noted (document below)
- [ ] ❌ FAIL - Blocking issues found (document below)

**Issues Found:**
1. _________________________________________________
2. _________________________________________________
3. _________________________________________________

**Notes:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

## 1️⃣3️⃣ Phase 8 / v2.3.0 Features Validation

### 13.1 Plugin System

**Verify Plugin Framework:**
```bash
# Check plugin system is loaded (via logs)
sudo journalctl -u server-monitor-api -n 100 | grep -i plugin

# Check event model in code
cat /opt/server-monitor/backend/event_model.py | head -20
```

**Validation Checklist:**
- [ ] Plugin system initializes on startup
- [ ] Event model defined (Event dataclass)
- [ ] Plugin manager loaded
- [ ] No plugin errors in logs
- [ ] Structured logging shows plugin events

### 13.2 Webhooks UI (Admin Settings)

**Access Webhooks Page:**
```bash
# URL: http://localhost:9081/settings/integrations
# Login as admin user
```

**Create Webhook:**
- [ ] Navigate to Settings → Integrations
- [ ] Click "Add Webhook" or similar button
- [ ] Fill in webhook details:
  - Name: "Test Webhook"
  - URL: https://webhook.site/<your-unique-url>
  - Secret: "test-secret-123"
  - Event types: Select "task.finished", "alert.triggered"
  - Enabled: Yes
- [ ] Save webhook
- [ ] Webhook appears in list

**Edit Webhook:**
- [ ] Click edit on test webhook
- [ ] Change name to "Updated Webhook"
- [ ] Toggle enabled off
- [ ] Save changes
- [ ] Changes reflected in list

**Test Webhook:**
- [ ] Click "Test" button on webhook
- [ ] Test event sent successfully
- [ ] Check webhook.site for received request
- [ ] Verify payload structure
- [ ] Verify headers (X-SM-Event-Id, X-SM-Signature, etc.)

**Delete Webhook:**
- [ ] Click delete on test webhook
- [ ] Confirm deletion dialog
- [ ] Webhook removed from list

**Internationalization:**
- [ ] UI text appears in correct language
- [ ] Language switcher works
- [ ] All labels translated (8 languages)

### 13.3 Webhooks API (Authenticated Tests)

**Get Admin Token:**
```bash
TOKEN=$(curl -s -X POST http://localhost:9083/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"YOUR_PASSWORD"}' | jq -r '.token')

echo "Token: $TOKEN"
```

**List Webhooks:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:9083/api/webhooks | jq
```

**Expected:**
- [ ] HTTP 200 status
- [ ] Returns JSON with "webhooks" array
- [ ] Array may be empty or contain webhooks

**Create Webhook via API:**
```bash
curl -X POST http://localhost:9083/api/webhooks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Test Webhook",
    "url": "https://webhook.site/<your-url>",
    "secret": "api-secret-456",
    "enabled": true,
    "event_types": ["task.finished"],
    "retry_max": 3,
    "timeout": 10
  }' | jq
```

**Expected:**
- [ ] HTTP 201 status
- [ ] Returns webhook ID
- [ ] Webhook created in database

**Test Webhook Delivery:**
```bash
WEBHOOK_ID="<webhook-id-from-create>"

curl -X POST http://localhost:9083/api/webhooks/$WEBHOOK_ID/test \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Expected:**
- [ ] HTTP 200 status
- [ ] Test event sent
- [ ] Check webhook.site for delivery
- [ ] Verify HMAC signature in X-SM-Signature header

**Get Delivery Logs:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9083/api/webhooks/$WEBHOOK_ID/deliveries?limit=10" | jq
```

**Expected:**
- [ ] HTTP 200 status
- [ ] Returns array of delivery attempts
- [ ] Shows status (success/failed/retrying)
- [ ] Includes status_code, response_body, timestamps

**Delete Webhook:**
```bash
curl -X DELETE http://localhost:9083/api/webhooks/$WEBHOOK_ID \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:**
- [ ] HTTP 200 status
- [ ] Webhook deleted

### 13.4 SSRF Protection Testing

**Test Blocked URLs:**

```bash
# Test localhost (should be blocked)
curl -X POST http://localhost:9083/api/webhooks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SSRF Test - Localhost",
    "url": "http://localhost/webhook",
    "enabled": true
  }' | jq
```

**Expected:**
- [ ] HTTP 400 or 422 status
- [ ] Error message: "Internal/localhost URLs are not allowed" or similar
- [ ] Webhook not created

**Test private IP (should be blocked):**
```bash
curl -X POST http://localhost:9083/api/webhooks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SSRF Test - Private IP",
    "url": "http://192.168.1.100/webhook",
    "enabled": true
  }' | jq
```

**Expected:**
- [ ] HTTP 400 or 422 status
- [ ] Error message: "Private network addresses are not allowed" or similar
- [ ] Webhook not created

**Test internal hostname (should be blocked):**
```bash
curl -X POST http://localhost:9083/api/webhooks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SSRF Test - Internal Host",
    "url": "http://server.local/webhook",
    "enabled": true
  }' | jq
```

**Expected:**
- [ ] HTTP 400 or 422 status
- [ ] Error message: "Internal hostname patterns are not allowed"
- [ ] Webhook not created

**SSRF Validation Summary:**
- [ ] Localhost blocked (127.0.0.1, ::1, localhost)
- [ ] Private networks blocked (10.x, 172.16.x, 192.168.x)
- [ ] Link-local blocked (169.254.x.x)
- [ ] Internal hostnames blocked (.local, .internal, .lan)
- [ ] Invalid schemes blocked (file://, ftp://)
- [ ] Valid external URLs accepted

### 13.5 HMAC Signature Verification

**Python Verification Script:**

Save as `/tmp/verify_webhook.py`:
```python
#!/usr/bin/env python3
import hmac
import hashlib
import json

def verify_webhook(payload_str, signature_header, secret):
    """Verify webhook HMAC signature"""
    payload_bytes = payload_str.encode('utf-8')
    expected = hmac.new(
        secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    received = signature_header.split('=')[1] if '=' in signature_header else signature_header
    
    return hmac.compare_digest(expected, received)

# Example usage
if __name__ == "__main__":
    # Paste actual values from webhook.site
    payload = '{"event_id":"123","event_type":"task.finished","timestamp":"2026-01-08T00:00:00Z"}'
    signature = "sha256=abc123def456..."  # From X-SM-Signature header
    secret = "your-webhook-secret"
    
    if verify_webhook(payload, signature, secret):
        print("✅ Signature valid!")
    else:
        print("❌ Signature invalid!")
```

**Test HMAC:**
```bash
# Run verification script with actual webhook data
python3 /tmp/verify_webhook.py
```

**Expected:**
- [ ] Script outputs "✅ Signature valid!"
- [ ] Signature matches expected HMAC-SHA256 value

### 13.6 Rate Limiting (HTTP 429)

**Test Rate Limit on Inventory Refresh:**
```bash
# Make rapid requests to trigger rate limit
SERVER_ID="<existing-server-id>"

for i in {1..15}; do
  echo "Request $i:"
  curl -s -o /dev/null -w "HTTP %{http_code}\n" \
    -X POST http://localhost:9083/api/servers/$SERVER_ID/inventory/refresh \
    -H "Authorization: Bearer $TOKEN"
  sleep 0.5
done
```

**Expected:**
- [ ] First 10 requests: HTTP 200 or 202
- [ ] Subsequent requests: HTTP 429 (Too Many Requests)
- [ ] Response includes `Retry-After` header (seconds)
- [ ] Response includes rate limit headers:
  - `X-RateLimit-Limit: 10`
  - `X-RateLimit-Remaining: 0`
  - `X-RateLimit-Reset: <timestamp>`

**Rate Limit Summary:**
- [ ] Rate limiting active on heavy endpoints
- [ ] 429 status returned when limit exceeded
- [ ] Retry-After header present
- [ ] Rate resets after window expires

### 13.7 Cache Performance Validation

**Check Cache Metrics:**
```bash
curl http://localhost:9083/api/metrics | grep cache
```

**Expected metrics:**
```
cache_hits_total <number>
cache_misses_total <number>
cache_hit_rate <0.0-1.0>
```

**Test Cache Behavior:**
```bash
# First request (cache miss)
time curl -s http://localhost:9083/api/stats/overview > /dev/null

# Second request (cache hit, should be faster)
time curl -s http://localhost:9083/api/stats/overview > /dev/null

# Wait for TTL expiration (30+ seconds for stats/overview)
sleep 35

# Third request (cache miss again)
time curl -s http://localhost:9083/api/stats/overview > /dev/null
```

**Expected:**
- [ ] Second request faster than first (cache hit)
- [ ] Third request slower again after TTL (cache miss)
- [ ] Cache hit rate increases in metrics
- [ ] Performance improvement visible (40-60% faster on cached)

**Cache Summary:**
- [ ] Cache hit/miss metrics available
- [ ] Cached endpoints respond faster on hit
- [ ] TTL expiration works correctly
- [ ] No stale data issues

### 13.8 Webhook Delivery Metrics

**Check Webhook Metrics:**
```bash
curl http://localhost:9083/api/metrics | grep webhook
```

**Expected metrics:**
```
webhook_deliveries_total{status="success"} <number>
webhook_deliveries_total{status="failed"} <number>
webhook_deliveries_total{status="retrying"} <number>
```

**Validation:**
- [ ] Webhook delivery counters present
- [ ] Metrics increment on delivery
- [ ] Success/failed/retrying tracked separately

---

## 1️⃣4️⃣ RBAC & Admin-Only Validation

### 14.1 Non-Admin User Test

**Create non-admin user:**
```bash
# Via UI or API (as admin)
# Username: testuser, Role: operator or user
```

**Get non-admin token:**
```bash
USER_TOKEN=$(curl -s -X POST http://localhost:9083/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password"}' | jq -r '.token')
```

**Test webhooks access (should fail):**
```bash
curl -H "Authorization: Bearer $USER_TOKEN" \
  http://localhost:9083/api/webhooks
```

**Expected:**
- [ ] HTTP 403 Forbidden
- [ ] Error message: "Admin access required" or similar
- [ ] Non-admin users cannot access webhooks

**RBAC Summary:**
- [ ] Admin-only endpoints enforced
- [ ] Non-admin users get 403 on webhooks
- [ ] Proper error messages returned

---

## 📝 Post-Validation Actions

After successful staging validation:

1. [ ] Create Git tag `v2.3.0`
2. [ ] Create GitHub Release with notes
3. [ ] Attach OpenAPI spec to release
4. [ ] Generate and attach checksums (install.sh, SBOM files)
5. [ ] Update README badges
6. [ ] Announce release (if applicable)
7. [ ] Schedule production deployment
8. [ ] Prepare production runbook
9. [ ] Brief operations team
10. [ ] Monitor initial production deployment

---

**Document Version:** 1.0  
**Last Updated:** January 2026  
**Maintained By:** DevSecOps Team
