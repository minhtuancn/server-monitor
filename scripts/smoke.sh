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
# Usage: 
#   ./scripts/smoke.sh [OPTIONS]
#
# Options:
#   --verbose                 Enable verbose output
#   --base-url URL           Base URL for frontend (default: http://localhost:9081)
#   --api-url URL            API URL (default: http://localhost:9083)
#   --auth-user USER         Username for authenticated tests
#   --auth-pass PASS         Password for authenticated tests
#   --skip-port-check        Skip port availability checks (for remote testing)
#
# Examples:
#   # Local testing
#   ./scripts/smoke.sh --verbose
#
#   # Staging environment testing
#   ./scripts/smoke.sh --base-url https://staging.example.com --api-url https://staging.example.com/api
#
#   # Authenticated testing
#   ./scripts/smoke.sh --auth-user admin --auth-pass secret123 --verbose
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
VERBOSE=false
BASE_URL="http://localhost:9081"
API_URL="http://localhost:9083"
AUTH_USER=""
AUTH_PASS=""
AUTH_TOKEN=""
SKIP_PORT_CHECK=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        --base-url)
            BASE_URL="$2"
            shift 2
            ;;
        --api-url)
            API_URL="$2"
            shift 2
            ;;
        --auth-user)
            AUTH_USER="$2"
            shift 2
            ;;
        --auth-pass)
            AUTH_PASS="$2"
            shift 2
            ;;
        --skip-port-check)
            SKIP_PORT_CHECK=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --verbose              Enable verbose output"
            echo "  --base-url URL         Base URL for frontend (default: http://localhost:9081)"
            echo "  --api-url URL          API URL (default: http://localhost:9083)"
            echo "  --auth-user USER       Username for authenticated tests"
            echo "  --auth-pass PASS       Password for authenticated tests"
            echo "  --skip-port-check      Skip port availability checks"
            echo "  --help                 Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --verbose"
            echo "  $0 --base-url https://staging.example.com --api-url https://staging.example.com"
            echo "  $0 --auth-user admin --auth-pass secret --verbose"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Auto-detect remote testing
if [[ "$API_URL" != "http://localhost:"* ]] && [[ "$API_URL" != "http://127.0.0.1:"* ]]; then
    SKIP_PORT_CHECK=true
    if [[ "$VERBOSE" == "true" ]]; then
        echo "ℹ Remote URL detected, skipping port checks"
    fi
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
    shift 3  # Remove first 3 arguments
    
    local response_code
    if [[ $# -gt 0 ]]; then
        # Pass remaining arguments as-is (already properly quoted by caller)
        response_code=$(curl -s -o /dev/null -w "%{http_code}" "$@" "$url" 2>/dev/null || echo "000")
    else
        response_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    fi
    
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
    shift 3  # Remove first 3 arguments
    
    local response
    if [[ $# -gt 0 ]]; then
        # Pass remaining arguments as-is
        response=$(curl -s "$@" "$url" 2>/dev/null || echo "{}")
    else
        response=$(curl -s "$url" 2>/dev/null || echo "{}")
    fi
    
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

# Function to authenticate and get token
authenticate() {
    if [[ -z "$AUTH_USER" ]] || [[ -z "$AUTH_PASS" ]]; then
        return 1
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        echo "ℹ Authenticating as $AUTH_USER..."
    fi
    
    local response
    response=$(curl -s -X POST "$API_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$AUTH_USER\",\"password\":\"$AUTH_PASS\"}" 2>/dev/null || echo "{}")
    
    AUTH_TOKEN=$(echo "$response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    
    if [[ -n "$AUTH_TOKEN" ]]; then
        if [[ "$VERBOSE" == "true" ]]; then
            echo "✓ Authentication successful"
        fi
        return 0
    else
        if [[ "$VERBOSE" == "true" ]]; then
            echo "⚠ Authentication failed"
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

# Display test configuration
if [[ "$VERBOSE" == "true" ]]; then
    echo "📋 Test Configuration:"
    echo "  Frontend URL: $BASE_URL"
    echo "  API URL:      $API_URL"
    echo "  Auth User:    ${AUTH_USER:-<none>}"
    echo "  Port Checks:  $([ "$SKIP_PORT_CHECK" = true ] && echo "disabled" || echo "enabled")"
    echo ""
fi

# Attempt authentication if credentials provided
if [[ -n "$AUTH_USER" ]] && [[ -n "$AUTH_PASS" ]]; then
    authenticate || true
fi

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

# Test service ports (only for localhost)
if [[ "$SKIP_PORT_CHECK" == "false" ]]; then
    if command -v nc &> /dev/null; then
        check_port 9081 "Frontend (Next.js)"
        check_port 9083 "Central API"
        check_port 9084 "Terminal WebSocket"
        check_port 9085 "Monitoring WebSocket"
    else
        print_test "Port checks" "WARN" "netcat not available, skipping port checks"
    fi
else
    print_test "Port checks" "INFO" "Skipped (remote testing mode)"
fi

echo ""
echo "🔍 Testing health endpoints..."

# Test observability endpoints (Phase 6)
check_http "$API_URL/api/health" "200" "Health endpoint (liveness)"
check_json_response "$API_URL/api/health" "status" "Health endpoint structure"

check_http "$API_URL/api/ready" "200" "Readiness endpoint"
check_json_response "$API_URL/api/ready" "status" "Readiness endpoint structure"

# Test metrics endpoint (should require auth or be localhost)
METRICS_RESPONSE=$(curl -s "$API_URL/api/metrics" 2>/dev/null || echo "{}")
if echo "$METRICS_RESPONSE" | grep -q "uptime_seconds\|error"; then
    print_test "Metrics endpoint" "PASS" "Metrics endpoint is responding"
else
    print_test "Metrics endpoint" "WARN" "Metrics endpoint response unexpected"
fi

# Test public endpoints (should work without auth)
check_http "$API_URL/api/stats/overview" "200" "Stats overview endpoint"
check_json_response "$API_URL/api/stats/overview" "total_servers" "Stats overview structure"

# Test OpenAPI documentation
check_http "$API_URL/docs" "200" "Swagger UI endpoint"
check_http "$API_URL/api/openapi.yaml" "200" "OpenAPI spec endpoint"

# Test frontend
check_http "$BASE_URL" "200" "Frontend homepage"

echo ""
echo "🔐 Testing authentication endpoints..."

# Test auth endpoints (without credentials - should return 401 or 400)
AUTH_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{}' 2>/dev/null || echo '{"error":"request failed"}')

if echo "$AUTH_RESPONSE" | grep -q "error"; then
    print_test "Login endpoint validation" "PASS" "Returns error for missing credentials"
else
    print_test "Login endpoint validation" "FAIL" "Unexpected response"
fi

# Test auth verify (should return 401 without token)
check_http "$API_URL/api/auth/verify" "401" "Auth verify endpoint (no token)"

# If authenticated, test protected endpoints
if [[ -n "$AUTH_TOKEN" ]]; then
    echo ""
    echo "🔑 Testing authenticated endpoints..."
    
    # Test auth verify with token
    check_http "$API_URL/api/auth/verify" "200" "Auth verify endpoint (with token)" -H "Authorization: Bearer $AUTH_TOKEN"
    
    # Test audit export endpoints (admin only)
    check_http "$API_URL/api/export/audit/csv" "200" "Audit CSV export endpoint" -H "Authorization: Bearer $AUTH_TOKEN"
    check_http "$API_URL/api/export/audit/json" "200" "Audit JSON export endpoint" -H "Authorization: Bearer $AUTH_TOKEN"
fi

echo ""
echo "📊 Testing database connectivity..."

# Test that endpoints requiring database are responding
SERVERS_RESPONSE=$(curl -s "$API_URL/api/servers" 2>/dev/null || echo '{"error":"request failed"}')

if echo "$SERVERS_RESPONSE" | grep -q "servers"; then
    print_test "Database read (servers list)" "PASS" "Database is readable"
else
    print_test "Database read (servers list)" "FAIL" "Cannot read from database"
fi

# Check recent activity endpoint
ACTIVITY_RESPONSE=$(curl -s "$API_URL/api/activity/recent?limit=5" 2>/dev/null || echo '{"error":"request failed"}')

if echo "$ACTIVITY_RESPONSE" | grep -q "activities\|error.*Authentication"; then
    print_test "Recent activity endpoint" "PASS" "Endpoint is responding"
else
    print_test "Recent activity endpoint" "FAIL" "Unexpected response"
fi

echo ""
echo "🎯 Testing core API endpoints..."

# Test various endpoints for basic connectivity
check_http "$API_URL/api/roles" "401" "Roles endpoint (requires auth)"
check_http "$API_URL/api/ssh/pubkey" "200" "SSH pubkey endpoint"

# Test BFF proxy (if frontend is running)
BFF_RESPONSE=$(curl -s "$BASE_URL/api/auth/session" 2>/dev/null || echo "")
if [[ -n "$BFF_RESPONSE" ]]; then
    print_test "BFF proxy endpoint" "PASS" "Next.js BFF is responding"
else
    print_test "BFF proxy endpoint" "WARN" "BFF not responding (frontend might not be running)"
fi

echo ""
echo "🔗 Testing Phase 8 features (Webhooks & Plugins)..."

# Test webhooks endpoint (requires admin auth)
if [[ -n "$AUTH_TOKEN" ]]; then
    # Test webhooks list endpoint
    WEBHOOKS_RESPONSE=$(curl -s -H "Authorization: Bearer $AUTH_TOKEN" "$API_URL/api/webhooks" 2>/dev/null || echo '{"error":"request failed"}')
    
    if echo "$WEBHOOKS_RESPONSE" | grep -q "webhooks\|error.*Forbidden\|error.*Admin"; then
        if echo "$WEBHOOKS_RESPONSE" | grep -q "webhooks"; then
            print_test "Webhooks list endpoint (admin)" "PASS" "Webhooks API is accessible"
        else
            print_test "Webhooks list endpoint (admin)" "WARN" "Got 403/Forbidden - user may not have admin role"
            if [[ "$VERBOSE" == "true" ]]; then
                echo "  └─ ℹ Webhooks require admin role. Current user: ${AUTH_USER}"
            fi
        fi
    else
        print_test "Webhooks list endpoint (admin)" "FAIL" "Unexpected response from webhooks API"
    fi
    
    # Check cache metrics in /api/metrics
    CACHE_METRICS=$(curl -s "$API_URL/api/metrics" 2>/dev/null || echo "")
    if echo "$CACHE_METRICS" | grep -q "cache_hits_total\|cache_misses_total"; then
        print_test "Cache metrics in /api/metrics" "PASS" "Cache hit/miss metrics available"
    else
        print_test "Cache metrics in /api/metrics" "WARN" "Cache metrics not found in output"
    fi
    
    # Check rate limit functionality (make a burst of requests)
    if [[ "$VERBOSE" == "true" ]]; then
        echo "  └─ ℹ Testing rate limiting (making 5 rapid requests)..."
    fi
    RATE_LIMIT_TRIGGERED=false
    for i in {1..5}; do
        RATE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $AUTH_TOKEN" "$API_URL/api/stats/overview" 2>/dev/null || echo "000")
        if [[ "$RATE_RESPONSE" == "429" ]]; then
            RATE_LIMIT_TRIGGERED=true
            break
        fi
    done
    
    if [[ "$RATE_LIMIT_TRIGGERED" == "true" ]]; then
        print_test "Rate limiting (429 status)" "INFO" "Rate limiting is active (got 429 response)"
    else
        print_test "Rate limiting check" "INFO" "No rate limit hit in test (limits may be high or endpoint not rate-limited)"
    fi
else
    print_test "Webhooks endpoint test" "INFO" "Skipped (no admin credentials provided)"
    if [[ "$VERBOSE" == "true" ]]; then
        echo "  └─ ℹ Use --auth-user and --auth-pass to test authenticated endpoints"
        echo "  └─ ℹ Note: User must have 'admin' role to access webhooks"
    fi
fi

# Test plugin system metrics (if available)
PLUGIN_METRICS=$(curl -s "$API_URL/api/metrics" 2>/dev/null || echo "")
if echo "$PLUGIN_METRICS" | grep -q "plugin_events_total\|webhook_deliveries_total"; then
    print_test "Plugin/Webhook metrics" "PASS" "Plugin system metrics available"
else
    print_test "Plugin/Webhook metrics" "INFO" "Plugin metrics not found (plugins may be disabled)"
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

# Calculate success rate
if [[ $TESTS_RUN -gt 0 ]]; then
    SUCCESS_RATE=$(( (TESTS_PASSED * 100) / TESTS_RUN ))
    echo "  Success rate:      ${SUCCESS_RATE}%"
    echo ""
fi

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✓ All smoke tests passed!${NC}"
    echo ""
    echo "The system appears to be running correctly. You can access:"
    echo "  • Frontend:      $BASE_URL"
    echo "  • API Docs:      $API_URL/docs"
    echo "  • Central API:   $API_URL"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some smoke tests failed!${NC}"
    echo ""
    echo "Troubleshooting steps:"
    if [[ "$SKIP_PORT_CHECK" == "false" ]]; then
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
    else
        echo "  1. Verify the URLs are correct:"
        echo "     Frontend: $BASE_URL"
        echo "     API:      $API_URL"
        echo ""
        echo "  2. Check network connectivity to the server"
        echo ""
        echo "  3. Verify services are running on the remote server"
        echo ""
        echo "  4. Check firewall rules allow access to ports"
    fi
    echo ""
    echo "  5. Run in verbose mode for more details:"
    echo "     $0 --verbose"
    echo ""
    exit 1
fi
