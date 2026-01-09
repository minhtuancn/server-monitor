#!/bin/bash
###############################################################################
# Server Monitor - Quick Test Script
# Tests CORS fixes and offline mode
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "======================================================================"
echo "  Server Monitor - Testing CORS Fixes and Offline Mode"
echo "======================================================================"
echo ""

# Test 1: Check if local assets exist
echo -e "${YELLOW}Test 1: Checking local assets...${NC}"

if [ -f "frontend/assets/vendor/fontawesome/css/all.min.css" ]; then
    echo -e "${GREEN}✓ Font Awesome CSS found${NC}"
else
    echo -e "${RED}✗ Font Awesome CSS not found${NC}"
    exit 1
fi

if [ -d "frontend/assets/vendor/fontawesome/webfonts" ]; then
    echo -e "${GREEN}✓ Font Awesome webfonts found${NC}"
else
    echo -e "${RED}✗ Font Awesome webfonts not found${NC}"
    exit 1
fi

if [ -f "frontend/assets/vendor/xterm/lib/xterm.js" ]; then
    echo -e "${GREEN}✓ xterm.js found${NC}"
else
    echo -e "${RED}✗ xterm.js not found${NC}"
    exit 1
fi

if [ -f "frontend/assets/vendor/xterm/css/xterm.css" ]; then
    echo -e "${GREEN}✓ xterm.css found${NC}"
else
    echo -e "${RED}✗ xterm.css not found${NC}"
    exit 1
fi

echo ""

# Test 2: Check HTML files don't reference CDN
echo -e "${YELLOW}Test 2: Checking HTML files for CDN references...${NC}"

if grep -r "cdnjs.cloudflare.com" frontend/*.html > /dev/null 2>&1; then
    echo -e "${RED}✗ Found CDN references in HTML files:${NC}"
    grep -n "cdnjs.cloudflare.com" frontend/*.html
    exit 1
else
    echo -e "${GREEN}✓ No CDN references found in HTML files${NC}"
fi

echo ""

# Test 3: Check HTML files reference local assets
echo -e "${YELLOW}Test 3: Checking HTML files reference local assets...${NC}"

if grep -q "/assets/vendor/fontawesome" frontend/dashboard.html; then
    echo -e "${GREEN}✓ dashboard.html uses local Font Awesome${NC}"
else
    echo -e "${RED}✗ dashboard.html doesn't reference local Font Awesome${NC}"
    exit 1
fi

if grep -q "/assets/vendor/xterm" frontend/terminal.html; then
    echo -e "${GREEN}✓ terminal.html uses local xterm.js${NC}"
else
    echo -e "${RED}✗ terminal.html doesn't reference local xterm.js${NC}"
    exit 1
fi

echo ""

# Test 4: Check CORS configuration
echo -e "${YELLOW}Test 4: Checking CORS configuration in security.py...${NC}"

if grep -q "CORS_ALLOW_ALL" backend/security.py; then
    echo -e "${GREEN}✓ CORS_ALLOW_ALL configuration found${NC}"
else
    echo -e "${RED}✗ CORS_ALLOW_ALL configuration not found${NC}"
    exit 1
fi

if grep -q "endswith(':9081')" backend/security.py; then
    echo -e "${GREEN}✓ Port 9081 auto-allow found${NC}"
else
    echo -e "${RED}✗ Port 9081 auto-allow not found${NC}"
    exit 1
fi

echo ""

# Test 5: Check API URL detection
echo -e "${YELLOW}Test 5: Checking API URL detection in auth.js...${NC}"

if grep -q "getApiBaseUrl" frontend/assets/js/auth.js; then
    echo -e "${GREEN}✓ getApiBaseUrl method found${NC}"
else
    echo -e "${RED}✗ getApiBaseUrl method not found${NC}"
    exit 1
fi

if grep -q "window.location.protocol" frontend/assets/js/auth.js; then
    echo -e "${GREEN}✓ Protocol detection found in auth.js${NC}"
else
    echo -e "${RED}✗ Protocol detection not found in auth.js${NC}"
    exit 1
fi

if grep -q "window.location.protocol" frontend/assets/js/api.js; then
    echo -e "${GREEN}✓ Protocol detection found in api.js${NC}"
else
    echo -e "${RED}✗ Protocol detection not found in api.js${NC}"
    exit 1
fi

echo ""

# Test 6: Check documentation
echo -e "${YELLOW}Test 6: Checking documentation files...${NC}"

if [ -f "OFFLINE_MODE.md" ]; then
    echo -e "${GREEN}✓ OFFLINE_MODE.md exists${NC}"
else
    echo -e "${RED}✗ OFFLINE_MODE.md not found${NC}"
    exit 1
fi

if [ -f "NGINX_PROXY_GUIDE.md" ]; then
    echo -e "${GREEN}✓ NGINX_PROXY_GUIDE.md exists${NC}"
else
    echo -e "${RED}✗ NGINX_PROXY_GUIDE.md not found${NC}"
    exit 1
fi

if [ -f "HUONG_DAN_TIENG_VIET.md" ]; then
    echo -e "${GREEN}✓ HUONG_DAN_TIENG_VIET.md exists${NC}"
else
    echo -e "${RED}✗ HUONG_DAN_TIENG_VIET.md not found${NC}"
    exit 1
fi

echo ""

# Test 7: Check CSP doesn't reference CDN
echo -e "${YELLOW}Test 7: Checking Content Security Policy...${NC}"

if grep "cdnjs.cloudflare.com" backend/security.py > /dev/null 2>&1; then
    echo -e "${RED}✗ CSP still references CDN${NC}"
    exit 1
else
    echo -e "${GREEN}✓ CSP doesn't reference CDN${NC}"
fi

echo ""

# Test 8: Check .env.example updated
echo -e "${YELLOW}Test 8: Checking .env.example...${NC}"

if grep -q "CORS_ALLOW_ALL" .env.example; then
    echo -e "${GREEN}✓ CORS_ALLOW_ALL documented in .env.example${NC}"
else
    echo -e "${YELLOW}⚠ CORS_ALLOW_ALL not documented in .env.example${NC}"
fi

echo ""
echo "======================================================================"
echo -e "${GREEN}  All Tests Passed! ✓${NC}"
echo "======================================================================"
echo ""
echo "Next Steps:"
echo "  1. Start the application: ./start-all.sh"
echo "  2. Open http://localhost:9081/login.html"
echo "  3. Check browser DevTools (F12) → Network tab"
echo "  4. Verify no requests to cdnjs.cloudflare.com"
echo "  5. Test login functionality"
echo ""
echo "Documentation:"
echo "  - OFFLINE_MODE.md - Offline mode setup"
echo "  - NGINX_PROXY_GUIDE.md - Nginx reverse proxy config"
echo "  - HUONG_DAN_TIENG_VIET.md - Vietnamese guide"
echo ""
