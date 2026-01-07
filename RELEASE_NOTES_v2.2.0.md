# Server Monitor v2.2.0 Release Notes

**Release Date:** January 2026  
**Code Name:** Observability & Reliability

---

## 🎯 Overview

Version 2.2.0 brings **comprehensive observability, enhanced security, and system reliability** features to the Server Monitor platform. This release focuses on production readiness with zero breaking changes.

### Key Highlights

✨ **Observability:** Health checks, metrics, and request tracing  
🔒 **Security:** Startup validation, task safety policy, audit retention  
🛡️ **Reliability:** Graceful shutdown, automatic task recovery  
📊 **Monitoring:** Prometheus metrics, structured logging  
📦 **No Breaking Changes:** Fully backward compatible

---

## 🚀 New Features

### 1. Observability & Monitoring

#### Health & Readiness Checks

- **`GET /api/health`** - Liveness check (public)
  - Returns service status
  - Used by container orchestrators
  - Response: `{status: "ok", timestamp: "..."}`

- **`GET /api/ready`** - Readiness check (public)
  - Validates database connectivity
  - Checks critical configuration
  - Returns detailed check results

#### Metrics Endpoint

- **`GET /api/metrics`** - System metrics (admin/localhost)
  - Prometheus format (default)
  - JSON format with `?format=json`
  - Includes:
    - Uptime
    - Request counts by endpoint
    - Latency percentiles (avg, min, max, p95)
    - WebSocket connections
    - Terminal sessions
    - Running/queued tasks

#### Request Correlation

- Auto-generated `X-Request-Id` header
- Propagated through all services
- Included in structured logs
- Returned in response headers
- Enables end-to-end request tracing

#### Structured Logging

- JSON-formatted logs
- Consistent across all services
- Fields: timestamp, level, service, message, context
- Request correlation IDs
- Sensitive data automatically redacted

---

### 2. Security Enhancements

#### Startup Secret Validation

- Mandatory validation in production mode
- Checks for:
  - `JWT_SECRET` (min 32 chars)
  - `ENCRYPTION_KEY` (min 24 chars)
  - `KEY_VAULT_MASTER_KEY` (min 32 chars)
- Rejects placeholder values
- Exits with code 1 if validation fails
- Development mode: warnings only

#### Task Safety Policy

Prevents execution of dangerous commands with configurable policy:

**Denylist Mode (Default):**
- Blocks 29 dangerous command patterns
- Allows everything else
- Patterns include:
  - Filesystem destruction (`rm -rf /`, `mkfs`, `dd`)
  - System control (`shutdown`, `reboot`)
  - Permission manipulation (`chmod 777`, `usermod`)
  - Package removal (`apt-get remove`)
  - Kernel/boot (`grub-*`, `modprobe`)
  - Network disruption (`ifconfig down`)
  - Fork bombs

**Allowlist Mode:**
- Only permits explicitly configured commands
- High-security environments
- Customizable via `TASK_ALLOW_PATTERNS`

**Configuration:**
```bash
TASK_POLICY_MODE=denylist  # or 'allowlist'
TASK_DENY_PATTERNS=custom1,custom2  # Custom patterns
TASK_ALLOW_PATTERNS=^ls\b,^cat\b    # Allowlist patterns
```

#### Audit Log Management

**Retention & Cleanup:**
- Auto-cleanup of old audit logs
- Configurable retention period (default: 90 days)
- Runs on startup + periodic intervals
- Configurable via:
  - `AUDIT_RETENTION_DAYS=90`
  - `AUDIT_CLEANUP_ENABLED=true`
  - `AUDIT_CLEANUP_INTERVAL_HOURS=24`

**Export Endpoints (Admin-only):**
- **`GET /api/export/audit/csv`** - Export as CSV
- **`GET /api/export/audit/json`** - Export as JSON
- Supports filtering:
  - `from`, `to` (date range)
  - `user_id`, `action`, `target_type`
  - `limit` (max records)
- CSV injection prevention
- Sensitive data sanitization
- Audit log created for exports

---

### 3. System Reliability

#### Graceful Shutdown

All services handle `SIGTERM`/`SIGINT` gracefully:

**Central API:**
- Stops audit cleanup scheduler
- Marks running tasks as interrupted
- Marks active terminal sessions as interrupted
- Closes SSH connections
- Shuts down HTTP server

**Terminal Server:**
- Closes all SSH sessions
- Updates session status
- Closes WebSocket server

**WebSocket Server:**
- Closes all WebSocket connections
- Closes SSH connections
- Flushes logs

**Benefits:**
- No orphaned processes
- Clean database state
- Safe service restarts
- No data loss

#### Task Recovery on Startup

Automatically recovers from crashes/restarts:

- Detects stale tasks (status='running', >60 min old)
- Marks as 'interrupted'
- Recovers terminal sessions
- Creates audit log entries
- Logs recovery statistics

**Configuration:**
```bash
TASK_STALE_THRESHOLD_MINUTES=60  # Stale detection threshold
```

**Startup Output:**
```
🔄 Recovered 3 interrupted tasks/sessions
```

---

## 🔧 Configuration Changes

### New Environment Variables

```bash
# Audit log retention
AUDIT_RETENTION_DAYS=90
AUDIT_CLEANUP_ENABLED=true
AUDIT_CLEANUP_INTERVAL_HOURS=24

# Task safety policy
TASK_POLICY_MODE=denylist
TASK_DENY_PATTERNS=pattern1,pattern2
TASK_ALLOW_PATTERNS=^ls\b,^cat\b

# Task recovery
TASK_STALE_THRESHOLD_MINUTES=60

# Production validation (existing but now enforced)
ENVIRONMENT=production  # Enables secret validation
```

---

## 📊 API Changes

### New Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/health` | GET | Public | Liveness check |
| `/api/ready` | GET | Public | Readiness check |
| `/api/metrics` | GET | Admin/Localhost | Prometheus/JSON metrics |
| `/api/export/audit/csv` | GET | Admin | Export audit logs as CSV |
| `/api/export/audit/json` | GET | Admin | Export audit logs as JSON |

### Enhanced Endpoints

- All endpoints now return `X-Request-Id` header
- Structured logging for all requests
- Improved error responses

---

## 🧪 Testing

### New Test Suite

- `tests/test_observability.py` - Comprehensive observability tests
  - Health/ready endpoint tests
  - Metrics format validation
  - Request-ID propagation tests
  - Task policy validation tests
  - Audit export tests

### Smoke Tests

Updated `scripts/smoke.sh` with:
- Health endpoint checks
- Readiness validation
- Metrics endpoint tests
- Enhanced error reporting

---

## 📚 Documentation Updates

### Updated Documentation

- **SECURITY.md** - Phase 6 security features
  - Startup validation
  - Task safety policy
  - Audit retention
  - System reliability

- **ARCHITECTURE.md** - Observability flows (see separate update)

- **POST-PRODUCTION.md** - Monitoring guide (see separate update)

- **README.md** - Operational monitoring (see separate update)

- **.env.example** - New environment variables

---

## 🔄 Migration Guide

### Upgrading from v2.1.x

**No breaking changes!** However, consider these enhancements:

#### 1. Environment Variables (Optional but Recommended)

```bash
# Add to your .env file
AUDIT_RETENTION_DAYS=90
AUDIT_CLEANUP_ENABLED=true
TASK_POLICY_MODE=denylist
ENVIRONMENT=production  # For secret validation
```

#### 2. Production Secret Validation

If running in production, ensure secrets are properly configured:

```bash
# Generate secure secrets (if not already set)
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")
KEY_VAULT_MASTER_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
```

#### 3. Monitor New Endpoints

Update your monitoring to include:
- `/api/health` - Liveness
- `/api/ready` - Readiness
- `/api/metrics` - System metrics

#### 4. Test Graceful Shutdown

```bash
# Test that services shut down cleanly
sudo systemctl stop server-monitor-api
sudo systemctl stop server-monitor-terminal
sudo systemctl stop server-monitor-websocket

# Check logs for graceful shutdown messages
sudo journalctl -u server-monitor-api -n 50
```

#### 5. Verify Task Policy

Test that dangerous commands are blocked:

```bash
# This should be blocked:
# curl -X POST /api/tasks -d '{"command": "rm -rf /", ...}'
```

---

## 🐛 Bug Fixes

- Fixed: Tasks/sessions left in 'running' state after service restart
- Fixed: No graceful cleanup on SIGTERM
- Fixed: Audit logs growing indefinitely
- Fixed: Metrics not available for monitoring
- Fixed: No request tracing across services

---

## 📈 Performance

- Minimal overhead from observability features
- Structured logging optimized for production
- Audit cleanup runs asynchronously (no blocking)
- Request-ID generation uses UUID4 (fast)
- Metrics endpoint cached (configurable)

---

## 🔐 Security

- **CVE-None:** No known vulnerabilities
- Enhanced protection against dangerous command execution
- CSV injection prevention in exports
- Sensitive data sanitization in logs and exports
- Production secret validation

---

## ⚠️ Known Limitations

- Audit log exports limited to 50,000 records per request
- Metrics endpoint requires admin role or localhost access
- Task stale threshold is time-based only (no heartbeat yet)
- Cleanup scheduler is in-process (not systemd timer)

---

## 🎯 Future Enhancements (v2.3.0)

- Task heartbeat mechanism
- Distributed tracing with OpenTelemetry
- Advanced metrics dashboards
- Real-time alerting on metric thresholds
- Audit log archival to external storage

---

## 👥 Contributors

- @minhtuancn - Project lead and core development
- @copilot - AI pair programmer

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/minhtuancn/server-monitor/issues)
- **Documentation:** See `docs/` directory
- **Email:** vietkeynet@gmail.com

---

## 📄 License

MIT License - See LICENSE file for details

---

**Version:** 2.2.0  
**Release Date:** January 2026  
**Status:** ✅ Production Ready
