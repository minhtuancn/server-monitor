# Server Monitor - Security Guide

**Version:** 1.0.0  
**Last Updated:** 2026-01-07

---

## 📋 Security Summary

The Server Monitor Dashboard implements multiple layers of security:

| Category | Status | Score |
|----------|--------|-------|
| Authentication | ✅ Implemented | 9/10 |
| Authorization | ✅ Implemented | 8/10 |
| Input Validation | ✅ Implemented | 9/10 |
| Rate Limiting | ✅ Implemented | 9/10 |
| Security Headers | ✅ Implemented | 9/10 |
| Secrets Management | ⚠️ Manual | 7/10 |
| **Overall** | **Production Ready** | **8.5/10** |

---

## 🔐 Authentication

### JWT Token Authentication

The system uses JSON Web Tokens (JWT) for authentication:

- **Algorithm:** HS256
- **Default Expiration:** 24 hours (86400 seconds)
- **Token Location:** Authorization header (Bearer token)

```bash
# Login to get token
curl -X POST http://localhost:9083/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'

# Use token in requests
curl http://localhost:9083/api/servers \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Session Management

- Sessions stored in SQLite database
- Auto-cleanup of expired sessions on server start
- Logout invalidates session token

### Password Security

- Passwords hashed using SHA256 with salt
- Minimum password validation (client-side)
- Failed login attempts tracked

---

## 🛡️ Authorization

### Role-Based Access Control (RBAC)

| Role | Permissions |
|------|-------------|
| admin | Full access to all features |
| user | Read servers, limited write access |
| public | Read-only access to stats (no auth required) |

### Protected Endpoints

Most endpoints require authentication:

```
Public (no auth):
  GET /api/stats/overview
  GET /api/servers (limited data)

User (auth required):
  GET /api/servers/:id
  GET /api/export/*

Admin (admin role required):
  POST/PUT/DELETE /api/servers/*
  POST/PUT/DELETE /api/users/*
  GET/POST /api/settings/*
  GET/POST /api/email/config
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
