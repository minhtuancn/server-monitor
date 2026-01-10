# Upgrade & Rollback Guide

Version upgrade procedures and rollback strategies for Server Monitor.

**Last Updated**: 2026-01-09

---

## Before You Upgrade

### Pre-Upgrade Checklist

- [ ] **Read release notes**

  - Check [RELEASE_NOTES_vX.X.X.md](../product/) for breaking changes
  - Review upgrade notes for your specific version

- [ ] **Backup everything**

  ```bash
  ./scripts/backup.sh
  # Verify backup created in backups/
  ```

- [ ] **Check system requirements**

  - Python 3.8+ (`python3 --version`)
  - Node.js 18+ (`node --version`)
  - Disk space >1GB free (`df -h`)

- [ ] **Test in staging first** (if available)

  - Deploy to staging environment
  - Run smoke tests
  - Verify critical functionality

- [ ] **Schedule maintenance window**
  - Notify users of downtime
  - Choose low-traffic period
  - Allow 30-60 minutes for upgrade

---

## Upgrade Methods

### Method 1: Git Pull (Recommended)

**For**: Installations from Git repository

```bash
# 1. Backup first
./scripts/backup.sh

# 2. Stop services
./stop-all.sh

# 3. Pull latest code
git fetch origin
git pull origin main

# 4. Check for database migrations
cd backend
python3 -m migrations.check

# 5. Run migrations (if needed)
python3 -m migrations.run

# 6. Update dependencies
pip install -r requirements.txt

cd ../frontend-next
npm install

# 7. Rebuild frontend
npm run build

# 8. Start services
cd ..
./start-all.sh

# 9. Verify
curl http://localhost:9083/api/health
```

---

### Method 2: Download Release

**For**: Fresh installations from release tarball

```bash
# 1. Backup first
./scripts/backup.sh

# 2. Stop services
./stop-all.sh

# 3. Download new version
wget https://github.com/minhtuancn/server-monitor/archive/refs/tags/v2.4.0.tar.gz

# 4. Extract
tar -xzf v2.4.0.tar.gz

# 5. Preserve data & config
cp -r server-monitor-old/data server-monitor-2.4.0/
cp server-monitor-old/backend/.env server-monitor-2.4.0/backend/
cp server-monitor-old/frontend-next/.env.local server-monitor-2.4.0/frontend-next/

# 6. Install dependencies
cd server-monitor-2.4.0/backend
pip install -r requirements.txt
python3 -m migrations.run  # If migrations exist

cd ../frontend-next
npm install
npm run build

# 7. Start services
cd ..
./start-all.sh
```

---

### Method 3: In-Place Script (Production)

**For**: systemd service installations

```bash
# 1. Run upgrade script
sudo /opt/server-monitor/scripts/upgrade.sh v2.4.0

# Script does:
# - Backs up data
# - Stops services
# - Updates code
# - Runs migrations
# - Restarts services
```

---

## Version-Specific Upgrades

### v2.3.x → v2.4.0

**Breaking Changes**:

- Setup wizard replaces default admin (see [RELEASE_NOTES_v2.4.0.md](../product/RELEASE_NOTES_v2.4.0.md))

**Migration Required**: No

**Steps**:

```bash
git pull origin main
pip install -r backend/requirements.txt
npm install --prefix frontend-next
./stop-all.sh && ./start-all.sh
```

**Verify**:

- Login works with existing credentials
- Setup wizard only shows for fresh installs

---

### v2.2.x → v2.3.0

**Breaking Changes**:

- CORS configuration moved to .env (was hardcoded)

**Migration Required**: Yes (`backend/migrations/003_cors_config.py`)

**Steps**:

```bash
git pull origin main
pip install -r backend/requirements.txt

# Run migration
cd backend
python3 -m migrations.run

# Add CORS config to .env
echo "ALLOWED_FRONTEND_DOMAINS=localhost:9081,mon.yourdomain.com" >> .env

cd ..
./stop-all.sh && ./start-all.sh
```

**Verify**:

- Dashboard loads from allowed domains
- CORS errors gone

---

### v2.1.x → v2.2.0

**Breaking Changes**:

- Database schema change (new `audit_logs` table)

**Migration Required**: Yes (`backend/migrations/002_audit_logs.py`)

**Steps**:

```bash
git pull origin main
pip install -r backend/requirements.txt

# Run migration
cd backend
python3 -m migrations.run

cd ..
./stop-all.sh && ./start-all.sh
```

**Verify**:

```bash
sqlite3 data/servers.db "SELECT COUNT(*) FROM audit_logs;"
# Should return 0 (empty table)
```

---

## Database Migrations

### Check for Pending Migrations

```bash
cd backend
python3 -m migrations.check

# Output:
# Pending migrations: 002_audit_logs.py, 003_cors_config.py
```

---

### Run Migrations

```bash
cd backend
python3 -m migrations.run

# Output:
# Running migration: 002_audit_logs.py... OK
# Running migration: 003_cors_config.py... OK
```

---

### Manual Migration (if script fails)

```bash
# Apply SQL directly
sqlite3 data/servers.db < backend/migrations/002_audit_logs.sql

# Verify
sqlite3 data/servers.db ".schema audit_logs"
```

---

### Skip Migration (dangerous!)

```bash
# Mark migration as applied (without running)
cd backend
python3 -m migrations.mark_applied 002_audit_logs

# Use only if:
# - Migration already manually applied
# - Migration not applicable to your setup
```

---

## Rollback Procedures

### Rollback from Backup

**When**: Upgrade failed, data corrupted, major issues

```bash
# 1. Stop services
./stop-all.sh

# 2. Restore backup
./scripts/restore.sh backups/server-monitor-backup-20260109.tar.gz

# 3. Start services
./start-all.sh

# 4. Verify
curl http://localhost:9083/api/health
```

---

### Rollback to Previous Git Version

**When**: Upgrade succeeded but new version has issues

```bash
# 1. Stop services
./stop-all.sh

# 2. Revert to previous version
git log --oneline  # Find previous commit
git checkout <commit-hash>

# 3. Rollback migrations (if needed)
cd backend
python3 -m migrations.rollback  # Reverts last migration

# 4. Rebuild frontend
cd ../frontend-next
npm install
npm run build

# 5. Start services
cd ..
./start-all.sh
```

---

### Rollback Migration Only

**When**: Migration caused issues but code is OK

```bash
# 1. Stop services
./stop-all.sh

# 2. Rollback specific migration
cd backend
python3 -m migrations.rollback 002_audit_logs

# Or rollback last migration
python3 -m migrations.rollback

# 3. Restart
cd ..
./start-all.sh
```

---

### Emergency Rollback (systemd)

**When**: Production system down, need immediate rollback

```bash
# 1. Stop service
sudo systemctl stop server-monitor

# 2. Restore from backup
sudo tar -xzf /backups/server-monitor-backup-20260109.tar.gz -C /opt/

# 3. Restart service
sudo systemctl start server-monitor

# 4. Verify
sudo systemctl status server-monitor
```

---

## Testing After Upgrade

### Smoke Test Checklist

- [ ] **Services running**

  ```bash
  lsof -i:9081,9083,9084,9085
  # Should show 4 processes
  ```

- [ ] **Login works**

  - Go to http://localhost:9081
  - Login with existing credentials
  - Redirects to dashboard

- [ ] **Dashboard loads**

  - Servers list visible
  - Metrics updating every 3 seconds
  - No console errors (F12)

- [ ] **API functional**

  ```bash
  curl -H "Authorization: Bearer $TOKEN" http://localhost:9083/api/servers
  # Should return server list
  ```

- [ ] **WebSocket connected**

  ```bash
  wscat -c ws://localhost:9085/ws/monitoring
  # Should connect without errors
  ```

- [ ] **Terminal works** (if configured)

  - Go to Terminal page
  - Connect to a server
  - Run command: `df -h`

- [ ] **Database intact**
  ```bash
  sqlite3 data/servers.db "SELECT COUNT(*) FROM users;"
  sqlite3 data/servers.db "SELECT COUNT(*) FROM servers;"
  # Should match pre-upgrade counts
  ```

---

### Full Test Suite

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend build test
cd ../frontend-next
npm run lint
npm run build

# Integration test
./scripts/smoke-test.sh
```

---

## Downtime Minimization

### Blue-Green Deployment

**Setup**:

1. Two environments: Blue (production), Green (staging)
2. Upgrade Green environment
3. Test thoroughly
4. Switch traffic to Green
5. Keep Blue as rollback

**Switch traffic** (Nginx):

```nginx
# /etc/nginx/sites-available/server-monitor
upstream backend {
    server 127.0.0.1:9083;  # Blue
    # server 127.0.0.1:9183;  # Green (uncomment to switch)
}
```

---

### Rolling Restart (Multi-Instance)

**For**: Multiple backend instances behind load balancer

```bash
# Restart instances one by one
for instance in backend-1 backend-2 backend-3; do
    ssh $instance "systemctl stop server-monitor"
    ssh $instance "git pull && systemctl start server-monitor"
    sleep 30  # Wait for health check
done
```

---

## Upgrade Automation

### Automated Upgrade Script

```bash
#!/bin/bash
# scripts/upgrade.sh

VERSION=$1  # e.g., v2.4.0

# Validate input
if [ -z "$VERSION" ]; then
    echo "Usage: ./upgrade.sh <version>"
    exit 1
fi

# Backup
echo "Creating backup..."
./scripts/backup.sh

# Stop services
echo "Stopping services..."
./stop-all.sh

# Update code
echo "Updating to $VERSION..."
git fetch origin
git checkout tags/$VERSION

# Run migrations
echo "Running migrations..."
cd backend && python3 -m migrations.run

# Update dependencies
echo "Updating dependencies..."
pip install -r requirements.txt
cd ../frontend-next && npm install && npm run build

# Start services
echo "Starting services..."
cd .. && ./start-all.sh

# Health check
sleep 10
if curl -f http://localhost:9083/api/health; then
    echo "✅ Upgrade successful!"
else
    echo "❌ Health check failed! Rolling back..."
    ./scripts/rollback.sh
fi
```

**Usage**:

```bash
./scripts/upgrade.sh v2.4.0
```

---

## Troubleshooting Upgrades

### "Migration failed: syntax error"

**Cause**: SQL syntax incompatible with SQLite version

**Solution**:

```bash
# Check SQLite version
sqlite3 --version  # Should be 3.35+

# Upgrade SQLite if needed
sudo apt update
sudo apt install sqlite3
```

---

### "Module not found" after upgrade

**Cause**: New dependencies not installed

**Solution**:

```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend-next && rm -rf node_modules && npm install
```

---

### "Database locked" during migration

**Cause**: Services still running or stale lock

**Solution**:

```bash
# Stop all services
./stop-all.sh

# Wait 5 seconds
sleep 5

# Remove stale lock (if exists)
rm data/servers.db-wal data/servers.db-shm

# Retry migration
cd backend && python3 -m migrations.run
```

---

### Frontend build fails

**Cause**: Node.js version too old or cache issue

**Solution**:

```bash
cd frontend-next

# Check Node.js version
node --version  # Should be 18+

# Clear cache
rm -rf .next node_modules package-lock.json

# Reinstall
npm install
npm run build
```

---

### "JWT token invalid" after upgrade

**Cause**: JWT secret changed or token format changed

**Solution**:

```bash
# Check JWT_SECRET in .env
grep JWT_SECRET backend/.env

# If missing or changed, regenerate
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))" >> backend/.env

# All users must re-login
```

---

## Resources

- [Release Notes](../product/) — Version-specific changes
- [Backup Guide](BACKUP_RESTORE.md) — Backup procedures
- [Troubleshooting](../getting-started/TROUBLESHOOTING.md) — Common issues
- [Deployment Guide](docs/operations/DEPLOYMENT.md) — Production setup
- [Changelog](../../CHANGELOG.md) — All changes

---

**Upgrade issues?** [Open an issue](https://github.com/minhtuancn/server-monitor/issues) with tag `upgrade`.
