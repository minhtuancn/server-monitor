# Server Monitor - Tasks Backlog

**Organized task list using Now / Next / Later framework for clear prioritization.**

Last Updated: 2026-01-09

---

## How to Use This Document

- **Now**: Currently in progress or next up (this sprint/week)
- **Next**: Planned for upcoming sprint/month
- **Later**: Future work, not yet scheduled

Each task includes:

- **Owner**: Who's working on it (or `unassigned`)
- **Priority**: 🔴 Critical / 🟡 High / 🟢 Medium / 🔵 Low
- **Effort**: S (< 1 day) / M (1-3 days) / L (3-5 days) / XL (> 5 days)
- **Definition of Done**: Clear acceptance criteria

---

## NOW (This Week)

### 🔴 Critical

#### [NOW-1] Fix CORS Rate Limiting Test Failures

- **Owner**: `unassigned`
- **Priority**: 🔴 Critical
- **Effort**: M (2-3 days)
- **Issue**: #pending
- **Description**: Two rate limiting tests fail due to IP blocking between tests
- **Files**: `tests/test_security.py`, `backend/security.py`
- **DoD**:
  - [ ] Identify test interference root cause
  - [ ] Add test fixtures to prevent IP blocking
  - [ ] All 25 tests pass: `pytest tests/ -v`
  - [ ] Document findings in test comments

#### [NOW-2] Security Audit & Hardening

- **Owner**: `unassigned`
- **Priority**: 🔴 Critical (before production)
- **Effort**: L (3-5 days)
- **Description**: Complete security review before production deployment
- **DoD**:
  - [ ] Review Bandit security scan findings
  - [ ] Change default admin password policy (force change on first login)
  - [ ] Verify JWT_SECRET and ENCRYPTION_KEY are strong in production
  - [ ] Review CORS allowed origins (no wildcard \*)
  - [ ] Configure firewall rules (ports 9081, 9083, 9084, 9085)
  - [ ] Document security checklist in docs/security/PRODUCTION_SECURITY.md

---

### 🟡 High

#### [NOW-3] E2E Test Suite Setup (Playwright)

- **Owner**: `unassigned`
- **Priority**: 🟡 High
- **Effort**: L (4 days)
- **Issue**: #pending
- **Description**: Add end-to-end testing for critical user flows
- **Files**: `tests/e2e/`, `package.json`, `.github/workflows/e2e.yml`
- **DoD**:
  - [ ] Playwright installed and configured
  - [ ] Test: First-run setup flow (create admin)
  - [ ] Test: Login → Dashboard → Logout
  - [ ] Test: Add server → View metrics
  - [ ] Test: Terminal page loads (mock SSH if needed)
  - [ ] CI/CD pipeline runs E2E tests on PR
  - [ ] Documentation in docs/testing/E2E_TESTS.md

#### [NOW-4] Mobile Responsive Design Improvements

- **Owner**: `unassigned`
- **Priority**: 🟡 High
- **Effort**: M (2-3 days)
- **Description**: Ensure dashboard is usable on mobile devices
- **Files**: `frontend-next/src/app/[locale]/dashboard/page.tsx`, CSS modules
- **DoD**:
  - [ ] Dashboard loads on mobile (320px width)
  - [ ] All tables scrollable horizontally on mobile
  - [ ] Navigation menu works on mobile (hamburger menu)
  - [ ] Charts responsive (resize properly)
  - [ ] Touch targets 44x44px minimum (accessibility)
  - [ ] Tested on iOS Safari and Android Chrome

---

## NEXT (This Month)

### 🟢 Medium

#### [NEXT-1] Database Backup Automation

- **Owner**: `unassigned`
- **Priority**: 🟢 Medium
- **Effort**: S (< 1 day)
- **Description**: Automated daily backups of SQLite database
- **Files**: `scripts/backup_database.sh`, `crontab` or systemd timer
- **DoD**:
  - [ ] Backup script creates timestamped .db.backup files
  - [ ] Script rotates old backups (keep last 7 days)
  - [ ] Cron job runs daily at 2 AM
  - [ ] Backup location configurable via env var
  - [ ] Restore script provided: `scripts/restore_database.sh`
  - [ ] Documentation in docs/operations/BACKUP_RESTORE.md

#### [NEXT-2] Health Check Dashboard

- **Owner**: `unassigned`
- **Priority**: 🟢 Medium
- **Effort**: M (2 days)
- **Description**: Admin dashboard showing service health (API, WebSocket, Terminal, DB)
- **Files**: `frontend-next/src/app/[locale]/admin/health/page.tsx`, `backend/central_api.py`
- **DoD**:
  - [ ] GET /api/admin/health endpoint returns service status
  - [ ] Frontend page shows service status with indicators (green/yellow/red)
  - [ ] Shows uptime, memory usage, disk space
  - [ ] Auto-refreshes every 10 seconds
  - [ ] Admin-only access (role check)

#### [NEXT-3] Breadcrumb Navigation

- **Owner**: `unassigned`
- **Priority**: 🟢 Medium
- **Effort**: S (< 1 day)
- **Description**: Add breadcrumb navigation to all pages
- **Files**: `frontend-next/src/components/layout/`, all page.tsx files
- **DoD**:
  - [ ] Breadcrumb component created
  - [ ] Shows current path: Dashboard > Servers > Server Detail
  - [ ] Clickable links to parent pages
  - [ ] Localized (works with i18n)
  - [ ] Accessible (ARIA labels)

#### [NEXT-4] Performance Optimization

- **Owner**: `unassigned`
- **Priority**: 🟢 Medium
- **Effort**: M (2-3 days)
- **Description**: Improve page load and API response times
- **DoD**:
  - [ ] Database indexes added for common queries
  - [ ] Frontend assets minified and compressed
  - [ ] Response caching headers added to static assets
  - [ ] Lazy loading for images
  - [ ] Benchmark shows 30% improvement in page load time

---

### 🔵 Low

#### [NEXT-5] Docker Compose for Development

- **Owner**: `unassigned`
- **Priority**: 🔵 Low
- **Effort**: M (1-2 days)
- **Description**: Easy local setup with Docker Compose
- **Files**: `docker-compose.yml`, `Dockerfile.backend`, `Dockerfile.frontend`, `docs/getting-started/DOCKER.md`
- **DoD**:
  - [ ] docker-compose.yml brings up full stack
  - [ ] Backend, frontend, and database containers
  - [ ] Hot reload works for development
  - [ ] Documentation for Docker setup
  - [ ] docker-compose down cleans up properly

#### [NEXT-6] Configurable Alert Thresholds Per Server

- **Owner**: `unassigned`
- **Priority**: 🔵 Low
- **Effort**: M (2 days)
- **Description**: Allow custom alert thresholds for each server
- **Files**: `backend/alert_manager.py`, `backend/database.py`, frontend settings page
- **DoD**:
  - [ ] Database schema updated (server_alert_thresholds table)
  - [ ] API endpoints: GET/PUT /api/servers/{id}/alert-thresholds
  - [ ] Frontend settings page for per-server thresholds
  - [ ] Falls back to global defaults if not set
  - [ ] Migration script provided

---

## LATER (Future / Backlog)

### Features

#### [LATER-1] Two-Factor Authentication (2FA)

- **Priority**: 🟡 High (for v2.5)
- **Effort**: L (4-5 days)
- **Description**: TOTP-based 2FA for enhanced security
- **Scope**: Backend auth, frontend setup page, QR code generation
- **Blocked by**: None
- **Roadmap**: v2.5.0

#### [LATER-2] OAuth2 Integration

- **Priority**: 🟡 High (for v2.5)
- **Effort**: XL (1-2 weeks)
- **Description**: Login with Google, GitHub, Azure AD
- **Scope**: OAuth2 flow, user provisioning, config UI
- **Blocked by**: None
- **Roadmap**: v2.5.0

#### [LATER-3] PostgreSQL Support

- **Priority**: 🟡 High (for v3.0)
- **Effort**: XL (2 weeks)
- **Description**: Support PostgreSQL as alternative to SQLite
- **Scope**: Database abstraction layer, migrations (Alembic), connection pooling
- **Blocked by**: None
- **Roadmap**: v3.0.0

#### [LATER-4] Multi-Tenancy

- **Priority**: 🟡 High (for v2.5)
- **Effort**: XL (2-3 weeks)
- **Description**: Tenant isolation for SaaS deployment
- **Scope**: Tenant model, data isolation, tenant admin role, per-tenant config
- **Blocked by**: None
- **Roadmap**: v2.5.0

#### [LATER-5] Custom Dashboard Builder

- **Priority**: 🟢 Medium (for v3.1)
- **Effort**: XL (3-4 weeks)
- **Description**: Drag-and-drop dashboard customization
- **Scope**: Widget library, layout engine, save/load dashboards
- **Blocked by**: None
- **Roadmap**: v3.1.0

### Improvements

#### [LATER-6] API Documentation (Swagger/OpenAPI)

- **Priority**: 🟢 Medium
- **Effort**: M (2 days)
- **Description**: Complete API documentation with examples
- **Status**: Partial (openapi.yaml exists, needs completion)

#### [LATER-7] Internationalization Expansion

- **Priority**: 🔵 Low
- **Effort**: M (per language, 2 days)
- **Description**: Add more languages (currently 8)
- **Candidates**: Portuguese, Dutch, Korean, Polish

#### [LATER-8] Dark Mode Improvements

- **Priority**: 🔵 Low
- **Effort**: S (< 1 day)
- **Description**: Better dark mode colors, smoother toggle
- **Status**: Dark mode exists, needs polish

#### [LATER-9] Keyboard Shortcuts

- **Priority**: 🔵 Low
- **Effort**: M (1-2 days)
- **Description**: Power-user keyboard shortcuts (e.g., / for search, g+d for dashboard)

#### [LATER-10] Advanced Reporting

- **Priority**: 🟢 Medium (for v3.1)
- **Effort**: L (1 week)
- **Description**: Scheduled reports (PDF, email), trend analysis

### Technical Debt

#### [TD-1] Extract Duplicate Validation Code

- **Priority**: 🔵 Low
- **Effort**: S (< 1 day)
- **Description**: Centralize form validation logic
- **Files**: Backend validators, frontend form utilities

#### [TD-2] Refactor Large Functions (> 100 lines)

- **Priority**: 🔵 Low
- **Effort**: M (2-3 days)
- **Description**: Break down complex functions for readability
- **Candidate files**: `backend/central_api.py`, `backend/agent.py`

#### [TD-3] Add Type Hints to All Python Modules

- **Priority**: 🔵 Low
- **Effort**: M (2-3 days)
- **Description**: Full type hint coverage for better IDE support and type checking
- **Files**: All backend/\*.py

#### [TD-4] ESLint Configuration for Frontend

- **Priority**: 🔵 Low
- **Effort**: S (< 1 day)
- **Description**: Stricter linting rules, auto-fix on save
- **Files**: `frontend-next/.eslintrc.json`

---

## Completed Recently ✅

### 2026-01-09

- ✅ [NOW-0] First-Run Admin Setup (Onboarding)

  - Implemented /[locale]/setup page
  - Backend endpoints: /api/setup/status, /api/setup/initialize
  - Middleware redirect logic
  - SKIP_DEFAULT_ADMIN env var support

- ✅ [NOW-0] Custom Domain Support

  - ALLOWED_FRONTEND_DOMAINS env var (backend CORS)
  - Frontend WebSocket URL configuration
  - setup-custom-domain.sh helper script
  - CUSTOM-DOMAIN-GUIDE.md comprehensive docs

- ✅ [NOW-0] Documentation Restructure
  - Created AGENTS.md with agent workflow rules
  - Organized docs/ into subdirectories
  - Created PR_CHECKLIST.md, ISSUE_TEMPLATE_AGENT_TASK.md, AGENT_STATUS_REPORT.md
  - Updated CONTRIBUTING.md with governance rules

### 2026-01-07

- ✅ Frontend Code Cleanup

  - Removed backup HTML files
  - Removed old dashboard versions
  - Created frontend README
  - Updated .gitignore

- ✅ Form Helpers & UX Improvements
  - Loading spinners for async operations
  - Toast notifications (success/error)
  - Client-side form validation
  - Standardized button styles

---

## Priorities Summary

### By Priority

- 🔴 **Critical** (2): Security tests, security audit
- 🟡 **High** (2): E2E tests, mobile responsive
- 🟢 **Medium** (5): Backup, health check, breadcrumbs, performance, alerts
- 🔵 **Low** (4+): Docker, keyboard shortcuts, technical debt

### By Effort

- **S** (< 1 day): 4 tasks
- **M** (1-3 days): 8 tasks
- **L** (3-5 days): 3 tasks
- **XL** (> 5 days): 5 tasks

---

## How to Contribute

### Claiming a Task

1. Comment on task (or create issue if none exists)
2. Assign yourself
3. Move to "In Progress"
4. Follow AGENTS.md workflow

### Adding a Task

1. Create issue with proper template
2. Discuss & get approval
3. Maintainer adds to TASKS.md
4. Prioritize in triage meeting

### Task Lifecycle

```
Backlog (LATER) → Planned (NEXT) → In Progress (NOW) → Done (Completed)
```

---

## Resources

- **Roadmap**: [ROADMAP.md](ROADMAP.md) (version-based planning)
- **AGENTS.md**: [/AGENTS.md](/AGENTS.md) (workflow rules)
- **Issue Templates**: [docs/templates/ISSUE_TEMPLATE_AGENT_TASK.md](../templates/ISSUE_TEMPLATE_AGENT_TASK.md)
- **PR Checklist**: [docs/templates/PR_CHECKLIST.md](../templates/PR_CHECKLIST.md)
- **Contributing**: [/CONTRIBUTING.md](/CONTRIBUTING.md)
