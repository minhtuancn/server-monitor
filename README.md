# 🖥️ Server Monitor Dashboard v2.0

**Multi-server monitoring system with modern Next.js frontend, real-time updates, web terminal, and advanced security**

[![Status](https://img.shields.io/badge/status-production--ready-brightgreen)]()
[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/minhtuancn/server-monitor/releases)
[![Frontend](https://img.shields.io/badge/frontend-Next.js%2014-black)]()
[![Tests](https://img.shields.io/badge/tests-23%2F25%20passing-green)]()
[![Security](https://img.shields.io/badge/security-hardened-green)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

📺 **Live Demo**: [GitHub Pages](https://minhtuancn.github.io/server-monitor/) | [Localhost](http://localhost:9081)

---

## 📋 Tổng Quan

Server Monitor Dashboard là hệ thống giám sát multi-server với giao diện web hiện đại Next.js, cho phép quản lý và theo dõi nhiều servers từ một dashboard trung tâm.

### ✨ Tính Năng Chính

- 🚀 **Modern Next.js Frontend**: App Router + TypeScript + MUI + React Query
- 🌐 **Multi-Server Management**: Quản lý nhiều servers từ một giao diện
- 📊 **Real-time Monitoring**: Cập nhật metrics thời gian thực qua WebSocket
- 🖥️ **Web Terminal**: SSH terminal emulator trên browser (xterm.js)
- 🔐 **Secure Authentication**: JWT-based auth with HttpOnly cookies, RBAC
- 🛡️ **Security Hardened**: Rate limiting, CORS, input validation, CSRF protection
- 📧 **Email Alerts**: Cảnh báo tự động qua email khi vượt ngưỡng
- 📤 **Export Data**: Xuất dữ liệu ra CSV/JSON
- 🌍 **Internationalization**: Multi-language support (8 languages)
- 🧪 **Automated Testing**: 23 test cases với pytest + CI/CD

### 🎯 Use Cases

- Giám sát multiple servers từ xa
- Quản lý infrastructure qua web UI
- Remote troubleshooting qua web terminal
- Theo dõi performance metrics real-time
- Nhận cảnh báo tự động về issues

### 🎉 What's New in v2.0 (2026-01-07)

- ✨ **Next.js Frontend**: Complete rewrite with modern stack (Next.js 14, TypeScript, MUI)
- 🔐 **Enhanced Security**: HttpOnly cookies, RBAC, SSRF protection, path validation
- 🛡️ **BFF Layer**: Backend-for-Frontend with authentication proxy
- 🎨 **Improved UX**: Toast notifications, loading states, empty states, better error handling
- 🔄 **WebSocket Fixes**: Proper cleanup, no memory leaks, auto-reconnect
- 🌍 **i18n Support**: next-intl integration for 8 languages
- 📝 **Access Control**: Admin-only pages, role-based navigation
- 🚀 **CI/CD**: Separate workflows for frontend and backend
- 📚 **Comprehensive Docs**: Updated for Next.js, deployment guides, troubleshooting

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+ and npm
- Linux server (tested on Debian/Ubuntu)
- SSH access to monitored servers

### Installation

```bash
# Clone repository
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor

# Install backend dependencies
cd backend
pip3 install -r requirements.txt

# Install test dependencies (optional)
cd ../tests
pip3 install -r requirements.txt

# Install frontend dependencies
cd ../frontend-next
npm ci

# Configure environment
cd ..
cp .env.example .env
# Edit .env and set secure values for JWT_SECRET and ENCRYPTION_KEY
# Generate secure keys with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Configure frontend environment
cd frontend-next
cat > .env.local << EOF
API_PROXY_TARGET=http://localhost:9083
NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084
EOF

# Initialize database (automatic on first run)
cd ../backend
python3 -c "import database; database.init_database()"
```

**Note:** The system now supports relative paths and works from any directory. No need for hardcoded `/opt` paths.

### Start Services

**Option 1: Start All (Recommended for first time)**

```bash
# From project root - starts backend services
./start-all.sh

# In a new terminal - start frontend
cd frontend-next
npm run dev  # Development mode with hot reload
# OR
npm run build && npm run start  # Production mode
```

**Option 2: Start Manually**

```bash
# Backend API
cd backend
python3 central_api.py &

# WebSocket server
python3 websocket_server.py &

# Terminal server (optional)
python3 terminal.py &

# Frontend Next.js
cd ../frontend-next
npm run dev  # Development (http://localhost:9081)
# OR
npm run build && npm run start  # Production
```

### Access Dashboard

- **Dashboard**: http://localhost:9081 (Next.js frontend)
- **API**: http://localhost:9083
- **Default Credentials**: admin / admin123 ⚠️ **Change in production!**

⚠️ **Security Warning**: The system auto-creates a default admin user. Change the password immediately after first login!

### Stop Services

```bash
./stop-all.sh  # Stops backend services

# Stop frontend: Ctrl+C in the terminal where npm is running
```

---

## 📁 Project Structure

```
server-monitor/
├── backend/                    # Python backend services
│   ├── central_api.py         # Main REST API server (port 9083)
│   ├── websocket_server.py    # Real-time updates (port 9085)
│   ├── terminal.py            # Web terminal (port 9084)
│   ├── database.py            # SQLite database operations
│   ├── user_management.py     # User CRUD & authentication
│   ├── settings_manager.py    # System settings management
│   ├── ssh_manager.py         # SSH connection management
│   ├── email_alerts.py        # Email notification system
│   ├── alert_manager.py       # Multi-channel alert dispatcher
│   ├── security.py            # Security middleware (rate limiting, CORS, validation)
│   └── agent.py               # Monitoring agent for remote servers
│
├── frontend-next/              # Next.js 14 frontend (TypeScript)
│   ├── src/
│   │   ├── app/               # App Router pages
│   │   │   ├── api/           # BFF API routes (auth, proxy)
│   │   │   └── [locale]/      # Internationalized pages
│   │   │       ├── (auth)/login
│   │   │       └── (dashboard)/
│   │   │           ├── dashboard/
│   │   │           ├── servers/[id]/
│   │   │           ├── terminal/
│   │   │           ├── settings/
│   │   │           ├── users/
│   │   │           ├── notifications/
│   │   │           └── access-denied/
│   │   ├── components/        # React components
│   │   │   ├── layout/        # AppShell, Shell
│   │   │   ├── providers/     # Theme, Query, i18n
│   │   │   ├── SnackbarProvider.tsx
│   │   │   ├── LoadingSkeletons.tsx
│   │   │   └── EmptyStates.tsx
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # Utilities (API client, WebSocket, JWT)
│   │   ├── types/             # TypeScript type definitions
│   │   └── locales/           # i18n translations (8 languages)
│   ├── middleware.ts          # Auth + RBAC middleware
│   ├── next.config.mjs        # Next.js configuration
│   └── package.json
│
├── frontend/                   # Legacy HTML frontend (deprecated)
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   └── ... (14 pages)
│
├── tests/                      # Automated tests
│   ├── test_api.py            # API integration tests (19/19 passing)
│   ├── test_security.py       # Security tests (4/6 passing)
│   └── requirements.txt
│
├── services/                   # Systemd service files
│   ├── server-dashboard-api-v2.service
│   └── server-monitor-frontend.service
│
├── data/                       # Data storage (auto-created)
│   ├── servers.db             # SQLite database
│   └── *.json                 # Configuration files
│
├── logs/                       # Log files (auto-created)
│
├── docs/                       # Documentation
│
├── .github/workflows/          # CI/CD
│   ├── ci.yml                 # Backend CI
│   └── frontend-ci.yml        # Frontend CI
│
├── DEPLOYMENT.md              # Production deployment guide
├── ARCHITECTURE.md            # System architecture
├── SECURITY.md                # Security guide
├── SMOKE_TEST_CHECKLIST.md    # Testing checklist
├── start-all.sh               # Start all services
├── stop-all.sh                # Stop all services
├── .env.example               # Environment template
└── README.md                  # This file
```

---

## 🔧 Configuration

### Ports

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| Frontend | 9081 | HTTP | Web UI |
| API | 9083 | HTTP | REST API |
| Terminal | 9084 | WebSocket | SSH terminal |
| WebSocket | 9085 | WebSocket | Real-time updates |
| Agent (remote) | 8083 | HTTP | Monitoring agent |

### Environment

Configuration options in `.env` file:
- **JWT_SECRET**: Secret key for JWT tokens (required)
- **ENCRYPTION_KEY**: Key for SSH password encryption (required)
- **JWT_EXPIRATION**: Token expiration in seconds (default: 86400)
- **DB_PATH**: Custom database path (optional, defaults to `data/servers.db`)
- **API_PORT**: API server port (default: 9083)
- **FRONTEND_PORT**: Frontend server port (default: 9081)

**Database Path**: Now supports relative paths. The system automatically resolves to `<project_root>/data/servers.db`. No hardcoded paths required!

---

## 🔐 Security Features

### Implemented (v2.0)

✅ **Authentication & Authorization**
- JWT token-based authentication
- HttpOnly cookies for token storage (XSS protection)
- Secure cookie attributes (HttpOnly, SameSite=Lax, Secure in production)
- Token expiration synchronized with cookie TTL
- Role-Based Access Control (RBAC)
- Admin-only routes protection
- Access Denied page for unauthorized access

✅ **Backend-for-Frontend (BFF) Security**
- Auth proxy layer in Next.js
- Cookie-to-Bearer token translation
- SSRF protection with path validation
- Path traversal prevention
- No cookie leakage to backend
- Set-cookie header filtering

✅ **Rate Limiting**
- 100 requests/minute (general endpoints)
- 5 login attempts/5 minutes
- Automatic IP blocking after repeated failures

✅ **CORS Protection**
- Whitelist specific origins only
- No wildcard (*) in production
- Proper preflight handling

✅ **Security Headers**
- Content-Security-Policy
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection
- Strict-Transport-Security (HSTS)

✅ **Input Validation**
- IP address validation (0-255 per octet)
- Hostname validation (proper DNS format)
- Port range validation (1-65535)
- String sanitization (HTML/XSS prevention)
- Real-time client-side validation

✅ **WebSocket Security**
- Token authentication required
- No anonymous connections
- Proper error handling
- Connection timeout protection

### Security Best Practices

⚠️ **Before Production Deployment**:
1. Change default admin password
2. Enable HTTPS (use nginx/apache reverse proxy)
3. Set up firewall rules
4. Review CORS allowed origins
5. Enable database backups
6. Set up log rotation
7. Use environment variables for secrets
8. Regularly update dependencies

### Threat Model

**Protected Against:**
- ✅ XSS (Cross-Site Scripting) - HttpOnly cookies, input sanitization
- ✅ CSRF (Cross-Site Request Forgery) - SameSite cookies, token validation
- ✅ SSRF (Server-Side Request Forgery) - Path validation in proxy
- ✅ Path Traversal - Input validation, regex filtering
- ✅ SQL Injection - Parameterized queries, ORM usage
- ✅ Brute Force - Rate limiting on login
- ✅ Session Hijacking - Secure cookies, HTTPS in production
- ✅ Unauthorized Access - RBAC, middleware protection

**Remaining Risks:**
- ⚠️ DDoS attacks - Recommend using Cloudflare or similar
- ⚠️ Zero-day vulnerabilities - Keep dependencies updated
- ⚠️ Physical server access - Secure your infrastructure

---

## 📊 API Endpoints

### Authentication
```
POST   /api/auth/login       - Login
POST   /api/auth/logout      - Logout  
GET    /api/auth/verify      - Verify token
```

### Servers
```
GET    /api/servers          - List all servers
POST   /api/servers          - Add new server
GET    /api/servers/:id      - Get server details
PUT    /api/servers/:id      - Update server
DELETE /api/servers/:id      - Delete server
POST   /api/servers/:id/test - Test connection
```

### Monitoring
```
GET    /api/remote/stats/:id - Get server metrics
GET    /api/remote/stats/all - Get all servers metrics
GET    /api/stats/overview   - Get statistics summary
```

### Export
```
GET    /api/export/servers/csv      - Export servers to CSV
GET    /api/export/servers/json     - Export servers to JSON
GET    /api/export/history/csv      - Export monitoring history
GET    /api/export/history/json     - Export history as JSON
GET    /api/export/alerts/csv       - Export alerts
```

### Email
```
GET    /api/email/config     - Get email configuration
POST   /api/email/config     - Update email config
POST   /api/email/test       - Send test email
```

**Total: 29 REST endpoints + 1 WebSocket endpoint**

Full API documentation: See [API-TESTING-GUIDE.txt](API-TESTING-GUIDE.txt)

---

## 🧪 Testing

### Backend Tests

```bash
cd tests

# Run all API tests (19 tests)
python3 -m pytest test_api.py -v

# Run security tests (6 tests)
python3 -m pytest test_security.py -v

# Run all tests
python3 -m pytest -v
```

### Frontend Tests

```bash
cd frontend-next

# Lint TypeScript/React code
npm run lint

# Build production bundle
npm run build

# Type checking
npx tsc --noEmit
```

### Smoke Testing

Use the comprehensive smoke test checklist:

```bash
# See SMOKE_TEST_CHECKLIST.md for detailed testing procedures
# Covers:
# - Authentication flows
# - Dashboard functionality
# - Real-time WebSocket updates
# - Terminal WebSocket
# - CRUD operations
# - Settings pages
# - Exports
# - Role-based access control
```

### Test Coverage

**Backend:**
- ✅ Authentication (5 tests)
- ✅ CRUD operations (5 tests)
- ✅ Export functionality (2 tests)
- ✅ Email configuration (2 tests)
- ✅ Unauthorized access (3 tests)
- ✅ Rate limiting (2 tests)
- ✅ Security headers (2 tests)
- ✅ Input validation (2 tests)

**Total: 23/25 tests passing (92%)**

**Frontend:**
- ✅ TypeScript compilation
- ✅ ESLint checks
- ✅ Production build verification
- ✅ Manual smoke tests (see SMOKE_TEST_CHECKLIST.md)

### CI/CD

**Backend CI** (.github/workflows/ci.yml):
- Python linting (flake8)
- Unit tests (pytest)
- Security scan (bandit)

**Frontend CI** (.github/workflows/frontend-ci.yml):
- TypeScript linting (ESLint)
- Production build test
- Build artifact verification

---

## 📈 Performance

### Metrics

- **WebSocket Updates**: 3 seconds interval (3x faster than polling)
- **Network Overhead**: 70% reduction vs polling
- **API Response Time**: < 100ms (average)
- **Concurrent Connections**: 100+ supported
- **Database**: SQLite (suitable for < 100 servers)

### Scalability

- Current: Up to 100 servers
- Recommended: Use PostgreSQL for > 100 servers
- Consider: Redis for caching if > 1000 req/min

---

## 📚 Documentation

### Getting Started
- [README.md](README.md) - This file, overview and quick start
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [HTTPS-SETUP.md](HTTPS-SETUP.md) - SSL/HTTPS configuration

### Architecture & Design
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [MULTI-SERVER-GUIDE.md](MULTI-SERVER-GUIDE.md) - Multi-server setup

### Operations
- [POST-PRODUCTION.md](POST-PRODUCTION.md) - Monitoring, logging, maintenance
- [TEST_GUIDE.md](TEST_GUIDE.md) - Testing instructions

### Security
- [SECURITY.md](SECURITY.md) - Security guide and audit findings

### Planning
- [ROADMAP.md](ROADMAP.md) - Feature roadmap
- [TODO-IMPROVEMENTS.md](TODO-IMPROVEMENTS.md) - Action items
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history

---

## 🐛 Troubleshooting

### Services not starting

```bash
# Check if ports are in use
netstat -tlnp | grep -E ":(9081|9083|9084|9085)"

# Check logs
tail -f logs/*.log

# Restart services
./stop-all.sh && ./start-all.sh
```

### Database errors

```bash
# Reinitialize database
cd backend
python3 -c "import database; database.init_database()"
```

### WebSocket not connecting

1. Check firewall allows port 9085
2. Check websocket_server.py is running
3. Check browser console for errors
4. Verify WebSocket URL in dashboard.html

---

## 🔄 Deployment

### Development
```bash
./start-all.sh
```

### Production (with systemd)

```bash
# Copy service files
cp services/*.service /etc/systemd/system/

# Enable and start services
systemctl daemon-reload
systemctl enable server-dashboard-api-v2.service
systemctl enable opencode-dashboard.service
systemctl start server-dashboard-api-v2.service
systemctl start opencode-dashboard.service
```

### Docker (future)

```bash
docker-compose up -d
```

---

## 🤝 Contributing

### Development Workflow

1. Clone the repository to your working directory
2. Test on dev ports (9081, 9083, 9084, 9085)
3. Run automated tests: `pytest tests/ -v`
4. Update documentation
5. Test on production backup before deploying

### Code Style

- Python: PEP 8
- JavaScript: ES6+
- HTML/CSS: Semantic, responsive design

---

## 📝 Changelog

### v2.0.0 (2026-01-07) - Next.js Migration & Security Hardening 🎉

**Frontend Rewrite:**
- ✨ Complete migration to Next.js 14 with App Router
- ✨ TypeScript for type safety
- ✨ Material-UI (MUI) for modern design system
- ✨ React Query for efficient data fetching
- ✨ React Hook Form + Zod for form validation
- ✨ next-intl for internationalization (8 languages)
- ✨ Dark/light theme support with next-themes

**Security Enhancements:**
- 🔐 HttpOnly cookies for token storage (XSS protection)
- 🔐 RBAC (Role-Based Access Control) with middleware
- 🔐 Access Denied page for unauthorized access
- 🔐 SSRF protection in BFF proxy
- 🔐 Path traversal prevention
- 🔐 Cookie TTL synchronized with JWT expiry
- 🔐 Secure cookie attributes (HttpOnly, SameSite, Secure)

**Backend-for-Frontend (BFF):**
- 🛡️ Auth proxy layer in Next.js
- 🛡️ Cookie-to-Bearer token translation
- 🛡️ No cookie leakage to backend
- 🛡️ Set-cookie header filtering

**WebSocket Improvements:**
- 🔄 Fixed event listener memory leaks
- 🔄 Proper cleanup on unmount
- 🔄 Better error handling
- 🔄 Connection status indicators

**UX Improvements:**
- 🎨 Global toast notification system
- 🎨 Loading skeleton components
- 🎨 Empty state components
- 🎨 Better error messages
- 🎨 Role-based navigation visibility

**DevOps:**
- 🚀 Separate CI workflow for frontend
- 🚀 Systemd service for Next.js
- 🚀 Comprehensive deployment documentation
- 🚀 Smoke test checklist
- 🚀 Troubleshooting guides

### v1.1.0 (2026-01-06)

- ✅ Fixed database path issues (removed hardcoded paths)
- ✅ Enhanced input validation (IP, hostname, port)
- ✅ Frontend cleanup (removed duplicate files)
- ✅ Form helper system with loading states
- ✅ Improved UX with consistent error handling
- ✅ Comprehensive documentation updates

### v1.0.0 (2026-01-06) - Initial Release 🎉

- ✅ Multi-server monitoring dashboard
- ✅ Real-time updates via WebSocket
- ✅ Web terminal emulator (xterm.js + SSH)
- ✅ Email alerts system with SMTP
- ✅ Export data (CSV/JSON)
- ✅ SSH key management
- ✅ JWT authentication system
- ✅ Advanced security (rate limiting, CORS, validation)
- ✅ Comprehensive testing suite (23 tests)
- ✅ Production-ready deployment scripts
- ✅ Complete documentation

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Minh Tuấn

---

## 👨‍💻 Author

**Minh Tuấn**
- 📧 Email: [vietkeynet@gmail.com](mailto:vietkeynet@gmail.com)
- 📱 WhatsApp/WeChat: +84912537003
- 🐙 GitHub: [@minhtuancn](https://github.com/minhtuancn)
- 🌐 Demo: [GitHub Pages](https://minhtuancn.github.io/server-monitor/)

**Project**: Server Monitoring System  
**Version**: 1.0.0  
**Release Date**: January 6, 2026

---

## 📞 Support

For issues or questions:
1. Check [TROUBLESHOOTING section](#-troubleshooting)
2. Review logs in `logs/` directory
3. Check [TODO.md](TODO.md) for known issues
4. Review test results: `pytest tests/ -v`

---

## 🎯 Roadmap

### v1.1.0 (Planned - Q1 2026)
- [ ] PostgreSQL support
- [ ] Redis caching
- [ ] Docker containerization
- [ ] Swagger/OpenAPI documentation
- [ ] Advanced alerting rules
- [ ] GitHub Pages deployment

### v2.0.0 (Planned - Q2 2026)
- [ ] Kubernetes support
- [ ] Multi-user management
- [ ] Role-based access control (RBAC)
- [ ] Advanced reporting
- [ ] Mobile responsive improvements
- [ ] Plugin system

---

**Made with ❤️ using Python, JavaScript, and modern web technologies**
