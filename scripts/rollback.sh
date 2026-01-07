#!/bin/bash

###############################################################################
# Server Monitor Dashboard - Rollback Script
# Version: 2.0.0
# Description: Rollback to the last known good state
# Usage: sudo /opt/server-monitor/scripts/rollback.sh
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
DATA_DIR="/var/lib/server-monitor"
STATE_FILE="$DATA_DIR/.last-known-good"

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

check_state_file() {
    if [ ! -f "$STATE_FILE" ]; then
        print_error "No saved state found at $STATE_FILE"
        print_error "Cannot perform rollback"
        exit 1
    fi
}

load_state() {
    local state=$(cat "$STATE_FILE")
    SAVED_COMMIT=$(echo "$state" | cut -d'|' -f1)
    SAVED_BRANCH=$(echo "$state" | cut -d'|' -f2)
    SAVED_TIME=$(echo "$state" | cut -d'|' -f3)
    
    print_success "Found saved state:"
    print_success "  Commit: $SAVED_COMMIT"
    print_success "  Branch: $SAVED_BRANCH"
    print_success "  Time: $(date -d @$SAVED_TIME 2>/dev/null || date -r $SAVED_TIME 2>/dev/null)"
}

confirm_rollback() {
    echo ""
    echo -e "${YELLOW}This will rollback the installation to the saved state.${NC}"
    echo -e "${YELLOW}Data will NOT be affected, but code will be reverted.${NC}"
    echo ""
    read -p "Continue with rollback? (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "Rollback cancelled"
        exit 0
    fi
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

rollback_code() {
    print_step "Rolling back code..."
    
    cd "$INSTALL_DIR"
    
    git fetch --all
    git checkout "$SAVED_COMMIT"
    
    print_success "Code rolled back to: $SAVED_COMMIT"
}

rebuild_backend() {
    print_step "Rebuilding backend..."
    
    cd "$INSTALL_DIR"
    source .venv/bin/activate
    
    pip install -r backend/requirements.txt > /dev/null 2>&1
    
    print_success "Backend rebuilt"
}

rebuild_frontend() {
    print_step "Rebuilding frontend..."
    
    cd "$INSTALL_DIR/frontend-next"
    
    npm ci --production > /dev/null 2>&1
    npm run build > /dev/null 2>&1
    
    print_success "Frontend rebuilt"
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
        fi
    done
}

verify_rollback() {
    print_step "Verifying rollback..."
    
    sleep 3
    
    # Check services
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
        fi
    done
    
    # Check API
    if curl -s -f http://localhost:9083/api/stats/overview > /dev/null 2>&1; then
        print_success "API health check: OK"
    else
        print_warning "API health check: failed"
    fi
}

print_completion() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          Rollback Completed Successfully!                 ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}System rolled back to:${NC}"
    echo -e "  Commit: ${GREEN}$SAVED_COMMIT${NC}"
    echo ""
    echo -e "${CYAN}Check Status:${NC}"
    echo -e "  ${GREEN}systemctl status server-monitor-*${NC}"
    echo ""
}

###############################################################################
# Main Rollback Flow
###############################################################################

main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║      Server Monitor Dashboard - Rollback                   ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    
    check_root
    check_state_file
    load_state
    confirm_rollback
    stop_services
    rollback_code
    rebuild_backend
    rebuild_frontend
    start_services
    verify_rollback
    print_completion
}

# Run main
main
