# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 🎯 Project Overview

**Server Monitor Dashboard** là hệ thống giám sát multi-server với:
- **Backend**: Python (FastAPI/central_api.py cổng 9083, WebSocket 9085, Terminal 9084)
- **Frontend**: Next.js 16 (App Router, TypeScript, React 19, cổng 9081)
- **Database**: SQLite (production có thể dùng PostgreSQL)
- **Security**: JWT auth, RBAC, AES-256-GCM encrypted SSH vault

---

## 🛠️ Common Development Commands

### Backend Development (Python)

```bash
# Setup virtual environment (REQUIRED trước khi làm việc với Python)
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run specific test suite
pytest tests/test_security.py -v
pytest tests/test_user_management.py -v
pytest tests/test_api.py -v

# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=backend --cov-report=html

# Lint code
flake8 backend/ --max-line-length=120
black backend/ --check

# Format code
black backend/

# Security scan
bandit -r backend/ --severity-level medium
```

### Frontend Development (Next.js)

```bash
# Setup
cd frontend-next
npm install

# Development server với HMR
npm run dev  # Chạy tại http://localhost:9081

# Type checking
npx tsc --noEmit

# Lint
npm run lint

# Build production (local only, KHÔNG dùng khi đang làm việc interactive)
npm run build

# Start production server
npm run start
```

### Full Stack Testing

```bash
# Start all services (từ project root)
./start-all.sh

# Stop all services
./stop-all.sh

# Development mode (không tạo admin mặc định)
./start-dev.sh
```

### Database Operations

```bash
# Encrypted backup (khuyên dùng)
./scripts/backup-database.sh backup

# List all backups
./scripts/backup-database.sh list

# Restore from backup (interactive)
./scripts/restore-database.sh

# Non-interactive restore
./scripts/restore-database.sh --backup servers_db_20260110_012354.db.gpg --yes

# Check database schema
sqlite3 data/servers.db ".schema"

# Check database integrity
sqlite3 data/servers.db "PRAGMA integrity_check;"
```

---

## 🏗️ Architecture Overview

### High-Level System Design

```
Browser (Next.js Frontend :9081)
    ↓
    ├─── HTTP/REST → Next.js BFF Layer → Python Backend API (:9083)
    ├─── WebSocket → Monitoring WS (:9085) → Python Backend
    └─── WebSocket → Terminal WS (:9084) → SSH Sessions
                                ↓
                          SQLite Database (data/servers.db)
```

### Key Components

**Backend Core Services** (backend/):
- `central_api.py` - Main REST API (174KB, cổng 9083)
- `websocket_server.py` - Real-time monitoring updates (3s interval, cổng 9085)
- `terminal.py` - SSH terminal WebSocket proxy (cổng 9084)
- `database.py` - SQLite ORM và database operations (92KB)
- `security.py` - JWT auth, rate limiting, CORS, security headers (19KB)
- `user_management.py` - User CRUD operations
- `crypto_vault.py` - AES-256-GCM encryption cho SSH keys
- `plugin_system.py` - Event-driven plugin architecture
- `alert_manager.py` - Notification dispatcher (email, webhooks)

**Frontend Architecture** (frontend-next/src/):
- `app/api/` - BFF routes
  - `auth/` - Login, logout, session management
  - `proxy/[...path]/` - Backend API proxy với SSRF protection
- `app/[locale]/` - Internationalized pages (8 languages)
  - `(auth)/login/` - Login page
  - `(dashboard)/` - Protected dashboard pages
- `components/` - React components (MUI v5)
- `hooks/` - Custom React hooks (TanStack Query)
- `lib/` - API client, WebSocket utilities, JWT helpers
- `middleware.ts` - Auth guard + RBAC enforcement

### Authentication Flow

1. User login → POST `/api/auth/login`
2. BFF validates credentials với backend API
3. Backend trả về JWT token
4. BFF set HttpOnly cookie `auth_token`
5. Middleware checks cookie cho protected routes
6. RBAC enforced: admin-only routes (`/users`, `/settings/domain`, `/settings/email`)

### Data Flow Patterns

**REST API**: Component → apiFetch → BFF Proxy → Backend API → Database
**WebSocket**: Dashboard → ws://localhost:9085 → broadcast stats mỗi 3s
**Terminal**: xterm.js → ws://localhost:9084 → SSH session → remote server

---

## 📝 Code Patterns & Conventions

### Backend (Python)

- **Style**: PEP 8 với line length 120 chars
- **Type hints**: Required - `def get_user(user_id: int) -> Optional[User]:`
- **Formatting**: Dùng `black` (no arguments needed)
- **Imports**: Không dùng wildcard - `from module import specific_function`
- **File naming**: `snake_case.py`

### Frontend (TypeScript/React)

- **TypeScript**: Strict mode enabled (`strict: true`)
- **Components**: Functional components với hooks (NO class components)
- **Server Components**: Mặc định server components; chỉ dùng `"use client"` khi cần state/effects/browser APIs
- **UI Library**: MUI v5 (KHÔNG thêm UI libraries khác)
- **Data Fetching**: TanStack Query (xem `src/hooks/use-servers.ts`)
- **File naming**:
  - Pages: `kebab-case.tsx`
  - Components: `PascalCase.tsx`
  - Hooks: `use-feature-name.ts`

---

## 🔒 Security Considerations

### Multi-Layer Security Model

1. **Frontend (Next.js)**: Middleware auth guard, RBAC, HttpOnly cookies
2. **BFF Layer**: Cookie→Bearer translation, SSRF protection, path validation
3. **Backend API**: JWT verification, RBAC, rate limiting (100 req/min, 5 login/5min)
4. **Database**: Parameterized queries, password hashing (SHA256+salt), encrypted SSH keys

### Sacred Code - KHÔNG CẬP NHẬT trừ khi được yêu cầu rõ ràng

- `installer.sh`, systemd service files - production deployment
- Database migration/backup scripts (`scripts/backup-database.sh`, `scripts/restore-database.sh`)
- `start-all.sh`, `stop-all.sh` - production orchestration
- Auth core: `backend/security.py`, `backend/user_management.py`
- WebSocket core: `backend/websocket_server.py`

---

## 🧪 Testing Requirements

### Before Every Commit

**Backend:**
```bash
cd backend
source venv/bin/activate
pytest tests/ -v  # All tests must pass
flake8 backend/
black backend/
```

**Frontend:**
```bash
cd frontend-next
npm run lint
npx tsc --noEmit
npm run build  # Must compile successfully
```

### Test Structure

- Backend tests: `tests/test_*.py` (23+ tests, pytest)
- Coverage target: >80%
- Security scan: `bandit -r backend/`

### Integration Testing

```bash
./start-all.sh
# Verify:
# - Dashboard loads tại http://localhost:9081
# - Login works (admin/admin123 hoặc create via /setup)
# - WebSocket metrics update mỗi 3s
# - Terminal accessible (nếu có SSH configured)
```

---

## 📚 Key Documentation Files

- **AGENTS.md** - Workflow rules & best practices (ĐTKQ quan trọng!)
- **docs/architecture/ARCHITECTURE.md** - Chi tiết system design
- **docs/operations/TEST_GUIDE.md** - Testing procedures
- **docs/README.md** - Complete documentation index
- **API Docs**: http://localhost:9083/docs (Swagger UI khi services chạy)

---

## 🚫 What NOT to Do

- ❌ KHÔNG rewrite architecture (FastAPI, SQLite, MUI đã được chọn)
- ❌ KHÔNG thêm dependencies mới không cần thiết
- ❌ KHÔNG thay đổi design system (MUI v5 là chuẩn)
- ❌ KHÔNG thêm features "nice to have" không có trong ROADMAP
- ❌ KHÔNG move files mà không có migration plan
- ❌ KHÔNG commit localhost links vào production docs
- ❌ KHÔNG tạo markdown files không cần thiết

---

## 🔧 Common Development Workflows

### Fix Backend Bug

```bash
# 1. Identify file
cd backend
grep -r "error message" .

# 2. Write test first (TDD)
# Edit tests/test_<module>.py
pytest tests/test_<module>.py -v  # Should fail

# 3. Fix code in <module>.py
# 4. Test passes
pytest tests/test_<module>.py -v

# 5. Full suite
pytest tests/ -v

# 6. Lint & format
flake8 backend/
black backend/
```

### Add Frontend Feature

```bash
cd frontend-next

# 1. Create page component
mkdir -p src/app/[locale]/feature
touch src/app/[locale]/feature/page.tsx

# 2. Type check
npx tsc --noEmit

# 3. Lint
npm run lint

# 4. Test in browser
npm run dev
# Visit http://localhost:9081/en/feature
```

### Debugging

**Backend không start:**
```bash
tail -f logs/api.log
lsof -i:9083
cd backend && source venv/bin/activate && python central_api.py
```

**Frontend build fails:**
```bash
cd frontend-next
rm -rf .next node_modules
npm install
npm run build
```

**WebSocket không connect:**
```bash
lsof -i:9085
tail -f logs/websocket.log
# Test với wscat: npm install -g wscat && wscat -c ws://localhost:9085/ws/monitoring
```

---

## 📦 Tech Stack Summary

**Backend:**
- Python 3.12+
- Dependencies: paramiko, PyJWT, python-dotenv, cryptography, websockets
- Framework: FastAPI-style REST API
- Database: SQLite (production: PostgreSQL compatible)

**Frontend:**
- Next.js 16 (App Router)
- React 19
- TypeScript 5 (strict mode)
- MUI v5 (@mui/material)
- TanStack React Query v5
- xterm.js (terminal emulator)
- next-intl (i18n - 8 languages)

**Tools:**
- Testing: pytest (backend), Playwright (E2E frontend)
- Linting: flake8 (Python), ESLint (TypeScript)
- Formatting: black (Python)
- Security: bandit (SAST)

---

## 💡 Working with This Codebase

1. **Always work from project root** (`/opt/server-monitor`)
2. **Activate venv** trước khi làm việc với Python
3. **Read AGENTS.md** để hiểu workflow rules
4. **Test before commit**: pytest + lint cho backend, lint + build cho frontend
5. **Keep changes focused**: Fix ONE thing per commit
6. **Update docs** nếu behavior thay đổi
7. **Check for broken links** sau khi move files

---

## 🎯 Project Status

- **Version**: v2.3.1
- **Status**: Production-ready
- **Test Coverage**: 92% backend (23/25 tests passing)
- **Security**: Hardened (JWT, RBAC, rate limiting, encrypted vault)
- **Documentation**: Comprehensive (see docs/README.md)

---

**Last Updated**: 2026-01-11
