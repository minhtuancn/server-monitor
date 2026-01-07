#!/bin/bash

###############################################################################
# Server Monitor Dashboard v4.1 - Stop All Services
# Stops all backend services gracefully
###############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration - Use script directory as base
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="${SERVER_MONITOR_DIR:-$SCRIPT_DIR}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Server Monitor Dashboard v4.1 - Stop Services           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to stop service by PID file
stop_by_pidfile() {
    local name=$1
    local pidfile=$2
    
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping $name (PID: $pid)...${NC}"
            kill $pid 2>/dev/null
            sleep 1
            
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${YELLOW}  Force killing $name...${NC}"
                kill -9 $pid 2>/dev/null
            fi
            
            echo -e "${GREEN}  ✓ $name stopped${NC}"
        else
            echo -e "${YELLOW}  $name not running (stale PID file)${NC}"
        fi
        rm -f "$pidfile"
    else
        echo -e "${YELLOW}  $name PID file not found${NC}"
    fi
}

# Function to stop by port
stop_by_port() {
    local name=$1
    local port=$2
    
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}Stopping $name on port $port...${NC}"
        echo "$pids" | xargs kill -9 2>/dev/null
        echo -e "${GREEN}  ✓ $name stopped${NC}"
    else
        echo -e "${YELLOW}  $name not running on port $port${NC}"
    fi
}

# Stop services by PID files
stop_by_pidfile "Central API" "$BASE_DIR/api.pid"
stop_by_pidfile "WebSocket Server" "$BASE_DIR/websocket.pid"
stop_by_pidfile "Terminal Server" "$BASE_DIR/terminal.pid"
stop_by_pidfile "Frontend Server" "$BASE_DIR/web.pid"

# Double check by ports (in case PID files are missing)
echo ""
echo -e "${BLUE}Checking ports...${NC}"
stop_by_port "Port 9083" 9083
stop_by_port "Port 9085" 9085
stop_by_port "Port 9084" 9084
stop_by_port "Port 9081" 9081

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              All Services Stopped Successfully             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
