# Changelog - Server Monitor Dashboard

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2026-01-07 - Phase 5: Production Polish

### 🚀 Production-Ready Release with OpenAPI Documentation

This release focuses on production polish, comprehensive API documentation, and enhanced testing infrastructure to make the project OSS-ready and enterprise-grade.

### Added

**OpenAPI / Swagger Documentation**
- ✨ Comprehensive OpenAPI 3.0.3 specification at `docs/openapi.yaml`
  - All API endpoints documented with request/response schemas
  - Security schemes (Bearer token + HttpOnly cookies)
  - Error codes standardized (401/403/404/422/429/500)
  - Examples for all major operations
- ✨ Swagger UI integration at `/docs` endpoint
  - Interactive API documentation
  - "Try it out" functionality for testing endpoints
  - Accessible from Central API (port 9083)
- ✨ OpenAPI YAML endpoint at `/api/openapi.yaml`
  - Public access for API consumers
  - Machine-readable specification

**Testing Infrastructure**
- ✨ Automated smoke test script (`scripts/smoke.sh`)
  - Port availability checks
  - Health endpoint verification
  - Authentication flow testing
  - Database connectivity checks
  - Verbose mode for detailed output
  - Exit codes for CI integration
- ✨ Comprehensive smoke test checklist
  - Phase 4 features coverage (SSH Vault, Terminal, Inventory, Tasks, Notes/Tags)
  - Phase 5 features coverage (OpenAPI, Swagger UI)
  - Step-by-step manual testing procedures
  - Troubleshooting guides

**Documentation**
- ✨ API Reference complete with:
  - 70+ documented endpoints
  - Authentication flows
  - RBAC authorization patterns
  - WebSocket connection details
  - Ports and reverse proxy paths

### Changed

- ⚡ Improved startup messages with documentation links
- ⚡ Enhanced SMOKE_TEST_CHECKLIST.md with Phase 4 & 5 features
- ⚡ Better test organization and coverage documentation

### Documentation Improvements

- 📚 API endpoints now have canonical documentation
- 📚 Security schemes clearly defined
- 📚 Integration examples for API consumers
- 📚 Testing procedures standardized

### Technical Details

**API Coverage:**
- Authentication: login, logout, verify, session
- Users: CRUD, roles, password management
- Servers: CRUD, connection testing, inventory, tasks, notes
- SSH Keys: Vault operations, testing
- Terminal: Sessions management, stop operations
- Monitoring: Real-time stats, WebSocket
- Tasks: Remote command execution, status tracking
- Audit Logs: Activity tracking, filtering
- Settings: Application configuration
- Notifications: Email, Telegram, Slack
- Export: CSV, JSON formats

**Testing:**
- Crypto vault: 9/9 tests passing ✅
- Security tests: Require running server (integration tests)
- Smoke tests: Automated script for quick validation
- CI/CD: GitHub Actions workflows for backend and frontend

---

## [Unreleased] - Phase 4

### 🚀 Phase 4 Module 4 & 5: Tasks/Remote Command + Notes/Tags Enhancement

**Remote Command Execution + Enhanced Notes + Tags System**

### Added

**Module 4: Tasks / Remote Command Execution**
- ✨ Task execution engine with asynchronous worker threads
  - In-process task queue with concurrency limits
  - Configurable worker thread pool (default: 4 workers)
  - Per-server concurrency limits (default: 1 task)
  - Exponential backoff for task re-queueing
- ✨ `tasks` table with UUID primary keys and comprehensive indexes
- ✨ Task management functions in `database.py`
  - `create_task()` - Create new task
  - `get_task()` - Get task by ID
  - `get_tasks()` - List tasks with filtering
  - `update_task_status()` - Update task status and results
  - `delete_old_tasks()` - Cleanup old tasks
- ✨ REST API endpoints for tasks
  - `POST /api/servers/:id/tasks` - Execute remote command (admin/operator)
  - `GET /api/tasks` - List tasks with filtering (role-based access)
  - `GET /api/tasks/:id` - Get task details with output
  - `POST /api/tasks/:id/cancel` - Cancel running/queued tasks
- ✨ Security features
  - Output storage disabled by default
  - Configurable output truncation (max: 64KB default)
  - SSH authentication priority: vault → key file → password
  - Command length validation (max: 10KB default)
  - Comprehensive audit logging (create/start/finish/fail/timeout/cancel)
- ✨ UI components in Server Workspace
  - Tasks tab with real-time status updates (3s polling)
  - Task execution form with security warnings
  - Task list with status badges and duration
  - Task detail dialog with stdout/stderr viewer
- ✨ Task configuration via environment variables
  - `TASKS_STORE_OUTPUT_DEFAULT` - Output storage policy
  - `TASKS_OUTPUT_MAX_BYTES` - Max output size
  - `TASKS_CONCURRENT_PER_SERVER` - Concurrency limit
  - `TASKS_DEFAULT_TIMEOUT` - Default timeout
  - `TASKS_NUM_WORKERS` - Worker thread count
  - `TASK_COMMAND_MAX_LENGTH` - Max command length

**Module 5: Notes / Tags Enhancement**
- ✨ Enhanced `server_notes` table
  - Added `updated_by` field for edit tracking
  - Added `deleted_at` field for soft delete
  - Audit trail for note operations
- ✨ `tags` table for server categorization
  - Name, color, description fields
  - Created_by tracking
- ✨ `server_tag_map` table for server-tag associations
  - Many-to-many relationship
  - Unique constraint per server-tag pair
  - Cascade delete on server/tag removal
- ✨ Tag management functions in `database.py`
  - `create_tag()`, `get_tags()`, `get_tag()`, `update_tag()`, `delete_tag()`
  - `add_server_tag()`, `remove_server_tag()`, `get_server_tags()`
  - `get_servers_by_tag()` for reverse lookups
- ✨ Enhanced note functions
  - `add_server_note()` with proper field tracking
  - `get_server_notes()` with soft delete support
  - `update_server_note()` with updated_by tracking
  - `delete_server_note()` with soft delete option

**Database & Migrations**
- ✨ Migration 007: Module 4 Tasks table and indexes
- ✨ Migration 008: Module 5 Notes/Tags enhancement
- ✨ Safe schema upgrades with version tracking
- ✨ Backward compatible migrations

**Documentation**
- ✨ Comprehensive `docs/modules/TASKS.md`
  - Architecture and security model
  - API reference
  - Configuration guide
  - Troubleshooting section
- ✨ Updated `.env.example` with task configuration

### Changed
- ⚡ Improved error handling in task queue
  - Queue overflow detection and handling
  - Proper task failure marking
  - 5-second timeout on queue operations
- ⚡ Enhanced timeout detection
  - Use specific exception types (socket.timeout, paramiko.SSHException)
  - More reliable than string matching
- ⚡ Better task re-queueing with exponential backoff
  - Prevents busy-waiting when server limits reached
  - Adaptive delay based on queue size
- ⚡ Replaced magic numbers with configurable constants
  - `TASK_COMMAND_MAX_LENGTH` - Configurable command length limit
  - `TASK_COMMAND_PREVIEW_LENGTH` - Consistent preview truncation

### Fixed
- 🐛 Notes creation no longer sets `updated_by` on initial create
  - Prevents timestamp inconsistency
  - `updated_by` now only set on actual updates
- 🐛 Task timeout detection now uses proper exception handling
  - Handles both `socket.timeout` and `paramiko.SSHException`
  - No longer relies on error message strings
- 🐛 Task queue overflow properly handled
  - Failed tasks marked immediately
  - User feedback provided
  - No silent failures

### Security
- 🔒 Task output storage disabled by default
- 🔒 Output truncation to prevent data leaks (64KB limit)
- 🔒 Command length validation (10KB limit)
- 🔒 RBAC enforcement (admin/operator create, viewer read-only)
- 🔒 Comprehensive audit trail for all task operations
- 🔒 SSH key vault integration for secure authentication

---

### 🚀 Phase 4 Module 3: Server Inventory & System Info

**Agentless Inventory Collection + Server Workspace UX + Recent Activity Dashboard**

### Added

**Backend:**
- ✨ `inventory_collector.py` - Agentless system information collection via SSH
  - Read-only command execution with timeout
  - Support for various Linux distributions
  - SSH Key Vault integration
  - Best-effort collection with graceful fallback
- ✨ `server_inventory_latest` table - Store most recent inventory per server
- ✨ `server_inventory_snapshots` table - Historical inventory snapshots
- ✨ Inventory management functions in `database.py`
  - `save_server_inventory()` - Save/update inventory data
  - `get_server_inventory_latest()` - Get most recent inventory
  - `get_server_inventory_snapshots()` - Get historical snapshots
- ✨ API endpoints for inventory
  - `POST /api/servers/{id}/inventory/refresh` - Trigger collection (admin/operator)
  - `GET /api/servers/{id}/inventory/latest` - Get latest inventory (all roles)
  - `GET /api/activity/recent` - Get recent activity for dashboard
- ✨ Inventory collection includes:
  - OS information (name, version, kernel)
  - Hostname and uptime
  - CPU details (model, cores)
  - Memory usage (total, used, available)
  - Disk usage (total, used, available)
  - Network configuration (primary IP, interfaces)
  - Optional: Package counts and running services
- ✨ Audit logging for `inventory.refresh` actions

**Frontend:**
- ✨ Server Workspace page with tabbed interface
  - Overview tab: Server details and current metrics
  - Inventory tab: System information cards
  - Terminal tab: Quick access to terminal
  - Notes tab: Server notes with Markdown
- ✨ Inventory UI components
  - Refresh Inventory button with loading states
  - Card-based layout for OS, CPU, Memory, Disk, Network
  - Empty states and error handling
  - Timestamp display for last collection
- ✨ Recent Activity widget on Dashboard
  - Shows recent user actions (terminal, keys, inventory, etc.)
  - Enriched with usernames and server names
  - Icons for different action types
  - Time-ago formatting
  - Auto-refresh every 30 seconds
- ✨ TypeScript types for inventory data structures

**Documentation:**
- 📚 `docs/modules/INVENTORY.md` - Complete inventory module documentation
- 📚 Updated README.md with inventory features
- 📚 Updated CHANGELOG.md with Phase 4 Module 3 changes

**Features:**
- 📦 **Agentless Collection:** No agent installation required, uses SSH
- 🔐 **Secure Authentication:** Supports SSH Key Vault, file paths, and passwords
- 🖥️ **Comprehensive Data:** OS, kernel, hardware, and resource information
- 🔄 **Server Workspace:** Unified tabbed interface for server management
- 📊 **Recent Activity:** Real-time dashboard widget showing latest actions
- 🛡️ **RBAC Enforcement:** Proper role-based access control
- 📝 **Audit Logging:** All refresh operations logged for compliance

### 🚀 Phase 4 Module 2: Web Terminal Enhancement

**Secure Session Management with SSH Key Vault Integration**

### Added

**Backend:**
- ✨ `terminal_sessions` table - Track all terminal sessions with metadata
- ✨ `audit_logs` table - Append-only audit trail for all sensitive operations
- ✨ Session management functions in `database.py`
  - `create_terminal_session()` - Create new session record
  - `end_terminal_session()` - Mark session as ended
  - `update_terminal_session_activity()` - Update activity timestamp
  - `get_terminal_sessions()` - Query sessions with filters
- ✨ Audit log functions in `database.py`
  - `add_audit_log()` - Add audit entry (append-only)
  - `get_audit_logs()` - Query logs with filters and pagination
- ✨ Enhanced `backend/terminal.py`
  - SSH key vault integration via `ssh_key_id` parameter
  - Session tracking with database persistence
  - Idle timeout detection (30 minutes default)
  - Proper resource cleanup with audit logging
  - RBAC enforcement (admin/operator only)
- ✨ API endpoints for session management
  - `GET /api/terminal/sessions` - List sessions (filtered by role)
  - `POST /api/terminal/sessions/{id}/stop` - Stop session (with ownership check)
  - `GET /api/audit-logs` - View audit logs (admin only)
- ✨ Audit logging for sensitive operations
  - Terminal open/close events
  - SSH key create/delete events
  - Server delete events

**Features:**
- 🔐 **SSH Key Vault Integration:** Terminal can authenticate using encrypted SSH keys from vault
- 📊 **Session Tracking:** All terminal sessions tracked in database with status
- 📝 **Audit Trail:** Complete audit log for terminal access and sensitive operations
- ⏱️ **Idle Timeout:** Automatic session termination after 30 minutes of inactivity
- 🛡️ **RBAC:** Admin/operator access with ownership checks
- 🧹 **Proper Cleanup:** Session resources cleaned up on disconnect
- 🔍 **Session Management:** API endpoints to list and stop sessions

**Security:**
- Private keys decrypted only in memory
- Keys never logged or persisted decrypted
- Audit logs are append-only (no updates/deletes)
- RBAC enforcement on all new endpoints
- Operators can only see/manage their own sessions
- Admin has full visibility and control

**Documentation:**
- 📚 `docs/modules/WEB_TERMINAL.md` - Complete module documentation
  - Technical implementation details
  - API endpoint specifications
  - Security features
  - Testing guide
  - Troubleshooting guide

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
