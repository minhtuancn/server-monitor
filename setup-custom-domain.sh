#!/bin/bash

###############################################################################
# Server Monitor - Custom Domain Setup Helper
# Usage: ./setup-custom-domain.sh mon.go7s.net
#        ./setup-custom-domain.sh example.com
###############################################################################

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

if [ $# -eq 0 ]; then
    echo -e "${BLUE}Server Monitor - Custom Domain Setup${NC}"
    echo ""
    echo "Usage: $0 <domain>"
    echo ""
    echo "Examples:"
    echo "  $0 mon.go7s.net"
    echo "  $0 monitoring.example.com"
    echo "  $0 mon.local"
    echo ""
    echo "This script configures:"
    echo "  1. Backend CORS to accept your domain"
    echo "  2. Frontend WebSocket URLs to use your domain"
    echo "  3. Environment variables for production deployment"
    echo ""
    echo "After running this script:"
    echo "  1. Start services with: CUSTOM_DOMAIN=$1 ./start-all.sh"
    echo "  2. Set up a reverse proxy (nginx/Caddy) pointing to localhost:9081"
    echo "  3. Configure SSL/TLS certificates for HTTPS"
    echo ""
    exit 0
fi

DOMAIN="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Server Monitor - Custom Domain Setup                    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Validate domain
if ! [[ "$DOMAIN" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?(\.[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?)*$ ]]; then
    echo -e "${RED}✗ Invalid domain format: $DOMAIN${NC}"
    exit 1
fi

echo -e "${GREEN}Domain: $DOMAIN${NC}"
echo ""

# Create/update .env.local if needed
echo -e "${BLUE}Step 1: Updating frontend configuration...${NC}"
if [ ! -f "$SCRIPT_DIR/frontend-next/.env.local" ]; then
    cp "$SCRIPT_DIR/frontend-next/.env.example" "$SCRIPT_DIR/frontend-next/.env.local"
    echo -e "${GREEN}  ✓ Created .env.local from template${NC}"
else
    echo -e "${YELLOW}  ℹ Using existing .env.local${NC}"
fi

# Update .env.local
cd "$SCRIPT_DIR/frontend-next"

echo -e "${BLUE}Step 2: Configuring WebSocket and API endpoints...${NC}"

# Set WebSocket URLs for HTTPS
sed -i "s|NEXT_PUBLIC_MONITORING_WS_URL=.*|NEXT_PUBLIC_MONITORING_WS_URL=wss://$DOMAIN/ws/monitoring|" .env.local
echo -e "${GREEN}  ✓ Set monitoring WebSocket URL${NC}"

sed -i "s|NEXT_PUBLIC_TERMINAL_WS_URL=.*|NEXT_PUBLIC_TERMINAL_WS_URL=wss://$DOMAIN/ws/terminal|" .env.local
echo -e "${GREEN}  ✓ Set terminal WebSocket URL${NC}"

# Set domain identifier
sed -i "s|NEXT_PUBLIC_DOMAIN=.*|NEXT_PUBLIC_DOMAIN=$DOMAIN|" .env.local || echo "NEXT_PUBLIC_DOMAIN=$DOMAIN" >> .env.local
echo -e "${GREEN}  ✓ Set domain identifier${NC}"

# Set production environment
sed -i "s|NODE_ENV=.*|NODE_ENV=production|" .env.local || echo "NODE_ENV=production" >> .env.local
echo -e "${GREEN}  ✓ Set NODE_ENV=production${NC}"

# Ensure vars are in file (fallback if sed didn't work)
if ! grep -q "NEXT_PUBLIC_DOMAIN=" .env.local; then
    echo "" >> .env.local
    echo "NEXT_PUBLIC_DOMAIN=$DOMAIN" >> .env.local
fi
if ! grep -q "NODE_ENV=" .env.local; then
    echo "NODE_ENV=production" >> .env.local
fi

# API backend (uncomment the custom domain option if you want reverse proxy)
echo ""
echo -e "${BLUE}Step 3: Configuration details...${NC}"
echo ""
echo -e "${YELLOW}frontend-next/.env.local updated with:${NC}"
echo "  NEXT_PUBLIC_MONITORING_WS_URL=wss://$DOMAIN/ws/monitoring"
echo "  NEXT_PUBLIC_TERMINAL_WS_URL=wss://$DOMAIN/ws/terminal"
echo "  NEXT_PUBLIC_DOMAIN=$DOMAIN"
echo "  NODE_ENV=production"
echo ""

echo -e "${BLUE}Step 4: Starting services...${NC}"
echo ""
echo -e "${YELLOW}To start with custom domain, run:${NC}"
echo ""
echo "  CUSTOM_DOMAIN=$DOMAIN ./start-all.sh"
echo ""
echo -e "${YELLOW}This will automatically:${NC}"
echo "  • Export ALLOWED_FRONTEND_DOMAINS=$DOMAIN to backend"
echo "  • Configure CORS headers to accept requests from $DOMAIN"
echo "  • Start all services (API, WebSocket, Frontend)"
echo ""

echo -e "${BLUE}Step 5: Reverse Proxy Setup${NC}"
echo ""
echo -e "${YELLOW}After starting services, set up a reverse proxy:${NC}"
echo ""
echo -e "${GREEN}Option 1: Using Nginx${NC}"
echo "  See CUSTOM-DOMAIN-GUIDE.md for complete Nginx configuration"
echo "  Key locations:"
echo "    / → localhost:9081 (Next.js frontend)"
echo "    /api/proxy/* → localhost:9083 (Backend API)"
echo "    /ws/* → localhost:9085/9084 (WebSocket)"
echo ""

echo -e "${GREEN}Option 2: Using Caddy${NC}"
echo "  Quick setup:"
echo "    $DOMAIN {"
echo "        reverse_proxy * localhost:9081"
echo "        reverse_proxy /api/proxy/* localhost:9083"
echo "        reverse_proxy /ws/* localhost:9085"
echo "    }"
echo ""

echo -e "${BLUE}Step 6: HTTPS/SSL Setup${NC}"
echo ""
echo -e "${YELLOW}For production, you need HTTPS:${NC}"
echo "  • Caddy: Automatic SSL via Let's Encrypt"
echo "  • Nginx: Use Let's Encrypt (Certbot) or upload certificates"
echo "  • See: HTTPS-SETUP.md for details"
echo ""

echo -e "${GREEN}✓ Custom domain configuration ready!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review CUSTOM-DOMAIN-GUIDE.md for detailed setup"
echo "  2. Configure reverse proxy (Nginx/Caddy)"
echo "  3. Set up HTTPS/SSL certificates"
echo "  4. Run: CUSTOM_DOMAIN=$DOMAIN ./start-all.sh"
echo "  5. Visit: https://$DOMAIN"
echo ""
