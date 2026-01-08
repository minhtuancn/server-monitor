#!/bin/bash

###############################################################################
# Server Monitor Dashboard - One-Command Installer
# Version: 2.2.0
# Description: Automated installation script for Linux systems
# Usage: curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash
#        curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash -s -- --ref v2.2.0
#        curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash -s -- --dry-run
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/server-monitor"
CONFIG_DIR="/etc/server-monitor"
DATA_DIR="/var/lib/server-monitor"
LOG_DIR="/var/log/server-monitor"
BACKUP_DIR="$DATA_DIR/backups"
SERVICE_USER="server-monitor"
REPO_URL="https://github.com/minhtuancn/server-monitor.git"
GIT_REF="main"
DRY_RUN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --ref)
            GIT_REF="$2"
            shift 2
            ;;
        --install-dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --ref REF           Git reference to install (branch, tag, commit)"
            echo "  --install-dir DIR   Installation directory (default: /opt/server-monitor)"
            echo "  --dry-run           Show what would be done without making changes"
            echo "  --help              Show this help message"
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

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${BLUE}║   Server Monitor Dashboard - Installer v2.2 (DRY RUN)     ║${NC}"
    else
        echo -e "${BLUE}║   Server Monitor Dashboard - Installer v2.2               ║${NC}"
    fi
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo ""
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${CYAN}▶ [DRY RUN] $1${NC}"
    else
        echo -e "${CYAN}▶ $1${NC}"
    fi
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

# Execute command or show what would be executed
run_cmd() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}  Would run: $*${NC}"
    else
        "$@"
    fi
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        echo "Please run with sudo: sudo bash $0"
        exit 1
    fi
}

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        DISTRO_VERSION=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        DISTRO="rhel"
    else
        DISTRO="unknown"
    fi
    
    case $DISTRO in
        ubuntu|debian)
            PKG_MANAGER="apt"
            ;;
        centos|rhel|almalinux|rocky)
            PKG_MANAGER="dnf"
            if ! command -v dnf &> /dev/null; then
                PKG_MANAGER="yum"
            fi
            ;;
        fedora)
            PKG_MANAGER="dnf"
            ;;
        arch|manjaro)
            PKG_MANAGER="pacman"
            ;;
        *)
            print_error "Unsupported distribution: $DISTRO"
            exit 1
            ;;
    esac
    
    print_success "Detected: $DISTRO (Package manager: $PKG_MANAGER)"
}

install_system_deps() {
    print_step "Installing system dependencies..."
    
    case $PKG_MANAGER in
        apt)
            apt-get update -qq
            apt-get install -y -qq git python3 python3-pip python3-venv curl lsof
            
            # Install Node.js 18+ if not present
            if ! command -v node &> /dev/null || [ "$(node -v | cut -d'v' -f2 | cut -d'.' -f1)" -lt 18 ]; then
                print_step "Installing Node.js 18..."
                curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
                apt-get install -y -qq nodejs
            fi
            ;;
        dnf|yum)
            $PKG_MANAGER install -y -q git python3 python3-pip curl lsof
            
            # Install Node.js 18+
            if ! command -v node &> /dev/null || [ "$(node -v | cut -d'v' -f2 | cut -d'.' -f1)" -lt 18 ]; then
                print_step "Installing Node.js 18..."
                curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
                $PKG_MANAGER install -y -q nodejs
            fi
            ;;
        pacman)
            pacman -Sy --noconfirm --needed git python python-pip nodejs npm curl lsof
            ;;
    esac
    
    print_success "System dependencies installed"
    print_success "Python: $(python3 --version)"
    print_success "Node.js: $(node --version)"
    print_success "npm: $(npm --version)"
}

create_service_user() {
    print_step "Creating service user: $SERVICE_USER..."
    
    if id "$SERVICE_USER" &>/dev/null; then
        print_warning "User $SERVICE_USER already exists"
    else
        useradd --system --no-create-home --shell /bin/false "$SERVICE_USER"
        print_success "User $SERVICE_USER created"
    fi
}

create_directories() {
    print_step "Creating directory structure..."
    
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$BACKUP_DIR"
    
    # Set ownership
    chown -R "$SERVICE_USER:$SERVICE_USER" "$DATA_DIR"
    chown -R "$SERVICE_USER:$SERVICE_USER" "$LOG_DIR"
    
    print_success "Directories created"
}

clone_repository() {
    print_step "Cloning repository..."
    
    if [ -d "$INSTALL_DIR/.git" ]; then
        print_warning "Repository already exists at $INSTALL_DIR"
        cd "$INSTALL_DIR"
        git fetch --all
        git checkout "$GIT_REF"
        git pull origin "$GIT_REF" || true
    else
        git clone "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
        git checkout "$GIT_REF"
    fi
    
    print_success "Repository ready at $INSTALL_DIR (ref: $GIT_REF)"
}

setup_python_env() {
    print_step "Setting up Python virtual environment..."
    
    cd "$INSTALL_DIR"
    
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate and install dependencies
    source .venv/bin/activate
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r backend/requirements.txt > /dev/null 2>&1
    
    print_success "Python dependencies installed"
}

setup_frontend() {
    print_step "Setting up Next.js frontend..."
    
    cd "$INSTALL_DIR/frontend-next"
    
    npm ci --production > /dev/null 2>&1
    npm run build > /dev/null 2>&1
    
    print_success "Frontend built successfully"
}

generate_env_file() {
    print_step "Generating environment configuration..."
    
    local env_file="$CONFIG_DIR/server-monitor.env"
    
    # Generate secure secrets
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")
    
    # Create env file (only if it doesn't exist to preserve user config)
    if [ ! -f "$env_file" ]; then
        cat > "$env_file" << EOF
# Server Monitor Dashboard - Environment Configuration
# Generated: $(date)

# ==================== SECURITY ====================
JWT_SECRET=$JWT_SECRET
JWT_EXPIRATION=86400
ENCRYPTION_KEY=$ENCRYPTION_KEY

# ==================== DATABASE ====================
DB_PATH=$DATA_DIR/servers.db

# ==================== PORTS ====================
API_PORT=9083
FRONTEND_PORT=9081
WEBSOCKET_PORT=9085
TERMINAL_PORT=9084

# ==================== FRONTEND (Next.js) ====================
NODE_ENV=production
PORT=9081
API_PROXY_TARGET=http://localhost:9083
NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084

# ==================== EMAIL ALERTS (optional) ====================
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
# SMTP_FROM=your-email@gmail.com
# SMTP_TO=admin@example.com

# ==================== TELEGRAM (optional) ====================
# TELEGRAM_BOT_TOKEN=your-bot-token
# TELEGRAM_CHAT_ID=your-chat-id

# ==================== SLACK (optional) ====================
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
EOF
        chmod 600 "$env_file"
        print_success "Environment file created: $env_file"
    else
        print_warning "Environment file already exists: $env_file"
        print_warning "Keeping existing configuration"
    fi
    
    # Create frontend .env.local
    local frontend_env="$INSTALL_DIR/frontend-next/.env.local"
    if [ ! -f "$frontend_env" ]; then
        cat > "$frontend_env" << EOF
NODE_ENV=production
API_PROXY_TARGET=http://localhost:9083
NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084
EOF
        print_success "Frontend environment file created"
    fi
}

init_database() {
    print_step "Initializing SQLite database..."
    
    cd "$INSTALL_DIR/backend"
    source "$INSTALL_DIR/.venv/bin/activate"
    
    # Set DB_PATH for init
    export DB_PATH="$DATA_DIR/servers.db"
    
    python3 -c "import database; database.init_database()" 2>/dev/null || true
    
    # Set ownership
    chown "$SERVICE_USER:$SERVICE_USER" "$DATA_DIR/servers.db"
    
    print_success "Database initialized: $DATA_DIR/servers.db"
}

install_systemd_services() {
    print_step "Installing systemd services..."
    
    local services=(
        "server-monitor-api"
        "server-monitor-ws"
        "server-monitor-terminal"
        "server-monitor-frontend"
    )
    
    for service in "${services[@]}"; do
        cp "$INSTALL_DIR/services/systemd/${service}.service" "/etc/systemd/system/"
        print_success "Installed: ${service}.service"
    done
    
    systemctl daemon-reload
    print_success "Systemd services installed"
}

set_permissions() {
    print_step "Setting file permissions..."
    
    # Set ownership of install directory
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    
    # Allow service user to read config
    chown root:$SERVICE_USER "$CONFIG_DIR/server-monitor.env"
    chmod 640 "$CONFIG_DIR/server-monitor.env"
    
    print_success "Permissions set"
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
        systemctl enable "$service" > /dev/null 2>&1
        systemctl start "$service"
        sleep 1
        if systemctl is-active --quiet "$service"; then
            print_success "${service}: active"
        else
            print_error "${service}: failed to start"
        fi
    done
}

verify_installation() {
    print_step "Verifying installation..."
    
    sleep 3  # Give services time to fully start
    
    # Check if ports are listening
    local ports=(9083 9081 9085 9084)
    local port_names=("API" "Frontend" "WebSocket" "Terminal")
    
    for i in "${!ports[@]}"; do
        if lsof -Pi :${ports[$i]} -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_success "${port_names[$i]} (port ${ports[$i]}): listening"
        else
            print_warning "${port_names[$i]} (port ${ports[$i]}): not listening"
        fi
    done
    
    # Try to reach API
    if curl -s -f http://localhost:9083/api/stats/overview > /dev/null 2>&1; then
        print_success "API health check: OK"
    else
        print_warning "API health check: failed (may need a moment to warm up)"
    fi
}

print_completion() {
    local ip=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║        Server Monitor Dashboard Installed!                 ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Access URLs:${NC}"
    echo -e "  Dashboard:  ${GREEN}http://$ip:9081${NC}"
    echo -e "  API:        ${GREEN}http://$ip:9083${NC}"
    echo ""
    echo -e "${CYAN}Default Credentials:${NC}"
    echo -e "  Username:   ${YELLOW}admin${NC}"
    echo -e "  Password:   ${YELLOW}admin123${NC}"
    echo -e "  ${RED}⚠  Change password immediately after first login!${NC}"
    echo ""
    echo -e "${CYAN}Service Management:${NC}"
    echo -e "  Status:     ${GREEN}systemctl status server-monitor-*${NC}"
    echo -e "  Restart:    ${GREEN}systemctl restart server-monitor-*${NC}"
    echo -e "  Logs:       ${GREEN}journalctl -u server-monitor-* -f${NC}"
    echo -e "  Control:    ${GREEN}$INSTALL_DIR/scripts/smctl [command]${NC}"
    echo ""
    echo -e "${CYAN}Update:${NC}"
    echo -e "  ${GREEN}sudo $INSTALL_DIR/scripts/update.sh${NC}"
    echo ""
    echo -e "${CYAN}Configuration:${NC}"
    echo -e "  Environment: ${GREEN}$CONFIG_DIR/server-monitor.env${NC}"
    echo -e "  Database:    ${GREEN}$DATA_DIR/servers.db${NC}"
    echo -e "  Logs:        ${GREEN}$LOG_DIR/${NC}"
    echo ""
    echo -e "${YELLOW}Note: Services may take a few seconds to fully initialize.${NC}"
    echo ""
}

###############################################################################
# Main Installation Flow
###############################################################################

main() {
    print_header
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}                    DRY RUN MODE                          ${NC}"
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
        echo ""
        echo -e "This is a ${YELLOW}DRY RUN${NC}. No actual changes will be made."
        echo -e "The script will show what would be executed."
        echo ""
        echo -e "${CYAN}Configuration:${NC}"
        echo -e "  Install Directory: ${GREEN}$INSTALL_DIR${NC}"
        echo -e "  Config Directory:  ${GREEN}$CONFIG_DIR${NC}"
        echo -e "  Data Directory:    ${GREEN}$DATA_DIR${NC}"
        echo -e "  Git Reference:     ${GREEN}$GIT_REF${NC}"
        echo ""
    fi
    
    check_root
    detect_distro
    install_system_deps
    create_service_user
    create_directories
    clone_repository
    setup_python_env
    setup_frontend
    generate_env_file
    init_database
    install_systemd_services
    set_permissions
    start_services
    verify_installation
    print_completion
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo ""
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}           DRY RUN COMPLETED SUCCESSFULLY                 ${NC}"
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
        echo ""
        echo -e "To perform the actual installation, run without ${YELLOW}--dry-run${NC} flag."
        echo ""
    fi
}

# Run main installation
main
