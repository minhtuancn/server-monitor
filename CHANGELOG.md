# Changelog - Server Monitor Dashboard

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] - Phase 4

### 🚀 Phase 4 Module 1: SSH Key Vault

**Secure SSH Private Key Management with AES-256-GCM Encryption**

### Added

**Backend:**
- ✨ `backend/crypto_vault.py` - AES-256-GCM encryption module
  - PBKDF2-HMAC-SHA256 key derivation (100k iterations)
  - Random 12-byte IV per encryption
  - 16-byte authentication tag for integrity
  - Comprehensive error handling
- ✨ `backend/ssh_key_manager.py` - SSH key CRUD operations
  - Create encrypted keys
  - List keys (metadata only)
  - Get key metadata
  - Soft delete keys
  - Decrypt keys for internal use only
- ✨ `tests/test_crypto_vault.py` - 9 comprehensive unit tests
  - Encrypt/decrypt roundtrip
  - Wrong key rejection
  - Tampered data detection
  - Base64 encoding/decoding
  - Unique IV generation
- ✨ API endpoints for SSH key management
  - `POST /api/ssh-keys` - Create encrypted key (admin/operator)
  - `GET /api/ssh-keys` - List keys (admin/operator)
  - `GET /api/ssh-keys/{id}` - Get key metadata (admin/operator)
  - `DELETE /api/ssh-keys/{id}` - Soft delete (admin only)
- ✨ New dependency: `cryptography>=41.0.0` for AES-256-GCM

**Frontend:**
- ✨ `/settings/ssh-keys` page - Professional SSH key management UI
  - Table view with key type badges, fingerprints, metadata
  - Add key dialog with validation and security warnings
  - Delete confirmation dialog
  - Empty state for first-time users
  - Monospace font for private key input
  - Form validation and error handling
  - Success/error toast notifications
- ✨ Updated `SSHKey` type definition for key vault schema

**Security:**
- 🔐 Military-grade AES-256-GCM encryption
- 🔐 Database compromise protection (keys unreadable without master key)
- 🔐 No plaintext storage of private keys
- 🔐 Private keys never exposed via API
- 🔐 Role-based access control (admin/operator only)
- 🔐 Soft delete prevents accidental data loss
- 🔐 Comprehensive unit test coverage

**Documentation:**
- 📚 `docs/modules/SSH_KEY_VAULT.md` - Technical specification
- 📚 Updated `SECURITY.md` with SSH Key Vault section
- 📚 Updated `.env.example` with `KEY_VAULT_MASTER_KEY`

**Configuration:**
- ⚙️ New environment variable: `KEY_VAULT_MASTER_KEY`
  - Required for SSH Key Vault functionality
  - Used for AES-256-GCM key derivation
  - Generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`

### Changed
- 🔄 Replaced old SSH key management with encrypted key vault
- 🔄 SSH keys now use UUIDs instead of integer IDs
- 🔄 Keys are immutable (create new key instead of updating)

### Security Notes
- ⚠️ The `KEY_VAULT_MASTER_KEY` must be kept secure and backed up
- ⚠️ If master key is lost, encrypted keys cannot be recovered
- ⚠️ Rotate SSH keys regularly (every 90-180 days)
- ✅ ED25519 keys recommended for better security and performance

---

## [2.0.0] - 2026-01-07

### 🎉 Major Release - Next.js Migration

Complete frontend rewrite with modern stack and comprehensive security hardening.

### Added

**Frontend (Next.js 14):**
- ✨ Complete migration to Next.js 14 with App Router
- ✨ TypeScript for type safety and better DX
- ✨ Material-UI (MUI) v5 for modern design system
- ✨ React Query for efficient data fetching and caching
- ✨ React Hook Form + Zod for robust form validation
- ✨ next-intl for internationalization (8 languages: en, vi, fr, es, de, ja, ko, zh-CN)
- ✨ next-themes for dark/light mode support
- ✨ Global toast notification system (SnackbarProvider)
- ✨ Loading skeleton components
- ✨ Empty state components
- ✨ Error state components
- ✨ Access Denied page for RBAC violations

**Security Enhancements:**
- 🔐 HttpOnly cookies for token storage (XSS protection)
- 🔐 Role-Based Access Control (RBAC) with middleware
- 🔐 SSRF protection in BFF proxy (path validation)
- 🔐 Path traversal prevention
- 🔐 Cookie TTL synchronized with JWT expiry
- 🔐 Secure cookie attributes (HttpOnly, SameSite=Lax, Secure)
- 🔐 Set-cookie header filtering in proxy
- 🔐 No cookie leakage to backend
- 🔐 Token expiry validation for WebSocket auth

**Backend-for-Frontend (BFF):**
- 🛡️ Auth proxy layer in Next.js
- 🛡️ Cookie-to-Bearer token translation
- 🛡️ /api/auth/* endpoints (login, logout, session, token)
- 🛡️ /api/proxy/* for secure backend proxying

**DevOps:**
- 🚀 Separate CI workflow for frontend (.github/workflows/frontend-ci.yml)
- 🚀 Systemd service for Next.js (services/server-monitor-frontend.service)
- 🚀 Smoke test checklist (SMOKE_TEST_CHECKLIST.md)

**Documentation:**
- 📚 Comprehensive deployment guide updates (DEPLOYMENT.md)
- 📚 Updated architecture documentation (ARCHITECTURE.md)
- 📚 Enhanced security documentation (SECURITY.md)
- 📚 Updated README with v2.0 features
- 📚 Troubleshooting guides for frontend, WebSocket, auth

### Changed

- 🔄 Frontend now runs on Next.js instead of static HTML
- 🔄 Authentication uses HttpOnly cookies instead of localStorage
- 🔄 All API calls go through BFF proxy (/api/proxy/*)
- 🔄 Middleware handles auth and RBAC checks
- 🔄 WebSocket cleanup improved (no memory leaks)
- 🔄 Terminal resize event listeners properly cleaned up

### Fixed

- 🐛 WebSocket event listener memory leaks
- 🐛 Terminal resize event not being cleaned up
- 🐛 Multiple resize listeners on window object
- 🐛 Cookie not synced with JWT expiration
- 🐛 CSRF vulnerability with SameSite cookie protection
- 🐛 Potential SSRF in proxy route

### Security

- ✅ XSS protection via HttpOnly cookies
- ✅ CSRF protection via SameSite cookies
- ✅ SSRF protection via path validation
- ✅ Path traversal prevention
- ✅ Role-based access control
- ✅ Admin-only route protection
- ✅ Token leakage prevention

### Breaking Changes

⚠️ **Frontend Migration:**
- Old HTML frontend (frontend/) is now deprecated
- All users must use new Next.js frontend on port 9081
- Local storage auth tokens will not work (uses HttpOnly cookies now)
- Need to re-login after upgrade

⚠️ **API Changes:**
- Frontend now calls `/api/proxy/api/*` instead of `/api/*` directly
- Auth endpoints moved to Next.js BFF: `/api/auth/*`
- WebSocket token endpoint: `/api/auth/token` (replaces direct backend call)

### Migration Guide

**From v1.x to v2.0:**

1. **Backup existing data:**
   ```bash
   cp data/servers.db data/servers.db.backup
   ```

2. **Install frontend dependencies:**
   ```bash
   cd frontend-next
   npm ci
   ```

3. **Configure frontend environment:**
   ```bash
   cd frontend-next
   cat > .env.local << EOF
   API_PROXY_TARGET=http://localhost:9083
   NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
   NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084
   EOF
   ```

4. **Build frontend:**
   ```bash
   npm run build
   ```

5. **Update systemd services** (if using):
   ```bash
   sudo cp services/server-monitor-frontend.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable server-monitor-frontend.service
   sudo systemctl start server-monitor-frontend.service
   ```

6. **Update nginx config** (if using reverse proxy):
   - Update frontend proxy to point to port 9081
   - Ensure `/api/auth/*` and `/api/proxy/*` go to Next.js
   - See DEPLOYMENT.md for full nginx config

7. **Clear browser data:**
   - Users need to clear cookies and local storage
   - Re-login required after upgrade

---

## [1.1.0] - 2026-01-06

### Added
- Form helper system with loading states
- Real-time form validation
- Toast notifications for user actions

### Fixed
- Database path issues (removed hardcoded `/opt` paths)
- Enhanced input validation (IP, hostname, port)
- Frontend cleanup (removed 11 duplicate files)

### Changed
- Improved UX with consistent error handling
- Loading indicators across all forms
- User-friendly error messages

### Documentation
- Added PROJECT_ASSESSMENT.md
- Added TODO-IMPROVEMENTS.md
- Enhanced form guides

---

## [1.0.0] - 2026-01-06

### Initial Release

#### Added
- 🌐 Multi-server monitoring dashboard
- 📊 Real-time updates via WebSocket
- 🖥️ Web terminal emulator (xterm.js + SSH)
- 📧 Email alerts system with SMTP
- 📤 Export data (CSV/JSON)
- 🔑 SSH key management
- 🔐 JWT authentication system
- 🛡️ Advanced security (rate limiting, CORS, validation)
- 🧪 Comprehensive testing suite (23 tests)
- 🚀 Production-ready deployment scripts
- 📚 Complete documentation

#### Technical Details
- **Backend:** Python 3.8+ with Flask-like HTTP server
- **Frontend:** Static HTML/CSS/JavaScript
- **Database:** SQLite
- **WebSocket:** Custom Python WebSocket server
- **Terminal:** WebSocket-based SSH proxy

---

## Version Comparison

| Version | Release Date | Frontend | Auth Method | Security Score | Status |
|---------|--------------|----------|-------------|----------------|--------|
| 1.0.0 | 2026-01-06 | HTML/JS | localStorage | 8.5/10 | Deprecated |
| 1.1.0 | 2026-01-06 | HTML/JS | localStorage | 8.5/10 | Deprecated |
| 2.0.0 | 2026-01-07 | Next.js | HttpOnly cookies | 9/10 | **Current** |

---

## Contributors

- **Minh Tuấn** ([@minhtuancn](https://github.com/minhtuancn)) - Project maintainer
- GitHub Copilot - Development assistance

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

**Last Updated:** 2026-01-07
