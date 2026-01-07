#!/bin/bash

#=============================================================================
# Server Monitor Dashboard - Stop Development Servers
# Usage: ./stop-dev.sh
#=============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Use script directory as base
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_DIR="${SERVER_MONITOR_DIR:-$SCRIPT_DIR}"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Stopping Development Servers...                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Stop API server
if [ -f "$DEV_DIR/api.pid" ]; then
    API_PID=$(cat "$DEV_DIR/api.pid")
    if ps -p $API_PID > /dev/null 2>&1; then
        kill $API_PID 2>/dev/null
        echo -e "${GREEN}✓ API server stopped (PID: $API_PID)${NC}"
        rm "$DEV_DIR/api.pid"
    else
        echo -e "${YELLOW}⚠️  API server not running${NC}"
        rm "$DEV_DIR/api.pid"
    fi
else
    echo -e "${YELLOW}⚠️  API PID file not found${NC}"
fi

# Stop Web server
if [ -f "$DEV_DIR/web.pid" ]; then
    WEB_PID=$(cat "$DEV_DIR/web.pid")
    if ps -p $WEB_PID > /dev/null 2>&1; then
        kill $WEB_PID 2>/dev/null
        echo -e "${GREEN}✓ Web server stopped (PID: $WEB_PID)${NC}"
        rm "$DEV_DIR/web.pid"
    else
        echo -e "${YELLOW}⚠️  Web server not running${NC}"
        rm "$DEV_DIR/web.pid"
    fi
else
    echo -e "${YELLOW}⚠️  Web PID file not found${NC}"
fi

# Check for any remaining processes
API_PORT=9083
WEB_PORT=9081

if lsof -Pi :$API_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Port $API_PORT still in use, killing...${NC}"
    PID=$(lsof -ti:$API_PORT)
    kill -9 $PID 2>/dev/null
    echo -e "${GREEN}✓ Killed process on port $API_PORT${NC}"
fi

if lsof -Pi :$WEB_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Port $WEB_PORT still in use, killing...${NC}"
    PID=$(lsof -ti:$WEB_PORT)
    kill -9 $PID 2>/dev/null
    echo -e "${GREEN}✓ Killed process on port $WEB_PORT${NC}"
fi

echo ""
echo -e "${GREEN}✓ All development servers stopped${NC}"
echo ""
echo -e "${BLUE}To start again:${NC} bash $DEV_DIR/start-dev.sh"
echo ""
