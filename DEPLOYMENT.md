# Server Monitor - Deployment Guide

**Version:** 1.0.0  
**Last Updated:** 2026-01-07

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Configuration](#environment-configuration)
3. [Deployment Options](#deployment-options)
4. [Database Setup](#database-setup)
5. [Service Management](#service-management)
6. [Reverse Proxy Setup](#reverse-proxy-setup)
7. [Security Hardening](#security-hardening)
8. [Health Checks](#health-checks)
9. [Rollback Procedure](#rollback-procedure)
10. [Troubleshooting](#troubleshooting)

---

## ✅ Pre-Deployment Checklist

Before deploying to production, ensure:

### Security
- [ ] Generate new `JWT_SECRET` (minimum 32 characters)
- [ ] Generate new `ENCRYPTION_KEY` (minimum 24 characters)
- [ ] Change default admin password (`admin123`)
- [ ] Review CORS allowed origins in `security.py`
- [ ] Configure firewall rules
- [ ] Set up HTTPS (see [HTTPS-SETUP.md](HTTPS-SETUP.md))

### Configuration
- [ ] Create `.env` file from `.env.example`
- [ ] Configure correct database path
- [ ] Set appropriate port numbers
- [ ] Configure email settings (optional)

### Testing
- [ ] Run test suite: `pytest tests/ -v`
- [ ] Verify all critical endpoints work
- [ ] Test authentication flow
- [ ] Test WebSocket connection

---

## 🔧 Environment Configuration

### Backend Configuration

Create `.env` file in project root:

```bash
# Copy example file
cp .env.example .env

# Generate secure keys
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")

# Update .env with generated keys
sed -i "s/REPLACE_WITH_SECURE_RANDOM_VALUE/$JWT_SECRET/1" .env
sed -i "s/REPLACE_WITH_SECURE_RANDOM_VALUE/$ENCRYPTION_KEY/" .env
```

### Essential Backend Variables

```bash
# Required for production
JWT_SECRET=<your-secure-secret>
ENCRYPTION_KEY=<your-encryption-key>

# Optional - use defaults if not set
JWT_EXPIRATION=86400
API_PORT=9083
FRONTEND_PORT=9081
WEBSOCKET_PORT=9085
TERMINAL_PORT=9084
```

### Frontend Configuration

Create `.env.local` file in `frontend-next/` directory:

```bash
cd frontend-next
cat > .env.local << EOF
# Backend API base URL (used by BFF proxy)
API_PROXY_TARGET=http://localhost:9083

# WebSocket URLs (public - exposed to browser)
NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084
EOF
```

**For production with domain:**
```bash
# In frontend-next/.env.local
API_PROXY_TARGET=http://localhost:9083
NEXT_PUBLIC_MONITORING_WS_URL=wss://monitor.example.com/ws
NEXT_PUBLIC_TERMINAL_WS_URL=wss://monitor.example.com/terminal
```

### Environment Variable Reference

| Variable | Location | Description | Required | Default |
|----------|----------|-------------|----------|---------|
| `JWT_SECRET` | Backend | JWT token secret | Yes | - |
| `ENCRYPTION_KEY` | Backend | SSH password encryption key | Yes | - |
| `JWT_EXPIRATION` | Backend | Token expiry (seconds) | No | 86400 |
| `API_PORT` | Backend | API server port | No | 9083 |
| `WEBSOCKET_PORT` | Backend | WebSocket server port | No | 9085 |
| `TERMINAL_PORT` | Backend | Terminal server port | No | 9084 |
| `API_PROXY_TARGET` | Frontend | Backend API URL for BFF | No | http://localhost:9083 |
| `NEXT_PUBLIC_MONITORING_WS_URL` | Frontend | Monitoring WebSocket URL | No | ws://localhost:9085 |
| `NEXT_PUBLIC_TERMINAL_WS_URL` | Frontend | Terminal WebSocket URL | No | ws://localhost:9084 |

---

## 🚀 Deployment Options

### Option 1: Manual Deployment

```bash
# 1. Clone repository
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor

# 2. Install dependencies
pip3 install -r backend/requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with secure values

# 4. Initialize database
cd backend
python3 -c "import database; database.init_database()"

# 5. Start services
cd ..
./start-all.sh  # backend + websocket + terminal

# 6. Start Next.js frontend (port 9081)
cd frontend-next
npm install
npm run build
npm run start  # Production mode on port 9081
```

**Frontend Development Mode:**
```bash
cd frontend-next
npm run dev  # Development mode with hot reload
```

### Option 2: Systemd Services

For production servers, use systemd for automatic service management and restart on failure:

#### Backend Services

```bash
# Copy backend service files
sudo cp services/server-dashboard-api-v2.service /etc/systemd/system/

# Edit paths in service file to match your installation
sudo nano /etc/systemd/system/server-dashboard-api-v2.service
# Update WorkingDirectory to your installation path (e.g., /opt/server-monitor/backend)

# Enable and start backend services
sudo systemctl daemon-reload
sudo systemctl enable server-dashboard-api-v2.service
sudo systemctl start server-dashboard-api-v2.service
```

#### Next.js Frontend Service

```bash
# Copy frontend service file
sudo cp services/server-monitor-frontend.service /etc/systemd/system/

# Edit paths and environment in service file
sudo nano /etc/systemd/system/server-monitor-frontend.service
# Update:
# - WorkingDirectory=/your/path/to/frontend-next
# - Environment variables if needed

# Create log directory
sudo mkdir -p /var/log/server-monitor
sudo chown www-data:www-data /var/log/server-monitor

# Enable and start frontend service
sudo systemctl daemon-reload
sudo systemctl enable server-monitor-frontend.service
sudo systemctl start server-monitor-frontend.service

# Check status
sudo systemctl status server-monitor-frontend.service
sudo journalctl -u server-monitor-frontend.service -f
```

**Note:** Make sure to build the Next.js app before starting the service:
```bash
cd frontend-next
npm ci  # Install exact versions from package-lock.json
npm run build  # Build for production
```

### Option 3: Docker (Future)

```bash
# Coming in v1.2.0
docker-compose up -d
```

---

## 🗄️ Database Setup

### Initialize Database

```bash
cd backend
python3 -c "import database; database.init_database()"
```

### Default Admin User

The system auto-creates a default admin user on first run:
- **Username:** admin
- **Password:** admin123

⚠️ **IMPORTANT:** Change this password immediately after first login!

### Database Backup

```bash
# Backup database
cp data/servers.db data/servers.db.backup.$(date +%Y%m%d)

# Restore from backup
cp data/servers.db.backup.YYYYMMDD data/servers.db
```

### Database Location

By default: `<project_root>/data/servers.db`

Override with environment variable:
```bash
export DB_PATH=/var/lib/server-monitor/servers.db
```

---

## ⚙️ Service Management

### Service Ports

| Service | Default Port | Purpose |
|---------|-------------|---------|
| Frontend | 9081 | Web UI |
| API | 9083 | REST API |
| Terminal | 9084 | SSH WebSocket |
| WebSocket | 9085 | Real-time updates |
| Agent | 8083 | Remote monitoring |

### Start All Services

```bash
./start-all.sh
```

### Stop All Services

```bash
./stop-all.sh
```

### Check Service Status

```bash
# Check if services are running
pgrep -f central_api.py
pgrep -f websocket_server.py
pgrep -f terminal.py

# Check ports
netstat -tlnp | grep -E ":(9081|9083|9084|9085)"
```

---

## 🔒 Reverse Proxy Setup

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/server-monitor
server {
    listen 80;
    server_name monitor.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name monitor.example.com;

    ssl_certificate /etc/letsencrypt/live/monitor.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monitor.example.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:9081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Next.js BFF/API (auth + proxy)
    location ^~ /api/auth/ {
        proxy_pass http://127.0.0.1:9081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location ^~ /api/proxy/ {
        proxy_pass http://127.0.0.1:9081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API (legacy fallback)
    location /api/ {
        proxy_pass http://127.0.0.1:9083/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:9085/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Terminal WebSocket
    location /terminal/ {
        proxy_pass http://127.0.0.1:9084/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/server-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

See [HTTPS-SETUP.md](HTTPS-SETUP.md) for detailed SSL configuration.

---

## 🛡️ Security Hardening

### 1. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP (redirect to HTTPS)
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

### 2. Update CORS Origins

Edit `backend/security.py`:
```python
ALLOWED_ORIGINS = [
    'https://monitor.example.com',
    'https://your-domain.com'
]
```

### 3. Change Default Password

After first login:
1. Go to Settings > Users
2. Click on admin user
3. Change password

Or via API:
```bash
curl -X POST http://localhost:9083/api/users/1/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"old_password":"admin123","new_password":"NewSecurePassword123!"}'
```

### 4. Disable Debug Mode

Ensure no debug output in production logs.

---

## 🏥 Health Checks

### API Health Check

```bash
# Simple health check
curl http://localhost:9083/api/stats/overview

# Expected response
{
  "total_servers": 0,
  "online_servers": 0,
  "offline_servers": 0,
  "unknown_servers": 0,
  "unread_alerts": 0
}
```

### Service Status Script

```bash
#!/bin/bash
# health-check.sh

API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9083/api/stats/overview)
if [ "$API_STATUS" != "200" ]; then
    echo "API is down! Status: $API_STATUS"
    exit 1
fi

echo "All services healthy"
exit 0
```

---

## ↩️ Rollback Procedure

### 1. Stop Services

```bash
./stop-all.sh
```

### 2. Restore Previous Version

```bash
# If using git
git checkout v1.0.0  # or previous version tag

# Restore database backup if needed
cp data/servers.db.backup data/servers.db
```

### 3. Restart Services

```bash
./start-all.sh
```

### 4. Verify

```bash
curl http://localhost:9083/api/stats/overview
```

---

## 🔧 Troubleshooting

### Services Not Starting

```bash
# Check if ports are in use
netstat -tlnp | grep -E ":(9081|9083|9084|9085)"

# Kill existing processes if needed
# Find the PID from netstat output, then:
kill <PID>

# Check logs
tail -f logs/*.log
```

### Next.js Frontend Issues

#### Build Fails

```bash
cd frontend-next

# Clear build cache and node_modules
rm -rf .next node_modules

# Reinstall dependencies
npm install

# Try building again
npm run build
```

#### Frontend Won't Start

```bash
# Check if port 9081 is available
lsof -i :9081

# Check environment variables
printenv | grep -E "API_PROXY|MONITORING_WS|TERMINAL_WS"

# Check logs
npm run start 2>&1 | tee frontend.log
```

#### Cookie/Authentication Issues

1. **Cookies not being set:**
   - Check DevTools → Application → Cookies
   - Verify `auth_token` cookie exists
   - Check `HttpOnly`, `SameSite=Lax`, `Secure` (in production) attributes

2. **Login redirects in a loop:**
   - Clear browser cookies for localhost:9081
   - Check `/api/auth/session` endpoint returns proper response
   - Verify JWT_SECRET in backend matches

3. **"Access Denied" on all pages:**
   - Check user role in `/api/auth/session` response
   - Verify middleware is not blocking legitimate routes

### Database Errors

```bash
# Reinitialize database (WARNING: loses data)
rm data/servers.db
cd backend
python3 -c "import database; database.init_database()"
```

### Authentication Issues

```bash
# Verify token
curl http://localhost:9083/api/auth/verify \
  -H "Authorization: Bearer $TOKEN"

# Re-login
curl -X POST http://localhost:9083/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### WebSocket Not Connecting

#### Monitoring WebSocket (port 9085)

```bash
# Check if WebSocket server is running
pgrep -f websocket_server.py

# Check logs
tail -f logs/websocket.log

# Test WebSocket connection
wscat -c ws://localhost:9085
```

#### Terminal WebSocket (port 9084)

```bash
# Check if terminal server is running
pgrep -f terminal.py

# Check logs
tail -f logs/terminal.log

# Verify port is listening
netstat -tlnp | grep 9084
```

#### Common WebSocket Issues

1. **Connection refused:**
   - Verify WebSocket server is running
   - Check firewall rules: `sudo ufw status`
   - Ensure ports 9084 and 9085 are open

2. **Connection drops immediately:**
   - Check authentication token is valid
   - Verify token is being sent in WebSocket handshake
   - Check backend logs for auth errors

3. **Nginx WebSocket proxy not working:**
   - Ensure Upgrade headers are set:
     ```nginx
     proxy_http_version 1.1;
     proxy_set_header Upgrade $http_upgrade;
     proxy_set_header Connection "upgrade";
     ```

4. **Multiple connections/memory leaks:**
   - Check browser console for unclosed connections
   - Verify cleanup in useEffect hooks
   - Clear browser cache and reload

### Proxy/API Issues

#### BFF Proxy Not Working

```bash
# Test proxy endpoint directly
curl -v http://localhost:9081/api/proxy/api/servers \
  -H "Cookie: auth_token=YOUR_TOKEN"

# Check Next.js logs
cd frontend-next
npm run start  # Watch for proxy errors
```

#### CORS Errors

1. Check backend `security.py` ALLOWED_ORIGINS
2. Verify Origin header in requests
3. For development, ensure `http://localhost:9081` is allowed

### Performance Issues

#### Slow Page Loads

1. Check network tab in DevTools for slow API calls
2. Verify backend server is not overloaded
3. Check database query performance
4. Enable React Query DevTools to inspect cache

#### WebSocket Lag

1. Check network latency to backend
2. Verify WebSocket update interval (default: 3 seconds)
3. Check if too many servers are being monitored simultaneously

---

## 📝 Post-Deployment

After successful deployment:

1. ✅ Verify all services are running
2. ✅ Test login with admin account
3. ✅ Change default admin password
4. ✅ Add first server to monitor
5. ✅ Test alerts (optional)
6. ✅ Set up monitoring for the monitor itself
7. ✅ Configure regular backups

See [POST-PRODUCTION.md](POST-PRODUCTION.md) for ongoing operations.

---

**Last Updated:** 2026-01-07
