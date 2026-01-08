#!/bin/bash

#=============================================================================
# Server Monitor Dashboard - Development Quick Start
# Usage: ./start-dev.sh
#=============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Use script directory as base
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_DIR="${SERVER_MONITOR_DIR:-$SCRIPT_DIR}"
API_PORT="${API_PORT:-9083}"
WEB_PORT="${FRONTEND_PORT:-9081}"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Server Monitor Dashboard - Development Environment          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for virtual environment and activate it
if [ -d "$DEV_DIR/venv" ]; then
    echo -e "${GREEN}Found virtual environment, activating...${NC}"
    source "$DEV_DIR/venv/bin/activate"
    PYTHON_CMD="python3"
elif [ -d "$DEV_DIR/.venv" ]; then
    echo -e "${GREEN}Found virtual environment (.venv), activating...${NC}"
    source "$DEV_DIR/.venv/bin/activate"
    PYTHON_CMD="python3"
else
    echo -e "${YELLOW}No virtual environment found. Using system Python.${NC}"
    echo -e "${YELLOW}For Python 3.12+, consider creating a venv: python3 -m venv venv${NC}"
    PYTHON_CMD="python3"
fi
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}⚠️  Not running as root. Some features may not work.${NC}"
    echo ""
fi

# Step 1: Check if ports are available
echo -e "${BLUE}===> Step 1: Checking ports...${NC}"
if lsof -Pi :$API_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}✗ Port $API_PORT is already in use!${NC}"
    lsof -i :$API_PORT
    echo ""
    read -p "Kill the process? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PID=$(lsof -ti:$API_PORT)
        kill -9 $PID
        echo -e "${GREEN}✓ Process killed${NC}"
    else
        echo -e "${RED}Aborting...${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Port $API_PORT is available${NC}"
fi

if lsof -Pi :$WEB_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}✗ Port $WEB_PORT is already in use!${NC}"
    lsof -i :$WEB_PORT
    echo ""
    read -p "Kill the process? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PID=$(lsof -ti:$WEB_PORT)
        kill -9 $PID
        echo -e "${GREEN}✓ Process killed${NC}"
    else
        echo -e "${RED}Aborting...${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Port $WEB_PORT is available${NC}"
fi
echo ""

# Step 2: Update API port in backend
echo -e "${BLUE}===> Step 2: Configuring backend...${NC}"
cd $DEV_DIR/backend/
if grep -q "PORT = 8083" central_api.py; then
    sed -i "s/PORT = 8083/PORT = $API_PORT/" central_api.py
    echo -e "${GREEN}✓ API port updated to $API_PORT${NC}"
else
    echo -e "${YELLOW}⚠️  API port already configured${NC}"
fi
echo ""

# Step 3: Update API URL in frontend
echo -e "${BLUE}===> Step 3: Configuring frontend...${NC}"
cd $DEV_DIR/frontend/
if grep -q "const API_URL = 'http://172.22.0.103:8083'" dashboard.html; then
    sed -i "s|const API_URL = 'http://172.22.0.103:8083'|const API_URL = 'http://172.22.0.103:$API_PORT'|" dashboard.html
    echo -e "${GREEN}✓ Frontend API URL updated${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend already configured${NC}"
fi
echo ""

# Step 4: Create necessary directories
echo -e "${BLUE}===> Step 4: Creating directories...${NC}"
mkdir -p $DEV_DIR/data
mkdir -p $DEV_DIR/logs
mkdir -p $DEV_DIR/exports
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Step 5: Start backend API
echo -e "${BLUE}===> Step 5: Starting Backend API...${NC}"
cd $DEV_DIR/backend/
$PYTHON_CMD central_api.py > $DEV_DIR/logs/api.log 2>&1 &
API_PID=$!
echo $API_PID > $DEV_DIR/api.pid
echo -e "${GREEN}✓ API started (PID: $API_PID)${NC}"
echo -e "  Log: $DEV_DIR/logs/api.log"
echo -e "  URL: http://172.22.0.103:$API_PORT"
echo ""

# Wait for API to start
echo -e "${BLUE}===> Waiting for API to start...${NC}"
sleep 3

# Check if API is running
if curl -s http://localhost:$API_PORT/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is responding${NC}"
else
    echo -e "${RED}✗ API failed to start!${NC}"
    echo -e "Check logs: tail -f $DEV_DIR/logs/api.log"
    exit 1
fi
echo ""

# Step 6: Start web server
echo -e "${BLUE}===> Step 6: Starting Web Server...${NC}"
cd $DEV_DIR/frontend/
$PYTHON_CMD -m http.server $WEB_PORT > $DEV_DIR/logs/web.log 2>&1 &
WEB_PID=$!
echo $WEB_PID > $DEV_DIR/web.pid
echo -e "${GREEN}✓ Web server started (PID: $WEB_PID)${NC}"
echo -e "  Log: $DEV_DIR/logs/web.log"
echo -e "  URL: http://172.22.0.103:$WEB_PORT"
echo ""

# Step 7: Summary
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  🎉 Development Server Started! 🎉                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📊 Access URLs:${NC}"
echo -e "  Dashboard:  ${GREEN}http://172.22.0.103:$WEB_PORT/dashboard.html${NC}"
echo -e "  API:        ${GREEN}http://172.22.0.103:$API_PORT/api/all${NC}"
echo -e "  API Health: ${GREEN}http://172.22.0.103:$API_PORT/api/health${NC}"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo -e "  API:  tail -f $DEV_DIR/logs/api.log"
echo -e "  Web:  tail -f $DEV_DIR/logs/web.log"
echo ""
echo -e "${BLUE}🔧 PIDs:${NC}"
echo -e "  API:  $API_PID (saved to $DEV_DIR/api.pid)"
echo -e "  Web:  $WEB_PID (saved to $DEV_DIR/web.pid)"
echo ""
echo -e "${BLUE}🛑 Stop servers:${NC}"
echo -e "  bash $DEV_DIR/stop-dev.sh"
echo -e "  Or manually: kill $API_PID $WEB_PID"
echo ""
echo -e "${YELLOW}⚠️  Note: This is DEVELOPMENT mode, not for production use!${NC}"
echo -e "${YELLOW}⚠️  Production servers are still running on ports 8081, 8083${NC}"
echo ""
echo -e "${GREEN}Happy Developing! 🚀${NC}"
