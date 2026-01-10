# Production Security Checklist

Security hardening checklist for production deployments.

**Last Updated**: 2026-01-09  
**Minimum Security Level**: Level 2 (HTTPS + Auth)  
**Recommended**: Level 3 (Full Hardening)

---

## Pre-Deployment Checklist

### ✅ Level 1: Basic Security (Minimum)

- [ ] **Change default admin password (first login)**

  ```bash
  # Login → Settings → Profile → Change Password
  # Use strong password (16+ chars, uppercase, lowercase, digits, symbols)
  ```

- [ ] **Force first-login password change (ops control)**

  - Create a one-time admin and rotate credentials immediately after first login
  - Document and enforce via runbook until app-level policy is added

- [ ] **Generate unique JWT secret**

  ```bash
  python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))" >> backend/.env
  # Should be 32+ characters, truly random
  ```

- [ ] **Set ENCRYPTION_KEY (min 24 chars, 32+ recommended)**

  ```bash
  python3 -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(32))" >> backend/.env
  ```

- [ ] **Disable debug mode**

  ```bash
  # backend/.env
  DEBUG=false
  ENVIRONMENT=production
  ```

- [ ] **Update CORS allowed domains**
  ```bash
  # backend/.env
  ALLOWED_FRONTEND_DOMAINS=mon.yourdomain.com
  # DO NOT use * in production
  ```

---

### ✅ Level 2: HTTPS + Auth (Recommended Minimum)

- [ ] **Enable HTTPS**

  - Use Let's Encrypt certificate (see [HTTPS-SETUP.md](../../HTTPS-SETUP.md))
  - Or use reverse proxy (Nginx/Caddy) with SSL
  - No mixed content (all resources over HTTPS)

- [ ] **Enforce strong passwords**

  ```bash
  # backend/security.py (already default)
  MIN_PASSWORD_LENGTH = 8
  REQUIRE_UPPERCASE = True
  REQUIRE_LOWERCASE = True
  REQUIRE_DIGIT = True
  ```

- [ ] **Enable rate limiting**

  ```bash
  # backend/rate_limiter.py
  RATE_LIMIT_ENABLED = True
  LOGIN_RATE_LIMIT = 5  # 5 attempts per minute per IP
  API_RATE_LIMIT = 100  # 100 requests per minute per user
  ```

- [ ] **Secure cookie settings**

  ```bash
  # backend/security.py (already default)
  COOKIE_SECURE = True  # HTTPS only
  COOKIE_HTTPONLY = True  # No JavaScript access
  COOKIE_SAMESITE = "Lax"  # CSRF protection
  ```

- [ ] **Set JWT expiration**
  ```bash
  # backend/.env
  JWT_EXPIRATION_HOURS=24  # Tokens expire in 24h
  ```

---

### ✅ Level 3: Full Hardening (Production Best Practice)

- [ ] **Firewall configuration**

  ```bash
  # Ubuntu/Debian
  sudo ufw default deny incoming
  sudo ufw default allow outgoing
  sudo ufw allow 22/tcp    # SSH (limit: ufw limit 22/tcp)
  sudo ufw allow 80/tcp    # HTTP (redirect to HTTPS)
  sudo ufw allow 443/tcp   # HTTPS
  sudo ufw enable

  # Block direct access to backend ports
  # Use reverse proxy instead
  ```

- [ ] **SSH key authentication only**

  ```bash
  # /etc/ssh/sshd_config
  PasswordAuthentication no
  PubkeyAuthentication yes
  PermitRootLogin no

  sudo systemctl restart sshd
  ```

- [ ] **Database encryption at rest**

  ```bash
  # Use LUKS encrypted partition for data/ folder
  # Or use encrypted filesystem (eCryptfs)
  sudo cryptsetup luksFormat /dev/sdX
  sudo cryptsetup open /dev/sdX server_data
  sudo mkfs.ext4 /dev/mapper/server_data
  sudo mount /dev/mapper/server_data /opt/server-monitor/data
  ```

- [ ] **Secure SSH private keys**

  ```bash
  # Encrypt SSH keys with passphrase
  ssh-keygen -p -f data/ssh/id_rsa

  # Restrict permissions
  chmod 600 data/ssh/id_rsa
  chmod 644 data/ssh/id_rsa.pub
  chown server-monitor:server-monitor data/ssh/*
  ```

- [ ] **Enable audit logging**

  ```bash
  # backend/.env
  AUDIT_LOG_ENABLED=true
  AUDIT_LOG_RETENTION_DAYS=90

  # Review audit logs regularly
  sqlite3 data/servers.db "SELECT * FROM audit_logs WHERE created_at > date('now', '-7 days');"
  ```

- [ ] **Limit user permissions**

  ```bash
  # Use principle of least privilege
  # Users table: role column (admin, user, viewer)
  # Viewer: Read-only access
  # User: Can manage servers they own
  # Admin: Full access
  ```

- [ ] **Network segmentation**

  ```bash
  # Run backend on internal network
  # Only expose reverse proxy to internet

  # backend/central_api.py
  app.run(host="127.0.0.1", port=9083)  # Localhost only
  ```

- [ ] **Fail2ban for brute force protection**

  ```bash
  sudo apt install fail2ban

  # /etc/fail2ban/jail.local
  [server-monitor]
  enabled = true
  port = 443
  filter = server-monitor
  logpath = /opt/server-monitor/logs/api.log
  maxretry = 5
  bantime = 3600

  sudo systemctl restart fail2ban
  ```

- [ ] **Security headers**
  ```bash
  # Reverse proxy (Nginx)
  add_header X-Frame-Options "DENY";
  add_header X-Content-Type-Options "nosniff";
  add_header X-XSS-Protection "1; mode=block";
  add_header Referrer-Policy "strict-origin-when-cross-origin";
  add_header Content-Security-Policy "default-src 'self'; ...";
  ```

---

## Secret Management

### Environment Variables (.env)

**Never commit to Git**:

```bash
# .gitignore (should already exist)
backend/.env
frontend-next/.env.local
data/
*.key
*.pem
```

**Secure storage**:

```bash
# Restrict .env permissions
chmod 600 backend/.env
chown server-monitor:server-monitor backend/.env

# Or use secrets manager (advanced)
# - HashiCorp Vault
# - AWS Secrets Manager
# - Azure Key Vault
```

**Required secrets**:

```bash
# Copy backend/.env.example to backend/.env and update values
cp backend/.env.example backend/.env

# Edit backend/.env with your production values
# See backend/.env.example for all available options

# CRITICAL: Generate strong secrets
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('KEY_VAULT_MASTER_KEY=' + secrets.token_urlsafe(32))"
```

---

## Database Security

### Encryption

```bash
# Option 1: SQLCipher (encrypted SQLite)
pip install pysqlcipher3

# backend/database.py
from pysqlcipher3 import dbapi2 as sqlite3
conn = sqlite3.connect('data/servers.db')
conn.execute(f"PRAGMA key = '{DB_ENCRYPTION_KEY}'")
```

### Backups

```bash
# Encrypt backups
gpg --symmetric --cipher-algo AES256 backups/servers.db

# Store offsite (encrypted)
rsync -avz backups/*.gpg user@backup-server:/backups/
```

### Access Control

```bash
# Restrict database file permissions
chmod 600 data/servers.db
chown server-monitor:server-monitor data/servers.db

# No world-readable permissions
ls -la data/servers.db
# Should show: -rw------- 1 server-monitor server-monitor
```

---

## Network Security

### Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/server-monitor
server {
    listen 80;
    server_name mon.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mon.yourdomain.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/mon.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mon.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;

    location /api/auth/login {
        limit_req zone=login_limit burst=3 nodelay;
        proxy_pass http://127.0.0.1:9083;
    }

    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://127.0.0.1:9083;
    }

    location / {
        proxy_pass http://127.0.0.1:9081;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:9085;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Monitoring & Alerts

### Failed Login Attempts

```bash
# Monitor auth logs
tail -f logs/api.log | grep "Failed login"

# Alert on brute force (>10 attempts in 1 min)
# Use alert_manager.py with custom rule
```

### Suspicious Activity

```bash
# Monitor audit logs
sqlite3 data/servers.db "
SELECT * FROM audit_logs
WHERE action IN ('delete_server', 'delete_user', 'change_role')
AND created_at > date('now', '-1 day');
"

# Alert on critical actions (email/Telegram)
```

### System Intrusion Detection

```bash
# Install AIDE (Advanced Intrusion Detection Environment)
sudo apt install aide
sudo aideinit

# Check for file changes daily
sudo aide --check | mail -s "AIDE Report" admin@example.com
```

---

## Incident Response

### Suspected Breach

1. **Isolate system**

   ```bash
   # Block all incoming traffic
   sudo ufw default deny incoming
   ```

2. **Preserve evidence**

   ```bash
   # Copy logs
   cp -r logs/ /evidence/logs-$(date +%Y%m%d-%H%M%S)

   # Dump database
   sqlite3 data/servers.db ".dump" > /evidence/db-dump.sql
   ```

3. **Revoke access**

   ```bash
   # Invalidate all JWT tokens (change secret)
   python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))" > backend/.env

   # Force all users to re-login
   ```

4. **Audit damage**

   ```bash
   # Check audit logs for unauthorized actions
   sqlite3 data/servers.db "SELECT * FROM audit_logs WHERE user_id=<suspect_id>;"

   # Check SSH connections
   grep "SSH connection" logs/terminal.log
   ```

5. **Patch and restore**

   ```bash
   # Update all packages
   sudo apt update && sudo apt upgrade

   # Restore from clean backup
   ./scripts/restore.sh /path/to/clean-backup.tar.gz

   # Change all passwords
   ```

---

## Compliance Checklist

### GDPR (if applicable)

- [ ] **Data minimization**: Only collect necessary data
- [ ] **User consent**: Privacy policy + terms of service
- [ ] **Right to deletion**: Implement user data export/delete
- [ ] **Data portability**: Export user data in JSON format
- [ ] **Breach notification**: Alert users within 72 hours
- [ ] **Data retention**: Auto-delete old logs (90 days)

### SOC 2 (if applicable)

- [ ] **Access control**: Role-based permissions
- [ ] **Audit logging**: All critical actions logged
- [ ] **Encryption**: Data at rest + in transit
- [ ] **Backup/DR**: Regular backups + tested restores
- [ ] **Monitoring**: Security alerts configured

---

## Security Audit

### Monthly Checklist

- [ ] Review audit logs for suspicious activity
- [ ] Check for failed login attempts (brute force)
- [ ] Verify HTTPS certificate expiry (30+ days remaining)
- [ ] Test backup restore process
- [ ] Update all dependencies (`pip list --outdated`, `npm outdated`)
- [ ] Scan for vulnerabilities (`safety check`, `npm audit`)
- [ ] Review user accounts (remove inactive users)
- [ ] Check disk usage (logs, backups)

### Quarterly Checklist

- [ ] Penetration testing (internal or external)
- [ ] Dependency upgrades (major versions)
- [ ] Security training for users
- [ ] Review and update security policies
- [ ] Rotate credentials (SSH keys, API tokens)

---

## Security Tools

### Vulnerability Scanning

```bash
# Python dependencies
pip install safety
safety check

# Node.js dependencies
npm audit

# System packages
sudo apt install debsecan
sudo debsecan --suite=jammy
```

### Port Scanning

```bash
# Scan open ports (from external machine)
nmap -sV mon.yourdomain.com

# Should only show 22 (SSH), 80 (HTTP), 443 (HTTPS)
# Ports 9081-9085 should NOT be exposed
```

### SSL Testing

```bash
# Test SSL configuration
curl -I https://mon.yourdomain.com

# Or use online tool
# https://www.ssllabs.com/ssltest/
```

---

## Resources

- [Security Policy](../../SECURITY.md) — Vulnerability reporting
- [HTTPS Setup](../../HTTPS-SETUP.md) — SSL certificate setup
- [Nginx Proxy](../../NGINX_PROXY_GUIDE.md) — Reverse proxy configuration
- [Backup Guide](../operations/BACKUP_RESTORE.md) — Backup procedures
- [Troubleshooting](../getting-started/TROUBLESHOOTING.md) — Common issues

---

**Security Questions?** [Open an issue](https://github.com/minhtuancn/server-monitor/issues) with tag `security`.
