#!/bin/bash
################################################################################
# Database Restore Script
# 
# Features:
# - Restores encrypted backups
# - Verifies checksums before restore
# - Creates pre-restore backup
# - Validates database integrity after restore
################################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DB_FILE="$PROJECT_ROOT/data/servers.db"
BACKUP_DIR="$PROJECT_ROOT/data/backups"
LOG_FILE="$PROJECT_ROOT/logs/restore.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

log_info() { log "INFO" "$@"; }
log_error() { log "ERROR" "${RED}$*${NC}"; }
log_success() { log "SUCCESS" "${GREEN}$*${NC}"; }
log_warning() { log "WARNING" "${YELLOW}$*${NC}"; }

# List available backups
list_backups() {
    log_info "Available backups:"
    local count=0
    if [[ -d "$BACKUP_DIR" ]]; then
        while IFS= read -r backup; do
            ((count++))
            local name=$(basename "$backup")
            local size=$(stat -f%z "$backup" 2>/dev/null || stat -c%s "$backup")
            local date=$(stat -f%Sm -t '%Y-%m-%d %H:%M:%S' "$backup" 2>/dev/null || date -r "$backup" '+%Y-%m-%d %H:%M:%S')
            printf "%2d) %s | %10s | %s\n" "$count" "$date" "$(numfmt --to=iec-i --suffix=B $size 2>/dev/null || echo "${size}B")" "$name"
        done < <(find "$BACKUP_DIR" -name "servers_db_*.db.gpg" -type f | sort -r)
    fi
    
    if [[ $count -eq 0 ]]; then
        log_warning "No backups found in $BACKUP_DIR"
        return 1
    fi
    return 0
}

# Decrypt backup
decrypt_backup() {
    local encrypted_path="$1"
    local decrypted_path="${encrypted_path%.gpg}"
    
    if [[ ! -f "$encrypted_path" ]]; then
        log_error "Encrypted backup not found: $encrypted_path"
        return 1
    fi
    
    log_info "Decrypting backup..."
    local passphrase="${DB_BACKUP_PASSPHRASE:-ServerMonitorBackup2026}"
    
    if command -v gpg &> /dev/null; then
        echo "$passphrase" | gpg --batch --yes --passphrase-fd 0 \
            --decrypt -o "$decrypted_path" "$encrypted_path" 2>/dev/null || {
            log_error "Decryption failed. Wrong passphrase?"
            return 1
        }
        log_success "Backup decrypted successfully"
        echo "$decrypted_path"
    else
        log_error "GPG not installed"
        return 1
    fi
}

# Verify backup integrity
verify_integrity() {
    local backup_path="$1"
    local metadata_path="${backup_path}.meta"
    
    log_info "Verifying backup integrity..."
    
    if [[ -f "$metadata_path" ]]; then
        local expected_checksum=$(grep -o '"checksum_sha256": "[^"]*"' "$metadata_path" | cut -d'"' -f4)
        local actual_checksum=$(sha256sum "$backup_path" | awk '{print $1}')
        
        if [[ "$expected_checksum" == "$actual_checksum" ]]; then
            log_success "Checksum verification passed"
        else
            log_error "Checksum mismatch!"
            log_error "Expected: $expected_checksum"
            log_error "Actual:   $actual_checksum"
            return 1
        fi
    else
        log_warning "Metadata file not found, skipping checksum verification"
    fi
    
    # Test SQLite database integrity
    if command -v sqlite3 &> /dev/null; then
        if sqlite3 "$backup_path" "PRAGMA integrity_check;" | grep -q "ok"; then
            log_success "SQLite integrity check passed"
        else
            log_error "SQLite integrity check failed"
            return 1
        fi
    fi
    
    return 0
}

# Create pre-restore backup
create_prerestore_backup() {
    if [[ -f "$DB_FILE" ]]; then
        local timestamp=$(date '+%Y%m%d_%H%M%S')
        local prerestore_backup="$BACKUP_DIR/prerestore_${timestamp}.db"
        
        log_info "Creating pre-restore backup..."
        cp "$DB_FILE" "$prerestore_backup"
        log_success "Pre-restore backup created: $prerestore_backup"
        echo "$prerestore_backup"
    else
        log_warning "No existing database to backup"
        echo ""
    fi
}

# Restore database
restore_database() {
    local backup_path="$1"
    local prerestore_backup="$2"
    
    log_info "Stopping services (if running)..."
    # Stop API server
    if [[ -f "$PROJECT_ROOT/api.pid" ]]; then
        local pid=$(cat "$PROJECT_ROOT/api.pid")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            log_info "API server stopped"
            sleep 2
        fi
    fi
    
    log_info "Restoring database..."
    cp "$backup_path" "$DB_FILE"
    chmod 644 "$DB_FILE"
    
    # Verify restored database
    if sqlite3 "$DB_FILE" "PRAGMA integrity_check;" | grep -q "ok"; then
        log_success "Database restored successfully"
        log_info "Database path: $DB_FILE"
        
        # Clean up decrypted backup
        rm -f "$backup_path"
        
        return 0
    else
        log_error "Restored database integrity check failed!"
        if [[ -n "$prerestore_backup" ]] && [[ -f "$prerestore_backup" ]]; then
            log_warning "Rolling back to pre-restore backup..."
            cp "$prerestore_backup" "$DB_FILE"
            log_info "Rollback complete"
        fi
        return 1
    fi
}

# Interactive restore
interactive_restore() {
    log_info "========================================"
    log_info "Database Restore - Interactive Mode"
    log_info "========================================"
    
    # List backups
    if ! list_backups; then
        return 1
    fi
    
    echo ""
    read -p "Enter backup number to restore (or 'q' to quit): " selection
    
    if [[ "$selection" == "q" ]] || [[ "$selection" == "Q" ]]; then
        log_info "Restore cancelled"
        return 0
    fi
    
    # Get selected backup
    local backup_file=$(find "$BACKUP_DIR" -name "servers_db_*.db.gpg" -type f | sort -r | sed -n "${selection}p")
    
    if [[ -z "$backup_file" ]]; then
        log_error "Invalid selection"
        return 1
    fi
    
    log_info "Selected backup: $(basename "$backup_file")"
    
    # Confirmation
    read -p "${YELLOW}WARNING: This will replace the current database. Continue? (yes/no): ${NC}" confirm
    if [[ "$confirm" != "yes" ]]; then
        log_info "Restore cancelled"
        return 0
    fi
    
    # Decrypt backup
    local decrypted_path=$(decrypt_backup "$backup_file")
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    
    # Verify integrity
    if ! verify_integrity "$decrypted_path"; then
        rm -f "$decrypted_path"
        return 1
    fi
    
    # Create pre-restore backup
    local prerestore_backup=$(create_prerestore_backup)
    
    # Restore
    if restore_database "$decrypted_path" "$prerestore_backup"; then
        log_success "========================================"
        log_success "Database Restore Completed Successfully"
        log_success "========================================"
        log_info "Please restart services:"
        log_info "  ./start-all.sh"
    else
        log_error "Restore failed"
        return 1
    fi
}

# Non-interactive restore
restore_by_name() {
    local backup_name="$1"
    local backup_file="$BACKUP_DIR/$backup_name"
    
    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup not found: $backup_name"
        return 1
    fi
    
    log_info "Restoring from: $backup_name"
    
    local decrypted_path=$(decrypt_backup "$backup_file")
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    
    if ! verify_integrity "$decrypted_path"; then
        rm -f "$decrypted_path"
        return 1
    fi
    
    local prerestore_backup=$(create_prerestore_backup)
    
    if restore_database "$decrypted_path" "$prerestore_backup"; then
        log_success "Restore completed successfully"
        return 0
    else
        return 1
    fi
}

# Main
case "${1:-interactive}" in
    interactive)
        interactive_restore
        ;;
    list)
        list_backups
        ;;
    restore)
        if [[ -n "${2:-}" ]]; then
            restore_by_name "$2"
        else
            log_error "Usage: $0 restore <backup_filename>"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 {interactive|list|restore <filename>}"
        exit 1
        ;;
esac
