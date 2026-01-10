# Production Security Checklist

**Complete this checklist before deploying Server Monitor to production.**

Last Updated: 2026-01-10

---

## 🔒 Pre-Deployment Security Audit

### ✅ Secrets & Environment

- [ ] **JWT_SECRET**: Generated using `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] **ENCRYPTION_KEY**: Generated using `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] **KEY_VAULT_MASTER_KEY**: Generated using `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] **DEBUG**: Set to `false` in production environment
- [ ] **ENVIRONMENT**: Set to `production`
- [ ] **ALLOWED_FRONTEND_DOMAINS**: Set to your domain(s), NO wildcards (\*)
- [ ] **.env file**: Created from .env.example with production values
- [ ] **.env permissions**: Set to `600` (readable only by application user)

### ✅ Authentication & Authorization

- [ ] **Default admin password**: Changed on first login (force password change policy)
- [ ] **Strong passwords**: Minimum 8 chars, mixed case, numbers, symbols
- [ ] **JWT expiration**: Set to reasonable timeframe (24h recommended)
- [ ] **Session security**: Secure, HttpOnly, SameSite cookies enabled
- [ ] **Role-based access**: Admin/operator/viewer permissions working

### ✅ Network Security

- [ ] **HTTPS**: SSL/TLS certificate installed and configured
- [ ] **HTTP redirect**: All HTTP traffic redirects to HTTPS
- [ ] **CORS**: Only allow trusted domains, no wildcard origins
- [ ] **Security headers**: CSP, X-Frame-Options, HSTS enabled
- [ ] **Rate limiting**: API and login rate limits enabled
- [ ] **Firewall**: Only required ports open (22, 80, 443)

### ✅ Infrastructure

- [ ] **Reverse proxy**: Nginx/Caddy configured (recommended)
- [ ] **Process isolation**: Run as non-root user
- [ ] **File permissions**: Restrictive permissions on all files
- [ ] **Database encryption**: SQLite encryption or encrypted filesystem
- [ ] **Backup encryption**: Encrypted backup storage
- [ ] **Log rotation**: Prevent disk space issues

---

## 🛡️ Security Configuration Validation

### Test HTTPS Configuration

```bash
# Test SSL certificate
curl -I https://your-domain.com

# Check SSL rating (optional)
# Visit: https://www.ssllabs.com/ssltest/
```

### Test Rate Limiting

```bash
# Should return 429 after 5 attempts
for i in {1..6}; do
  curl -X POST https://your-domain.com/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"wrong"}' \
    -w "Status: %{http_code}\n"
done
```

### Test CORS

```bash
# Should return proper CORS headers
curl -H "Origin: https://your-domain.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://your-domain.com/api/health
```

### Test Security Headers

```bash
# Should include security headers
curl -I https://your-domain.com
# Look for: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options
```

---

## 📊 Security Metrics Baseline

After deployment, monitor these security metrics:

### Authentication Metrics

- Failed login attempts per hour: < 50
- Account lockouts per day: < 5
- Session duration average: 2-8 hours
- Password reset requests per day: < 10

### API Security Metrics

- Rate limit violations per hour: < 100
- 4xx error rate: < 5%
- SSL/TLS errors per day: 0
- CORS violations per day: < 10

### System Security Metrics

- File permission violations: 0
- Unauthorized access attempts: 0
- Certificate expiration warnings: > 30 days
- Database access errors: 0

---

## 🚨 Incident Response Preparation

### Detection

- [ ] Log monitoring configured
- [ ] Alert thresholds set
- [ ] Automated notifications working
- [ ] Security scan schedule defined

### Response Plan

- [ ] Incident response team contacts
- [ ] Communication templates ready
- [ ] System isolation procedures documented
- [ ] Evidence collection procedures defined

### Recovery

- [ ] Backup restore procedures tested
- [ ] Rollback procedures documented
- [ ] Service restoration checklist
- [ ] Post-incident review template

---

## ✅ Compliance & Audit

### Regular Security Tasks

#### Weekly

- [ ] Review failed authentication logs
- [ ] Check certificate expiration status
- [ ] Review rate limiting violations
- [ ] Validate backup integrity

#### Monthly

- [ ] Update dependencies (`pip list --outdated`, `npm audit`)
- [ ] Run security scan (`bandit -r backend/`)
- [ ] Review user access permissions
- [ ] Test backup restore procedure

#### Quarterly

- [ ] Penetration testing
- [ ] Security policy review
- [ ] Incident response drill
- [ ] Compliance documentation update

---

## 🔍 Security Tools & Commands

### Vulnerability Scanning

```bash
# Python dependencies
pip install safety
safety check

# Node.js dependencies (if using frontend)
npm audit

# Code security scan
bandit -r backend/

# System packages (Ubuntu/Debian)
apt install debsecan
debsecan --suite=$(lsb_release -cs)
```

### Port Security Check

```bash
# Internal scan
nmap -sV localhost

# External scan (from different machine)
nmap -sV your-domain.com
# Should only show: 22 (SSH), 80 (HTTP), 443 (HTTPS)
```

### SSL/TLS Testing

```bash
# Certificate info
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Certificate expiration
openssl s_client -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates
```

---

## 📝 Security Documentation

Ensure these documents are current:

- [ ] [SECURITY.md](../SECURITY.md) - Vulnerability reporting policy
- [ ] [PRODUCTION_SECURITY.md](PRODUCTION_SECURITY.md) - Hardening guide
- [ ] [HTTPS_SETUP.md](../operations/HTTPS_SETUP.md) - SSL certificate setup
- [ ] [BACKUP_RESTORE.md](../operations/BACKUP_RESTORE.md) - Backup procedures
- [ ] [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md) - Incident response plan

---

## ⚠️ Security Warnings

### Never Do This in Production

- ❌ Use default passwords (admin/admin123)
- ❌ Set DEBUG=true
- ❌ Allow wildcard CORS origins (\*)
- ❌ Run as root user
- ❌ Commit .env files to version control
- ❌ Use HTTP instead of HTTPS
- ❌ Disable rate limiting
- ❌ Use weak encryption keys
- ❌ Skip backup encryption
- ❌ Ignore security updates

### Red Flags (Investigate Immediately)

- 🚩 Multiple failed login attempts from same IP
- 🚩 Database connection errors
- 🚩 SSL certificate warnings
- 🚩 Unusual API error rates
- 🚩 CORS violation alerts
- 🚩 File permission changes
- 🚩 Unexpected network connections
- 🚩 Disk space alerts (possible log flooding)

---

## ✅ Sign-Off

**Security Officer**: **********\_\_\_\_********** Date: ****\_\_****

**System Administrator**: ********\_\_\_\_******** Date: ****\_\_****

**Project Lead**: ************\_\_\_\_************ Date: ****\_\_****

**Notes**:

---

---

---

---

**Need Help?**

- Security Policy: [SECURITY.md](../SECURITY.md)
- Production Guide: [PRODUCTION_SECURITY.md](PRODUCTION_SECURITY.md)
- Create Security Issue: [GitHub Issues](https://github.com/minhtuancn/server-monitor/issues)
