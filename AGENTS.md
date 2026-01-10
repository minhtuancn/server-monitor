# AGENTS Guidelines for Server Monitor

This repository contains a **multi-server monitoring system** with:

- **Backend**: Python (FastAPI/central_api.py on port 9083, WebSocket 9085, Terminal 9084)
- **Frontend**: Next.js 16 (App Router, TypeScript, React 19, Turbopack, port 9081)
- **Agents**: Python SSH agents collecting metrics from remote servers

When working on this project with AI coding agents, follow these guidelines to maintain quality and avoid scope creep.

---

## 1. Scope & Non-Goals

### ✅ In Scope (What to work on)

- Bug fixes in existing features
- Performance improvements with evidence (benchmarks/profiling)
- Security patches (CVE fixes, hardening)
- Test coverage improvements
- Documentation updates reflecting actual code
- UI/UX polish within existing design system (MUI)

### ❌ Out of Scope (Do NOT do unless explicitly requested)

- **No architecture rewrites** — Don't replace FastAPI with Express, SQLite with PostgreSQL, etc.
- **No dependency changes** — Don't add new frameworks or replace existing ones
- **No design system changes** — MUI v5 is the standard; don't introduce Chakra/Ant/Shadcn
- **No "nice to have" features** — If it's not in ROADMAP.md or explicitly requested, create an issue first
- **No file moves without migration plan** — Respect existing structure; propose changes via issue

### 🚨 Sacred Code (Never Touch Without Explicit Permission)

- `installer.sh` / systemd service files — production deployment scripts
- Database migration scripts — risk of data loss
- Database backup/restore scripts (`scripts/backup-database.sh`, `scripts/restore-database.sh`) — production data safety
- `start-all.sh` / `stop-all.sh` — production start/stop orchestration
- Authentication/JWT logic in `backend/security.py` and `backend/user_management.py`
- WebSocket server core in `backend/websocket_server.py`

---

## 2. How to Work in This Repo

### Working Directory

**Always run commands from project root** (`/opt/server-monitor` or wherever cloned).

### Backend Development (Python)

```bash
# Setup Python environment (REQUIRED before any Python work)
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run tests (subset for speed)
pytest tests/test_security.py -v
pytest tests/test_user_management.py -v

# Lint
flake8 backend/ --max-line-length=120
black backend/ --check

# Before committing backend changes:
pytest tests/ -v  # Full suite
flake8 backend/
black backend/
```

### Frontend Development (Next.js)

```bash
# Setup
cd frontend-next
npm install

# Development server (HMR enabled)
npm run dev  # Runs on http://localhost:9081

# Type checking
npx tsc --noEmit

# Lint
npm run lint

# Build check (local only, NOT during interactive agent sessions)
npm run build

# Before committing frontend changes:
npm run lint
npx tsc --noEmit
npm run build  # Verify build succeeds
```

### Full Stack Testing

```bash
# Start all services
./start-all.sh

# Stop all services
./stop-all.sh

# Development mode (skip default admin creation for onboarding)
./start-dev.sh
```

---

## 3. Testing Requirements

### Before Every PR

- **Backend**: Run `pytest tests/ -v` — all tests must pass
- **Frontend**: Run `npm run lint && npx tsc --noEmit && npm run build` — no errors
- **Integration**: Start services with `./start-all.sh` and verify:
  - Dashboard loads at http://localhost:9081
  - Login works (create user via /setup if first-run)
  - WebSocket metrics update every 3 seconds
  - Terminal page accessible (if SSH configured)

### Writing New Tests

- Backend: Add pytest tests in `tests/` matching pattern `test_*.py`
- Frontend: (Currently manual; E2E tests are future roadmap item)
- Security: Run `bandit -r backend/` for security scan

---

## 4. No Rambling — PR/Issue Format

### Every PR Must Include:

```markdown
## Summary

- [One-line description of change]

## Scope

- Files changed: backend/security.py, frontend-next/src/app/[locale]/login/page.tsx
- Features affected: Authentication, login UI

## Out of Scope

- Did NOT touch user management, WebSocket, or database schema

## Testing

- [x] Ran pytest tests/ -v (all pass)
- [x] Ran npm run lint && npm run build (no errors)
- [x] Tested login flow manually: admin/admin123 → dashboard

## Risks

- Low: Only UI text changes
  OR
- Medium: Modified auth cookie logic; test thoroughly

## Docs Updated

- Updated SECURITY.md with new rate limit values
  OR
- No docs changes needed (UI-only)
```

### Every Issue for Agents Must Include:

```markdown
## Goal

[Clear, actionable goal. Example: "Fix CORS error when accessing API from custom domain"]

## Context

- User reports: "API calls fail with CORS error on mon.go7s.net"
- Current behavior: CORS only allows localhost:9081
- Expected: CORS should allow custom domains via env var

## Files Likely Affected

- backend/security.py (CORS logic)
- backend/.env.example (document new env var)
- CUSTOM-DOMAIN-GUIDE.md (update docs)

## Acceptance Criteria

- [ ] Add ALLOWED_FRONTEND_DOMAINS env var support to security.py
- [ ] Update .env.example with example
- [ ] Update CUSTOM-DOMAIN-GUIDE.md with CORS section
- [ ] Test: curl from custom domain succeeds with proper origin header

## Non-Goals

- Do NOT rewrite entire CORS system
- Do NOT add Redis caching (separate issue)
```

**If you want to do extra work not in the issue, create a new issue and link it. Do NOT lump unrelated changes into one PR.**

---

## 5. Documentation Rules

### Single Source of Truth

- **All documentation lives in `docs/` directory** — see `docs/README.md` for index
- **Root-level docs are stubs** that link to `docs/` (except README.md, LICENSE, CONTRIBUTING.md, AGENTS.md)

### When Adding/Moving Docs

1. Place file in appropriate `docs/` subdirectory:
   - `docs/getting-started/` — installation, setup, quick start
   - `docs/architecture/` — system design, components
   - `docs/operations/` — backup, logs, upgrades
   - `docs/security/` — security model, best practices
   - `docs/product/` — roadmap, tasks, release notes
   - `docs/templates/` — PR templates, issue templates
2. Update `docs/README.md` index with link
3. If moving existing doc from root, leave a stub:

   ```markdown
   # [Original Title]

   This document has moved to [docs/path/to/doc.md](docs/path/to/doc.md).
   ```

### No Broken Links

- After moving files, **grep for old paths** and update:
  ```bash
  grep -r "old-filename.md" .
  ```
- Test all links in README.md, DEPLOYMENT.md, SECURITY.md

### No "Localhost Links" in Production Docs

- Use relative paths: `docs/security/SECURITY_MODEL.md`
- NOT: `http://localhost:9083/docs` (wrong for prod users)
- Exception: Examples explicitly showing localhost usage

---

## 6. Code Style & Conventions

### Backend (Python)

- **PEP 8** with 120-char line length
- Use type hints: `def get_user(user_id: int) -> Optional[User]:`
- Use `black` for formatting (no arguments needed)
- No wildcard imports: `from module import specific_function`

### Frontend (TypeScript/React)

- **Strict TypeScript** (`strict: true` in tsconfig.json)
- **Functional components** with hooks (no class components)
- **Server Components** by default; use `"use client"` only when needed (state, effects, browser APIs)
- **MUI components** for UI; don't introduce new UI libraries
- **TanStack Query** for data fetching (see `src/hooks/use-servers.ts`)

### File Naming

- Backend: `snake_case.py`
- Frontend: `kebab-case.tsx` for pages, `PascalCase.tsx` for components
- No abbreviations: `user-management.tsx` not `usr-mgmt.tsx`

---

## 7. Release Hygiene

### Before Tagging a Release

1. **Update CHANGELOG.md**:

   ```markdown
   ## [v2.3.1] - 2026-01-10

   ### Fixed

   - CORS error with custom domains
   - Hydration error in locale layout
   ```

2. **Update version** in relevant files:

   - `frontend-next/package.json` version field
   - `README.md` badge
   - `docs/product/ROADMAP.md` (mark version as released)

3. **Run full test suite**:

   ```bash
   cd backend && pytest tests/ -v
   cd ../frontend-next && npm run lint && npm run build
   ```

4. **Smoke test checklist** (see `SMOKE_TEST_CHECKLIST.md`):

   - [ ] Fresh install works (`./installer.sh`)
   - [ ] First-run setup creates admin
   - [ ] Login → dashboard works
   - [ ] Metrics update via WebSocket
   - [ ] Terminal loads (if configured)

5. **Create release notes** (`docs/product/RELEASE_NOTES_vX.X.X.md`):
   - Summary (3-5 bullet points)
   - New features
   - Bug fixes
   - Breaking changes (if any)
   - Upgrade instructions (if needed)

### Versioning

- **Semantic Versioning** (semver): `vMAJOR.MINOR.PATCH`
  - MAJOR: Breaking changes (API changes, schema changes)
  - MINOR: New features (backward-compatible)
  - PATCH: Bug fixes

---

## 8. Common Workflows

### "Fix a bug in backend API"

```bash
# 1. Identify the file
cd backend
grep -r "the error message" .

# 2. Write a test first (TDD)
# Edit tests/test_<module>.py
pytest tests/test_<module>.py -v  # Should fail

# 3. Fix the code
# Edit <module>.py

# 4. Test passes
pytest tests/test_<module>.py -v  # Should pass

# 5. Full suite
pytest tests/ -v

# 6. Lint
flake8 backend/
black backend/
```

### "Add a new frontend page"

```bash
cd frontend-next

# 1. Create page component
mkdir -p src/app/[locale]/my-feature
touch src/app/[locale]/my-feature/page.tsx

# 2. Add to navigation (if needed)
# Edit src/components/layout/sidebar-navigation.tsx

# 3. Type check
npx tsc --noEmit

# 4. Lint
npm run lint

# 5. Test in browser
npm run dev
# Visit http://localhost:9081/en/my-feature
```

### "Update documentation"

```bash
# 1. Edit the doc
vim docs/getting-started/QUICK_START.md

# 2. Update index if new doc
vim docs/README.md

# 3. Check for broken links
grep -r "old-path" docs/
grep -r "old-path" *.md

# 4. Preview (if Markdown viewer available)
# Or commit and check on GitHub
```

---

## 9. Debugging Tips

### Backend Not Starting

```bash
# Check logs
tail -f logs/api.log

# Check port conflicts
lsof -i:9083

# Activate venv
cd backend
source venv/bin/activate
python central_api.py  # Manual start to see errors
```

### Frontend Build Fails

```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run build
```

### WebSocket Not Connecting

```bash
# Check WebSocket server
lsof -i:9085

# Check logs
tail -f logs/websocket.log

# Test with wscat
npm install -g wscat
wscat -c ws://localhost:9085/ws/monitoring
```

### Database Management

#### Backup Database (Recommended Way)

```bash
# Create encrypted backup with GPG (AES256)
./scripts/backup-database.sh backup

# List all backups
./scripts/backup-database.sh list

# Backups are stored in: data/backups/
# Format: servers_db_YYYYMMDD_HHMMSS.db.gpg
```

#### Restore Database

```bash
# Restore from backup (interactive with safety confirmation)
./scripts/restore-database.sh

# Non-interactive restore (for automation)
./scripts/restore-database.sh --backup servers_db_20260110_012354.db.gpg --yes

# Auto-creates pre-restore backup and rolls back on failure
```

#### Manual Database Operations (Dev Only)

```bash
# Manual backup (unencrypted, dev only)
cp data/servers.db data/servers.db.backup

# Check schema
sqlite3 data/servers.db ".schema"

# Check integrity
sqlite3 data/servers.db "PRAGMA integrity_check;"

# Fresh start (dev only!)
rm data/servers.db
./start-dev.sh  # Recreates DB
```

#### Automated Backups

```bash
# Setup cron job (2 AM daily with 7-day retention)
./scripts/setup-backup-automation.sh

# View backup logs
tail -f logs/backup.log

# Current schedule
crontab -l | grep backup
```

#### Database Management UI

- Frontend page: `/en/settings/database`
- Features: Health monitoring, backup/restore, storage stats
- Admin-only access
- Real-time status updates (30s refresh)

---

## 10. What to Report Back

### After Completing Work

Use this format (see `docs/templates/AGENT_STATUS_REPORT.md`):

```markdown
## Summary

[1-3 bullet points of what was done]

## Files Changed

- backend/security.py (added CORS env var support)
- backend/.env.example (documented ALLOWED_FRONTEND_DOMAINS)
- CUSTOM-DOMAIN-GUIDE.md (added CORS section)

## Testing Done

- [x] pytest tests/test_security.py -v (all pass)
- [x] Manual test: curl with custom origin header succeeds
- [x] Verified CORS error is gone

## Risks

- Low: Only adds env var support, no breaking changes

## Docs Updated

- Updated CUSTOM-DOMAIN-GUIDE.md
- Updated backend/.env.example

## Follow-up Items

- None
  OR
- Consider adding E2E test for CORS (separate issue)
```

---

## 11. Emergency Contacts & Resources

- **Project Docs**: `docs/README.md` (index)
- **Roadmap**: `docs/product/ROADMAP.md`
- **Tasks**: `docs/product/TASKS.md`
- **Architecture**: `docs/architecture/ARCHITECTURE.md`
- **Security**: `docs/security/SECURITY.md`
- **API Docs**: http://localhost:9083/docs (Swagger UI, when services running)

---

## Summary

**Golden Rules:**

1. ✅ Work from project root
2. ✅ Test before every PR (backend: pytest, frontend: lint + build)
3. ✅ Follow existing patterns (no rewrites)
4. ❌ Don't touch sacred code (installer, systemd, migrations)
5. ❌ Don't add scope creep (create separate issues)
6. 📚 Keep docs in `docs/`, update `docs/README.md`
7. 🔗 Fix broken links after moving files
8. 📝 Use PR template, report back with status

**When in doubt**: Ask first, code second. This prevents wasted effort and maintains project stability.
