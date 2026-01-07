# Server Monitor Dashboard - Installer Guide

**Version:** 2.0.0  
**Last Updated:** 2026-01-07

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [One-Command Installation](#one-command-installation)
4. [Manual Installation](#manual-installation)
5. [Post-Installation](#post-installation)
6. [Update & Maintenance](#update--maintenance)
7. [Uninstallation](#uninstallation)
8. [Directory Structure](#directory-structure)
9. [Firewall & Network Configuration](#firewall--network-configuration)
10. [Reverse Proxy Setup](#reverse-proxy-setup)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The Server Monitor Dashboard installer provides a fully automated, production-ready deployment on Linux systems. With a single command, you can:

- Install all dependencies (Python, Node.js, system packages)
- Clone and configure the application
- Set up SQLite database with automatic initialization
- Create systemd services for auto-start on boot
- Generate secure configuration with random secrets

### Key Features

- ✅ **One-command installation** - No manual configuration needed
- ✅ **Multi-distro support** - Ubuntu, Debian, CentOS, RHEL, Fedora, Arch
- ✅ **Automatic updates** - Safe update with backup and rollback
- ✅ **Systemd integration** - Auto-start on reboot, auto-restart on failure
- ✅ **Security hardened** - Non-root execution, secure defaults
- ✅ **SQLite database** - No external database required
- ✅ **Backup & restore** - Built-in database backup tools

---

## 💻 System Requirements

### Minimum Requirements

- **OS**: Linux (Ubuntu 20.04+, Debian 10+, CentOS 8+, RHEL 8+, Fedora 35+, Arch)
- **CPU**: 1 core (2+ recommended)
- **RAM**: 512 MB (1 GB+ recommended)
- **Disk**: 2 GB free space
- **Network**: Internet connection for installation

### Required Ports

The following ports must be available:

| Port | Service | Description |
|------|---------|-------------|
| 9081 | Frontend | Next.js web interface |
| 9083 | API | Backend REST API |
| 9084 | Terminal | WebSocket terminal service |
| 9085 | WebSocket | Real-time monitoring updates |

### Supported Distributions

| Distribution | Versions | Status |
|-------------|----------|---------|
| Ubuntu | 20.04, 22.04, 24.04 | ✅ Fully tested |
| Debian | 10, 11, 12 | ✅ Fully tested |
| CentOS | 8, 9 Stream | ✅ Tested |
| RHEL | 8, 9 | ✅ Tested |
| AlmaLinux | 8, 9 | ✅ Tested |
| Rocky Linux | 8, 9 | ✅ Tested |
| Fedora | 35+ | ✅ Tested |
| Arch Linux | Latest | ⚠️ Best-effort |

---

## 🚀 One-Command Installation

### Quick Install (Latest Version)

```bash
curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash
```

### Install Specific Version

```bash
# Install a specific tag
curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash -s -- --ref v2.0.0

# Install a specific branch
curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash -s -- --ref develop
```

### What Happens During Installation?

1. **System Detection**: Identifies your Linux distribution and package manager
2. **Dependency Installation**: Installs Python 3.8+, Node.js 18+, git, and system tools
3. **User Creation**: Creates dedicated `server-monitor` service user (non-root)
4. **Directory Setup**: Creates `/opt/server-monitor`, `/etc/server-monitor`, `/var/lib/server-monitor`, `/var/log/server-monitor`
5. **Code Download**: Clones repository from GitHub
6. **Backend Setup**: Creates Python virtual environment, installs dependencies
7. **Frontend Build**: Installs Node packages, builds Next.js application
8. **Configuration**: Generates `.env` with secure random secrets
9. **Database Init**: Creates SQLite database with default schema
10. **Service Installation**: Installs and starts 4 systemd services
11. **Health Check**: Verifies all services are running

**Installation time**: 3-5 minutes on typical systems

---

## 🔧 Manual Installation

If you prefer manual control or the automated installer doesn't work for your system:

### Step 1: Install Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv curl lsof

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs
```

**RHEL/CentOS/Fedora:**
```bash
sudo dnf install -y git python3 python3-pip curl lsof

# Install Node.js 18
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo dnf install -y nodejs
```

### Step 2: Create Service User

```bash
sudo useradd --system --no-create-home --shell /bin/false server-monitor
```

### Step 3: Create Directories

```bash
sudo mkdir -p /opt/server-monitor
sudo mkdir -p /etc/server-monitor
sudo mkdir -p /var/lib/server-monitor
sudo mkdir -p /var/log/server-monitor
sudo mkdir -p /var/lib/server-monitor/backups

sudo chown -R server-monitor:server-monitor /var/lib/server-monitor
sudo chown -R server-monitor:server-monitor /var/log/server-monitor
```

### Step 4: Clone Repository

```bash
cd /opt
sudo git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor
```

### Step 5: Setup Backend

```bash
cd /opt/server-monitor
sudo python3 -m venv .venv
sudo .venv/bin/pip install --upgrade pip
sudo .venv/bin/pip install -r backend/requirements.txt
```

### Step 6: Setup Frontend

```bash
cd /opt/server-monitor/frontend-next
sudo npm ci --production
sudo npm run build
```

### Step 7: Configure Environment

```bash
# Generate secrets
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")

# Create environment file
sudo tee /etc/server-monitor/server-monitor.env > /dev/null << EOF
JWT_SECRET=$JWT_SECRET
JWT_EXPIRATION=86400
ENCRYPTION_KEY=$ENCRYPTION_KEY
DB_PATH=/var/lib/server-monitor/servers.db
API_PORT=9083
FRONTEND_PORT=9081
WEBSOCKET_PORT=9085
TERMINAL_PORT=9084
NODE_ENV=production
PORT=9081
API_PROXY_TARGET=http://localhost:9083
NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084
EOF

sudo chmod 600 /etc/server-monitor/server-monitor.env
```

### Step 8: Initialize Database

```bash
cd /opt/server-monitor/backend
source /opt/server-monitor/.venv/bin/activate
export DB_PATH=/var/lib/server-monitor/servers.db
python3 -c "import database; database.init_database()"
sudo chown server-monitor:server-monitor /var/lib/server-monitor/servers.db
```

### Step 9: Install Systemd Services

```bash
cd /opt/server-monitor
sudo cp services/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### Step 10: Set Permissions

```bash
sudo chown -R server-monitor:server-monitor /opt/server-monitor
sudo chown root:server-monitor /etc/server-monitor/server-monitor.env
sudo chmod 640 /etc/server-monitor/server-monitor.env
```

### Step 11: Start Services

```bash
sudo systemctl enable server-monitor-api
sudo systemctl enable server-monitor-ws
sudo systemctl enable server-monitor-terminal
sudo systemctl enable server-monitor-frontend

sudo systemctl start server-monitor-api
sudo systemctl start server-monitor-ws
sudo systemctl start server-monitor-terminal
sudo systemctl start server-monitor-frontend
```

---

## 🎉 Post-Installation

### Access the Dashboard

Open your browser and navigate to:
```
http://YOUR_SERVER_IP:9081
```

### Default Credentials

```
Username: admin
Password: admin123
```

**⚠️ IMPORTANT**: Change the default password immediately after first login!

### Change Admin Password

1. Log in with default credentials
2. Go to **Settings** → **Users**
3. Click on **admin** user
4. Change password
5. Save changes

### Verify Services

```bash
# Check all services
sudo systemctl status server-monitor-*

# Check individual service
sudo systemctl status server-monitor-api

# View logs
sudo journalctl -u server-monitor-* -f
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:9083/api/stats/overview

# Login test
curl -X POST http://localhost:9083/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 🔄 Update & Maintenance

### Update to Latest Version

```bash
# Update to latest on current branch
sudo /opt/server-monitor/scripts/update.sh

# Update to specific version
sudo /opt/server-monitor/scripts/update.sh --ref v2.1.0
```

**What happens during update:**
1. Current state is saved for rollback
2. Database is backed up to `/var/lib/server-monitor/backups/`
3. Services are stopped
4. Code is updated from GitHub
5. Backend dependencies are reinstalled
6. Frontend is rebuilt
7. Database migrations are run (if any)
8. Services are restarted
9. Health check is performed

### Rollback to Previous Version

If an update fails or causes issues:

```bash
sudo /opt/server-monitor/scripts/rollback.sh
```

### Using the Control Script

The `smctl` command provides unified management:

```bash
# Install symlink for easy access
sudo ln -s /opt/server-monitor/scripts/smctl /usr/local/bin/smctl

# Check status
smctl status

# Restart all services
sudo smctl restart

# View logs
smctl logs           # All services
smctl logs api       # API only
smctl logs frontend  # Frontend only

# Backup database
sudo smctl backup

# Restore database
sudo smctl restore /var/lib/server-monitor/backups/servers-20260107-120000.db

# Update
sudo smctl update
```

### Manual Service Management

```bash
# Start/stop/restart individual services
sudo systemctl start server-monitor-api
sudo systemctl stop server-monitor-api
sudo systemctl restart server-monitor-api

# View service logs
sudo journalctl -u server-monitor-api -f
sudo journalctl -u server-monitor-api -n 100  # Last 100 lines

# Check service status
sudo systemctl status server-monitor-api
```

---

## 🗑️ Uninstallation

### Quick Uninstall

```bash
sudo smctl uninstall
```

Or:

```bash
# Stop and disable services
sudo systemctl stop server-monitor-*
sudo systemctl disable server-monitor-*

# Remove service files
sudo rm /etc/systemd/system/server-monitor-*.service
sudo systemctl daemon-reload

# Remove installation directory
sudo rm -rf /opt/server-monitor
```

### Complete Cleanup (Including Data)

```bash
# After uninstalling, remove data directories
sudo rm -rf /var/lib/server-monitor
sudo rm -rf /etc/server-monitor
sudo rm -rf /var/log/server-monitor

# Remove service user
sudo userdel server-monitor
```

---

## 📁 Directory Structure

### Installation Layout

```
/opt/server-monitor/                 # Application code
├── backend/                         # Python backend
│   ├── central_api.py              # Main API server
│   ├── websocket_server.py         # WebSocket server
│   ├── terminal.py                 # Terminal server
│   └── database.py                 # Database module
├── frontend-next/                   # Next.js frontend
│   ├── .next/                      # Built output
│   └── src/                        # Source code
├── scripts/                         # Management scripts
│   ├── install.sh                  # Installer
│   ├── update.sh                   # Update script
│   ├── rollback.sh                 # Rollback script
│   └── smctl                       # Control script
├── services/systemd/                # Systemd unit files
└── .venv/                          # Python virtual environment

/etc/server-monitor/                 # Configuration
└── server-monitor.env              # Environment variables

/var/lib/server-monitor/             # Data directory
├── servers.db                       # SQLite database
└── backups/                        # Database backups

/var/log/server-monitor/             # Logs (via journald)
```

### Configuration Files

| File | Purpose | Owner |
|------|---------|-------|
| `/etc/server-monitor/server-monitor.env` | Environment variables | root:server-monitor (640) |
| `/var/lib/server-monitor/servers.db` | SQLite database | server-monitor:server-monitor (644) |
| `/opt/server-monitor/frontend-next/.env.local` | Frontend config | server-monitor:server-monitor (644) |

---

## 🔥 Firewall & Network Configuration

### UFW (Ubuntu/Debian)

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow application ports (if accessing directly)
sudo ufw allow 9081/tcp comment 'Server Monitor Frontend'
sudo ufw allow 9083/tcp comment 'Server Monitor API'
sudo ufw allow 9084/tcp comment 'Server Monitor Terminal'
sudo ufw allow 9085/tcp comment 'Server Monitor WebSocket'

# Enable firewall
sudo ufw enable
```

### firewalld (RHEL/CentOS/Fedora)

```bash
# Allow HTTP/HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# Allow application ports
sudo firewall-cmd --permanent --add-port=9081/tcp
sudo firewall-cmd --permanent --add-port=9083/tcp
sudo firewall-cmd --permanent --add-port=9084/tcp
sudo firewall-cmd --permanent --add-port=9085/tcp

# Reload firewall
sudo firewall-cmd --reload
```

### iptables

```bash
# Allow application ports
sudo iptables -A INPUT -p tcp --dport 9081 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 9083 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 9084 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 9085 -j ACCEPT

# Save rules
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

---

## 🔒 Reverse Proxy Setup

For production deployments, use a reverse proxy (Nginx or Apache) for SSL/TLS and domain mapping.

### Nginx Configuration

Create `/etc/nginx/sites-available/server-monitor`:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name monitor.example.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name monitor.example.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/monitor.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monitor.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:9081;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket (monitoring)
    location /ws {
        proxy_pass http://localhost:9085;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # WebSocket (terminal)
    location /terminal {
        proxy_pass http://localhost:9084;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # API (proxied through Next.js BFF)
    location /api/ {
        proxy_pass http://localhost:9081;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/server-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Update Environment for Domain

Edit `/etc/server-monitor/server-monitor.env`:

```bash
# Update WebSocket URLs for domain
NEXT_PUBLIC_MONITORING_WS_URL=wss://monitor.example.com/ws
NEXT_PUBLIC_TERMINAL_WS_URL=wss://monitor.example.com/terminal
```

Restart frontend:
```bash
sudo systemctl restart server-monitor-frontend
```

### SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx  # Ubuntu/Debian
sudo dnf install certbot python3-certbot-nginx  # RHEL/Fedora

# Obtain certificate
sudo certbot --nginx -d monitor.example.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

---

## 🔧 Troubleshooting

### Services Won't Start

**Check service status:**
```bash
sudo systemctl status server-monitor-*
```

**View detailed logs:**
```bash
sudo journalctl -u server-monitor-api -n 100 --no-pager
```

**Common issues:**

1. **Port already in use**
   ```bash
   # Find process using port
   sudo lsof -i :9083
   
   # Kill process
   sudo kill -9 <PID>
   ```

2. **Permission denied**
   ```bash
   # Fix ownership
   sudo chown -R server-monitor:server-monitor /opt/server-monitor
   sudo chown -R server-monitor:server-monitor /var/lib/server-monitor
   ```

3. **Database locked**
   ```bash
   # Check for stale processes
   ps aux | grep python
   
   # Kill stale processes
   sudo pkill -9 -f central_api.py
   ```

### WebSocket Connection Fails

**Symptoms:** Real-time updates don't work, terminal doesn't connect

**Solutions:**

1. **Check WebSocket service**
   ```bash
   sudo systemctl status server-monitor-ws
   sudo journalctl -u server-monitor-ws -f
   ```

2. **Verify port is listening**
   ```bash
   sudo lsof -i :9085
   sudo lsof -i :9084
   ```

3. **Check firewall**
   ```bash
   sudo ufw status
   sudo firewall-cmd --list-all
   ```

4. **Test WebSocket connection**
   ```bash
   # Install wscat
   npm install -g wscat
   
   # Test connection
   wscat -c ws://localhost:9085
   ```

5. **Check browser console**
   - Open Developer Tools (F12)
   - Check Console for WebSocket errors
   - Check Network tab for failed connections

### Frontend Shows 502 Bad Gateway

**Causes:**
- Frontend service not running
- API service not running
- Port mismatch in configuration

**Solutions:**

1. **Check services**
   ```bash
   sudo systemctl status server-monitor-frontend
   sudo systemctl status server-monitor-api
   ```

2. **Check frontend logs**
   ```bash
   sudo journalctl -u server-monitor-frontend -n 50
   ```

3. **Verify API is accessible**
   ```bash
   curl http://localhost:9083/api/stats/overview
   ```

4. **Check environment configuration**
   ```bash
   cat /etc/server-monitor/server-monitor.env | grep PORT
   ```

### Login Fails with "Invalid Credentials"

**Solutions:**

1. **Reset admin password**
   ```bash
   cd /opt/server-monitor/backend
   source /opt/server-monitor/.venv/bin/activate
   export DB_PATH=/var/lib/server-monitor/servers.db
   python3 -c "
   import database as db
   conn = db.get_connection()
   cursor = conn.cursor()
   hashed = db.hash_password('admin123')
   cursor.execute('UPDATE users SET password = ? WHERE username = ?', (hashed, 'admin'))
   conn.commit()
   print('Password reset to: admin123')
   "
   ```

2. **Check JWT_SECRET is set**
   ```bash
   grep JWT_SECRET /etc/server-monitor/server-monitor.env
   ```

### Database Corruption

**Symptoms:** API returns 500 errors, services crash

**Solutions:**

1. **Restore from backup**
   ```bash
   sudo smctl restore /var/lib/server-monitor/backups/servers-LATEST.db
   ```

2. **Recreate database**
   ```bash
   # Backup current database
   sudo cp /var/lib/server-monitor/servers.db /tmp/servers.db.backup
   
   # Remove corrupted database
   sudo rm /var/lib/server-monitor/servers.db
   
   # Reinitialize
   cd /opt/server-monitor/backend
   source /opt/server-monitor/.venv/bin/activate
   export DB_PATH=/var/lib/server-monitor/servers.db
   python3 -c "import database; database.init_database()"
   
   # Fix permissions
   sudo chown server-monitor:server-monitor /var/lib/server-monitor/servers.db
   
   # Restart services
   sudo systemctl restart server-monitor-*
   ```

### High CPU/Memory Usage

**Check resource usage:**
```bash
# Overall system
top
htop

# Specific services
systemctl status server-monitor-*

# Memory usage per service
ps aux | grep -E 'central_api|websocket|terminal|npm'
```

**Solutions:**

1. **Limit resources in systemd**
   Edit service files in `/etc/systemd/system/`:
   ```ini
   [Service]
   MemoryMax=200M
   CPUQuota=50%
   ```

2. **Reduce WebSocket update frequency**
   Edit `backend/websocket_server.py`:
   ```python
   UPDATE_INTERVAL = 5  # Increase from 3 to 5 seconds
   ```

### Installation Fails

**Common issues:**

1. **Unsupported distribution**
   - Check `/etc/os-release` for distribution ID
   - Ensure you're using a supported distro
   - Try manual installation

2. **Network issues**
   ```bash
   # Test GitHub connectivity
   curl -I https://github.com
   
   # Test npm registry
   npm ping
   ```

3. **Insufficient disk space**
   ```bash
   df -h /opt
   df -h /var
   ```

4. **Package manager issues**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt-get -f install
   
   # RHEL/Fedora
   sudo dnf clean all
   sudo dnf update
   ```

### Getting Help

If you're still experiencing issues:

1. **Check logs**
   ```bash
   sudo journalctl -u server-monitor-* -n 200 --no-pager > /tmp/logs.txt
   ```

2. **Gather system information**
   ```bash
   uname -a
   cat /etc/os-release
   python3 --version
   node --version
   ```

3. **Create GitHub issue**
   - Visit: https://github.com/minhtuancn/server-monitor/issues
   - Include logs, system info, and steps to reproduce
   - Tag with `bug` label

---

## 📚 Additional Resources

- **Main README**: [README.md](../README.md)
- **Deployment Guide**: [DEPLOYMENT.md](../DEPLOYMENT.md)
- **Post-Production Guide**: [POST-PRODUCTION.md](../POST-PRODUCTION.md)
- **Security Guide**: [SECURITY.md](../SECURITY.md)
- **HTTPS Setup**: [HTTPS-SETUP.md](../HTTPS-SETUP.md)
- **GitHub Repository**: https://github.com/minhtuancn/server-monitor
- **Issue Tracker**: https://github.com/minhtuancn/server-monitor/issues

---

**Happy Monitoring! 🎉**
