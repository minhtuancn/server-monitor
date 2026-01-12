#!/bin/bash

#
# E2E Test Runner with Rate Limiting Disabled
# 
# This script temporarily disables rate limiting in the backend to allow
# E2E tests to run successfully without hitting rate limits.
#
# WARNING: Only use in test/dev environments, NEVER in production!
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Server Monitor E2E Tests - Rate Limiting Disabled       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if backend is running
if ! curl -s -m 2 http://172.22.0.103:9083/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend is not running or not responding${NC}"
    echo -e "${YELLOW}Please start services first: cd /opt/server-monitor && ./start-all.sh${NC}"
    exit 1
fi

# Check if frontend is running
if ! curl -s -m 2 http://172.22.0.103:9081 > /dev/null 2>&1; then
    echo -e "${RED}❌ Frontend is not running or not responding${NC}"
    echo -e "${YELLOW}Please start services first: cd /opt/server-monitor && ./start-all.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backend and Frontend are running${NC}"
echo ""

# Export environment variable to disable rate limiting
export DISABLE_RATE_LIMIT=true

echo -e "${YELLOW}⚠️  Rate limiting is DISABLED for this test run${NC}"
echo -e "${YELLOW}   Backend needs to be restarted with DISABLE_RATE_LIMIT=true${NC}"
echo ""

# Restart backend with rate limiting disabled
echo -e "${BLUE}Restarting backend with rate limiting disabled...${NC}"

# Kill existing backend
BACKEND_PID=$(lsof -ti:9083 || echo "")
if [ -n "$BACKEND_PID" ]; then
    kill -9 $BACKEND_PID 2>/dev/null || true
    sleep 2
fi

# Start backend with DISABLE_RATE_LIMIT=true
cd /opt/server-monitor/backend
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${YELLOW}Warning: No virtual environment found, using system Python${NC}"
fi
DISABLE_RATE_LIMIT=true nohup python3 central_api.py > ../logs/api.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
for i in {1..15}; do
    if lsof -i:9083 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
        break
    fi
    sleep 1
done

if ! lsof -i:9083 > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

# Wait a bit for backend to be fully ready
sleep 3

echo ""
echo -e "${BLUE}Running E2E tests...${NC}"
echo ""

# Run Playwright tests
cd /opt/server-monitor/e2e-tests

# Parse command line arguments
TEST_PROJECT="${1:-Desktop Chrome}"
TEST_PATTERN="${2:-}"

if [ -n "$TEST_PATTERN" ]; then
    echo -e "${BLUE}Running tests matching: ${TEST_PATTERN}${NC}"
    npx playwright test "$TEST_PATTERN" --project="$TEST_PROJECT" --reporter=line
else
    echo -e "${BLUE}Running all tests for project: ${TEST_PROJECT}${NC}"
    npx playwright test --project="$TEST_PROJECT" --reporter=line --workers=1
fi

TEST_EXIT_CODE=$?

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}║              E2E Tests Completed Successfully              ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}║                 E2E Tests Failed                           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
fi

echo ""
echo -e "${BLUE}Test Results:${NC}"
echo -e "  HTML Report: ${GREEN}e2e-tests/playwright-report/index.html${NC}"
echo -e "  JSON Report: ${GREEN}e2e-tests/test-results.json${NC}"
echo ""

echo -e "${YELLOW}⚠️  Remember to restart services normally after testing:${NC}"
echo -e "${YELLOW}   cd /opt/server-monitor && ./stop-all.sh && ./start-all.sh${NC}"
echo ""

exit $TEST_EXIT_CODE
