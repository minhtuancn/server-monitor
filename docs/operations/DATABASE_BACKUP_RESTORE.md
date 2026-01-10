# Database Backup & Restore Guide

Complete guide for database backup, restore, and management operations.

## Overview

The Server Monitor system includes comprehensive database management tools:

- **Automated Backups**: Daily encrypted backups with retention policy
- **Manual Backups**: On-demand backup creation via API or script
- **Restore Operations**: Safe restore with pre-restore backups
- **Health Monitoring**: Database integrity checks and metrics
- **Storage Management**: Track backup sizes and storage usage

## Quick Start

### Create Manual Backup

```bash
cd /opt/server-monitor
./scripts/backup-database.sh backup
```

### List Available Backups

```bash
./scripts/backup-database.sh list
```

### Restore from Backup

Interactive mode:

```bash
./scripts/restore-database.sh interactive
```

Non-interactive mode:

```bash
./scripts/restore-database.sh restore servers_db_20260110_012354.db.gpg
```

### Setup Automated Backups

```bash
./scripts/setup-backup-automation.sh
```

This creates a cron job that runs daily at 2:00 AM.

## Backup System

### Backup Script Features

Located at: `/opt/server-monitor/scripts/backup-database.sh`

Features:

- **GPG Encryption**: AES256 symmetric encryption with passphrase
- **Metadata Tracking**: JSON metadata with checksum, size, timestamp
- **Integrity Verification**: SHA256 checksums for backup validation
- **Retention Policy**: Automatic cleanup of old backups (7 days)
- **Logging**: All operations logged to `logs/backup.log`

### Backup File Structure

```
data/backups/
├── servers_db_20260110_012354.db.gpg  # Encrypted backup
├── servers_db_20260110_012354.db.meta # Metadata JSON
└── prerestore_20260110_015530.db      # Pre-restore backup (if any)
```

### Metadata Format

```json
{
  "backup_name": "servers_db_20260110_012354.db",
  "timestamp": "2026-01-10T01:23:54+00:00",
  "size_bytes": 225280,
  "checksum_sha256": "75701fd08e780c56fe827ec0682d49c68b00477aa45284f0ef772015e0514612",
  "database_path": "/opt/server-monitor/data/servers.db",
  "encrypted": true
}
```

### Encryption Passphrase

Default passphrase: `ServerMonitorBackup2026`

To use custom passphrase:

```bash
export DB_BACKUP_PASSPHRASE="YourSecurePassphrase"
./scripts/backup-database.sh backup
```

**Important**: Store passphrase securely! Backups cannot be restored without it.

## Restore System

### Restore Script Features

Located at: `/opt/server-monitor/scripts/restore-database.sh`

Features:

- **Pre-Restore Backup**: Automatically creates backup before restoring
- **Checksum Verification**: Validates backup integrity before restore
- **SQLite Integrity Check**: Ensures restored database is valid
- **Automatic Rollback**: Reverts to pre-restore backup if restore fails
- **Service Management**: Stops services during restore

### Restore Process

1. **Select Backup**: Choose from available backups
2. **Decrypt**: Decrypt GPG-encrypted backup file
3. **Verify Integrity**: Check checksum and SQLite integrity
4. **Pre-Restore Backup**: Create safety backup of current database
5. **Stop Services**: Halt API server to prevent corruption
6. **Restore**: Replace database with backup
7. **Validate**: Verify restored database integrity
8. **Restart**: Manual service restart required

### Restore Safety

- Always creates pre-restore backup
- Automatic rollback on failure
- Validates database integrity before finalizing
- Logs all operations

## API Endpoints

All database management endpoints require admin authentication.

### Health Check

```http
GET /api/database/health
```

Response:

```json
{
  "healthy": true,
  "integrity_check": "passed",
  "size": 225280,
  "size_human": "220.00 KB",
  "tables": 15,
  "table_details": [
    { "name": "servers", "rows": 5 },
    { "name": "users", "rows": 2 }
  ],
  "page_count": 56,
  "page_size": 4096,
  "foreign_key_errors": 0,
  "last_checked": "2026-01-10T01:30:00Z"
}
```

### List Backups

```http
GET /api/database/backups
```

Response:

```json
{
  "backups": [
    {
      "filename": "servers_db_20260110_012354.db.gpg",
      "path": "/opt/server-monitor/data/backups/servers_db_20260110_012354.db.gpg",
      "size": 5529,
      "size_human": "5.40 KB",
      "created_at": "2026-01-10T01:23:56",
      "encrypted": true,
      "checksum": "75701fd08e780c56fe827ec0682d49c68b00477aa45284f0ef772015e0514612"
    }
  ],
  "count": 1
}
```

### Create Manual Backup

```http
POST /api/database/backup
Authorization: Bearer <token>
```

Response:

```json
{
  "success": true,
  "message": "Backup created successfully",
  "backup": {
    "filename": "servers_db_20260110_013045.db.gpg",
    "size": 5529,
    "size_human": "5.40 KB",
    "created_at": "2026-01-10T01:30:45"
  }
}
```

### Restore Backup

```http
POST /api/database/restore
Authorization: Bearer <token>
Content-Type: application/json

{
  "filename": "servers_db_20260110_012354.db.gpg"
}
```

Response:

```json
{
  "success": true,
  "message": "Database restored successfully",
  "warning": "Please restart services for changes to take effect"
}
```

### Delete Backup

```http
DELETE /api/database/backups/{filename}
Authorization: Bearer <token>
```

Response:

```json
{
  "success": true,
  "message": "Backup deleted: servers_db_20260110_012354.db.gpg"
}
```

### Storage Statistics

```http
GET /api/database/storage
Authorization: Bearer <token>
```

Response:

```json
{
  "database": {
    "size": 225280,
    "size_human": "220.00 KB"
  },
  "backups": {
    "count": 5,
    "total_size": 27645,
    "size_human": "27.00 KB",
    "average_size": 5529
  },
  "data_directory": {
    "total_size": 252925,
    "size_human": "247.00 KB"
  }
}
```

## Retention Policy

### Current Settings

- **Daily Backups**: Keep last 7 days
- **Weekly Backups**: Keep last 4 weeks (planned)
- **Monthly Backups**: Keep last 12 months (planned)

### Cleanup Process

Automatic cleanup runs after each backup:

- Identifies backups older than retention period
- Deletes old backup files and metadata
- Logs deletion operations

### Manual Cleanup

```bash
# Delete backups older than 7 days
find /opt/server-monitor/data/backups -name "servers_db_*.db.gpg" -mtime +7 -delete
find /opt/server-monitor/data/backups -name "servers_db_*.meta" -mtime +7 -delete
```

## Troubleshooting

### Backup Issues

**GPG not found**:

```bash
# Install GPG
sudo apt-get install gnupg
```

**Permission denied**:

```bash
# Fix permissions
chmod +x /opt/server-monitor/scripts/backup-database.sh
chmod 755 /opt/server-monitor/data/backups
```

**Backup timeout**:

- Check if database is locked by another process
- Verify sufficient disk space
- Review logs: `tail -f logs/backup.log`

### Restore Issues

**Wrong passphrase**:

- Verify passphrase matches the one used during backup
- Check if `DB_BACKUP_PASSPHRASE` environment variable is set correctly

**Integrity check failed**:

- Backup file may be corrupted
- Try restoring from a different backup
- Check logs for specific error messages

**Rollback occurred**:

- Restored database failed integrity check
- Pre-restore backup is automatically restored
- Check `logs/restore.log` for details

### Database Health Issues

**Foreign key errors**:

```bash
# Check foreign key violations
sqlite3 data/servers.db "PRAGMA foreign_key_check"
```

**Integrity check failed**:

```bash
# Check database integrity
sqlite3 data/servers.db "PRAGMA integrity_check"
```

**Database locked**:

- Stop all services: `./stop-all.sh`
- Wait 5 seconds
- Retry backup/restore operation

## Best Practices

### Regular Backups

1. **Daily Automated**: Let cron handle daily backups
2. **Before Major Changes**: Manual backup before upgrades
3. **Test Restores**: Periodically test restore process
4. **Monitor Logs**: Check backup logs regularly

### Security

1. **Secure Passphrase**: Use strong, unique passphrase
2. **Passphrase Storage**: Store securely (password manager, vault)
3. **Backup Location**: Consider off-site backup storage
4. **Access Control**: Restrict backup directory permissions

### Monitoring

1. **Check Health**: Monitor database health endpoint
2. **Storage Usage**: Track backup storage consumption
3. **Backup Success**: Verify daily backups complete successfully
4. **Log Review**: Review backup/restore logs weekly

### Disaster Recovery

1. **Document Process**: Keep restore procedures accessible
2. **Test Recovery**: Test full restore process quarterly
3. **Multiple Backups**: Keep multiple backup copies
4. **Off-Site Storage**: Store copies in different location

## Advanced Features

### Custom Retention Policy

Edit `/opt/server-monitor/scripts/backup-database.sh`:

```bash
RETENTION_DAYS=7      # Change to desired days
RETENTION_WEEKLY=4    # Weekly backups (planned)
RETENTION_MONTHLY=12  # Monthly backups (planned)
```

### Backup to Remote Location

Add to backup script:

```bash
# After backup creation
rsync -avz $BACKUP_DIR/ user@remote:/backups/server-monitor/
```

### Backup Verification Cron

Add separate cron job for verification:

```bash
0 3 * * * /opt/server-monitor/scripts/backup-database.sh verify $(ls -t /opt/server-monitor/data/backups/*.gpg | head -1)
```

## Reference

### File Locations

- **Backup Script**: `scripts/backup-database.sh`
- **Restore Script**: `scripts/restore-database.sh`
- **Automation Setup**: `scripts/setup-backup-automation.sh`
- **Database Manager**: `backend/database_manager.py`
- **Backups Directory**: `data/backups/`
- **Backup Log**: `logs/backup.log`
- **Restore Log**: `logs/restore.log`

### Command Reference

```bash
# Backup operations
./scripts/backup-database.sh backup   # Create backup
./scripts/backup-database.sh list     # List backups
./scripts/backup-database.sh verify <file>  # Verify backup

# Restore operations
./scripts/restore-database.sh interactive     # Interactive restore
./scripts/restore-database.sh list            # List backups
./scripts/restore-database.sh restore <file>  # Restore specific backup

# Automation
./scripts/setup-backup-automation.sh  # Setup cron job
crontab -l | grep backup              # View backup cron jobs
crontab -e                            # Edit cron jobs
```

### API Integration Examples

**JavaScript/TypeScript**:

```typescript
// Create backup
const response = await fetch("/api/database/backup", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});
const result = await response.json();

// List backups
const backups = await fetch("/api/database/backups", {
  headers: { Authorization: `Bearer ${token}` },
}).then((r) => r.json());
```

**Python**:

```python
import requests

# Create backup
response = requests.post(
    'http://localhost:9083/api/database/backup',
    headers={'Authorization': f'Bearer {token}'}
)

# List backups
backups = requests.get(
    'http://localhost:9083/api/database/backups',
    headers={'Authorization': f'Bearer {token}'}
).json()
```

## Support

For issues or questions:

- Check logs: `logs/backup.log`, `logs/restore.log`
- Review this documentation
- Check system health: `GET /api/database/health`
- Verify disk space: `df -h /opt/server-monitor/data`
