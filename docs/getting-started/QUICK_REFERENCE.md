# Server Monitor Dashboard - Quick Reference

## 🚀 Installation

### One-Command Install
```bash
curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash
```

### Install Specific Version
```bash
curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash -s -- --ref v2.0.0
```

---

## 📋 Management Commands

### Check Status
```bash
sudo smctl status
sudo systemctl status server-monitor-*
```

### Start/Stop/Restart
```bash
sudo smctl start
sudo smctl stop
sudo smctl restart
```

### View Logs
```bash
sudo smctl logs              # All services
sudo smctl logs api          # API only
sudo smctl logs frontend     # Frontend only
sudo journalctl -u server-monitor-* -f
```

---

## 🔄 Update & Rollback

### Update to Latest
```bash
sudo smctl update
# OR
sudo /opt/server-monitor/scripts/update.sh
```

### Update to Specific Version
```bash
sudo /opt/server-monitor/scripts/update.sh --ref v2.1.0
```

### Rollback
```bash
sudo /opt/server-monitor/scripts/rollback.sh
```

---

## 💾 Backup & Restore

### Backup Database
```bash
sudo smctl backup
```

### List Backups
```bash
ls -lh /var/lib/server-monitor/backups/
```

### Restore Database
```bash
sudo smctl restore /var/lib/server-monitor/backups/servers-20260107-120000.db
```

---

## 🗑️ Uninstall

### Remove Services (Keep Data)
```bash
sudo smctl uninstall
```

### Complete Removal (Including Data)
```bash
sudo smctl uninstall
sudo rm -rf /var/lib/server-monitor
sudo rm -rf /etc/server-monitor
sudo rm -rf /var/log/server-monitor
sudo userdel server-monitor
```

---

## 📁 Important Locations

| Path | Description |
|------|-------------|
| `/opt/server-monitor/` | Application code |
| `/etc/server-monitor/server-monitor.env` | Configuration |
| `/var/lib/server-monitor/servers.db` | Database |
| `/var/lib/server-monitor/backups/` | Database backups |
| `/var/log/server-monitor/` | Logs (journald) |

---

## 🌐 Default Access

- **Dashboard**: http://YOUR_SERVER_IP:9081
- **API**: http://YOUR_SERVER_IP:9083
- **WebSocket**: ws://YOUR_SERVER_IP:9085
- **Terminal**: ws://YOUR_SERVER_IP:9084

**Default Login**:
- Username: `admin`
- Password: `admin123`
- ⚠️ **Change immediately after first login!**

---

## 🔥 Firewall Configuration

### UFW (Ubuntu/Debian)
```bash
sudo ufw allow 9081/tcp
sudo ufw allow 9083/tcp
sudo ufw allow 9084/tcp
sudo ufw allow 9085/tcp
```

### firewalld (RHEL/CentOS/Fedora)
```bash
sudo firewall-cmd --permanent --add-port=9081/tcp
sudo firewall-cmd --permanent --add-port=9083/tcp
sudo firewall-cmd --permanent --add-port=9084/tcp
sudo firewall-cmd --permanent --add-port=9085/tcp
sudo firewall-cmd --reload
```

---

## 🔧 Troubleshooting

### Service Won't Start
```bash
# Check status
sudo systemctl status server-monitor-api

# View logs
sudo journalctl -u server-monitor-api -n 100

# Check port availability
sudo lsof -i :9083
```

### Reset Admin Password
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

### Database Issues
```bash
# Check database integrity
sqlite3 /var/lib/server-monitor/servers.db "PRAGMA integrity_check;"

# Restore from backup
sudo smctl restore /var/lib/server-monitor/backups/servers-LATEST.db
```

---

## 📚 Documentation

- **Installation Guide**: [docs/INSTALLER.md](docs/INSTALLER.md)
- **Deployment Guide**: [DEPLOYMENT.md](docs/operations/DEPLOYMENT.md)
- **Post-Production**: [POST-PRODUCTION.md](POST-PRODUCTION.md)
- **Security**: [SECURITY.md](docs/security/SECURITY.md)

---

## 🆘 Support

- **GitHub Issues**: https://github.com/minhtuancn/server-monitor/issues
- **Documentation**: https://github.com/minhtuancn/server-monitor
- **Email**: Include logs and system info when reporting issues

---

**Version**: 2.0.0  
**Last Updated**: 2026-01-07
