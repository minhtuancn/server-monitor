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

**For installer-based systems (systemd with journald):**
```bash
# View logs
sudo journalctl -u server-monitor-api -f
sudo journalctl -u server-monitor-ws -f
sudo journalctl -u server-monitor-terminal -f
sudo journalctl -u server-monitor-frontend -f

# All services
sudo journalctl -u 'server-monitor-*' -f

# Last 100 lines
sudo journalctl -u server-monitor-api -n 100

# Logs since yesterday
sudo journalctl -u server-monitor-api --since yesterday

# Logs with priority (errors only)
sudo journalctl -u server-monitor-api -p err
```

**For manual installations:**
```
<install-dir>/logs/
├── central_api.log      # API requests and responses
├── websocket.log        # WebSocket connections
├── terminal.log         # SSH terminal sessions
└── web.log              # Frontend HTTP server
```

### Log Rotation

**For systemd/journald (installer-based):**

Journald automatically rotates logs. Configure limits in `/etc/systemd/journald.conf`:

```ini
[Journal]
# Limit journal size to 500MB
SystemMaxUse=500M

# Keep 1 month of logs
MaxRetentionSec=1month

# Compress logs older than 1 day
MaxFileSec=1day

# Forward to syslog if needed
ForwardToSyslog=no

# Store on disk
Storage=persistent
```

Apply changes:
```bash
sudo systemctl restart systemd-journald
```

**Check current journal usage:**
```bash
# Show disk usage
sudo journalctl --disk-usage

# Show current limits
sudo journalctl --header
```

**Manually clean old logs:**
```bash
# Remove logs older than 2 weeks
sudo journalctl --vacuum-time=2weeks

# Keep only 200MB of logs
sudo journalctl --vacuum-size=200M

# Verify journal integrity
sudo journalctl --verify
```

### Request-ID Based Log Querying

Server Monitor v2.2.0+ includes request correlation via `X-Request-Id` headers. Use these IDs to trace requests across all services.

**Query logs by Request-ID:**
```bash
# Find all logs for a specific request
REQUEST_ID="req_abc123def456"
sudo journalctl -u 'server-monitor-*' --since "1 hour ago" | grep "$REQUEST_ID"

# With JSON parsing (for structured logs)
sudo journalctl -u server-monitor-api -o json --since "1 hour ago" | \
  jq -r "select(.MESSAGE | contains(\"$REQUEST_ID\")) | .MESSAGE"

# Find error logs for a request
sudo journalctl -u server-monitor-api -p err --since "1 hour ago" | grep "$REQUEST_ID"
```

**Extract Request-ID from API response:**
```bash
# Make request and capture Request-ID
curl -i http://localhost:9083/api/servers 2>&1 | grep -i x-request-id

# Example output:
# x-request-id: req_1704672345_abc123
```

**Trace request flow:**
```bash
# 1. Extract Request-ID from response
REQUEST_ID=$(curl -s -i http://localhost:9083/api/servers | grep -i x-request-id | cut -d: -f2 | tr -d ' \r')

# 2. Find all logs for this request across services
sudo journalctl -u 'server-monitor-*' --since "5 minutes ago" | grep "$REQUEST_ID"

# 3. Check if request hit multiple services
for service in api ws terminal frontend; do
  echo "=== server-monitor-$service ==="
  sudo journalctl -u "server-monitor-$service" --since "5 minutes ago" | grep "$REQUEST_ID" || echo "No logs found"
done
```

**Debug slow requests:**
```bash
# Find slow API requests (duration > 1000ms)
sudo journalctl -u server-monitor-api --since "1 hour ago" -o json | \
  jq -r 'select(.MESSAGE | contains("\"duration\":")) | 
         select(.MESSAGE | contains("duration") and 
                ((.MESSAGE | fromjson | .duration) > 1000)) | 
         .MESSAGE' | jq .

# Output structured logs with request details
sudo journalctl -u server-monitor-api -o json --since "1 hour ago" | \
  jq -r 'select(.MESSAGE | contains("request_id")) | 
         {time: .__REALTIME_TIMESTAMP, message: (.MESSAGE | fromjson)}'
```

**For manual installations:**

Create `/etc/logrotate.d/server-monitor`:

```
/opt/server-monitor/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 644 server-monitor server-monitor
    sharedscripts
    postrotate
        # Send HUP signal to processes to reopen log files
        pkill -HUP -f "python3.*central_api.py" || true
        pkill -HUP -f "python3.*websocket_server.py" || true
        pkill -HUP -f "python3.*terminal.py" || true
    endscript
}
```

Test log rotation:
```bash
sudo logrotate -f /etc/logrotate.d/server-monitor
```

### Log Analysis

#### Find Error Patterns

**With journald:**
```bash
# Recent errors
sudo journalctl -u 'server-monitor-*' -p err --since today

# Authentication failures
sudo journalctl -u server-monitor-api | grep -i "401\|Invalid\|Authentication failed"

# Rate limiting events
sudo journalctl -u server-monitor-api | grep -i "Rate limit\|blocked\|429"

# Export logs for analysis
sudo journalctl -u server-monitor-api --since "2026-01-07" > /tmp/api-logs.txt
```

**With file-based logs:**
```bash
# Recent errors
grep -i "error\|exception\|fail" logs/*.log | tail -50

# Authentication failures
grep "401\|Invalid\|Authentication failed" logs/central_api.log

# Rate limiting events
grep "Rate limit\|blocked\|429" logs/central_api.log
```

#### Parse Logs by Time

**With journald:**
```bash
# Errors in last hour
sudo journalctl -u server-monitor-api --since "1 hour ago" -p err

# Specific time range
sudo journalctl -u server-monitor-api --since "2026-01-07 10:00:00" --until "2026-01-07 11:00:00"
```

**With file-based logs:**
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

### SQLite Database Backup

The Server Monitor uses SQLite for data storage. Database files are located at:
- **Installer-based**: `/var/lib/server-monitor/servers.db`
- **Manual install**: `<install-dir>/data/servers.db`

#### Automated Backup (Installer-Based Systems)

For systems installed via the one-command installer:

```bash
# Manual backup
sudo smctl backup

# Backups are stored at: /var/lib/server-monitor/backups/
# Format: servers-YYYYmmdd-HHMMSS.db
```

**Automatic backup happens:**
- Before every update (`sudo smctl update`)
- When manually triggered (`sudo smctl backup`)

#### Automated Daily Backup Script

Create `/opt/server-monitor/scripts/backup-cron.sh`:

```bash
#!/bin/bash
# Automated SQLite backup script

BACKUP_DIR="/var/lib/server-monitor/backups"
DB_PATH="/var/lib/server-monitor/servers.db"
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup with timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/servers-$TIMESTAMP.db"

# Stop write operations briefly for consistent backup
systemctl stop server-monitor-api server-monitor-ws server-monitor-terminal

# Copy database
cp "$DB_PATH" "$BACKUP_FILE"

# Restart services
systemctl start server-monitor-api server-monitor-ws server-monitor-terminal

# Compress backup
gzip "$BACKUP_FILE"

# Set permissions
chown server-monitor:server-monitor "$BACKUP_FILE.gz"

# Remove old backups
find "$BACKUP_DIR" -name "servers-*.db.gz" -mtime +$RETENTION_DAYS -delete

echo "[$(date)] Backup completed: $BACKUP_FILE.gz"
```

Make it executable and schedule in cron:

```bash
sudo chmod +x /opt/server-monitor/scripts/backup-cron.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add line:
0 2 * * * /opt/server-monitor/scripts/backup-cron.sh >> /var/log/server-monitor-backup.log 2>&1
```

#### Manual Backup

**For installer-based systems:**
```bash
# Quick backup with smctl
sudo smctl backup

# Manual copy
sudo cp /var/lib/server-monitor/servers.db /tmp/servers.db.backup.$(date +%Y%m%d)
```

**For manual installations:**
```bash
# Stop services first for consistency
./stop-all.sh

# Backup database
cp data/servers.db data/servers.db.backup.$(date +%Y%m%d)

# Restart services
./start-all.sh
```

#### Export Data (Alternative Backup)

```bash
# Export as SQL dump
sqlite3 /var/lib/server-monitor/servers.db .dump > backup.sql

# Export specific tables
sqlite3 /var/lib/server-monitor/servers.db << EOF
.mode csv
.output servers_backup.csv
SELECT * FROM servers;
.output users_backup.csv
SELECT * FROM users;
EOF
```

### Audit Export Schedule

**Configure automated audit log exports** (v2.2.0+):

```bash
# Create audit export script
cat > /opt/server-monitor/scripts/audit-export.sh << 'EOF'
#!/bin/bash
# Automated audit log export

EXPORT_DIR="/var/lib/server-monitor/audit-exports"
API_URL="http://localhost:9083"
ADMIN_TOKEN="YOUR_ADMIN_TOKEN"  # Store securely, e.g., from vault
RETENTION_DAYS=90

mkdir -p "$EXPORT_DIR"

# Export to CSV
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$API_URL/api/export/audit/csv" > "$EXPORT_DIR/audit-$TIMESTAMP.csv"

# Export to JSON (for archival)
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$API_URL/api/export/audit/json" > "$EXPORT_DIR/audit-$TIMESTAMP.json"

# Compress exports
gzip "$EXPORT_DIR/audit-$TIMESTAMP.csv"
gzip "$EXPORT_DIR/audit-$TIMESTAMP.json"

# Remove old exports
find "$EXPORT_DIR" -name "audit-*.gz" -mtime +$RETENTION_DAYS -delete

echo "[$(date)] Audit export completed"
EOF

chmod +x /opt/server-monitor/scripts/audit-export.sh

# Schedule weekly audit exports (Sundays at 3 AM)
sudo crontab -e
# Add: 0 3 * * 0 /opt/server-monitor/scripts/audit-export.sh >> /var/log/audit-export.log 2>&1
```

**Export audit logs filtered by criteria:**
```bash
# Export last 30 days
curl -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/export/audit/csv?days=30" > audit-30days.csv

# Export specific user actions
curl -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/export/audit/json?user_id=123" > audit-user123.json

# Export specific action types
curl -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/export/audit/csv?action=login,logout" > audit-auth.csv
```

### Backup Best Practices

#### 1. Consistent Snapshots

**SQLite requires consistent snapshots.** Use one of these methods:

**Method A: Stop-copy-start (most reliable)**
```bash
#!/bin/bash
# Consistent backup with service stop

# Stop write services
systemctl stop server-monitor-api server-monitor-ws server-monitor-terminal

# Wait for writes to complete
sleep 2

# Backup database
cp /var/lib/server-monitor/servers.db /backup/servers-$(date +%Y%m%d).db

# Restart services
systemctl start server-monitor-api server-monitor-ws server-monitor-terminal
```

**Method B: SQLite backup command (no downtime)**
```bash
#!/bin/bash
# Online backup using SQLite3 backup API

sqlite3 /var/lib/server-monitor/servers.db << EOF
.backup /backup/servers-$(date +%Y%m%d).db
EOF
```

**Method C: Filesystem snapshot (if available)**
```bash
# LVM snapshot
lvcreate --size 1G --snapshot --name server-monitor-snap /dev/vg0/lv-data

# Mount and copy
mount /dev/vg0/server-monitor-snap /mnt/snap
cp /mnt/snap/servers.db /backup/servers-$(date +%Y%m%d).db
umount /mnt/snap
lvremove -f /dev/vg0/server-monitor-snap

# Or with ZFS
zfs snapshot tank/data@backup-$(date +%Y%m%d)
zfs send tank/data@backup-$(date +%Y%m%d) | gzip > /backup/zfs-backup.gz
```

#### 2. Backup Verification

**Always verify backups:**
```bash
#!/bin/bash
# Verify backup integrity

BACKUP_FILE="/backup/servers-20260107.db"

# Check SQLite integrity
if sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" | grep -q "ok"; then
  echo "✓ Backup integrity verified"
else
  echo "✗ Backup integrity check failed!"
  exit 1
fi

# Check file size (should be > 0)
SIZE=$(stat -c%s "$BACKUP_FILE")
if [ "$SIZE" -gt 0 ]; then
  echo "✓ Backup file size OK: $SIZE bytes"
else
  echo "✗ Backup file is empty!"
  exit 1
fi

# Check table counts
TABLE_COUNT=$(sqlite3 "$BACKUP_FILE" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
if [ "$TABLE_COUNT" -gt 5 ]; then
  echo "✓ Backup contains expected tables: $TABLE_COUNT"
else
  echo "✗ Backup has too few tables: $TABLE_COUNT"
  exit 1
fi
```

#### 3. Backup Retention Policy

**Recommended retention schedule:**

| Backup Type | Retention | Frequency |
|------------|-----------|-----------|
| Hourly     | 24 hours  | Every hour |
| Daily      | 30 days   | Daily at 2 AM |
| Weekly     | 90 days   | Sundays at 3 AM |
| Monthly    | 1 year    | 1st of month |
| Annual     | 3 years   | Jan 1st |

**Implement with backup script:**
```bash
#!/bin/bash
# Multi-tier backup retention

HOURLY_DIR="/backup/hourly"
DAILY_DIR="/backup/daily"
WEEKLY_DIR="/backup/weekly"
MONTHLY_DIR="/backup/monthly"

DB_PATH="/var/lib/server-monitor/servers.db"
BACKUP_FILE="servers-$(date +%Y%m%d-%H%M%S).db"

# Create directories
mkdir -p "$HOURLY_DIR" "$DAILY_DIR" "$WEEKLY_DIR" "$MONTHLY_DIR"

# Always create hourly backup
sqlite3 "$DB_PATH" ".backup $HOURLY_DIR/$BACKUP_FILE"

# Copy to daily if it's a new day
if [ $(date +%H) -eq 2 ]; then
  cp "$HOURLY_DIR/$BACKUP_FILE" "$DAILY_DIR/"
fi

# Copy to weekly if it's Sunday
if [ $(date +%u) -eq 7 ] && [ $(date +%H) -eq 3 ]; then
  cp "$HOURLY_DIR/$BACKUP_FILE" "$WEEKLY_DIR/"
fi

# Copy to monthly if it's 1st of month
if [ $(date +%d) -eq 01 ] && [ $(date +%H) -eq 3 ]; then
  cp "$HOURLY_DIR/$BACKUP_FILE" "$MONTHLY_DIR/"
fi

# Cleanup old backups
find "$HOURLY_DIR" -name "servers-*.db" -mmin +1440 -delete  # 24 hours
find "$DAILY_DIR" -name "servers-*.db" -mtime +30 -delete     # 30 days
find "$WEEKLY_DIR" -name "servers-*.db" -mtime +90 -delete    # 90 days
find "$MONTHLY_DIR" -name "servers-*.db" -mtime +365 -delete  # 1 year
```

#### 4. Off-Site Backups

**Configure off-site backup (recommended):**
```bash
# To AWS S3
aws s3 sync /backup/daily/ s3://my-bucket/server-monitor/backup/ \
  --storage-class STANDARD_IA

# To remote server via rsync
rsync -avz --delete /backup/daily/ backup-server:/backups/server-monitor/

# To another data center with encryption
tar czf - /backup/daily/ | \
  openssl enc -aes-256-cbc -salt -out - | \
  ssh backup-server "cat > /backups/server-monitor-$(date +%Y%m%d).tar.gz.enc"
```

### Database Restore

#### Using smctl (Recommended)

```bash
# List available backups
ls -lh /var/lib/server-monitor/backups/

# Restore from backup
sudo smctl restore /var/lib/server-monitor/backups/servers-20260107-120000.db

# The script will:
# 1. Confirm restoration
# 2. Stop affected services
# 3. Replace database file
# 4. Fix permissions
# 5. Restart services
```

#### Manual Restore

```bash
# 1. Stop all services
sudo systemctl stop server-monitor-api server-monitor-ws server-monitor-terminal server-monitor-frontend

# 2. Backup current database (just in case)
sudo cp /var/lib/server-monitor/servers.db /var/lib/server-monitor/servers.db.before-restore

# 3. Restore from backup
# If compressed:
sudo gunzip -c /var/lib/server-monitor/backups/servers-20260107-120000.db.gz > /var/lib/server-monitor/servers.db
# If not compressed:
sudo cp /var/lib/server-monitor/backups/servers-20260107-120000.db /var/lib/server-monitor/servers.db

# 4. Verify database integrity
sqlite3 /var/lib/server-monitor/servers.db "PRAGMA integrity_check;"
# Should output: ok

# 5. Fix permissions
sudo chown server-monitor:server-monitor /var/lib/server-monitor/servers.db
sudo chmod 644 /var/lib/server-monitor/servers.db

# 6. Restart services
sudo systemctl start server-monitor-api server-monitor-ws server-monitor-terminal server-monitor-frontend

# 7. Verify functionality
curl http://localhost:9083/api/stats/overview
```

#### Restore from SQL Dump

```bash
# Stop services
sudo systemctl stop server-monitor-*

# Remove old database
sudo rm /var/lib/server-monitor/servers.db

# Import SQL dump
sqlite3 /var/lib/server-monitor/servers.db < backup.sql

# Fix permissions
sudo chown server-monitor:server-monitor /var/lib/server-monitor/servers.db

# Restart services
sudo systemctl start server-monitor-*
```

### Configuration Backup

```bash
# Backup all configuration
sudo tar -czf /tmp/server-monitor-config-$(date +%Y%m%d).tar.gz \
  /etc/server-monitor/server-monitor.env \
  /opt/server-monitor/frontend-next/.env.local \
  /etc/systemd/system/server-monitor-*.service

# Restore configuration
sudo tar -xzf /tmp/server-monitor-config-20260107.tar.gz -C /
sudo systemctl daemon-reload
```

### Disaster Recovery

**Complete system backup:**

```bash
#!/bin/bash
# Full backup script

BACKUP_DIR="/backup/server-monitor/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Database
sudo cp /var/lib/server-monitor/servers.db "$BACKUP_DIR/"

# Configuration
sudo cp /etc/server-monitor/server-monitor.env "$BACKUP_DIR/"
sudo cp /opt/server-monitor/frontend-next/.env.local "$BACKUP_DIR/"

# Service files
sudo cp /etc/systemd/system/server-monitor-*.service "$BACKUP_DIR/"

# Create archive
tar -czf "/backup/server-monitor-full-$(date +%Y%m%d).tar.gz" "$BACKUP_DIR"

echo "Full backup completed: server-monitor-full-$(date +%Y%m%d).tar.gz"
```

### Backup Best Practices

1. **Schedule regular backups** - Daily at minimum
2. **Test restores** - Monthly restore test to verify backup integrity
3. **Off-site storage** - Copy backups to remote location or cloud storage
4. **Retention policy** - Keep 30 daily, 12 monthly, and yearly backups
5. **Monitor backup jobs** - Alert on failed backups
6. **Document procedures** - Keep restoration steps accessible

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
# From project root
python3 -c "
import sys
sys.path.insert(0, 'backend')
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
