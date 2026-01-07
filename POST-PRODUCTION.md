# Server Monitor - Post-Production Operations Guide

**Version:** 1.0.0  
**Last Updated:** 2026-01-07

---

## 📋 Table of Contents

1. [Monitoring the Monitor](#monitoring-the-monitor)
2. [Logging Strategy](#logging-strategy)
3. [Alerting Strategy](#alerting-strategy)
4. [Backup & Recovery](#backup--recovery)
5. [Maintenance Workflow](#maintenance-workflow)
6. [Incident Response](#incident-response)
7. [Performance Tuning](#performance-tuning)

---

## 📊 Monitoring the Monitor

### Health Check Endpoints

Use these endpoints to monitor system health:

```bash
# API availability
GET /api/stats/overview

# Authentication service
POST /api/auth/verify (with valid token)

# Server connectivity
GET /api/servers
```

### External Monitoring Setup

#### Option 1: Uptime Kuma (Recommended)

```yaml
# Monitor configuration
- name: Server Monitor API
  type: http
  url: https://monitor.example.com/api/stats/overview
  interval: 60
  retryInterval: 60
  maxretries: 3

- name: Server Monitor Frontend
  type: http
  url: https://monitor.example.com/
  interval: 60
```

#### Option 2: Cron-based Health Check

```bash
# /etc/cron.d/server-monitor-health
*/5 * * * * root /opt/server-monitor/scripts/health-check.sh >> /var/log/server-monitor-health.log 2>&1
```

Health check script:
```bash
#!/bin/bash
# /opt/server-monitor/scripts/health-check.sh

API_URL="http://localhost:9083"
ALERT_EMAIL="admin@example.com"

# Check API
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/stats/overview")

if [ "$HTTP_CODE" != "200" ]; then
    echo "[$(date)] ALERT: API returned $HTTP_CODE"
    echo "Server Monitor API is down! HTTP $HTTP_CODE" | mail -s "ALERT: Server Monitor Down" "$ALERT_EMAIL"
    exit 1
fi

echo "[$(date)] OK: API healthy"
```

### Key Metrics to Monitor

| Metric | Warning Threshold | Critical Threshold |
|--------|-------------------|-------------------|
| API Response Time | > 500ms | > 2000ms |
| Error Rate | > 1% | > 5% |
| WebSocket Connections | > 80% capacity | > 95% capacity |
| Database Size | > 80% disk | > 90% disk |
| Memory Usage | > 80% | > 90% |

---

## 📝 Logging Strategy

### Log Locations

```
/opt/server-monitor/logs/
├── central_api.log      # API requests and responses
├── websocket.log        # WebSocket connections
├── terminal.log         # SSH terminal sessions
└── web.log              # Frontend HTTP server
```

### Log Rotation

Create `/etc/logrotate.d/server-monitor`:

```
/opt/server-monitor/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        # Optionally restart services to rotate properly
        /opt/server-monitor/stop-all.sh
        /opt/server-monitor/start-all.sh
    endscript
}
```

### Log Analysis

#### Find Error Patterns
```bash
# Recent errors
grep -i "error\|exception\|fail" logs/*.log | tail -50

# Authentication failures
grep "401\|Invalid\|Authentication failed" logs/central_api.log

# Rate limiting events
grep "Rate limit\|blocked\|429" logs/central_api.log
```

#### Parse Logs by Time
```bash
# Errors in last hour
awk -v date="$(date -d '1 hour ago' '+%Y-%m-%d %H')" '$0 ~ date' logs/central_api.log | grep -i error
```

### Centralized Logging (Optional)

For production, consider:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Loki + Grafana**
- **Papertrail** (SaaS)

---

## 🔔 Alerting Strategy

### Built-in Alerts

The system includes multi-channel alerting:

1. **Email Alerts** - Configure in Email Settings
2. **Telegram Alerts** - Configure bot token and chat ID
3. **Slack Alerts** - Configure webhook URL

### Default Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| CPU Usage | 80% | 90% |
| Memory Usage | 75% | 85% |
| Disk Usage | 80% | 90% |
| Server Offline | - | Immediate |

### Alert Configuration

Via Settings page or API:

```bash
# Update thresholds via API
curl -X POST http://localhost:9083/api/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cpu_warning_threshold": 80,
    "cpu_critical_threshold": 90,
    "memory_warning_threshold": 75,
    "memory_critical_threshold": 85,
    "disk_warning_threshold": 80,
    "disk_critical_threshold": 90
  }'
```

### Alert Escalation

1. **Level 1** - Warning alerts → Email
2. **Level 2** - Critical alerts → Email + Telegram/Slack
3. **Level 3** - Service down → All channels + SMS (external)

---

## 💾 Backup & Recovery

### Database Backup

#### Automated Daily Backup

```bash
#!/bin/bash
# /opt/server-monitor/scripts/backup.sh

BACKUP_DIR="/opt/server-monitor/backups"
DB_PATH="/opt/server-monitor/data/servers.db"
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp "$DB_PATH" "$BACKUP_DIR/servers_$TIMESTAMP.db"

# Compress backup
gzip "$BACKUP_DIR/servers_$TIMESTAMP.db"

# Remove old backups
find "$BACKUP_DIR" -name "servers_*.db.gz" -mtime +$RETENTION_DAYS -delete

echo "[$(date)] Backup completed: servers_$TIMESTAMP.db.gz"
```

Schedule in cron:
```bash
# Daily backup at 2 AM
0 2 * * * /opt/server-monitor/scripts/backup.sh >> /var/log/server-monitor-backup.log 2>&1
```

#### Manual Backup

```bash
# Quick backup
cp data/servers.db data/servers.db.backup.$(date +%Y%m%d)
```

### Recovery Procedure

```bash
# 1. Stop services
./stop-all.sh

# 2. Restore database
gunzip backups/servers_20260107_020000.db.gz
cp backups/servers_20260107_020000.db data/servers.db

# 3. Verify database integrity
sqlite3 data/servers.db "PRAGMA integrity_check;"

# 4. Restart services
./start-all.sh

# 5. Verify functionality
curl http://localhost:9083/api/stats/overview
```

### Configuration Backup

```bash
# Backup configuration files
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
  .env \
  services/*.service \
  backend/requirements.txt
```

---

## 🔧 Maintenance Workflow

### Regular Maintenance Tasks

#### Daily
- [ ] Review error logs
- [ ] Check service health
- [ ] Verify backup completed

#### Weekly
- [ ] Review security alerts
- [ ] Check disk space
- [ ] Review rate limiting stats
- [ ] Clean up old sessions

#### Monthly
- [ ] Update dependencies (security patches)
- [ ] Review and rotate logs
- [ ] Test backup restoration
- [ ] Security audit review
- [ ] Performance review

### Session Cleanup

The system auto-cleans expired sessions on startup. Manual cleanup:

```bash
cd backend
python3 -c "
import database
result = database.cleanup_expired_sessions(days=7)
print(f'Cleaned up {result[\"deleted\"]} expired sessions')
"
```

### Database Maintenance

```bash
# Vacuum database (reclaim space)
sqlite3 data/servers.db "VACUUM;"

# Check integrity
sqlite3 data/servers.db "PRAGMA integrity_check;"

# Show table sizes
sqlite3 data/servers.db "
SELECT name, 
       (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=t.name) 
FROM sqlite_master t WHERE type='table';
"
```

### Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update specific package (test first!)
pip install --upgrade package-name

# Update all (CAUTION: test in staging first)
pip install --upgrade -r backend/requirements.txt
```

---

## 🚨 Incident Response

### Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| P1 - Critical | Service completely down | < 15 minutes |
| P2 - Major | Core feature broken | < 1 hour |
| P3 - Minor | Non-critical issue | < 4 hours |
| P4 - Low | Cosmetic/minor | Next business day |

### Incident Workflow

1. **Detect** - Alert received or issue reported
2. **Assess** - Determine severity and impact
3. **Communicate** - Notify stakeholders
4. **Respond** - Apply fix or workaround
5. **Resolve** - Verify fix and close incident
6. **Review** - Post-mortem analysis

### Common Issues and Fixes

#### API Not Responding
```bash
# Check if process is running
pgrep -f central_api.py

# Check port availability
netstat -tlnp | grep 9083

# Restart API
./stop-all.sh && ./start-all.sh

# Check logs for errors
tail -100 logs/central_api.log
```

#### Database Locked
```bash
# Stop all services
./stop-all.sh

# Check for zombie processes
ps aux | grep python | grep server-monitor

# Kill if needed
pkill -f central_api.py

# Restart
./start-all.sh
```

#### High Memory Usage
```bash
# Check memory usage
free -h

# Restart services to free memory
./stop-all.sh && ./start-all.sh

# Consider adding swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## ⚡ Performance Tuning

### Optimize for Scale

#### Database Indexes
```sql
-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_servers_status ON servers(status);
CREATE INDEX IF NOT EXISTS idx_alerts_server_id ON alerts(server_id);
CREATE INDEX IF NOT EXISTS idx_monitoring_history_server ON monitoring_history(server_id, timestamp);
```

#### Connection Limits
If monitoring many servers, adjust in `ssh_manager.py`:
```python
MAX_CONNECTIONS = 100  # Increase from default
CONNECTION_TIMEOUT = 30  # Adjust timeout
```

### Caching (Future)

For high-traffic deployments, consider Redis caching:
```python
# Example (planned for v1.2)
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)

def get_server_stats(server_id):
    cached = cache.get(f"stats:{server_id}")
    if cached:
        return json.loads(cached)
    # ... fetch from database
```

---

## 📞 Support

For issues:
1. Check logs in `logs/` directory
2. Review [TROUBLESHOOTING section](DEPLOYMENT.md#troubleshooting)
3. Open issue on [GitHub](https://github.com/minhtuancn/server-monitor/issues)

**Contact:**
- 📧 Email: [vietkeynet@gmail.com](mailto:vietkeynet@gmail.com)
- 🐙 GitHub: [@minhtuancn](https://github.com/minhtuancn)

---

**Last Updated:** 2026-01-07
