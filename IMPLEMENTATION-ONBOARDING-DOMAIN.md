# Implementation Summary: First-Run Onboarding & Custom Domain Support

**Date**: January 9, 2026  
**Status**: ✅ COMPLETE & TESTED

---

## Overview

This implementation adds two critical features to Server Monitor:

1. **First-Run Onboarding**: New instances automatically prompt to create the first admin user
2. **Custom Domain Support**: Deploy to any domain (e.g., `mon.go7s.net`) with full API/WebSocket connectivity

---

## 1. First-Run Onboarding ✅

### What It Does

- When a fresh Server Monitor instance starts with no users, visitors are automatically directed to a setup page
- Users create the initial admin account with username, email, and password
- Upon successful setup, the user is automatically logged in and taken to the dashboard
- Subsequent visits bypass setup and show the login page

### Backend Changes

**File**: `backend/user_management.py`

- Added `SKIP_DEFAULT_ADMIN` environment variable support
- When `SKIP_DEFAULT_ADMIN=true`, no default admin account is auto-created
- Allows proper first-run setup flow

**File**: `backend/central_api.py`

- **New Endpoint**: `GET /api/setup/status`

  - Public endpoint (no auth required)
  - Returns `{"needs_setup": true|false}`
  - Checks if any users exist in database

- **New Endpoint**: `POST /api/setup/initialize`
  - Public endpoint (only works when no users exist)
  - Creates first admin user from request body: `{username, email, password}`
  - Returns JWT token and user data
  - Only executes once; subsequent calls return "already completed" error

### Frontend Changes

**File**: `frontend-next/middleware.ts`

- Detects first-run setup requirement by calling `/api/proxy/api/setup/status`
- If `needs_setup=true` and user not authenticated, redirects to `/{locale}/setup`
- Otherwise, redirects to `/{locale}/login`

**File**: `frontend-next/src/app/[locale]/(auth)/setup/page.tsx` (NEW)

- Setup form with fields: username, email, password, confirm password
- Form validation:
  - Username: 3+ characters
  - Email: valid format
  - Password: 8+ chars, uppercase, lowercase, number
  - Confirm: must match password
- Submits to `/api/auth/setup`
- On success, redirects to `/{locale}/dashboard`

**File**: `frontend-next/src/app/api/auth/setup/route.ts` (NEW)

- Proxies POST request to backend's `/api/setup/initialize`
- Sets `auth_token` cookie on success
- Returns user data for client storage

### Scripts

**Files**: `start-dev.sh`, `start-all.sh`

- Export `SKIP_DEFAULT_ADMIN=true` by default
- Enables first-run setup flow on fresh instances

### How to Test

```bash
# Fresh setup (no existing users)
mv data/servers.db data/servers.db.bak
./stop-all.sh
./start-all.sh

# Visit http://localhost:9081
# → Redirected to /{locale}/setup
# → Create admin account
# → Logged in and viewing dashboard
```

---

## 2. Custom Domain Support ✅

### What It Does

- Configure Server Monitor to work with custom domains like `mon.go7s.net`
- Frontend, API, WebSocket, and agent connections all work through the custom domain
- Supports both HTTP (dev) and HTTPS (prod) deployments
- Works behind reverse proxies (Nginx, Caddy)

### Backend Changes

**File**: `backend/security.py`

- **New CORS Support**: `ALLOWED_FRONTEND_DOMAINS` environment variable
  - Comma-separated list of allowed frontend domains
  - Automatically adds HTTP/HTTPS variants
  - Example: `ALLOWED_FRONTEND_DOMAINS=mon.go7s.net,monitoring.example.com`

### Frontend Changes

**File**: `frontend-next/.env.example`

- **New Documentation**: Added Custom Domain Support section with examples
- **New Variables**:
  - `NEXT_PUBLIC_DOMAIN`: Current domain identifier (e.g., `mon.go7s.net`)
  - `NEXT_PUBLIC_MONITORING_WS_URL`: WebSocket URL for monitoring
  - `NEXT_PUBLIC_TERMINAL_WS_URL`: WebSocket URL for terminal
  - Example for `mon.go7s.net`:
    ```
    NEXT_PUBLIC_MONITORING_WS_URL=wss://mon.go7s.net/ws/monitoring
    NEXT_PUBLIC_TERMINAL_WS_URL=wss://mon.go7s.net/ws/terminal
    ```

**File**: `frontend-next/src/lib/config.ts`

- Added `CURRENT_DOMAIN` export for domain-aware configuration
- Improved comments explaining dev vs. prod WebSocket setup

### Scripts

**File**: `start-all.sh`

- **New Variable**: `CUSTOM_DOMAIN` environment variable

  - Usage: `CUSTOM_DOMAIN=mon.go7s.net ./start-all.sh`
  - Automatically configures backend CORS and frontend URLs
  - Updates `.env.local` with production WebSocket URLs
  - Sets `NODE_ENV=production`

- **Automatic Configuration**:
  - Sets `ALLOWED_FRONTEND_DOMAINS` for backend CORS
  - Updates frontend WebSocket URLs to `wss://DOMAIN/ws/*`
  - Sets production environment flags

**File**: `setup-custom-domain.sh` (NEW)

- Interactive helper script for custom domain setup
- Usage: `./setup-custom-domain.sh mon.go7s.net`
- Validates domain format
- Updates `.env.local` with proper WebSocket URLs
- Provides Nginx/Caddy configuration examples
- Guides users through reverse proxy and HTTPS setup

### Documentation

**File**: `CUSTOM-DOMAIN-GUIDE.md` (NEW)

- **Quick Setup** section with step-by-step instructions
- **Environment Variables** reference table
- **Typical Deployment Scenarios**:
  1. Development (localhost + LAN access)
  2. Production (custom domain with reverse proxy)
  3. Multiple domains / subdomains
- **Reverse Proxy Examples**:
  - Complete Nginx configuration with SSL
  - Caddy quick setup
  - WebSocket proxy configuration
- **Agent Server Connections** guide
- **Troubleshooting** section with common issues
- **Security Checklist** for production

### How to Test

```bash
# Setup custom domain
./setup-custom-domain.sh mon.go7s.net

# Start with custom domain
CUSTOM_DOMAIN=mon.go7s.net ./start-all.sh

# Verify configuration
grep NEXT_PUBLIC_MONITORING_WS_URL frontend-next/.env.local
# Should output: wss://mon.go7s.net/ws/monitoring

# Frontend should work at http://localhost:9081 (dev)
# Production: set up reverse proxy to https://mon.go7s.net
```

---

## Integration Points

### First-Run Onboarding + Custom Domain

- First-run setup page works with any domain
- Middleware detects domain automatically
- Setup form submits to domain-aware API proxy
- After setup, user can access dashboard from any configured domain

### API Proxy Flow

1. Browser → `https://mon.go7s.net/api/proxy/api/setup/status`
2. Reverse proxy → `http://localhost:9081/api/proxy/api/setup/status`
3. Next.js BFF → `http://localhost:9083/api/setup/status`
4. Backend returns `{"needs_setup": true|false}`

### WebSocket Flow (Custom Domain)

1. Browser → `wss://mon.go7s.net/ws/monitoring`
2. Reverse proxy → `http://localhost:9085` (with upgrade headers)
3. Monitoring WebSocket server responds with metrics stream
4. Browser receives real-time data for dashboard

---

## Files Modified

### Backend

- `backend/user_management.py` — SKIP_DEFAULT_ADMIN support
- `backend/central_api.py` — Setup endpoints (/api/setup/\*)
- `backend/security.py` — CORS custom domain support

### Frontend

- `frontend-next/.env.example` — Updated docs and examples
- `frontend-next/src/lib/config.ts` — Added CURRENT_DOMAIN export
- `frontend-next/middleware.ts` — Setup status check and redirect
- `frontend-next/src/app/[locale]/(auth)/setup/page.tsx` — Setup form (NEW)
- `frontend-next/src/app/api/auth/setup/route.ts` — Setup API handler (NEW)

### Scripts

- `start-dev.sh` — SKIP_DEFAULT_ADMIN=true
- `start-all.sh` — Custom domain support and config
- `setup-custom-domain.sh` — Interactive setup helper (NEW)

### Documentation

- `CUSTOM-DOMAIN-GUIDE.md` — Comprehensive custom domain guide (NEW)
- `docs/README.md` — Added reference to custom domain guide
- `CONTRIBUTING.md` — Enforces doc structure and scope limits

---

## Testing Status

✅ **First-Run Onboarding**

- Setup status endpoint works (returns false when users exist)
- Setup page accessible at `/{locale}/setup` (when needs_setup=true)
- Admin creation form validates and submits correctly
- JWT token set in cookie on success
- Redirect to dashboard works

✅ **Custom Domain Support**

- setup-custom-domain.sh configures .env.local correctly
- start-all.sh applies CUSTOM_DOMAIN environment variable
- Frontend WebSocket URLs updated for domain
- Backend CORS accepts custom domain via ALLOWED_FRONTEND_DOMAINS
- API proxy works with domain configuration

✅ **Integration**

- Services start cleanly with or without CUSTOM_DOMAIN
- No breaking changes to existing localhost workflows
- Proper environment variable propagation

---

## Usage Examples

### Development (Localhost)

```bash
# Standard dev setup (no custom domain)
./start-all.sh

# Dev from LAN IP
./start-all.sh
# Access from other machines: http://192.168.1.100:9081
```

### Production (Custom Domain mon.go7s.net)

```bash
# 1. Setup custom domain
./setup-custom-domain.sh mon.go7s.net

# 2. Start with custom domain
CUSTOM_DOMAIN=mon.go7s.net ./start-all.sh

# 3. Configure reverse proxy (Nginx/Caddy)
# See CUSTOM-DOMAIN-GUIDE.md for examples

# 4. Setup HTTPS/SSL (Let's Encrypt or manual)
# See HTTPS-SETUP.md for details

# 5. Access: https://mon.go7s.net
```

### Agent Configuration

```bash
# Agent environment
export CENTRAL_API_URL=https://mon.go7s.net/api
export SSH_USER=root
export SSH_KEY_PATH=/root/.ssh/id_rsa
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│ Custom Domain: mon.go7s.net (HTTPS)                    │
├─────────────────────────────────────────────────────────┤
│ Reverse Proxy (Nginx/Caddy)                             │
│  • Port 443 (HTTPS)                                     │
│  • Forwards / → localhost:9081                          │
│  • Forwards /api/* → localhost:9083                     │
│  • Forwards /ws/* → localhost:9085/9084 (WebSocket)    │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┴───────────┬────────────────┐
        │                      │                │
   ┌────▼─────┐       ┌───────▼──────┐  ┌─────▼──────┐
   │ Next.js   │       │ Backend API  │  │ WebSocket  │
   │ :9081     │       │ :9083        │  │ :9085/9084 │
   │           │       │              │  │            │
   │ • Setup   │       │ • Auth       │  │ • Metrics  │
   │ • Auth    │       │ • Setup      │  │ • Terminal │
   │ • Dashboard       │ • CRUD       │  │            │
   │ • Settings│       │ • Proxy      │  │            │
   └───────────┘       └──────────────┘  └────────────┘
```

---

## Security Considerations

✅ **First-Run Onboarding**

- Public endpoints only accessible when no users exist
- Password validation enforced (8+ chars, uppercase, lowercase, number)
- JWT token expires after set interval
- Admin must change password on first login (recommended)

✅ **Custom Domain**

- CORS whitelist controlled via `ALLOWED_FRONTEND_DOMAINS`
- HTTPS/SSL required for production
- WebSocket auth via cookie (auth_token)
- Reverse proxy should restrict backend port 9083 to local only
- Environment variables in `.env` (not committed to git)

---

## Next Steps (Optional Enhancements)

1. **First-Login Password Reset**: Require admin to change default password
2. **Domain Validation**: Verify DNS before accepting custom domain
3. **SSL Certificate Auto-Renewal**: Integrate with Let's Encrypt
4. **Multi-Domain Support**: Support multiple domains simultaneously
5. **Agent Auto-Discovery**: Agents auto-detect custom domain via DNS

---

## References

- [CUSTOM-DOMAIN-GUIDE.md](../CUSTOM-DOMAIN-GUIDE.md) — Detailed setup guide
- [HTTPS-SETUP.md](../HTTPS-SETUP.md) — SSL/TLS configuration
- [CONTRIBUTING.md](../CONTRIBUTING.md) — Development guidelines
- [docs/README.md](../docs/README.md) — Documentation index
