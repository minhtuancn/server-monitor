# Backup & Restore Guide

Database backup and restore procedures for Server Monitor.

**Last Updated**: 2026-01-09

---

## Quick Reference

```bash
# Backup
./scripts/backup.sh

# Restore
./scripts/restore.sh /path/to/backup.tar.gz

# Automated daily backups
crontab -e
# Add: 0 2 * * * /opt/server-monitor/scripts/backup.sh
```

---

## What Gets Backed Up

### Database (`data/servers.db`)

- User accounts and credentials
- Server configurations (hostname, SSH credentials)
- Server notes and custom fields
- Alert configurations and history
- Task history
- Audit logs

### SSH Keys (`data/ssh/`)

- Private keys for server connections
- Known hosts file

### Configuration (`backend/.env`)

- JWT secret
- Email/Telegram/Slack credentials
- Custom settings

### Logs (Optional)

- API logs (`logs/api.log`)
- WebSocket logs (`logs/websocket.log`)
- Terminal logs (`logs/terminal.log`)

---

## Backup Methods

### Method 1: Automated Script (Recommended)

```bash
# Manual backup
./scripts/backup.sh

# Output:
# Backup created: backups/server-monitor-backup-20260109-143022.tar.gz
```

**What it does**:

1. Stops services (to ensure database consistency)
2. Creates tarball of `data/`, `backend/.env`
3. Optionally includes logs
4. Saves to `backups/` directory
5. Restarts services

**Schedule automatic backups**:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/server-monitor/scripts/backup.sh

# Add weekly backup (Sundays at 3 AM)
0 3 * * 0 /opt/server-monitor/scripts/backup.sh --weekly
```

---

### Method 2: Manual Database Backup

```bash
# Stop services (important!)
./stop-all.sh

# Backup database
cp data/servers.db data/servers.db.backup-$(date +%Y%m%d)

# Or use SQLite backup command (safer)
sqlite3 data/servers.db ".backup /path/to/backup/servers.db"

# Restart services
./start-all.sh
```

---

### Method 3: Live Backup (No Downtime)

```bash
# SQLite online backup (safe while running)
sqlite3 data/servers.db "VACUUM INTO 'backups/servers-$(date +%Y%m%d).db'"

# Or use backup API (if implemented)
curl -X POST http://localhost:9083/api/admin/backup \
  -H "Authorization: Bearer $TOKEN" \
  -o backups/backup-$(date +%Y%m%d).tar.gz
```

**Warning**: Live backups may include incomplete transactions. Prefer stopped services for production backups.

---

## Backup Retention

### Default Policy

- **Daily backups**: Keep 7 days
- **Weekly backups**: Keep 4 weeks
- **Monthly backups**: Keep 12 months

### Cleanup Script

```bash
#!/bin/bash
# scripts/cleanup-old-backups.sh

BACKUP_DIR="/opt/server-monitor/backups"
DAILY_RETENTION=7
WEEKLY_RETENTION=28
MONTHLY_RETENTION=365

# Delete daily backups older than 7 days
find $BACKUP_DIR -name "server-monitor-backup-*.tar.gz" -mtime +$DAILY_RETENTION -delete

# Keep weekly backups (every Sunday)
# (More complex logic; see full script)
```

**Schedule cleanup**:

```bash
crontab -e
# Add: 0 4 * * * /opt/server-monitor/scripts/cleanup-old-backups.sh
```

---

## Restore Procedures

### Full Restore from Backup

```bash
# Stop services
./stop-all.sh

# Extract backup
tar -xzf backups/server-monitor-backup-20260109.tar.gz

# Restore database
cp data/servers.db data/servers.db.old  # Backup current
cp extracted/data/servers.db data/servers.db

# Restore SSH keys
cp -r extracted/data/ssh/* data/ssh/

# Restore configuration
cp extracted/backend/.env backend/.env

# Restart services
./start-all.sh
```

---

### Partial Restore (Database Only)

```bash
# Stop services
./stop-all.sh

# Backup current database
cp data/servers.db data/servers.db.before-restore

# Restore from backup
cp /path/to/backup/servers.db data/servers.db

# Restart services
./start-all.sh
```

---

### Restore from Corrupted Database

If database is corrupted:

```bash
# Try recovery first
sqlite3 data/servers.db ".recover" > recovered.sql
rm data/servers.db
sqlite3 data/servers.db < recovered.sql

# If recovery fails, restore from backup
cp /path/to/backup/servers.db data/servers.db

# If no backup, start fresh (data loss!)
rm data/servers.db
./start-all.sh  # Creates new empty database
```

---

## Remote Backups

### Option 1: rsync to Remote Server

```bash
# Sync backups to remote server
rsync -avz --delete \
  /opt/server-monitor/backups/ \
  user@backup-server:/backups/server-monitor/

# Add to backup script or crontab
```

---

### Option 2: S3/Cloud Storage

```bash
# Install AWS CLI
sudo apt install awscli

# Configure credentials
aws configure

# Upload backup
aws s3 cp backups/server-monitor-backup-20260109.tar.gz \
  s3://my-bucket/server-monitor/

# Automate in backup script
```

---

### Option 3: Git Backup (Config Only)

```bash
# Backup configuration to Git (NOT database!)
git add backend/.env data/ssh/*.pub
git commit -m "Backup config $(date +%Y%m%d)"
git push origin backup-branch

# NEVER commit:
# - data/servers.db (contains secrets)
# - data/ssh/*_rsa (private keys)
# - .env with secrets
```

---

## Testing Backups

### Backup Validation Checklist

1. **File integrity**:

   ```bash
   tar -tzf backups/server-monitor-backup-20260109.tar.gz
   # Should list all files without errors
   ```

2. **Database integrity**:

   ```bash
   sqlite3 backups/servers.db "PRAGMA integrity_check;"
   # Should return "ok"
   ```

3. **Restore test** (on test system):
   ```bash
   # Extract and start on test machine
   tar -xzf backup.tar.gz
   cd server-monitor
   ./start-all.sh
   # Verify login and data
   ```

---

## Disaster Recovery

### Complete System Loss

**Prerequisites**:

- Recent backup file
- Fresh server with same OS
- Backup of `.env` secrets

**Steps**:

```bash
# 1. Clone repository
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor

# 2. Run installer
./installer.sh

# 3. Stop services
./stop-all.sh

# 4. Restore backup
tar -xzf /path/to/backup.tar.gz
cp backup/data/servers.db data/servers.db
cp -r backup/data/ssh data/
cp backup/backend/.env backend/.env

# 5. Start services
./start-all.sh

# 6. Verify
curl http://localhost:9083/api/health
```

---

### Data Loss Scenarios

| Scenario               | Recovery                                              |
| ---------------------- | ----------------------------------------------------- |
| **Deleted server**     | Restore from backup (data/ folder)                    |
| **Lost user password** | Restore users table or reset password manually        |
| **Corrupt database**   | Try `.recover` command, else restore from backup      |
| **Lost SSH keys**      | Restore from backup or regenerate (re-add to servers) |
| **Lost .env secrets**  | Regenerate secrets (users must re-login)              |
| **Deleted logs**       | No recovery (not in backup by default)                |

---

## Backup Best Practices

### ✅ Do

- **Automate backups** (daily cron job)
- **Test restores** regularly (monthly)
- **Store offsite** (remote server, cloud)
- **Encrypt backups** (if stored remotely)
- **Monitor backup success** (check logs)
- **Keep multiple versions** (7 daily + 4 weekly)

### ❌ Don't

- **Don't commit secrets** to Git
- **Don't store backups on same disk** (RAID/disk failure)
- **Don't skip testing** (untested backups are useless)
- **Don't backup while running** (prefer stopped services)
- **Don't keep backups forever** (rotate old backups)

---

## Encryption (Optional)

### Encrypt Backup

```bash
# Encrypt with GPG
gpg --symmetric --cipher-algo AES256 \
  backups/server-monitor-backup-20260109.tar.gz

# Decrypt
gpg backups/server-monitor-backup-20260109.tar.gz.gpg
```

### Encrypt with Password

```bash
# Encrypt with openssl
openssl enc -aes-256-cbc -salt \
  -in backups/backup.tar.gz \
  -out backups/backup.tar.gz.enc

# Decrypt
openssl enc -d -aes-256-cbc \
  -in backups/backup.tar.gz.enc \
  -out backups/backup.tar.gz
```

---

## Monitoring Backups

### Backup Health Check

```bash
#!/bin/bash
# scripts/check-backups.sh

BACKUP_DIR="/opt/server-monitor/backups"
MAX_AGE=86400  # 24 hours in seconds

# Check latest backup age
LATEST=$(ls -t $BACKUP_DIR/*.tar.gz | head -1)
AGE=$(($(date +%s) - $(stat -c %Y "$LATEST")))

if [ $AGE -gt $MAX_AGE ]; then
  echo "ALERT: No recent backup! Latest is $AGE seconds old."
  # Send alert (email, Telegram, etc.)
fi
```

**Schedule check**:

```bash
crontab -e
# Add: 0 10 * * * /opt/server-monitor/scripts/check-backups.sh
```

---

## Resources

- [Deployment Guide](docs/operations/DEPLOYMENT.md) — Production setup
- [Operations Guide](LOGGING.md) — Log management
- [Security Guide](../security/PRODUCTION_SECURITY.md) — Production hardening
- [Upgrade Guide](UPGRADE_ROLLBACK.md) — Version upgrades

---

**Questions?** See [TROUBLESHOOTING.md](../getting-started/TROUBLESHOOTING.md) or [open an issue](https://github.com/minhtuancn/server-monitor/issues).
