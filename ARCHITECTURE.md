# Server Monitor Dashboard v2.0 - Architecture

**Last Updated:** 2026-01-07

This document describes the technical architecture of the Server Monitor Dashboard v2.0, including the new Next.js frontend, Backend-for-Frontend (BFF) layer, and security model.

---

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
│  Next.js Frontend (React + TypeScript + MUI)                    │
│  Port: 9081                                                      │
└──────────────────┬──────────────────────────────────────────────┘
                   │
          ┌────────┴────────┐
          │                 │
    ┌─────▼─────┐     ┌─────▼────────────┐
    │ WebSocket │     │   HTTP Requests  │
    │ (Direct)  │     │   (via BFF)      │
    └─────┬─────┘     └─────┬────────────┘
          │                 │
  ┌───────▼────────┐  ┌─────▼─────────────────┐
  │  Monitoring WS │  │   Next.js BFF Layer   │
  │  Port: 9085    │  │   (Auth + Proxy)      │
  │                │  │   /api/auth/*         │
  │  Terminal WS   │  │   /api/proxy/*        │
  │  Port: 9084    │  └─────┬─────────────────┘
  └───────┬────────┘        │
          │                 │
          │          ┌──────▼──────────────────┐
          │          │  Python Backend API     │
          │          │  Port: 9083             │
          │          │  - central_api.py       │
          └──────────┤  - user_management.py   │
                     │  - security.py          │
                     │  - database.py          │
                     │  - inventory_collector  │
                     └──────┬──────────────────┘
                            │
                     ┌──────▼──────────┐
                     │  SQLite Database │
                     │  data/servers.db │
                     │  - servers       │
                     │  - inventory     │
                     │  - audit_logs    │
                     └──────────────────┘
```

---

## 🎨 Frontend Architecture (Next.js 14)

### Tech Stack

- **Framework:** Next.js 14 with App Router
- **Language:** TypeScript
- **UI Library:** Material-UI (MUI) v5
- **Data Fetching:** TanStack React Query
- **Forms:** React Hook Form + Zod validation
- **i18n:** next-intl (8 languages)
- **Theming:** next-themes (dark/light mode)
- **Terminal:** xterm.js + xterm-addon-fit

### Directory Structure

```
frontend-next/src/
├── app/                        # Next.js App Router
│   ├── api/                    # BFF API routes
│   │   ├── auth/               # Authentication endpoints
│   │   │   ├── login/          # POST /api/auth/login
│   │   │   ├── logout/         # POST /api/auth/logout
│   │   │   ├── session/        # GET /api/auth/session
│   │   │   └── token/          # GET /api/auth/token (WebSocket auth)
│   │   └── proxy/[...path]/    # Proxy to backend API
│   │
│   └── [locale]/               # Internationalized pages
│       ├── (auth)/
│       │   └── login/          # Login page
│       └── (dashboard)/        # Protected dashboard pages
│           ├── dashboard/      # Main dashboard
│           ├── servers/[id]/   # Server detail
│           ├── terminal/       # Web terminal
│           ├── settings/       # Settings pages
│           │   ├── domain/     # Domain settings (admin)
│           │   ├── email/      # Email settings (admin)
│           │   └── ssh-keys/   # SSH key management
│           ├── users/          # User management (admin)
│           ├── notifications/  # Alerts/notifications
│           ├── access-denied/  # RBAC denial page
│           └── ...
│
├── components/                 # React components
│   ├── layout/
│   │   ├── AppShell.tsx        # Main app layout with sidebar
│   │   └── Shell.tsx           # Layout wrapper
│   ├── providers/
│   │   └── AppProviders.tsx    # Theme, Query, i18n providers
│   ├── SnackbarProvider.tsx    # Global toast notifications
│   ├── LoadingSkeletons.tsx    # Loading states
│   └── EmptyStates.tsx         # Empty/error states
│
├── hooks/
│   └── useSession.ts           # Session/user data hook
│
├── lib/
│   ├── api-client.ts           # API fetch wrapper
│   ├── config.ts               # Configuration
│   ├── jwt.ts                  # JWT utilities
│   └── websocket.ts            # WebSocket utilities
│
├── types/
│   └── index.ts                # TypeScript types
│
└── locales/                    # i18n translations
    ├── en.json
    ├── vi.json
    └── ...

middleware.ts                   # Auth + RBAC middleware
```

---
## 🔐 Authentication & Authorization Flow

### Authentication Flow (v2.0)

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ 1. GET /{locale}/dashboard (no cookie)
       ▼
┌──────────────────────┐
│ Next.js Middleware   │  ◄─── Auth check
│ middleware.ts        │
└──────┬───────────────┘
       │
       │ 2. Redirect to /{locale}/login
       ▼
┌──────────────────────┐
│  Login Page          │
│  Enter credentials   │
└──────┬───────────────┘
       │
       │ 3. POST /api/auth/login {username, password}
       ▼
┌──────────────────────┐
│  BFF Login Route     │  ◄─── Validates credentials
│  /api/auth/login     │       with backend
└──────┬───────────────┘
       │
       │ 4. POST http://localhost:9083/api/auth/login
       ▼
┌──────────────────────┐
│  Backend API         │
│  central_api.py      │  ◄─── Returns JWT token
└──────┬───────────────┘
       │
       │ 5. JWT token
       ▼
┌──────────────────────┐
│  BFF Login Route     │  ◄─── Sets HttpOnly cookie
│  Set-Cookie:         │       with JWT
│  auth_token=...      │
└──────┬───────────────┘
       │
       │ 6. Redirect to dashboard
       ▼
┌──────────────────────┐
│  Dashboard Page      │  ◄─── Cookie sent automatically
│  /{locale}/dashboard │
└──────────────────────┘
```

### RBAC Middleware Protection

```typescript
// middleware.ts checks:
1. Is user authenticated? (cookie exists & valid)
2. Is route admin-only? (/users, /settings/domain, /settings/email)
3. If admin-only, verify user role via /api/auth/session
4. If not admin → redirect to /access-denied
5. If admin → allow access
```

**Admin-Only Routes:**
- `/users` - User management
- `/settings/domain` - Domain & SSL settings
- `/settings/email` - Email configuration

**Authenticated Routes (any role):**
- `/dashboard` - Main dashboard
- `/servers/*` - Server management
- `/terminal` - Web terminal
- `/settings` - General settings
- `/settings/ssh-keys` - SSH key management
- `/notifications` - Alerts

---

## 🔄 Data Flow Patterns

### 1. API Request Flow (via BFF Proxy)

```
Frontend Component
  ↓
apiFetch("/api/servers")  ←  React Query
  ↓
Fetch: /api/proxy/api/servers
  ↓
Next.js Proxy Route
  ├─ Get auth_token from cookie
  ├─ Validate path (SSRF protection)
  ├─ Forward to: http://localhost:9083/api/servers
  ├─ Add header: Authorization: Bearer {token}
  └─ Remove Set-Cookie from response
  ↓
Backend API (central_api.py)
  ├─ Verify JWT token
  ├─ Check permissions
  ├─ Query database
  └─ Return JSON
  ↓
BFF Proxy filters response
  ↓
Frontend receives data
  ↓
React Query caches result
```

### 2. WebSocket Connection Flow

**Monitoring WebSocket (Real-time metrics):**

```
Dashboard Component
  ↓
createReconnectingWebSocket(MONITORING_WS_URL)
  ↓
ws://localhost:9085
  ↓
websocket_server.py
  ├─ Broadcast stats every 3 seconds
  └─ Send to all connected clients
  ↓
Frontend receives: {type: "stats_update", data: {...}}
  ↓
Update React state → UI re-renders
```

**Terminal WebSocket (SSH session):**

```
Terminal Component
  ↓
1. GET /api/auth/token  ←  Fetch token for WS auth
  ↓
2. Connect ws://localhost:9084
  ↓
3. Send: {token, server_id}
  ↓
terminal.py
  ├─ Verify token
  ├─ Establish SSH connection
  └─ Proxy stdin/stdout
  ↓
4. Receive: {type: "output", data: "..."}
  ↓
xterm.js writes to terminal
```

---

## 📊 Backend API Structure

### Core Services

```python
# central_api.py - Main REST API
- Authentication (/api/auth/*)
- Server CRUD (/api/servers/*)
- Stats & Monitoring (/api/stats/*, /api/remote/stats/*)
- Settings (/api/settings/*)
- Email (/api/email/*)
- SSH Keys (/api/ssh-keys/*)
- Users (/api/users/*)
- Exports (/api/export/*)
- Notifications (/api/alerts)

# websocket_server.py - Real-time updates
- Broadcast server stats every 3 seconds
- Connection management
- Auto-cleanup

# terminal.py - SSH terminal WebSocket
- WebSocket ←→ SSH proxy
- PTY management
- Resize handling
```

### API Endpoints

**Authentication:**
```
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/verify
```

**Servers:**
```
GET    /api/servers
POST   /api/servers
GET    /api/servers/:id
PUT    /api/servers/:id
DELETE /api/servers/:id
POST   /api/servers/:id/test
```

**Monitoring:**
```
GET    /api/stats/overview
GET    /api/remote/stats/:id
GET    /api/remote/stats/all
```

**Settings:**
```
GET    /api/settings
POST   /api/settings
GET    /api/domain/settings
POST   /api/domain/settings
GET    /api/email/config
POST   /api/email/config
POST   /api/email/test
```

**SSH Keys:**
```
GET    /api/ssh-keys
POST   /api/ssh-keys
GET    /api/ssh-keys/:id
PUT    /api/ssh-keys/:id
DELETE /api/ssh-keys/:id
```

**Users (Admin):**
```
GET    /api/users
POST   /api/users
GET    /api/users/:id
PUT    /api/users/:id
DELETE /api/users/:id
```

**Exports:**
```
GET    /api/export/servers/csv
GET    /api/export/servers/json
GET    /api/export/alerts/csv
```

---

## 🔒 Security Architecture

### Multi-Layer Security Model

**Layer 1: Frontend (Next.js)**
- Middleware auth guard (cookie-based)
- RBAC route protection
- CSRF protection (SameSite cookies)
- XSS protection (HttpOnly cookies)

**Layer 2: BFF (Backend-for-Frontend)**
- Cookie to Bearer token translation
- SSRF protection (path validation)
- Path traversal prevention
- Cookie leakage prevention
- Set-cookie header filtering

**Layer 3: Backend API (Python)**
- JWT token verification
- Role-based access control
- Rate limiting (100 req/min, 5 login/5min)
- Input validation & sanitization
- SQL injection prevention (parameterized queries)
- Security headers (CSP, X-Frame-Options, etc.)

**Layer 4: Database**
- Parameterized queries only
- No raw SQL execution
- Password hashing (SHA256 with salt)
- SSH password encryption

### Security Headers

```
Content-Security-Policy: default-src 'self'; ...
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Referrer-Policy: strict-origin-when-cross-origin
```

---

## 📁 File Structure

```
server-monitor/
├── backend/                    # Python backend
│   ├── central_api.py         # Main REST API (port 9083)
│   ├── websocket_server.py    # Monitoring WS (port 9085)
│   ├── terminal.py            # Terminal WS (port 9084)
│   ├── database.py            # SQLite ORM
│   ├── user_management.py     # User CRUD
│   ├── security.py            # Security middleware
│   ├── ssh_manager.py         # SSH connections
│   ├── email_alerts.py        # Email system
│   ├── alert_manager.py       # Alert dispatcher
│   ├── settings_manager.py    # Settings API
│   └── agent.py               # Remote monitoring agent
│
├── frontend-next/              # Next.js frontend
│   ├── src/                   # Source code
│   │   ├── app/               # App Router
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks
│   │   ├── lib/               # Utilities
│   │   ├── types/             # TypeScript types
│   │   └── locales/           # i18n translations
│   ├── middleware.ts          # Auth + RBAC
│   ├── next.config.mjs        # Next.js config
│   └── package.json
│
├── frontend/                   # Legacy HTML frontend (deprecated)
│
├── data/                       # Runtime data
│   ├── servers.db             # SQLite database
│   └── *.json                 # Config files
│
├── logs/                       # Application logs
│   ├── api.log
│   ├── websocket.log
│   └── terminal.log
│
├── services/                   # Systemd services
│   ├── systemd/               # Production service files (source of truth)
│   │   ├── server-monitor-api.service
│   │   ├── server-monitor-ws.service
│   │   ├── server-monitor-terminal.service
│   │   └── server-monitor-frontend.service
│   ├── legacy/                # Deprecated service files
│   └── server-monitor-frontend.service  # Alternative frontend service
│
└── .github/workflows/          # CI/CD
    ├── ci.yml                 # Backend CI
    └── frontend-ci.yml        # Frontend CI
```

---

## 🚀 Deployment Architecture

### Development

```
Terminal 1: ./start-all.sh      # Backend services
Terminal 2: cd frontend-next && npm run dev
```

### Production (Systemd)

```
systemd
  ├─ server-monitor-api.service
  │   └─ central_api.py (9083)
  │
  ├─ server-monitor-ws.service
  │   └─ websocket_server.py (9085)
  │
  ├─ server-monitor-terminal.service
  │   └─ terminal.py (9084)
  │
  └─ server-monitor-frontend.service
      └─ Next.js (9081)
          └─ npm start
```

### Production (Nginx Reverse Proxy)

```
Internet
  ↓
HTTPS (443)
  ↓
Nginx
  ├─ / → Next.js (9081)
  ├─ /api/auth/* → Next.js BFF (9081)
  ├─ /api/proxy/* → Next.js BFF (9081)
  ├─ /ws/* → WebSocket (9085)
  └─ /terminal/* → Terminal WS (9084)
```

---

## 📈 Performance Characteristics

- **API Response Time:** < 100ms average
- **WebSocket Update Interval:** 3 seconds
- **Concurrent Connections:** 100+ supported
- **Database:** SQLite (suitable for < 100 servers)
- **Frontend Build:** Static + SSR hybrid
- **Bundle Size:** < 1MB (optimized)

---

**Last Updated:** 2026-01-07
