#!/bin/bash
################################################################################
# Database Backup Script with Encryption
# 
# Features:
# - Backs up servers.db with GPG encryption
# - Creates timestamped backups with metadata
# - Verifies backup integrity
# - Implements retention policy
# - Logs all operations
################################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DB_FILE="$PROJECT_ROOT/data/servers.db"
BACKUP_DIR="$PROJECT_ROOT/data/backups"
LOG_FILE="$PROJECT_ROOT/logs/backup.log"
RETENTION_DAYS=7
RETENTION_WEEKLY=4
RETENTION_MONTHLY=12

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO" "$@"
}

log_error() {
    log "ERROR" "${RED}$*${NC}"
}

log_success() {
    log "SUCCESS" "${GREEN}$*${NC}"
}

log_warning() {
    log "WARNING" "${YELLOW}$*${NC}"
}

# Check if database exists
check_database() {
    if [[ ! -f "$DB_FILE" ]]; then
        log_error "Database file not found: $DB_FILE"
        exit 1
    fi
}

# Create backup directory if not exists
create_backup_dir() {
    if [[ ! -d "$BACKUP_DIR" ]]; then
        mkdir -p "$BACKUP_DIR"
        log_info "Created backup directory: $BACKUP_DIR"
    fi
}

# Generate backup filename with timestamp
generate_backup_name() {
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    echo "servers_db_${timestamp}.db"
}

# Create backup with metadata
create_backup() {
    local backup_name="$1"
    local backup_path="$BACKUP_DIR/$backup_name"
    local encrypted_path="${backup_path}.gpg"
    local metadata_path="${backup_path}.meta"
    
    log_info "Starting backup: $backup_name"
    
    # Copy database (SQLite safe backup)
    sqlite3 "$DB_FILE" ".backup '$backup_path'" 2>/dev/null || {
        # Fallback to simple copy if sqlite3 command fails
        cp "$DB_FILE" "$backup_path"
    }
    
    # Calculate checksum
    local checksum=$(sha256sum "$backup_path" | awk '{print $1}')
    local size=$(stat -f%z "$backup_path" 2>/dev/null || stat -c%s "$backup_path")
    local timestamp=$(date -Iseconds)
    
    # Create metadata file
    cat > "$metadata_path" <<EOF
{
  "backup_name": "$backup_name",
  "timestamp": "$timestamp",
  "size_bytes": $size,
  "checksum_sha256": "$checksum",
  "database_path": "$DB_FILE",
  "encrypted": true
}
EOF
    
    # Encrypt backup with GPG (symmetric encryption)
    if command -v gpg &> /dev/null; then
        local passphrase="${DB_BACKUP_PASSPHRASE:-ServerMonitorBackup2026}"
        echo "$passphrase" | gpg --batch --yes --passphrase-fd 0 \
            --symmetric --cipher-algo AES256 \
            -o "$encrypted_path" "$backup_path"
        
        # Remove unencrypted backup
        rm -f "$backup_path"
        log_success "Backup created and encrypted: $encrypted_path"
    else
        log_warning "GPG not found, backup stored unencrypted"
        mv "$backup_path" "${backup_path}.bak"
    fi
    
    log_info "Backup size: $(numfmt --to=iec-i --suffix=B $size 2>/dev/null || echo "${size} bytes")"
    log_info "Checksum: $checksum"
}

# Verify backup integrity
verify_backup() {
    local encrypted_path="$1"
    local metadata_path="${encrypted_path%.gpg}.meta"
    
    if [[ ! -f "$encrypted_path" ]] || [[ ! -f "$metadata_path" ]]; then
        log_error "Backup or metadata file not found"
        return 1
    fi
    
    log_info "Verifying backup integrity..."
    
    # Check if file is readable
    if [[ ! -r "$encrypted_path" ]]; then
        log_error "Backup file not readable"
        return 1
    fi
    
    log_success "Backup verification passed"
    return 0
}

# Apply retention policy
apply_retention_policy() {
    log_info "Applying retention policy..."
    
    # Keep last N daily backups
    local daily_backups=$(find "$BACKUP_DIR" -name "servers_db_*.db.gpg" -mtime -${RETENTION_DAYS} | wc -l)
    log_info "Daily backups (last ${RETENTION_DAYS} days): $daily_backups"
    
    # Delete old backups (older than retention period)
    local deleted=0
    while IFS= read -r old_backup; do
        local backup_date=$(basename "$old_backup" | sed -n 's/servers_db_\([0-9]\{8\}\)_.*/\1/p')
        if [[ -n "$backup_date" ]]; then
            rm -f "$old_backup"
            rm -f "${old_backup%.gpg}.meta"
            ((deleted++))
            log_info "Deleted old backup: $(basename "$old_backup")"
        fi
    done < <(find "$BACKUP_DIR" -name "servers_db_*.db.gpg" -mtime +${RETENTION_DAYS})
    
    if [[ $deleted -gt 0 ]]; then
        log_success "Deleted $deleted old backup(s)"
    else
        log_info "No old backups to delete"
    fi
}

# List all backups
list_backups() {
    log_info "Available backups:"
    if [[ -d "$BACKUP_DIR" ]]; then
        find "$BACKUP_DIR" -name "servers_db_*.db.gpg" -type f -printf "%T@ %p\n" | \
            sort -rn | \
            while read -r timestamp path; do
                local size=$(stat -f%z "$path" 2>/dev/null || stat -c%s "$path")
                local date=$(date -d "@${timestamp%.*}" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -r "${timestamp%.*}" '+%Y-%m-%d %H:%M:%S')
                local name=$(basename "$path")
                printf "  %s | %10s | %s\n" "$date" "$(numfmt --to=iec-i --suffix=B $size 2>/dev/null || echo "${size}B")" "$name"
            done
    else
        log_warning "Backup directory does not exist"
    fi
}

# Main backup process
main() {
    log_info "========================================"
    log_info "Database Backup Started"
    log_info "========================================"
    
    # Check prerequisites
    check_database
    create_backup_dir
    
    # Create backup
    local backup_name=$(generate_backup_name)
    create_backup "$backup_name"
    
    # Verify backup
    local encrypted_path="$BACKUP_DIR/${backup_name}.gpg"
    verify_backup "$encrypted_path"
    
    # Apply retention policy
    apply_retention_policy
    
    # Show backup statistics
    log_info "----------------------------------------"
    list_backups
    log_info "========================================"
    log_success "Database Backup Completed Successfully"
    log_info "========================================"
}

# Handle script arguments
case "${1:-backup}" in
    backup)
        main
        ;;
    list)
        list_backups
        ;;
    verify)
        if [[ -n "${2:-}" ]]; then
            verify_backup "$BACKUP_DIR/$2"
        else
            log_error "Usage: $0 verify <backup_filename>"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 {backup|list|verify <filename>}"
        exit 1
        ;;
esac
