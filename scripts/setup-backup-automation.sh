#!/bin/bash
################################################################################
# Setup Automated Database Backups
# 
# Creates a cron job for daily database backups at 2 AM
################################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_SCRIPT="$PROJECT_ROOT/scripts/backup-database.sh"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "  Database Backup Automation Setup"
echo "========================================"
echo ""

# Check if backup script exists
if [[ ! -f "$BACKUP_SCRIPT" ]]; then
    echo "❌ Backup script not found: $BACKUP_SCRIPT"
    exit 1
fi

echo "✓ Backup script found: $BACKUP_SCRIPT"

# Create cron job entry
CRON_JOB="0 2 * * * $BACKUP_SCRIPT backup >> $PROJECT_ROOT/logs/backup.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -qF "$BACKUP_SCRIPT"; then
    echo ""
    echo -e "${YELLOW}⚠️  Backup cron job already exists${NC}"
    echo ""
    echo "Current cron jobs for database backup:"
    crontab -l | grep "$BACKUP_SCRIPT"
    echo ""
    read -p "Do you want to replace it? (yes/no): " replace
    
    if [[ "$replace" != "yes" ]]; then
        echo "Setup cancelled"
        exit 0
    fi
    
    # Remove old cron job
    (crontab -l 2>/dev/null | grep -vF "$BACKUP_SCRIPT") | crontab -
    echo "✓ Removed old cron job"
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo -e "${GREEN}✅ Backup automation configured successfully!${NC}"
echo ""
echo "Backup Schedule:"
echo "  • Time: 2:00 AM daily"
echo "  • Location: $PROJECT_ROOT/data/backups/"
echo "  • Retention: 7 daily backups"
echo "  • Log file: $PROJECT_ROOT/logs/backup.log"
echo ""
echo "Current cron jobs:"
crontab -l
echo ""
echo "To manually test the backup:"
echo "  $BACKUP_SCRIPT backup"
echo ""
echo "To view backup logs:"
echo "  tail -f $PROJECT_ROOT/logs/backup.log"
echo ""
echo "========================================"
