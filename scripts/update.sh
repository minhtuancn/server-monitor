#!/bin/bash

###############################################################################
# Server Monitor Dashboard - Update Script
# Version: 2.0.0
# Description: Safely update the installation with backup and rollback support
# Usage: sudo /opt/server-monitor/scripts/update.sh [--ref <branch|tag|commit>]
###############################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
INSTALL_DIR="/opt/server-monitor"
CONFIG_DIR="/etc/server-monitor"
DATA_DIR="/var/lib/server-monitor"
BACKUP_DIR="$DATA_DIR/backups"
STATE_FILE="$DATA_DIR/.last-known-good"
GIT_REF=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --ref)
            GIT_REF="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --ref REF    Git reference to update to (branch, tag, commit)"
            echo "  --help       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

###############################################################################
# Utility Functions
###############################################################################

print_step() {
    echo ""
    echo -e "${CYAN}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

check_installation() {
    if [ ! -d "$INSTALL_DIR" ]; then
        print_error "Installation not found at $INSTALL_DIR"
        print_error "Please run install.sh first"
        exit 1
    fi
}

backup_database() {
    print_step "Backing up database..."
    
    if [ -f "$DATA_DIR/servers.db" ]; then
        local timestamp=$(date +%Y%m%d-%H%M%S)
        local backup_file="$BACKUP_DIR/servers-$timestamp.db"
        
        mkdir -p "$BACKUP_DIR"
        cp "$DATA_DIR/servers.db" "$backup_file"
        
        print_success "Database backed up: $backup_file"
        
        # Keep only last 10 backups
        ls -t "$BACKUP_DIR"/servers-*.db | tail -n +11 | xargs -r rm
        print_success "Old backups cleaned (kept last 10)"
    else
        print_warning "No database to backup"
    fi
}

save_current_state() {
    print_step "Saving current state..."
    
    cd "$INSTALL_DIR"
    local current_commit=$(git rev-parse HEAD)
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    
    echo "$current_commit|$current_branch|$(date +%s)" > "$STATE_FILE"
    print_success "Current state saved: $current_commit ($current_branch)"
}

stop_services() {
    print_step "Stopping services..."
    
    local services=(
        "server-monitor-frontend"
        "server-monitor-terminal"
        "server-monitor-ws"
        "server-monitor-api"
    )
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            systemctl stop "$service"
            print_success "${service}: stopped"
        fi
    done
}

update_code() {
    print_step "Updating code..."
    
    cd "$INSTALL_DIR"
    
    # Stash any local changes
    git stash > /dev/null 2>&1 || true
    
    # Fetch latest
    git fetch --all
    
    # Checkout specified ref or pull latest
    if [ -n "$GIT_REF" ]; then
        git checkout "$GIT_REF"
        print_success "Checked out: $GIT_REF"
    else
        local current_branch=$(git rev-parse --abbrev-ref HEAD)
        git pull origin "$current_branch"
        print_success "Pulled latest from: $current_branch"
    fi
    
    local new_commit=$(git rev-parse HEAD)
    print_success "Now at commit: $new_commit"
}

update_backend() {
    print_step "Updating backend dependencies..."
    
    cd "$INSTALL_DIR"
    source .venv/bin/activate
    
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r backend/requirements.txt > /dev/null 2>&1
    
    print_success "Backend dependencies updated"
}

run_migrations() {
    print_step "Running database migrations..."
    
    cd "$INSTALL_DIR/backend"
    source "$INSTALL_DIR/.venv/bin/activate"
    
    export DB_PATH="$DATA_DIR/servers.db"
    
    # Check if migrations directory exists
    if [ -d "migrations" ]; then
        if [ -f "migrations/migrate.py" ]; then
            python3 migrations/migrate.py || print_warning "Migrations completed with warnings"
            print_success "Migrations executed"
        else
            print_warning "No migration script found"
        fi
    else
        print_warning "No migrations directory found"
    fi
}

update_frontend() {
    print_step "Updating frontend..."
    
    cd "$INSTALL_DIR/frontend-next"
    
    npm ci --production > /dev/null 2>&1
    npm run build > /dev/null 2>&1
    
    print_success "Frontend rebuilt"
}

reload_systemd() {
    print_step "Reloading systemd configuration..."
    
    # Copy updated service files if they exist
    if [ -d "$INSTALL_DIR/services/systemd" ]; then
        cp "$INSTALL_DIR/services/systemd"/*.service /etc/systemd/system/ 2>/dev/null || true
        systemctl daemon-reload
        print_success "Systemd reloaded"
    fi
}

start_services() {
    print_step "Starting services..."
    
    local services=(
        "server-monitor-api"
        "server-monitor-ws"
        "server-monitor-terminal"
        "server-monitor-frontend"
    )
    
    for service in "${services[@]}"; do
        systemctl start "$service"
        sleep 1
        if systemctl is-active --quiet "$service"; then
            print_success "${service}: started"
        else
            print_error "${service}: failed to start"
            print_error "Check logs: journalctl -u $service -n 50"
        fi
    done
}

verify_update() {
    print_step "Verifying update..."
    
    sleep 3
    
    # Check services
    local all_ok=true
    local services=(
        "server-monitor-api"
        "server-monitor-ws"
        "server-monitor-terminal"
        "server-monitor-frontend"
    )
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            print_success "${service}: running"
        else
            print_error "${service}: not running"
            all_ok=false
        fi
    done
    
    # Check API health
    if curl -s -f http://localhost:9083/api/stats/overview > /dev/null 2>&1; then
        print_success "API health check: OK"
    else
        print_warning "API health check: failed"
        all_ok=false
    fi
    
    if [ "$all_ok" = false ]; then
        print_error "Update verification failed!"
        print_error "Consider running: sudo $INSTALL_DIR/scripts/rollback.sh"
        return 1
    fi
}

print_completion() {
    local ip=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           Update Completed Successfully!                  ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Access URLs:${NC}"
    echo -e "  Dashboard:  ${GREEN}http://$ip:9081${NC}"
    echo ""
    echo -e "${CYAN}Check Status:${NC}"
    echo -e "  ${GREEN}systemctl status server-monitor-*${NC}"
    echo -e "  ${GREEN}journalctl -u server-monitor-* -f${NC}"
    echo ""
    echo -e "${CYAN}Rollback if needed:${NC}"
    echo -e "  ${GREEN}sudo $INSTALL_DIR/scripts/rollback.sh${NC}"
    echo ""
}

###############################################################################
# Main Update Flow
###############################################################################

main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║      Server Monitor Dashboard - Update                     ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    
    check_root
    check_installation
    save_current_state
    backup_database
    stop_services
    update_code
    update_backend
    run_migrations
    update_frontend
    reload_systemd
    start_services
    
    if verify_update; then
        print_completion
    else
        print_error "Update completed with errors"
        exit 1
    fi
}

# Run main
main
