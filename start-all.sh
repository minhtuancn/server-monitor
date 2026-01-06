#!/bin/bash

###############################################################################
# Server Monitor Dashboard v4.1 - Start All Services
# Starts all backend services for development environment
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_DIR="/opt/server-monitor-dev"
BACKEND_DIR="$BASE_DIR/backend"
LOGS_DIR="$BASE_DIR/logs"
DATA_DIR="$BASE_DIR/data"

# Ports
FRONTEND_PORT=9081
API_PORT=9083
TERMINAL_PORT=9084
WEBSOCKET_PORT=9085

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Server Monitor Dashboard v4.1 - Start Services          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Create directories if they don't exist
mkdir -p "$LOGS_DIR"
mkdir -p "$DATA_DIR"

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Function to stop existing services
stop_service() {
    local name=$1
    local pidfile=$2
    
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping existing $name (PID: $pid)...${NC}"
            kill $pid 2>/dev/null || true
            sleep 1
        fi
        rm -f "$pidfile"
    fi
}

# Function to start a service
start_service() {
    local name=$1
    local command=$2
    local pidfile=$3
    local logfile=$4
    local port=$5
    local workdir=${6:-$BACKEND_DIR}  # Optional working directory, default to backend
    
    echo -e "${BLUE}Starting $name...${NC}"
    
    # Check if port is already in use
    if check_port $port; then
        echo -e "${YELLOW}  Port $port already in use, stopping existing process...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    # Start service
    cd "$workdir"
    nohup $command > "$logfile" 2>&1 &
    local pid=$!
    echo $pid > "$pidfile"
    
    # Wait a moment and check if it started
    sleep 2
    if ps -p $pid > /dev/null 2>&1; then
        if check_port $port; then
            echo -e "${GREEN}  ✓ $name started successfully (PID: $pid, Port: $port)${NC}"
            cd "$BASE_DIR"
            return 0
        else
            echo -e "${RED}  ✗ $name process running but port $port not listening${NC}"
            cd "$BASE_DIR"
            return 1
        fi
    else
        echo -e "${RED}  ✗ Failed to start $name${NC}"
        tail -10 "$logfile"
        cd "$BASE_DIR"
        return 1
    fi
}

# Initialize database
echo -e "${BLUE}Initializing database...${NC}"
cd "$BACKEND_DIR"
python3 -c "import database; database.init_database()" 2>/dev/null || echo -e "${YELLOW}  Database already initialized${NC}"

# Stop existing services
echo ""
echo -e "${BLUE}Stopping existing services...${NC}"
stop_service "Central API" "$BASE_DIR/api.pid"
stop_service "WebSocket Server" "$BASE_DIR/websocket.pid"
stop_service "Terminal Server" "$BASE_DIR/terminal.pid"
stop_service "Frontend Server" "$BASE_DIR/web.pid"

echo ""
echo -e "${BLUE}Starting services...${NC}"

# Start Central API
start_service \
    "Central API" \
    "python3 central_api.py" \
    "$BASE_DIR/api.pid" \
    "$LOGS_DIR/central_api.log" \
    $API_PORT

# Start WebSocket Server
start_service \
    "WebSocket Server" \
    "python3 websocket_server.py" \
    "$BASE_DIR/websocket.pid" \
    "$LOGS_DIR/websocket.log" \
    $WEBSOCKET_PORT

# Start Terminal Server (optional)
if [ -f "$BACKEND_DIR/terminal.py" ]; then
    start_service \
        "Terminal Server" \
        "python3 terminal.py" \
        "$BASE_DIR/terminal.pid" \
        "$LOGS_DIR/terminal.log" \
        $TERMINAL_PORT
fi

# Start Frontend Server
start_service \
    "Frontend Server" \
    "python3 -m http.server $FRONTEND_PORT" \
    "$BASE_DIR/web.pid" \
    "$LOGS_DIR/web.log" \
    $FRONTEND_PORT \
    "$BASE_DIR/frontend"

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 All Services Started!                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo -e "  Frontend:   ${GREEN}http://$(hostname -I | awk '{print $1}'):$FRONTEND_PORT${NC}"
echo -e "  API:        ${GREEN}http://$(hostname -I | awk '{print $1}'):$API_PORT${NC}"
echo -e "  WebSocket:  ${GREEN}ws://$(hostname -I | awk '{print $1}'):$WEBSOCKET_PORT${NC}"
echo -e "  Terminal:   ${GREEN}ws://$(hostname -I | awk '{print $1}'):$TERMINAL_PORT${NC}"
echo ""
echo -e "${BLUE}Default Credentials:${NC}"
echo -e "  Username: ${GREEN}admin${NC}"
echo -e "  Password: ${GREEN}admin123${NC}"
echo ""
echo -e "${BLUE}Logs Directory:${NC}"
echo -e "  ${GREEN}$LOGS_DIR/${NC}"
echo ""
echo -e "${BLUE}Commands:${NC}"
echo -e "  Stop:    ${GREEN}$BASE_DIR/stop-dev.sh${NC}"
echo -e "  Restart: ${GREEN}$BASE_DIR/start-dev.sh${NC}"
echo -e "  Logs:    ${GREEN}tail -f $LOGS_DIR/*.log${NC}"
echo ""
echo -e "${YELLOW}Note: It may take a few seconds for all services to be fully ready.${NC}"
echo ""
