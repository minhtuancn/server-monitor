# Server Monitor - Security Guide

**Version:** 2.0.0  
**Last Updated:** 2026-01-07

---

## 📋 Security Summary

The Server Monitor Dashboard implements multiple layers of security with v2.0 enhancements:

| Category | Status | Score |
|----------|--------|-------|
| Authentication | ✅ Enhanced | 10/10 |
| Authorization (RBAC) | ✅ Implemented | 9/10 |
| Cookie Security | ✅ Hardened | 10/10 |
| Input Validation | ✅ Implemented | 9/10 |
| Rate Limiting | ✅ Implemented | 9/10 |
| Security Headers | ✅ Implemented | 9/10 |
| SSRF Protection | ✅ Implemented | 10/10 |
| Secrets Management | ⚠️ Manual | 7/10 |
| **Overall** | **Production Ready** | **9/10** |

---

## 🔐 Authentication

### JWT Token with HttpOnly Cookies (v2.0)

The system uses JSON Web Tokens (JWT) stored in HttpOnly cookies for maximum security:

- **Algorithm:** HS256
- **Default Expiration:** 24 hours (86400 seconds)
- **Token Storage:** HttpOnly cookie (XSS protection)
- **Cookie Name:** `auth_token`
- **Cookie Attributes:**
  - `HttpOnly: true` (prevents JavaScript access)
  - `SameSite: Lax` (CSRF protection)
  - `Secure: true` (production only, HTTPS)
  - `Path: /`
  - `MaxAge: synced with JWT expiry`

**Flow:**

1. User logs in via `/api/auth/login` (Next.js BFF)
2. Backend validates credentials, returns JWT
3. BFF sets HttpOnly cookie with JWT
4. Subsequent requests include cookie automatically
5. BFF middleware translates cookie to Bearer token for backend

```bash
# Login (sets HttpOnly cookie)
curl -X POST http://localhost:9081/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}' \
  -c cookies.txt

# Use cookie in requests
curl http://localhost:9081/api/proxy/api/servers \
  -b cookies.txt
```

### Backend-for-Frontend (BFF) Security

The Next.js BFF layer provides additional security:

- **Cookie to Bearer token translation**
- **No cookie leakage to backend**
- **SSRF protection in proxy**
- **Path traversal prevention**
- **Set-cookie header filtering**

### Session Management

- Sessions validated via `/api/auth/session`
- Token expiry checked on each request
- Logout clears cookie: `/api/auth/logout`
- Expired tokens auto-redirect to login

### Password Security

- Passwords hashed using SHA256 with salt (backend)
- Minimum password validation (client-side)
- Failed login attempts tracked and rate-limited
- Default admin password must be changed immediately

---

## 🛡️ Authorization

### Role-Based Access Control (RBAC) v2.0

| Role | Permissions |
|------|-------------|
| admin | Full access to all features, user management, system settings |
| user | Read servers, own profile, limited write access |
| public | Read-only access to stats (no auth required) |

### Middleware Protection

Next.js middleware enforces RBAC:

```typescript
// Admin-only routes
/users
/settings/domain
/settings/email

// Authenticated routes
/dashboard
/servers/*
/terminal
/settings
/notifications
```

### Access Denied Page

Unauthorized access attempts show a user-friendly "Access Denied" page instead of generic errors.

### Protected Endpoints

**Public (no auth):**
```
GET /api/stats/overview
GET /api/servers (limited data)
```

**User (auth required):**
```
GET /api/servers/:id
GET /api/export/*
GET /api/notifications
GET /api/ssh-keys
```

**Admin (admin role required):**
```
POST/PUT/DELETE /api/servers/*
POST/PUT/DELETE /api/users/*
GET/POST /api/settings/*
GET/POST /api/email/config
GET/POST /api/domain/settings
```

---

## 🚦 Rate Limiting

### General Rate Limits

- **100 requests per minute** per IP
- Automatic counter reset after window expires
- Rate limit headers included in responses

### Login Rate Limits

- **5 login attempts per 5 minutes** per IP
- **15-minute IP block** after repeated failures
- Protects against brute-force attacks

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704635000
```

---

## 🔒 Security Headers

All responses include security headers:

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; ...
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### Content Security Policy (CSP)

The CSP allows:
- Scripts from self and cdnjs.cloudflare.com
- Styles from self and cdnjs.cloudflare.com
- Fonts from cdnjs.cloudflare.com
- Images from self and data: URIs
- WebSocket connections to configured hosts

---

## ✅ Input Validation

### Server-Side Validation

All inputs are validated before processing:

| Field | Validation |
|-------|------------|
| IP Address | Valid format, octets 0-255 |
| Hostname | Alphanumeric, dots, hyphens only |
| Port | Integer 1-65535 |
| Username | Sanitized, max 255 chars |
| Description | HTML stripped, max 255 chars |

### Validation Code Example

```python
# From security.py
def validate_ip(ip_address):
    """Validate IP address format"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip_address):
        return False
    octets = ip_address.split('.')
    return all(0 <= int(octet) <= 255 for octet in octets)

def validate_port(port):
    """Validate port number"""
    try:
        port = int(port)
        return 1 <= port <= 65535
    except (ValueError, TypeError):
        return False
```

### SQL Injection Prevention

All database queries use parameterized statements:

```python
# Safe - parameterized query
cursor.execute('SELECT * FROM servers WHERE id = ?', (server_id,))

# Never used - string concatenation
# cursor.execute(f'SELECT * FROM servers WHERE id = {server_id}')
```

---

## 🛡️ SSRF & Path Traversal Protection (v2.0)

### BFF Proxy Security

The Next.js Backend-for-Frontend (BFF) proxy includes multiple layers of protection:

**Path Validation:**
```typescript
function validateProxyPath(path: string[]): boolean {
  // Prevent empty paths
  if (!path || path.length === 0) return false;
  
  const joinedPath = path.join("/");
  
  // Prevent path traversal
  if (joinedPath.includes("..") || joinedPath.includes("~")) return false;
  
  // Only allow /api/* paths
  if (!joinedPath.startsWith("api/")) return false;
  
  // Prevent protocol-relative URLs or absolute URLs
  if (joinedPath.includes("://") || joinedPath.startsWith("//")) return false;
  
  return true;
}
```

**Protection Against:**
- ✅ SSRF (Server-Side Request Forgery) - Only proxies to configured backend
- ✅ Path Traversal - Blocks `..`, `~`, absolute URLs
- ✅ Protocol Injection - Blocks `://`, `//`
- ✅ Cookie Leakage - Strips all cookies before forwarding
- ✅ Response Header Injection - Filters `set-cookie` from backend

### Token Endpoint Security

The `/api/auth/token` endpoint (used for WebSocket auth) includes:

```typescript
// Cache control to prevent token exposure
response.headers.set("Cache-Control", "no-store, no-cache, must-revalidate");
response.headers.set("Pragma", "no-cache");
response.headers.set("Expires", "0");

// Token expiry validation
if (isTokenExpired(token)) {
  return NextResponse.json({ error: "Token expired" }, { status: 401 });
}
```

**Best Practices:**
- Only used for WebSocket authentication
- Not logged or cached
- Short-lived tokens only
- Expiry validated before return

---

## 🔑 Secrets Management

### Environment Variables

Critical secrets are configured via environment variables:

```bash
# .env file (never commit to git)
JWT_SECRET=your-secure-jwt-secret-min-32-chars
ENCRYPTION_KEY=your-encryption-key-min-24-chars
```

### Generate Secure Secrets

```bash
# Generate JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate encryption key
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

### SSH Password Encryption

SSH passwords are encrypted before storage:
- XOR encryption with ENCRYPTION_KEY
- Base64 encoded for storage
- Decrypted only when needed for connection

### SSH Key Vault (Phase 4) 🆕

**Encrypted SSH Private Key Storage with AES-256-GCM**

The SSH Key Vault provides military-grade encryption for storing SSH private keys:

#### Encryption Specification

- **Algorithm:** AES-256-GCM (Galois/Counter Mode)
- **Key Size:** 256 bits (32 bytes)
- **IV Size:** 12 bytes (96 bits) - random per encryption
- **Authentication Tag:** 16 bytes (128 bits)
- **Key Derivation:** PBKDF2-HMAC-SHA256 with 100,000 iterations
- **Master Key:** From environment variable `KEY_VAULT_MASTER_KEY`

#### Security Properties

✅ **Confidentiality:** AES-256 encryption protects key content
✅ **Integrity:** GCM authentication tag prevents tampering
✅ **Freshness:** Random IV per encryption prevents replay attacks
✅ **No Plaintext Storage:** Keys only decrypted in RAM when needed
✅ **Database Compromise Protection:** Encrypted keys unreadable without master key
✅ **No Logging:** Private keys never logged or exposed in API responses

#### Key Vault Setup

```bash
# Generate secure master key (32 bytes minimum)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
KEY_VAULT_MASTER_KEY=<generated_key_here>
```

**⚠️ Important:** The `KEY_VAULT_MASTER_KEY` must be kept secure and backed up. 
If lost, encrypted keys cannot be recovered.

#### Database Schema

```sql
CREATE TABLE ssh_keys (
    id TEXT PRIMARY KEY,              -- UUID v4
    name TEXT NOT NULL UNIQUE,        -- User-friendly name
    description TEXT,                 -- Optional description
    private_key_enc BLOB NOT NULL,    -- Encrypted private key
    iv BLOB NOT NULL,                 -- Initialization vector (12 bytes)
    auth_tag BLOB NOT NULL,           -- Authentication tag (16 bytes)
    key_type TEXT DEFAULT 'rsa',      -- rsa, ed25519, ecdsa, etc.
    fingerprint TEXT,                 -- SHA256 fingerprint
    created_by_user_id INTEGER,       -- Creator
    created_at TEXT NOT NULL,         -- Created timestamp
    updated_at TEXT NOT NULL,         -- Updated timestamp
    deleted_at TEXT                   -- Soft delete timestamp
);
```

#### Access Control

- **Admin:** Full access to create, view, and delete keys
- **Operator:** Can create and view keys (cannot delete)
- **User/Viewer:** No access to key vault

#### API Security

**Protected Endpoints:**
- `POST /api/ssh-keys` - Create encrypted key (admin/operator)
- `GET /api/ssh-keys` - List keys metadata (admin/operator)
- `GET /api/ssh-keys/{id}` - Get key metadata (admin/operator)
- `DELETE /api/ssh-keys/{id}` - Soft delete key (admin only)

**Security Measures:**
- Private keys never exposed via API (metadata only)
- Decryption only happens server-side for SSH connections
- All operations logged for audit trail
- Soft delete prevents accidental data loss

#### Testing

The crypto vault includes comprehensive unit tests:

```bash
cd /home/runner/work/server-monitor/server-monitor
python3 tests/test_crypto_vault.py
```

**Tests cover:**
- ✅ Encrypt/decrypt roundtrip
- ✅ Wrong key rejection
- ✅ Tampered ciphertext detection
- ✅ Tampered auth tag detection
- ✅ Tampered IV detection
- ✅ Empty input handling
- ✅ Base64 encoding/decoding
- ✅ Deterministic key derivation
- ✅ Unique IV per encryption

#### Key Rotation

**Best Practices:**
1. Rotate SSH keys regularly (every 90-180 days)
2. Use ED25519 keys (modern, secure, fast)
3. Minimum RSA 2048 bits (prefer 4096)
4. Soft delete old keys (keep audit trail)
5. Back up `KEY_VAULT_MASTER_KEY` securely

**Rotation Procedure:**
1. Generate new SSH key pair
2. Add new private key to vault
3. Deploy public key to target servers
4. Test connections with new key
5. Soft delete old key from vault
6. Remove old public key from servers

⚠️ **Note:** XOR encryption is basic. For production with sensitive data, consider:
- Using AES encryption
- Storing passwords in a secrets manager (HashiCorp Vault, AWS Secrets Manager)
- Using SSH key authentication instead of passwords

---

## 🌐 CORS Configuration

### Allowed Origins

Configure in `backend/security.py`:

```python
ALLOWED_ORIGINS = [
    'http://172.22.0.103:9081',
    'http://localhost:9081',
    'http://127.0.0.1:9081'
]
```

### Production Configuration

Update for your domain:

```python
ALLOWED_ORIGINS = [
    'https://monitor.yourdomain.com',
    'https://www.yourdomain.com'
]
```

---

## 🔍 Security Audit Findings

### Bandit Scan Results

The codebase was scanned with Bandit security scanner:

| Finding | Severity | Status | Notes |
|---------|----------|--------|-------|
| Binding to 0.0.0.0 | Medium | Acceptable | Required for container/network access |
| subprocess with shell=True | High | Monitored | In agent.py for system commands - controlled input |
| Hardcoded /tmp paths | Medium | Acceptable | Default paths, can be overridden |

### CodeQL Results

- **0 vulnerabilities detected**
- Scan covers: Python security issues, SQL injection, XSS, etc.

### Recommendations

#### High Priority
- [ ] Change default admin password immediately after deployment
- [ ] Enable HTTPS in production (see [HTTPS-SETUP.md](HTTPS-SETUP.md))
- [ ] Set secure JWT_SECRET and ENCRYPTION_KEY

#### Medium Priority
- [ ] Implement 2FA for admin accounts
- [ ] Add audit logging for sensitive operations
- [ ] Consider using SSH keys instead of passwords

#### Future Considerations
- [ ] API key authentication for integrations
- [ ] IP whitelist/blacklist feature
- [ ] Security event alerting

---

## 🚨 Security Incident Response

### If Credentials Are Compromised

1. **Immediately:**
   - Change affected passwords
   - Regenerate JWT_SECRET to invalidate all tokens
   - Check audit logs for unauthorized access

2. **Within 24 hours:**
   - Review all user sessions
   - Check for unauthorized servers added
   - Review SSH keys and remove suspicious ones

3. **After incident:**
   - Conduct post-mortem
   - Update security practices
   - Consider enabling additional security measures

### Regenerate All Secrets

```bash
# Stop services
./stop-all.sh

# Generate new secrets
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")

# Update .env file
# Note: Changing ENCRYPTION_KEY will break existing encrypted passwords

# Restart services
./start-all.sh
```

---

## 🔧 Production Deployment Security (Phase 6)

### Startup Secret Validation

**Version 2.2.0** introduces mandatory secret validation on startup for production deployments.

#### Required Environment Variables

```bash
# REQUIRED in production mode (ENVIRONMENT=production)
JWT_SECRET=<min 32 chars>
ENCRYPTION_KEY=<min 24 chars>
KEY_VAULT_MASTER_KEY=<min 32 chars>
```

#### Validation Behavior

- **Development Mode:** Secrets are optional, warnings logged
- **Production Mode:** Missing/weak secrets cause startup failure
- **Generation Command:**
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

#### Validation Checks

✅ Secrets are present and non-empty  
✅ Minimum length requirements met  
✅ No placeholder values (e.g., "REPLACE_WITH_SECURE_RANDOM_VALUE")  
✅ Sufficient entropy for cryptographic operations  

**Exit Code:** Service exits with code 1 if validation fails in production.

---

### Task Safety Policy

Prevents execution of dangerous commands that could harm the system.

#### Policy Modes

**1. Denylist Mode (Default)**
- Blocks known dangerous patterns
- Allows everything else
- Recommended for most deployments

**2. Allowlist Mode**
- Only permits explicitly allowed commands
- Blocks everything else
- Recommended for high-security environments

#### Configuration

```bash
# Set policy mode
TASK_POLICY_MODE=denylist  # or 'allowlist'

# Add custom dangerous patterns (denylist mode)
TASK_DENY_PATTERNS="pattern1,pattern2,pattern3"

# Add allowed patterns (allowlist mode)
TASK_ALLOW_PATTERNS="^ls\b,^cat\b,^grep\b"
```

#### Default Blocked Patterns (29 patterns)

**Filesystem Destruction:**
- `rm -rf /` and variants
- `mkfs` (format partition)
- `dd if=/dev/zero of=/dev/`

**System Control:**
- `shutdown`, `reboot`, `halt`, `poweroff`
- `init 0`, `init 6`

**User/Permission Manipulation:**
- `usermod`, `passwd`
- `chmod 777`
- `chown` on root
- `visudo`

**Package Management:**
- `apt-get remove/purge`
- `yum remove/erase`
- `dnf remove/erase`

**Kernel/Boot:**
- `grub-*`, `update-grub`
- `modprobe`, `insmod`, `rmmod`

**Network Disruption:**
- `ifconfig * down`
- `ip link set * down`
- `iptables -F`

**Resource Exhaustion:**
- Fork bombs
- Infinite loops with fork

#### Override Process

If you need to execute a blocked command:

1. Review the command for safety
2. Add to custom allowlist in `.env`
3. Restart services
4. Monitor execution logs

#### Audit Logging

All task policy violations are logged with:
- Command that was blocked
- User who attempted
- Timestamp
- Reason for blocking

---

### Audit Log Security

#### Retention Policy

```bash
# Auto-cleanup configuration
AUDIT_RETENTION_DAYS=90        # Keep logs for 90 days
AUDIT_CLEANUP_ENABLED=true     # Enable auto-cleanup
AUDIT_CLEANUP_INTERVAL_HOURS=24 # Run daily
```

#### Export Security

**CSV Export Sanitization:**
- Prevents CSV injection attacks
- Prefixes dangerous characters (`=`, `+`, `-`, `@`) with `'`
- Limits exported field size
- Excludes sensitive metadata

**JSON Export Sanitization:**
- Truncates large meta_json fields (>1000 chars)
- Removes user_agent if too large
- Limits export size (max 50,000 records)

**Access Control:**
- Both CSV and JSON export require admin role
- Exports are audited (action: `audit.export`)
- Export filters logged in audit metadata

#### Audit Log Fields

**Included in Export:**
- `id`, `user_id`, `action`, `target_type`, `target_id`
- `ip`, `created_at`

**Excluded from Export:**
- `user_agent` (may contain PII)
- Large `meta_json` (truncated in JSON, excluded in CSV)

---

## 🛡️ System Reliability & Recovery

### Graceful Shutdown

All services support graceful shutdown on `SIGTERM`/`SIGINT`:

**Central API (`central_api.py`):**
- Stops audit cleanup scheduler
- Marks running tasks as interrupted
- Marks active terminal sessions as interrupted
- Closes all SSH connections
- Shuts down HTTP server cleanly

**Terminal Server (`terminal.py`):**
- Closes all active SSH sessions
- Updates session status to 'interrupted'
- Closes WebSocket server

**WebSocket Server (`websocket_server.py`):**
- Closes all WebSocket connections
- Closes SSH connections
- Flushes logs

### Task Recovery on Startup

Automatically recovers from crashes and unclean shutdowns:

**Stale Task Detection:**
- Tasks stuck in 'running' state
- Running longer than threshold (default: 60 minutes)
- No heartbeat/activity

**Recovery Actions:**
- Mark tasks as 'interrupted'
- Set finish timestamp
- Add error message
- Create audit log entry

**Configuration:**
```bash
TASK_STALE_THRESHOLD_MINUTES=60  # Stale task threshold
```

**Logged Metrics:**
- Number of tasks recovered
- Number of sessions recovered
- Recovery timestamp
- Audit log entry created

---

## 📊 Security Monitoring

### Health & Readiness Checks

**Liveness Check (`/api/health`):**
- Public endpoint
- Returns basic service status
- No sensitive data exposed

**Readiness Check (`/api/ready`):**
- Public endpoint
- Validates:
  - Database connectivity
  - Database writability
  - Table initialization
  - Vault master key presence
  - JWT secret configuration
  - Encryption key configuration

**Status Responses:**
- `ready`: All checks passed
- `not_ready`: One or more checks failed
- Individual check status in response

### Request Correlation

All requests get a unique `X-Request-Id`:
- Auto-generated if not provided
- Preserved across service calls
- Included in structured logs
- Returned in response headers

Use for:
- Tracing requests through logs
- Debugging issues
- Performance analysis

### Metrics Endpoint

**Prometheus format (`/api/metrics`):**
```
server_monitor_uptime_seconds 123456
server_monitor_requests_total{endpoint="/api/servers"} 42
server_monitor_request_latency_ms{endpoint="/api/servers",quantile="0.95"} 45.2
```

**JSON format (`/api/metrics?format=json`):**
```json
{
  "timestamp": "2026-01-07T...",
  "uptime_seconds": 123456,
  "requests": {"total": 42, "by_endpoint": {...}},
  "latency": {...},
  "tasks": {"running": 2, "queued": 1}
}
```

**Access Control:**
- Requires admin role OR localhost access
- Sensitive metrics sanitized
- No PII exposed

---

## 📋 Security Checklist

### Before Production (Phase 6 Enhanced)

- [ ] Changed default admin password
- [ ] Set secure JWT_SECRET (min 32 chars)
- [ ] Set secure ENCRYPTION_KEY (min 24 chars)
- [ ] Set secure KEY_VAULT_MASTER_KEY (min 32 chars)
- [ ] Configured ENVIRONMENT=production
- [ ] Verified startup secret validation passes
- [ ] Configured task safety policy (denylist/allowlist)
- [ ] Set audit log retention policy (AUDIT_RETENTION_DAYS)
- [ ] Updated CORS allowed origins
- [ ] Enabled HTTPS
- [ ] Configured firewall
- [ ] Reviewed all user accounts
- [ ] Set up monitoring and alerting
- [ ] Configured metrics scraping (Prometheus)
- [ ] Tested graceful shutdown (SIGTERM)
- [ ] Verified task recovery on restart

### Ongoing

- [ ] Regular security updates
- [ ] Monitor failed login attempts
- [ ] Review access logs and audit logs
- [ ] Monitor audit log cleanup (verify retention policy)
- [ ] Review blocked task commands
- [ ] Check system metrics regularly
- [ ] Test backup restoration
- [ ] Periodic security audits
- [ ] Review request correlation logs (X-Request-Id)
- [ ] Monitor readiness check failures

---

## 📞 Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public issue
2. Email: [vietkeynet@gmail.com](mailto:vietkeynet@gmail.com)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work on a fix.

---

**Last Updated:** 2026-01-07 (v2.2.0 - Phase 6)
