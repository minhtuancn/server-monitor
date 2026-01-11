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

# Configuration - Use script directory as base
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="${SERVER_MONITOR_DIR:-$SCRIPT_DIR}"
BACKEND_DIR="$BASE_DIR/backend"
LOGS_DIR="$BASE_DIR/logs"
DATA_DIR="$BASE_DIR/data"

# Custom domain configuration (optional, for production deployments)
# Examples:
#   CUSTOM_DOMAIN=mon.go7s.net
#   CUSTOM_DOMAIN=monitoring.example.com
CUSTOM_DOMAIN="${CUSTOM_DOMAIN:-}"

# Ports (can be overridden via environment)
FRONTEND_PORT="${FRONTEND_PORT:-9081}"
API_PORT="${API_PORT:-9083}"
TERMINAL_PORT="${TERMINAL_PORT:-9084}"
WEBSOCKET_PORT="${WEBSOCKET_PORT:-9085}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Server Monitor Dashboard v4.1 - Start Services          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Load nvm if available (for Node.js 20+ required by Next.js 16)
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    source "$NVM_DIR/nvm.sh"
    nvm use default > /dev/null 2>&1 || true
fi

# Check for virtual environment and activate it
if [ -d "$BASE_DIR/venv" ]; then
    echo -e "${GREEN}Found virtual environment, activating...${NC}"
    source "$BASE_DIR/venv/bin/activate"
    PYTHON_CMD="python3"
elif [ -d "$BASE_DIR/.venv" ]; then
    echo -e "${GREEN}Found virtual environment (.venv), activating...${NC}"
    source "$BASE_DIR/.venv/bin/activate"
    PYTHON_CMD="python3"
else
    echo -e "${YELLOW}No virtual environment found. Using system Python.${NC}"
    echo -e "${YELLOW}For Python 3.12+, consider creating a venv: python3 -m venv venv${NC}"
    PYTHON_CMD="python3"
fi

# Check if .env file exists
if [ ! -f "$BASE_DIR/.env" ]; then
    echo -e "${YELLOW}WARNING: .env file not found!${NC}"
    echo -e "${YELLOW}Please create .env file with required keys. See .env.example${NC}"
    echo -e "${YELLOW}Generate keys with:${NC}"
    echo -e "  python3 -c \"import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))\" >> .env"
    echo -e "  python3 -c \"import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(24))\" >> .env"
    echo -e "  python3 -c \"import secrets; print('KEY_VAULT_MASTER_KEY=' + secrets.token_urlsafe(32))\" >> .env"
    echo ""
fi

# Create directories if they don't exist
mkdir -p "$LOGS_DIR"
mkdir -p "$DATA_DIR"

# Function to check if port is in use (handles both IPv4 and IPv6)
check_port() {
    local port=$1
    
    # Method 1: Try lsof (works for both IPv4 and IPv6)
    if lsof -i :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    fi
    
    # Method 2: Try netstat as fallback
    if netstat -tln 2>/dev/null | grep -q ":$port " ; then
        return 0
    fi
    
    # Method 3: Try ss as another fallback
    if ss -tln 2>/dev/null | grep -q ":$port " ; then
        return 0
    fi
    
    return 1
}

# Function to aggressively kill processes on a port
kill_process_on_port() {
    local port=$1
    local service_name=$2
    
    echo -e "${YELLOW}Checking for processes on port $port...${NC}"
    
    # Try lsof first
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}  Found processes using port $port: $pids${NC}"
        echo -e "${YELLOW}  Sending TERM signal...${NC}"
        echo "$pids" | xargs kill 2>/dev/null || true
        sleep 2
        
        # Check if processes are still running
        pids=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$pids" ]; then
            echo -e "${YELLOW}  Processes still running, sending KILL signal...${NC}"
            echo "$pids" | xargs kill -9 2>/dev/null || true
            sleep 1
        fi
    fi
    
    # Double check with netstat/ss as backup
    if check_port $port; then
        echo -e "${YELLOW}  Port still in use, trying alternative method...${NC}"
        fuser -k -9 $port/tcp 2>/dev/null || true
        sleep 1
    fi
    
    # Final verification
    if check_port $port; then
        echo -e "${RED}  ✗ Warning: Could not free port $port${NC}"
        return 1
    else
        echo -e "${GREEN}  ✓ Port $port is now free${NC}"
        return 0
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
            
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${YELLOW}  Process still running, force killing...${NC}"
                kill -9 $pid 2>/dev/null || true
                sleep 1
            fi
            
            if ! ps -p $pid > /dev/null 2>&1; then
                echo -e "${GREEN}  ✓ $name stopped${NC}"
            fi
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
        echo -e "${YELLOW}  Port $port already in use, attempting to free it...${NC}"
        kill_process_on_port $port "$name"
    fi
    
    # Start service
    cd "$workdir"
    nohup $command > "$logfile" 2>&1 &
    local pid=$!
    echo $pid > "$pidfile"
    
    # Determine wait time based on service (Next.js needs more time)
    local wait_time=2
    local max_wait=30
    if [[ "$name" == *"Next.js"* ]] || [[ "$name" == *"Frontend"* ]]; then
        echo -e "${YELLOW}  Waiting for Next.js to compile and start (may take 10-30 seconds)...${NC}"
        wait_time=5
        max_wait=45
    fi
    
    # Wait for process to start
    sleep $wait_time
    
    # Check if process is running
    if ! ps -p $pid > /dev/null 2>&1; then
        echo -e "${RED}  ✗ Failed to start $name - Process died immediately${NC}"
        echo -e "${YELLOW}  Checking if port conflict caused the failure...${NC}"
        if check_port $port; then
            echo -e "${YELLOW}  Port $port is in use. Attempting cleanup and retry...${NC}"
            kill_process_on_port $port "$name"
            
            # Retry once after cleanup
            echo -e "${BLUE}  Retrying $name...${NC}"
            cd "$workdir"
            nohup $command > "$logfile" 2>&1 &
            pid=$!
            echo $pid > "$pidfile"
            sleep $wait_time
            
            if ps -p $pid > /dev/null 2>&1 && check_port $port; then
                echo -e "${GREEN}  ✓ $name started successfully on retry (PID: $pid, Port: $port)${NC}"
                cd "$BASE_DIR"
                return 0
            else
                echo -e "${RED}  ✗ Retry failed. Check logs:${NC}"
                tail -10 "$logfile" 2>/dev/null || echo "  (log file not found)"
                cd "$BASE_DIR"
                return 1
            fi
        else
            echo -e "${RED}  Port $port is free. Error is not port-related.${NC}"
            echo -e "${YELLOW}  Last 10 lines of log:${NC}"
            tail -10 "$logfile" 2>/dev/null || echo "  (log file not found)"
            cd "$BASE_DIR"
            return 1
        fi
    fi
    
    # Process is running, now wait for port to start listening
    echo -e "${YELLOW}  Process started (PID: $pid), waiting for port $port to listen...${NC}"
    local elapsed=0
    while [ $elapsed -lt $max_wait ]; do
        if check_port $port; then
            echo -e "${GREEN}  ✓ $name started successfully (PID: $pid, Port: $port)${NC}"
            cd "$BASE_DIR"
            return 0
        fi
        sleep 2
        elapsed=$((elapsed + 2))
        
        # Check if process is still alive
        if ! ps -p $pid > /dev/null 2>&1; then
            echo -e "${RED}  ✗ Process died while waiting for port to listen${NC}"
            echo -e "${YELLOW}  Last 10 lines of log:${NC}"
            tail -10 "$logfile" 2>/dev/null || echo "  (log file not found)"
            cd "$BASE_DIR"
            return 1
        fi
        
        # Show progress for long waits
        if [[ "$name" == *"Next.js"* ]] || [[ "$name" == *"Frontend"* ]]; then
            echo -e "${YELLOW}  Still waiting... (${elapsed}s/${max_wait}s)${NC}"
        fi
    done
    
    # Timeout reached
    echo -e "${RED}  ✗ Timeout: $name process running but port $port not listening after ${max_wait}s${NC}"
    echo -e "${YELLOW}  Process may still be starting. Check logs at: $logfile${NC}"
    echo -e "${YELLOW}  You can check status with: ps -p $pid && lsof -i:$port${NC}"
    cd "$BASE_DIR"
    return 1
}

# Initialize database
echo -e "${BLUE}Initializing database...${NC}"
cd "$BACKEND_DIR"
$PYTHON_CMD -c "import database; database.init_database()" 2>/dev/null || echo -e "${YELLOW}  Database already initialized${NC}"

# Configure custom domain if provided
if [ -n "$CUSTOM_DOMAIN" ]; then
    echo -e "${BLUE}Configuring custom domain: $CUSTOM_DOMAIN${NC}"
    export ALLOWED_FRONTEND_DOMAINS="${CUSTOM_DOMAIN}"
fi

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
export SKIP_DEFAULT_ADMIN=${SKIP_DEFAULT_ADMIN:-true}
start_service \
    "Central API" \
    "$PYTHON_CMD backend/central_api.py" \
    "$BASE_DIR/api.pid" \
    "$LOGS_DIR/central_api.log" \
    $API_PORT \
    "$BASE_DIR"

# Start WebSocket Server
start_service \
    "WebSocket Server" \
    "$PYTHON_CMD websocket_server.py" \
    "$BASE_DIR/websocket.pid" \
    "$LOGS_DIR/websocket.log" \
    $WEBSOCKET_PORT

# Start Terminal Server (optional)
if [ -f "$BACKEND_DIR/terminal.py" ]; then
    start_service \
        "Terminal Server" \
        "$PYTHON_CMD terminal.py" \
        "$BASE_DIR/terminal.pid" \
        "$LOGS_DIR/terminal.log" \
        $TERMINAL_PORT
fi

# Start Frontend Server (Next.js)
echo ""
echo -e "${BLUE}Starting Next.js Frontend...${NC}"
cd "$BASE_DIR/frontend-next"

# Ensure .env.local exists
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}Creating .env.local from .env.example...${NC}"
    cp .env.example .env.local
    sed -i "s|API_PROXY_TARGET=.*|API_PROXY_TARGET=http://localhost:$API_PORT|" .env.local
fi

# If custom domain is set, update WebSocket URLs
if [ -n "$CUSTOM_DOMAIN" ]; then
    echo -e "${BLUE}Configuring custom domain: $CUSTOM_DOMAIN${NC}"
    # For custom domain, assume reverse proxy on standard HTTPS ports
    # WebSocket URLs point to reverse proxy domain
    sed -i "s|NEXT_PUBLIC_MONITORING_WS_URL=.*|NEXT_PUBLIC_MONITORING_WS_URL=wss://$CUSTOM_DOMAIN/ws/monitoring|" .env.local
    sed -i "s|NEXT_PUBLIC_TERMINAL_WS_URL=.*|NEXT_PUBLIC_TERMINAL_WS_URL=wss://$CUSTOM_DOMAIN/ws/terminal|" .env.local
    sed -i "s|NEXT_PUBLIC_DOMAIN=.*|NEXT_PUBLIC_DOMAIN=$CUSTOM_DOMAIN|" .env.local
    sed -i "s|NODE_ENV=.*|NODE_ENV=production|" .env.local
    # If reverse proxy is on same host, API can also go through proxy
    # Uncomment if needed:
    # sed -i "s|API_PROXY_TARGET=.*|API_PROXY_TARGET=https://$CUSTOM_DOMAIN/api/backend|" .env.local
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing Next.js dependencies...${NC}"
    npm install
fi

# Check if port is already in use before starting
if check_port $FRONTEND_PORT; then
    echo -e "${YELLOW}Port $FRONTEND_PORT is already in use. Attempting to free it...${NC}"
    
    # Try to identify what's using the port
    echo -e "${YELLOW}Processes using port $FRONTEND_PORT:${NC}"
    lsof -i:$FRONTEND_PORT 2>/dev/null || echo "  (unable to identify)"
    
    # Kill processes on the port
    if lsof -ti:$FRONTEND_PORT >/dev/null 2>&1; then
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
        pkill -9 -f "npm run dev.*frontend-next" 2>/dev/null || true
        pkill -9 -f "next dev.*$FRONTEND_PORT" 2>/dev/null || true
        pkill -9 -f "\.bin/next dev" 2>/dev/null || true
        fuser -k -9 $FRONTEND_PORT/tcp 2>/dev/null || true
        sleep 2
        
        if check_port $FRONTEND_PORT; then
            echo -e "${RED}Failed to free port $FRONTEND_PORT. Please manually kill the process.${NC}"
            echo -e "${YELLOW}Run: lsof -i:$FRONTEND_PORT${NC}"
            exit 1
        else
            echo -e "${GREEN}Port $FRONTEND_PORT freed successfully${NC}"
        fi
    fi
fi

echo ""
start_service \
    "Next.js Frontend" \
    "npm run dev" \
    "$BASE_DIR/web.pid" \
    "$LOGS_DIR/web.log" \
    $FRONTEND_PORT \
    "$BASE_DIR/frontend-next"

# Function to monitor and restart frontend if it exits
monitor_frontend() {
    local frontend_pidfile="$BASE_DIR/web.pid"
    local restart_count=0
    local max_restarts=10
    
    while true; do
        sleep 5  # Check every 5 seconds
        
        # Check if frontend PID file exists and process is running
        if [ -f "$frontend_pidfile" ]; then
            local pid=$(cat "$frontend_pidfile")
            if ! ps -p $pid > /dev/null 2>&1; then
                echo ""
                echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                echo -e "${YELLOW}Frontend process (PID: $pid) has exited unexpectedly!${NC}"
                echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                rm -f "$frontend_pidfile"
                
                # Limit restart attempts to prevent infinite loops
                if [ $restart_count -ge $max_restarts ]; then
                    echo -e "${RED}Frontend has been restarted $max_restarts times. Stopping monitoring.${NC}"
                    echo -e "${YELLOW}Check the logs at $LOGS_DIR/web.log for errors.${NC}"
                    echo -e "${YELLOW}Manual restart required: cd $BASE_DIR && ./start-all.sh${NC}"
                    break
                fi
                
                # Check if port is in use and cleanup only if needed
                if check_port $FRONTEND_PORT; then
                    echo -e "${YELLOW}Port $FRONTEND_PORT is in use. Cleaning up before restart...${NC}"
                    lsof -ti:$FRONTEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
                    pkill -9 -f "npm run dev.*frontend-next" 2>/dev/null || true
                    pkill -9 -f "next dev.*$FRONTEND_PORT" 2>/dev/null || true
                    fuser -k -9 $FRONTEND_PORT/tcp 2>/dev/null || true
                    sleep 2
                    
                    # Verify port is free
                    if check_port $FRONTEND_PORT; then
                        echo -e "${RED}Cannot free port $FRONTEND_PORT for restart!${NC}"
                        echo -e "${YELLOW}Skipping restart attempt. Will retry on next check.${NC}"
                        continue
                    fi
                fi
                
                # Restart frontend
                restart_count=$((restart_count + 1))
                echo -e "${BLUE}Restarting frontend (attempt $restart_count/$max_restarts)...${NC}"
                cd "$BASE_DIR/frontend-next"
                nohup npm run dev > "$LOGS_DIR/web.log" 2>&1 &
                local new_pid=$!
                echo $new_pid > "$frontend_pidfile"
                
                # Wait and verify startup
                sleep 5
                if ps -p $new_pid > /dev/null 2>&1 && check_port $FRONTEND_PORT; then
                    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                    echo -e "${GREEN}Frontend restarted successfully! (PID: $new_pid)${NC}"
                    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                    echo ""
                else
                    echo -e "${RED}Failed to restart frontend!${NC}"
                    echo -e "${YELLOW}Check logs: tail -f $LOGS_DIR/web.log${NC}"
                    rm -f "$frontend_pidfile"
                fi
                cd "$BASE_DIR"
            fi
        fi
    done
}

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 All Services Started!                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo -e "  Next.js App: ${GREEN}http://$(hostname -I | awk '{print $1}'):$FRONTEND_PORT${NC}"
echo -e "  API:         ${GREEN}http://$(hostname -I | awk '{print $1}'):$API_PORT${NC}"
echo -e "  WebSocket:   ${GREEN}ws://$(hostname -I | awk '{print $1}'):$WEBSOCKET_PORT${NC}"
echo -e "  Terminal:    ${GREEN}ws://$(hostname -I | awk '{print $1}'):$TERMINAL_PORT${NC}"
echo ""

if [ -n "$CUSTOM_DOMAIN" ]; then
    echo -e "${BLUE}Custom Domain Configuration:${NC}"
    echo -e "  Domain:      ${GREEN}$CUSTOM_DOMAIN${NC}"
    echo -e "  Frontend:    ${GREEN}https://$CUSTOM_DOMAIN${NC}"
    echo -e "  Reverse Proxy: Required (nginx/Caddy) for HTTPS and WebSocket"
    echo -e "  See: ${YELLOW}CUSTOM-DOMAIN-GUIDE.md${NC} for setup"
    echo ""
fi

echo -e "${BLUE}First-Run Setup:${NC}"
echo -e "  ${GREEN}Open the Next.js app; you'll be prompted to create the first admin account.${NC}"
echo ""
echo -e "${BLUE}Logs Directory:${NC}"
echo -e "  ${GREEN}$LOGS_DIR/${NC}"
echo ""
echo -e "${BLUE}Commands:${NC}"
echo -e "  Stop:    ${GREEN}$BASE_DIR/stop-all.sh${NC}"
echo -e "  Restart: ${GREEN}$BASE_DIR/start-all.sh${NC}"
echo -e "  Logs:    ${GREEN}tail -f $LOGS_DIR/*.log${NC}"
echo ""
echo -e "${YELLOW}Note: Next.js may take 10-30 seconds to compile and be ready.${NC}"
echo ""
echo -e "${BLUE}Frontend Monitoring:${NC}"
echo -e "  ${GREEN}Monitoring frontend process and auto-restarting if it exits...${NC}"
echo -e "  ${YELLOW}Press Ctrl+C to stop monitoring (services will continue running)${NC}"
echo ""

# Start frontend monitoring in background
MONITOR_PID=$!
monitor_frontend &
MONITOR_PID=$!

# Function to cleanup on exit
cleanup() {
    echo -e "${YELLOW}Stopping frontend monitoring...${NC}"
    if [ -n "$MONITOR_PID" ] && ps -p $MONITOR_PID > /dev/null 2>&1; then
        kill $MONITOR_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}Services continue running. Use $BASE_DIR/stop-all.sh to stop all services.${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

echo -e "${GREEN}Frontend monitoring started. Press Ctrl+C to stop monitoring.${NC}"
echo ""

# Keep the main script running to maintain the monitoring
wait $MONITOR_PID
