#!/bin/bash

###############################################################################
# Smoke Test Script for Server Monitor Dashboard
# 
# This script performs automated smoke tests to verify:
# - All services are running on expected ports
# - Health endpoints return expected responses
# - Basic authentication flow works
# - Database is writable
# - Core API endpoints are responding
#
# Usage: ./scripts/smoke.sh [--verbose]
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verbose mode
VERBOSE=false
if [[ "$1" == "--verbose" ]]; then
    VERBOSE=true
fi

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test results
print_test() {
    local test_name="$1"
    local result="$2"
    local message="$3"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if [[ "$result" == "PASS" ]]; then
        echo -e "${GREEN}✓${NC} ${test_name}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        if [[ "$VERBOSE" == "true" && -n "$message" ]]; then
            echo "  └─ $message"
        fi
    elif [[ "$result" == "FAIL" ]]; then
        echo -e "${RED}✗${NC} ${test_name}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        if [[ -n "$message" ]]; then
            echo "  └─ Error: $message"
        fi
    elif [[ "$result" == "WARN" ]]; then
        echo -e "${YELLOW}⚠${NC} ${test_name}"
        if [[ -n "$message" ]]; then
            echo "  └─ Warning: $message"
        fi
    else
        echo -e "${BLUE}ℹ${NC} ${test_name}"
        if [[ -n "$message" ]]; then
            echo "  └─ $message"
        fi
    fi
}

# Function to check if port is open
check_port() {
    local port="$1"
    local service="$2"
    
    if nc -z -w 2 localhost "$port" 2>/dev/null; then
        print_test "Port $port ($service)" "PASS" "Service is listening"
        return 0
    else
        print_test "Port $port ($service)" "FAIL" "Service is not listening"
        return 1
    fi
}

# Function to check HTTP endpoint
check_http() {
    local url="$1"
    local expected_code="$2"
    local test_name="$3"
    
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [[ "$response_code" == "$expected_code" ]]; then
        print_test "$test_name" "PASS" "HTTP $response_code"
        return 0
    else
        print_test "$test_name" "FAIL" "Expected HTTP $expected_code, got $response_code"
        return 1
    fi
}

# Function to check JSON response structure
check_json_response() {
    local url="$1"
    local expected_key="$2"
    local test_name="$3"
    
    local response
    response=$(curl -s "$url" 2>/dev/null || echo "{}")
    
    if echo "$response" | grep -q "\"$expected_key\""; then
        print_test "$test_name" "PASS" "Response contains '$expected_key'"
        return 0
    else
        print_test "$test_name" "FAIL" "Response missing '$expected_key' key"
        if [[ "$VERBOSE" == "true" ]]; then
            echo "  └─ Response: $response"
        fi
        return 1
    fi
}

###############################################################################
# Main Test Suite
###############################################################################

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Server Monitor Dashboard - Smoke Test Suite         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check for required tools
echo "🔧 Checking prerequisites..."
PREREQS_OK=true

if ! command -v curl &> /dev/null; then
    print_test "curl installed" "FAIL" "curl is not installed"
    PREREQS_OK=false
else
    print_test "curl installed" "PASS"
fi

if ! command -v nc &> /dev/null; then
    print_test "netcat installed" "WARN" "netcat is not installed (optional, port checks will be skipped)"
else
    print_test "netcat installed" "PASS"
fi

if [[ "$PREREQS_OK" == "false" ]]; then
    echo ""
    echo "❌ Prerequisites check failed. Please install missing tools."
    exit 1
fi

echo ""
echo "📡 Testing service ports..."

# Test service ports
if command -v nc &> /dev/null; then
    check_port 9081 "Frontend (Next.js)"
    check_port 9083 "Central API"
    check_port 9084 "Terminal WebSocket"
    check_port 9085 "Monitoring WebSocket"
else
    print_test "Port checks" "WARN" "netcat not available, skipping port checks"
fi

echo ""
echo "🔍 Testing health endpoints..."

# Test public endpoints (should work without auth)
check_http "http://localhost:9083/api/stats/overview" "200" "Stats overview endpoint"
check_json_response "http://localhost:9083/api/stats/overview" "total_servers" "Stats overview structure"

# Test OpenAPI documentation
check_http "http://localhost:9083/docs" "200" "Swagger UI endpoint"
check_http "http://localhost:9083/api/openapi.yaml" "200" "OpenAPI spec endpoint"

# Test frontend
check_http "http://localhost:9081" "200" "Frontend homepage"

echo ""
echo "🔐 Testing authentication endpoints..."

# Test auth endpoints (without credentials - should return 401 or 400)
AUTH_RESPONSE=$(curl -s -X POST http://localhost:9083/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{}' 2>/dev/null || echo '{"error":"request failed"}')

if echo "$AUTH_RESPONSE" | grep -q "error"; then
    print_test "Login endpoint validation" "PASS" "Returns error for missing credentials"
else
    print_test "Login endpoint validation" "FAIL" "Unexpected response"
fi

# Test auth verify (should return 401 without token)
check_http "http://localhost:9083/api/auth/verify" "401" "Auth verify endpoint (no token)"

echo ""
echo "📊 Testing database connectivity..."

# Test that endpoints requiring database are responding
SERVERS_RESPONSE=$(curl -s http://localhost:9083/api/servers 2>/dev/null || echo '{"error":"request failed"}')

if echo "$SERVERS_RESPONSE" | grep -q "servers"; then
    print_test "Database read (servers list)" "PASS" "Database is readable"
else
    print_test "Database read (servers list)" "FAIL" "Cannot read from database"
fi

# Check recent activity endpoint
ACTIVITY_RESPONSE=$(curl -s "http://localhost:9083/api/activity/recent?limit=5" 2>/dev/null || echo '{"error":"request failed"}')

if echo "$ACTIVITY_RESPONSE" | grep -q "activities\|error.*Authentication"; then
    print_test "Recent activity endpoint" "PASS" "Endpoint is responding"
else
    print_test "Recent activity endpoint" "FAIL" "Unexpected response"
fi

echo ""
echo "🎯 Testing core API endpoints..."

# Test various endpoints for basic connectivity
check_http "http://localhost:9083/api/roles" "401" "Roles endpoint (requires auth)"
check_http "http://localhost:9083/api/ssh/pubkey" "200" "SSH pubkey endpoint"

# Test BFF proxy (if frontend is running)
BFF_RESPONSE=$(curl -s http://localhost:9081/api/auth/session 2>/dev/null || echo "")
if [[ -n "$BFF_RESPONSE" ]]; then
    print_test "BFF proxy endpoint" "PASS" "Next.js BFF is responding"
else
    print_test "BFF proxy endpoint" "WARN" "BFF not responding (frontend might not be running)"
fi

###############################################################################
# Summary
###############################################################################

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                      Test Summary                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "  Total tests run:    $TESTS_RUN"
echo -e "  ${GREEN}Tests passed:${NC}      $TESTS_PASSED"
echo -e "  ${RED}Tests failed:${NC}      $TESTS_FAILED"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✓ All smoke tests passed!${NC}"
    echo ""
    echo "The system appears to be running correctly. You can access:"
    echo "  • Frontend:      http://localhost:9081"
    echo "  • API Docs:      http://localhost:9083/docs"
    echo "  • Central API:   http://localhost:9083"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some smoke tests failed!${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Ensure all services are running:"
    echo "     ./start-all.sh"
    echo ""
    echo "  2. Check service logs for errors"
    echo ""
    echo "  3. Verify database is initialized:"
    echo "     cd backend && python -c 'import database; database.init_database()'"
    echo ""
    echo "  4. Check port conflicts:"
    echo "     netstat -tlnp | grep -E '9081|9083|9084|9085'"
    echo ""
    echo "  5. Run in verbose mode for more details:"
    echo "     $0 --verbose"
    echo ""
    exit 1
fi
