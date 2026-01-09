# Logging Guide

Log management and monitoring for Server Monitor.

**Last Updated**: 2026-01-09

---

## Log Locations

All logs stored in `/opt/server-monitor/logs/`:

| Log File        | Purpose                        | Typical Size |
| --------------- | ------------------------------ | ------------ |
| `api.log`       | Backend API requests, errors   | ~100MB/week  |
| `websocket.log` | WebSocket connections, metrics | ~50MB/week   |
| `terminal.log`  | SSH terminal sessions          | ~20MB/week   |
| `web.log`       | Frontend Next.js logs          | ~30MB/week   |
| `installer.log` | Installation process           | ~1MB (once)  |

---

## Log Formats

### API Log (`api.log`)

```
2026-01-09 14:30:22 INFO [central_api.py:345] GET /api/servers 200 OK (12ms)
2026-01-09 14:30:25 ERROR [user_management.py:78] Failed login attempt for user 'admin' from 192.168.1.100
2026-01-09 14:30:30 INFO [ssh_manager.py:123] SSH connection established to server-01 (192.168.1.10)
```

**Fields**:

- Timestamp (ISO 8601)
- Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Source file and line number
- Message

---

### WebSocket Log (`websocket.log`)

```
2026-01-09 14:30:22 INFO [websocket_server.py:234] New connection from 192.168.1.100
2026-01-09 14:30:23 INFO [websocket_server.py:456] Subscribed to monitoring channel: server-01
2026-01-09 14:30:25 ERROR [websocket_server.py:567] Connection lost: Connection reset by peer
```

---

### Terminal Log (`terminal.log`)

```
2026-01-09 14:30:22 INFO [terminal.py:123] Terminal session started for server-01 by user admin
2026-01-09 14:30:30 INFO [terminal.py:234] Command executed: df -h
2026-01-09 14:31:00 INFO [terminal.py:345] Terminal session ended (duration: 38s)
```

**Security Note**: Terminal logs DO NOT contain command output (only command executed).

---

## Log Levels

### DEBUG (Verbose)

- Database queries
- Cache hits/misses
- Detailed WebSocket events
- **Use**: Development only

### INFO (Default)

- API requests (with status code)
- User logins/logouts
- Server connections
- Task executions
- **Use**: Production default

### WARNING

- Failed authentication attempts (not errors yet)
- Slow queries (>1s)
- Deprecated API usage
- **Use**: Potential issues

### ERROR

- Authentication failures (after retries)
- Database errors
- SSH connection failures
- **Use**: Issues requiring attention

### CRITICAL

- System crashes
- Database corruption
- Security incidents (brute force detected)
- **Use**: Immediate action required

---

## Configuration

### Backend Logging (`backend/observability.py`)

```python
import logging

# Set log level
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for verbose
    format='%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()  # Also print to console
    ]
)

# Per-module log levels
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)  # Quiet SQLAlchemy
logging.getLogger('websockets').setLevel(logging.INFO)
```

### Environment Variables

```bash
# backend/.env
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR | CRITICAL
LOG_TO_FILE=true
LOG_TO_CONSOLE=false  # Disable console logging in production
LOG_MAX_SIZE=100MB  # Rotate when file reaches 100MB
LOG_RETENTION_DAYS=30  # Delete logs older than 30 days
```

---

## Log Rotation

### Manual Rotation

```bash
# Compress old logs
cd /opt/server-monitor/logs
gzip api.log websocket.log terminal.log web.log

# Move to archive
mkdir -p archive/$(date +%Y%m)
mv *.gz archive/$(date +%Y%m)/

# Restart services to create new log files
./stop-all.sh && ./start-all.sh
```

---

### Automatic Rotation (logrotate)

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/server-monitor
```

**Configuration**:

```
/opt/server-monitor/logs/*.log {
    daily                # Rotate daily
    rotate 30            # Keep 30 days
    compress             # Compress old logs
    delaycompress        # Don't compress current day
    missingok            # OK if log missing
    notifempty           # Don't rotate empty logs
    create 644 server-monitor server-monitor  # Permissions for new logs
    sharedscripts
    postrotate
        # Restart services to release file handles
        /opt/server-monitor/stop-all.sh
        /opt/server-monitor/start-all.sh
    endscript
}
```

**Test rotation**:

```bash
sudo logrotate -f /etc/logrotate.d/server-monitor
```

---

## Monitoring Logs

### Real-Time Monitoring

```bash
# Tail all logs
tail -f logs/*.log

# Tail specific log
tail -f logs/api.log

# Follow multiple logs with color
multitail logs/api.log logs/websocket.log logs/terminal.log
```

---

### Search Logs

```bash
# Find errors in last hour
grep "ERROR" logs/api.log | tail -100

# Find failed logins
grep "Failed login" logs/api.log

# Find slow queries (>1s)
grep "SLOW QUERY" logs/api.log

# Count errors per hour
grep "ERROR" logs/api.log | cut -d' ' -f2 | cut -d: -f1 | sort | uniq -c
```

---

### Advanced Search (jq for JSON logs)

If logs are JSON format:

```bash
# Parse JSON logs
cat logs/api.log | jq 'select(.level=="ERROR")'

# Count errors by type
cat logs/api.log | jq -r '.error_type' | sort | uniq -c

# Filter by user
cat logs/api.log | jq 'select(.user=="admin")'
```

---

## Log Analysis

### Common Patterns

**Failed Login Attempts** (potential brute force):

```bash
grep "Failed login" logs/api.log | cut -d' ' -f8 | sort | uniq -c | sort -rn
# Output: Count of failed attempts per IP
```

**Slow API Endpoints**:

```bash
grep "SLOW" logs/api.log | awk '{print $6}' | sort | uniq -c | sort -rn
# Output: Slowest endpoints
```

**WebSocket Connection Churn**:

```bash
grep -c "New connection" logs/websocket.log
grep -c "Connection lost" logs/websocket.log
# Compare counts (should be similar)
```

**SSH Session Duration**:

```bash
grep "Terminal session ended" logs/terminal.log | awk '{print $9}' | sed 's/[()]//g'
# Output: Session durations
```

---

### Alerts

Set up alerts for critical patterns:

**Failed Login Alert**:

```bash
#!/bin/bash
# scripts/alert-failed-logins.sh

COUNT=$(grep "Failed login" logs/api.log | tail -100 | wc -l)

if [ $COUNT -gt 10 ]; then
  echo "ALERT: $COUNT failed logins in last 100 log lines!" | \
    mail -s "Security Alert" admin@example.com
fi
```

**Error Spike Alert**:

```bash
#!/bin/bash
# scripts/alert-error-spike.sh

ERRORS=$(grep "ERROR" logs/api.log | tail -1000 | wc -l)

if [ $ERRORS -gt 50 ]; then
  echo "ALERT: $ERRORS errors in last 1000 log lines!" | \
    mail -s "Error Spike" admin@example.com
fi
```

**Schedule alerts**:

```bash
crontab -e
# Add:
*/5 * * * * /opt/server-monitor/scripts/alert-failed-logins.sh
*/5 * * * * /opt/server-monitor/scripts/alert-error-spike.sh
```

---

## Log Aggregation

### Option 1: ELK Stack (Elasticsearch, Logstash, Kibana)

```bash
# Install Filebeat
sudo apt install filebeat

# Configure Filebeat
sudo nano /etc/filebeat/filebeat.yml
```

**Config**:

```yaml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /opt/server-monitor/logs/*.log

output.elasticsearch:
  hosts: ["localhost:9200"]

setup.kibana:
  host: "localhost:5601"
```

**Start Filebeat**:

```bash
sudo systemctl start filebeat
sudo systemctl enable filebeat
```

---

### Option 2: Grafana Loki

```bash
# Install Promtail (Loki agent)
wget https://github.com/grafana/loki/releases/download/v2.8.0/promtail-linux-amd64.zip
unzip promtail-linux-amd64.zip
sudo mv promtail-linux-amd64 /usr/local/bin/promtail

# Configure Promtail
sudo nano /etc/promtail.yml
```

**Config**:

```yaml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://localhost:3100/loki/api/v1/push

scrape_configs:
  - job_name: server-monitor
    static_configs:
      - targets:
          - localhost
        labels:
          job: server-monitor
          __path__: /opt/server-monitor/logs/*.log
```

---

### Option 3: Centralized Syslog

```bash
# Configure rsyslog to send logs to remote server
sudo nano /etc/rsyslog.d/server-monitor.conf
```

**Config**:

```
# Send all logs to remote syslog server
*.* @syslog-server.example.com:514
```

**Restart rsyslog**:

```bash
sudo systemctl restart rsyslog
```

---

## Disk Space Management

### Check Log Size

```bash
# Total log directory size
du -sh logs/

# Individual log sizes
du -sh logs/*.log | sort -h

# Growth rate (compare with yesterday)
du -sb logs/*.log > today.txt
du -sb logs_backup/*.log > yesterday.txt
diff yesterday.txt today.txt
```

---

### Automatic Cleanup

```bash
#!/bin/bash
# scripts/cleanup-old-logs.sh

LOG_DIR="/opt/server-monitor/logs"
RETENTION_DAYS=30

# Delete logs older than 30 days
find $LOG_DIR -name "*.log.gz" -mtime +$RETENTION_DAYS -delete
find $LOG_DIR/archive -name "*.log" -mtime +$RETENTION_DAYS -delete

echo "Cleaned up logs older than $RETENTION_DAYS days"
```

**Schedule cleanup**:

```bash
crontab -e
# Add: 0 3 * * * /opt/server-monitor/scripts/cleanup-old-logs.sh
```

---

## Debugging with Logs

### Step-by-Step Debug Process

1. **Reproduce issue**:

   ```bash
   # Clear logs first
   > logs/api.log

   # Enable DEBUG level
   LOG_LEVEL=DEBUG ./start-all.sh

   # Reproduce issue
   # ...
   ```

2. **Find relevant logs**:

   ```bash
   # Search for errors
   grep ERROR logs/api.log

   # Search for specific operation
   grep "create_server" logs/api.log
   ```

3. **Get context** (lines before/after error):

   ```bash
   grep -A 10 -B 10 "ERROR.*create_server" logs/api.log
   ```

4. **Correlate across services**:
   ```bash
   # Get timestamp from api.log
   # Search same timestamp in other logs
   grep "2026-01-09 14:30:22" logs/*.log
   ```

---

## Performance Monitoring

### Log Query Performance

```bash
# Benchmark log search
time grep "ERROR" logs/api.log

# If slow (>1s for 100MB log), consider:
# - Structured logging (JSON)
# - Log aggregation (ELK, Loki)
# - Indexed search (Elasticsearch)
```

---

### Log I/O Impact

```bash
# Check log write rate
iostat -x 1 10 | grep sda

# If high write I/O:
# - Reduce log level (INFO → WARNING)
# - Disable verbose modules
# - Use async logging
```

---

## Best Practices

### ✅ Do

- **Log all authentication events** (login, logout, failed attempts)
- **Log all critical actions** (delete server, change user role)
- **Include context** (user ID, IP, server ID)
- **Use consistent format** (parseable by tools)
- **Rotate logs regularly** (daily or by size)
- **Monitor log disk usage** (alert at 80% full)
- **Test log aggregation** (ensure logs flow to central system)

### ❌ Don't

- **Don't log passwords** (plain text or hashed)
- **Don't log credit cards** (PCI compliance)
- **Don't log PII** (personal data, unless required)
- **Don't log to console in production** (performance impact)
- **Don't keep logs forever** (GDPR, storage cost)
- **Don't ignore CRITICAL logs** (set up alerts)

---

## Resources

- [Backup Guide](BACKUP_RESTORE.md) — Backup procedures (includes logs)
- [Troubleshooting](../getting-started/TROUBLESHOOTING.md) — Using logs to debug
- [Security](../security/PRODUCTION_SECURITY.md) — Audit logging
- [Operations](UPGRADE_ROLLBACK.md) — Upgrade logs

---

**Questions?** See [docs/README.md](../README.md) or [open an issue](https://github.com/minhtuancn/server-monitor/issues).
