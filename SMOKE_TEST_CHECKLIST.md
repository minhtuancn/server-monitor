# Smoke Test Checklist - Server Monitor Dashboard

**Version:** 2.0 (Next.js Frontend)  
**Last Updated:** 2026-01-07

This document provides a comprehensive checklist for end-to-end testing of the Server Monitor Dashboard with the new Next.js frontend.

---

## Prerequisites

Before running smoke tests:

- [ ] Backend services are running (central_api.py, websocket_server.py, terminal.py)
- [ ] Frontend Next.js is running on port 9081
- [ ] Database is initialized with at least one admin user
- [ ] Environment variables are properly configured (.env file)

---

## Quick Start Commands

### Start Backend Services

```bash
cd /path/to/server-monitor
./start-all.sh
```

This starts:
- Central API (port 9083)
- WebSocket Server (port 9085)
- Terminal Server (port 9084)

### Start Frontend (Production Build)

```bash
cd frontend-next

# Install dependencies (first time only)
npm ci

# Build for production
npm run build

# Start production server
npm run start
```

Frontend will be available at: http://localhost:9081

### Start Frontend (Development Mode)

```bash
cd frontend-next
npm run dev
```

---

## Test Checklist

### 1. Authentication & Authorization

#### 1.1 Login Flow
- [ ] Navigate to http://localhost:9081
- [ ] Should redirect to login page (/{locale}/login)
- [ ] Enter credentials: `admin` / `admin123`
- [ ] Login successful, redirects to dashboard
- [ ] Cookie `auth_token` is set (check DevTools → Application → Cookies)
- [ ] Cookie has `HttpOnly` and `SameSite=Lax` attributes

#### 1.2 Session Management
- [ ] Refresh page - should stay logged in
- [ ] Navigate to `/api/auth/session` - returns authenticated user data
- [ ] Token expiry: wait for token expiration (or manually delete cookie) - should redirect to login

#### 1.3 Logout
- [ ] Click logout button in header
- [ ] Redirected to login page
- [ ] Cookie `auth_token` is removed
- [ ] Cannot access dashboard without re-login

#### 1.4 Authorization (RBAC)
- [ ] As admin: can access `/users`, `/settings/domain`, `/settings/email`
- [ ] Create a non-admin user (if backend supports)
- [ ] Login as non-admin user
- [ ] Try to access `/users` - should see "Access Denied" page
- [ ] Try to access `/settings/domain` - should see "Access Denied" page
- [ ] Sidebar should not show admin-only menu items for non-admin users

---

### 2. Dashboard

#### 2.1 Overview Stats
- [ ] Dashboard loads at `/{locale}/dashboard`
- [ ] Stats cards display correctly:
  - Total Servers
  - Online Servers
  - Offline Servers
  - Alerts (last 24h)
- [ ] Stats are fetched from `/api/stats/overview`

#### 2.2 Server List
- [ ] Server cards/table displays all servers
- [ ] Each server shows: name, host, status, metrics (CPU, Memory, Disk)
- [ ] Loading state shows while fetching
- [ ] Empty state shows if no servers exist

#### 2.3 Add Server
- [ ] Click "Add Server" button
- [ ] Fill form with valid data:
  - Name: `Test Server`
  - Host: `192.168.1.100`
  - Port: `22`
  - Username: `testuser`
- [ ] Submit form
- [ ] Success toast/snackbar appears
- [ ] Server appears in list
- [ ] Form validation works (try invalid IP, empty fields)

#### 2.4 Export Data
- [ ] Navigate to `/exports`
- [ ] Click "Export Servers (CSV)"
- [ ] File downloads successfully
- [ ] Click "Export Servers (JSON)"
- [ ] File downloads successfully
- [ ] CSV and JSON contain correct server data

---

### 3. Real-time Monitoring (WebSocket)

#### 3.1 Connection
- [ ] Open DevTools → Network → WS filter
- [ ] WebSocket connection to `ws://localhost:9085` establishes
- [ ] Connection status indicator shows "Connected" (if UI has one)

#### 3.2 Live Updates
- [ ] Server metrics update in real-time (CPU, Memory, Disk)
- [ ] New servers appear automatically when added
- [ ] Server status changes reflect immediately
- [ ] Check DevTools Console for WebSocket messages

#### 3.3 Reconnection
- [ ] Stop websocket server: `./stop-all.sh` then restart just WS
- [ ] WebSocket should attempt reconnection with backoff
- [ ] When server restarts, connection re-establishes automatically
- [ ] No duplicate listeners or memory leaks (check Console for errors)

---

### 4. Terminal (Web SSH)

#### 4.1 Connection
- [ ] Navigate to `/terminal`
- [ ] Select a server from dropdown (or pass `?server={id}` in URL)
- [ ] Terminal connects to `ws://localhost:9084`
- [ ] Terminal displays connection success message

#### 4.2 Commands
- [ ] Type command: `ls -la`
- [ ] Output displays correctly
- [ ] Type command: `pwd`
- [ ] Output displays current directory
- [ ] Try interactive command: `top` then press `q` to exit

#### 4.3 Terminal Features
- [ ] Copy/paste works in terminal
- [ ] Terminal resizes correctly with window resize
- [ ] Terminal scrolls correctly
- [ ] Terminal supports colors (check with `ls --color`)

#### 4.4 Cleanup
- [ ] Navigate away from terminal page
- [ ] No WebSocket connection leaks (check DevTools → Network → WS)
- [ ] No console errors about unclosed connections
- [ ] Return to terminal page - reconnects properly

---

### 5. Server Management

#### 5.1 Server Detail
- [ ] Click on a server from dashboard
- [ ] Navigates to `/servers/{id}`
- [ ] Server details display: name, host, port, username, description
- [ ] Server metrics display (CPU, Memory, Disk, Network)
- [ ] "Test Connection" button works
- [ ] Notes section loads (if server has notes)

#### 5.2 Server Notes (Markdown)
- [ ] Navigate to `/server-notes` or server detail page
- [ ] Click "Add Note" or similar action
- [ ] Write markdown content: `# Test Note\n\n- Item 1\n- Item 2`
- [ ] Save note
- [ ] Note renders with markdown formatting
- [ ] Edit note works
- [ ] Delete note works with confirmation

#### 5.3 Update Server
- [ ] Edit server details (if backend supports PUT /api/servers/:id)
- [ ] Change server name
- [ ] Save changes
- [ ] Success toast appears
- [ ] Server list reflects updated name

#### 5.4 Delete Server
- [ ] Click delete button on a server
- [ ] Confirmation dialog appears
- [ ] Confirm deletion
- [ ] Server removed from list
- [ ] Success toast appears

---

### 6. Settings

#### 6.1 General Settings
- [ ] Navigate to `/settings`
- [ ] System settings form displays
- [ ] Update a setting value
- [ ] Save changes
- [ ] Success toast appears

#### 6.2 Domain & SSL (Admin Only)
- [ ] Navigate to `/settings/domain`
- [ ] Domain settings form displays
- [ ] Fields: domain name, SSL enabled, SSL type, cert paths
- [ ] Update settings
- [ ] Save changes
- [ ] Success toast appears

#### 6.3 Email Configuration (Admin Only)
- [ ] Navigate to `/settings/email`
- [ ] Email form displays: SMTP host, port, username, password, recipients
- [ ] Update email config
- [ ] Click "Test Email" button
- [ ] Email test result appears
- [ ] Save changes if valid

#### 6.4 SSH Keys
- [ ] Navigate to `/settings/ssh-keys`
- [ ] SSH keys list displays
- [ ] Click "Add SSH Key"
- [ ] Paste public key
- [ ] Enter key name
- [ ] Save key
- [ ] Key appears in list with fingerprint
- [ ] Delete key works

---

### 7. Notifications & Alerts

#### 7.1 Notifications Page
- [ ] Navigate to `/notifications`
- [ ] Alerts/notifications list displays
- [ ] Each alert shows: message, severity, timestamp
- [ ] Empty state shows if no alerts

#### 7.2 Alert Channels (if backend supports)
- [ ] Check if `/api/telegram/config` endpoint exists
- [ ] Check if `/api/slack/config` endpoint exists
- [ ] If yes, verify UI for Telegram/Slack config (may need to add UI)

---

### 8. User Management (Admin Only)

#### 8.1 User List
- [ ] Navigate to `/users`
- [ ] Users table displays all users
- [ ] Columns: username, email, role, actions

#### 8.2 Create User
- [ ] Click "Add User" button
- [ ] Fill form: username, email, password, role
- [ ] Submit form
- [ ] Success toast appears
- [ ] New user appears in list

#### 8.3 Update User
- [ ] Click edit button on a user
- [ ] Update user details (e.g., change role)
- [ ] Save changes
- [ ] Success toast appears

#### 8.4 Delete User
- [ ] Click delete button
- [ ] Confirmation dialog appears
- [ ] Confirm deletion
- [ ] User removed from list

---

### 9. System Check

#### 9.1 API Checks
- [ ] Navigate to `/system-check`
- [ ] API status checks display
- [ ] Check status for:
  - Central API (9083)
  - WebSocket Server (9085)
  - Terminal Server (9084)
- [ ] All should show "Online" or similar status

#### 9.2 WebSocket Checks
- [ ] WebSocket connection status displays
- [ ] Shows "Connected" for monitoring WS
- [ ] Shows "Connected" for terminal WS (if connected)

---

### 10. Security & Edge Cases

#### 10.1 CORS Test
- [ ] Navigate to `/test-cors`
- [ ] Test CORS configuration
- [ ] Should show successful API call if same origin
- [ ] Or proper CORS headers if different origin

#### 10.2 CSRF Protection
- [ ] All POST/PUT/DELETE requests work correctly
- [ ] Cookie-based auth is properly forwarded via BFF proxy

#### 10.3 Input Validation
- [ ] Try adding server with invalid IP (e.g., `999.999.999.999`)
- [ ] Should show validation error
- [ ] Try adding server with invalid port (e.g., `99999`)
- [ ] Should show validation error
- [ ] All forms validate required fields

#### 10.4 Error Handling
- [ ] Stop backend API server
- [ ] Try to fetch data in dashboard
- [ ] Proper error message displays (not just blank screen)
- [ ] Restart backend
- [ ] Data loads again

---

### 11. Internationalization (i18n)

#### 11.1 Language Switching
- [ ] Check if language switcher exists in UI
- [ ] Switch to Vietnamese (`/vi/dashboard`)
- [ ] UI text changes to Vietnamese
- [ ] Switch back to English (`/en/dashboard`)

#### 11.2 Translations
- [ ] Login page has translations
- [ ] Dashboard page has translations
- [ ] Settings pages have translations
- [ ] Error messages are translated

---

### 12. Performance & UX

#### 12.1 Loading States
- [ ] All data fetching shows loading indicators
- [ ] Skeleton loaders or spinners appear while loading
- [ ] No blank screens during loading

#### 12.2 Error States
- [ ] Failed API calls show error messages
- [ ] Error messages are user-friendly
- [ ] Retry options available where appropriate

#### 12.3 Empty States
- [ ] Empty server list shows helpful message
- [ ] Empty notifications shows "No alerts"
- [ ] Empty SSH keys shows "No keys configured"

#### 12.4 Toast Notifications
- [ ] Success toasts appear for successful actions
- [ ] Error toasts appear for failed actions
- [ ] Toasts auto-dismiss after 6 seconds
- [ ] Multiple toasts don't overlap badly

---

## Troubleshooting

### Backend Not Starting

```bash
# Check if ports are in use
netstat -tlnp | grep -E ":(9081|9083|9084|9085)"

# Check logs
tail -f logs/*.log

# Restart all services
./stop-all.sh
./start-all.sh
```

### Frontend Build Fails

```bash
cd frontend-next

# Clear cache and reinstall
rm -rf .next node_modules
npm install
npm run build
```

### WebSocket Not Connecting

1. Check firewall allows ports 9085 and 9084
2. Verify WebSocket servers are running: `ps aux | grep python3`
3. Check browser console for WebSocket errors
4. Verify WebSocket URL in config: `NEXT_PUBLIC_MONITORING_WS_URL`

### Cookie Not Being Set

1. Check browser DevTools → Application → Cookies
2. Verify `auth_token` cookie exists
3. Check cookie attributes: `HttpOnly`, `SameSite=Lax`
4. If using HTTPS in production, verify `Secure` flag is set

---

## Success Criteria

All tests pass ✅ when:

- [ ] All authentication flows work correctly
- [ ] RBAC properly restricts admin pages
- [ ] Dashboard loads and displays data
- [ ] Real-time WebSocket updates work
- [ ] Terminal connects and executes commands
- [ ] All CRUD operations work (servers, users, notes, SSH keys)
- [ ] Settings pages save configurations
- [ ] Exports download files
- [ ] No console errors in browser DevTools
- [ ] No WebSocket connection leaks
- [ ] Toast notifications appear for all actions
- [ ] Loading/error/empty states display correctly

---

## Notes

- Default credentials: `admin` / `admin123` (CHANGE IN PRODUCTION!)
- Frontend: http://localhost:9081
- Backend API: http://localhost:9083
- WebSocket Monitoring: ws://localhost:9085
- WebSocket Terminal: ws://localhost:9084

---

**Report any issues found during smoke testing to the development team.**
