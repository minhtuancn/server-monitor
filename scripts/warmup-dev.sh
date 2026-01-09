#!/bin/bash

# Dev Warm-up Script for Server Monitor Dashboard
# Triggers Next.js compilation for commonly used routes to reduce cold start lag

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_URL="${FRONTEND_URL:-http://localhost:9081}"
API_URL="${API_URL:-http://localhost:9083}"
WARMUP_TIMEOUT="${WARMUP_TIMEOUT:-10}"

echo -e "${YELLOW}=== Next.js Dev Warm-up Script ===${NC}"
echo "This script will trigger compilation of commonly used routes"
echo "Frontend URL: $FRONTEND_URL"
echo "API URL: $API_URL"
echo "Timeout per request: ${WARMUP_TIMEOUT}s"
echo ""

# Function to check if service is responding
check_service() {
    local url=$1
    local name=$2
    echo -e "${YELLOW}Checking $name...${NC}"
    if curl -s --connect-timeout 5 "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $name is responding${NC}"
        return 0
    else
        echo -e "${RED}✗ $name is not responding${NC}"
        return 1
    fi
}

# Function to warm up a route
warmup_route() {
    local url=$1
    local name=$2
    echo -e "${YELLOW}Warming up: $name${NC}"
    if curl -s --max-time "$WARMUP_TIMEOUT" "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $name compiled${NC}"
    else
        echo -e "${RED}✗ Failed to warm up $name (this might be normal if auth is required)${NC}"
    fi
}

# Check if services are running
echo -e "\n${YELLOW}=== Checking Services ===${NC}"
frontend_up=false
api_up=false

if check_service "$FRONTEND_URL" "Frontend"; then
    frontend_up=true
fi

if check_service "$API_URL/api/health" "Backend API"; then
    api_up=true
fi

if [ "$frontend_up" = false ] && [ "$api_up" = false ]; then
    echo -e "\n${RED}ERROR: Both frontend and backend are not responding.${NC}"
    echo "Please start the services first:"
    echo "  Terminal 1: ./start-all.sh"
    echo "  Terminal 2: cd frontend-next && npm run dev"
    exit 1
fi

# Warm up frontend routes
if [ "$frontend_up" = true ]; then
    echo -e "\n${YELLOW}=== Warming up Frontend Routes ===${NC}"
    warmup_route "$FRONTEND_URL" "Home page"
    warmup_route "$FRONTEND_URL/en/dashboard" "Dashboard (English)"
    warmup_route "$FRONTEND_URL/en/settings" "Settings page"
    warmup_route "$FRONTEND_URL/en/servers" "Servers list"
    warmup_route "$FRONTEND_URL/en/terminal" "Terminal page"
    warmup_route "$FRONTEND_URL/en/users" "Users page"
    warmup_route "$FRONTEND_URL/vi/dashboard" "Dashboard (Vietnamese)"
else
    echo -e "\n${YELLOW}Skipping frontend warm-up (service not running)${NC}"
fi

# Warm up API routes (through Next.js proxy)
if [ "$frontend_up" = true ] && [ "$api_up" = true ]; then
    echo -e "\n${YELLOW}=== Warming up API Proxy Routes ===${NC}"
    warmup_route "$FRONTEND_URL/api/proxy/api/stats/overview" "Stats overview"
    warmup_route "$FRONTEND_URL/api/proxy/api/servers" "Servers API"
    warmup_route "$FRONTEND_URL/api/proxy/api/health" "Health check"
else
    echo -e "\n${YELLOW}Skipping API proxy warm-up${NC}"
fi

echo -e "\n${GREEN}=== Warm-up Complete ===${NC}"
echo "Your Next.js dev server should now be more responsive!"
echo ""
echo -e "${YELLOW}Note:${NC} Some routes may show errors if they require authentication."
echo "This is normal - the compilation is still triggered."
echo ""
echo -e "${YELLOW}Tip:${NC} Run this script after starting dev servers for the first time."
