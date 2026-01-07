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

## 📋 Security Checklist

### Before Production

- [ ] Changed default admin password
- [ ] Set secure JWT_SECRET (min 32 chars)
- [ ] Set secure ENCRYPTION_KEY (min 24 chars)
- [ ] Updated CORS allowed origins
- [ ] Enabled HTTPS
- [ ] Configured firewall
- [ ] Reviewed all user accounts
- [ ] Set up monitoring and alerting

### Ongoing

- [ ] Regular security updates
- [ ] Monitor failed login attempts
- [ ] Review access logs
- [ ] Test backup restoration
- [ ] Periodic security audits

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

**Last Updated:** 2026-01-07
