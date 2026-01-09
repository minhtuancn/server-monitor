# Issue Template: Agent Task

Use this template when creating issues for AI coding agents (GitHub Copilot, Cursor, etc.).

Clear, actionable issues help agents deliver better results and prevent scope creep.

---

## Issue Title Format

Use clear, actionable titles:

```
✅ Good:
- Fix CORS error when accessing API from custom domain
- Add input validation to user registration form
- Update CUSTOM-DOMAIN-GUIDE.md with Caddy examples

❌ Bad:
- CORS doesn't work
- Fix bug
- Update docs
```

---

## Issue Template

````markdown
## Goal

<!-- One clear, actionable sentence describing what should be accomplished -->

[Example: Fix CORS error when accessing API from custom domain mon.go7s.net]

## Problem/Context

<!-- Describe the current situation and why it needs to change -->

- **Current behavior**: [What happens now]
- **Expected behavior**: [What should happen]
- **Impact**: [Who is affected, how critical]

[Example:

- Current: CORS only allows localhost:9081; custom domains blocked
- Expected: CORS should allow domains specified in ALLOWED_FRONTEND_DOMAINS env var
- Impact: Blocks production deployment with custom domains]

## Files Likely Affected

<!-- List files that will need changes (helps agent scope work) -->

- `path/to/file1.py` — [why this file]
- `path/to/file2.tsx` — [why this file]
- `docs/guide.md` — [documentation update]

[Example:

- `backend/security.py` — CORS configuration logic
- `backend/.env.example` — document new environment variable
- `CUSTOM-DOMAIN-GUIDE.md` — add CORS troubleshooting section]

## Acceptance Criteria

<!-- Checkbox list of requirements; all must be met for issue to be closed -->

- [ ] [Criterion 1: specific, testable requirement]
- [ ] [Criterion 2: specific, testable requirement]
- [ ] [Criterion 3: documentation requirement]
- [ ] [Criterion 4: testing requirement]

[Example:

- [ ] Add ALLOWED_FRONTEND_DOMAINS environment variable support to backend/security.py
- [ ] CORS headers correctly include custom domain when env var is set
- [ ] Default behavior unchanged (localhost:9081) when env var not set
- [ ] Update backend/.env.example with ALLOWED_FRONTEND_DOMAINS example
- [ ] Update CUSTOM-DOMAIN-GUIDE.md with CORS configuration section
- [ ] All existing tests pass: pytest tests/test_security.py -v
- [ ] Manual test: curl with custom origin header succeeds]

## Non-Goals (Out of Scope)

<!-- Explicitly list what should NOT be done -->

- Do NOT [thing 1 that might be tempting but is out of scope]
- Do NOT [thing 2 that should be a separate issue]
- Defer [thing 3 for future work]

[Example:

- Do NOT rewrite entire CORS system (only add env var support)
- Do NOT add Redis caching (separate issue)
- Do NOT modify WebSocket CORS (uses same config, should work automatically)]

## Testing Instructions

<!-- How to verify the fix works -->

1. [Step 1]
2. [Step 2]
3. [Expected result]

[Example:

1. Set ALLOWED_FRONTEND_DOMAINS=mon.go7s.net in backend/.env
2. Start backend: cd backend && source venv/bin/activate && python central_api.py
3. Test: curl -H "Origin: https://mon.go7s.net" http://localhost:9083/api/servers
4. Expected: Response includes "Access-Control-Allow-Origin: https://mon.go7s.net"]

## Background/Resources

<!-- Optional: Links, screenshots, logs, related issues -->

- Related issue: #123
- Error logs: [paste relevant logs]
- Screenshot: [attach if UI bug]
- Documentation: [link to relevant docs]
- Reference implementation: [link if applicable]

## Priority

<!-- Help agent understand urgency -->

- 🔴 **Critical**: [Blocks production / security issue / data loss risk]
- 🟡 **High**: [Blocks key feature / impacts many users]
- 🟢 **Medium**: [Nice to have / quality of life improvement]
- 🔵 **Low**: [Future enhancement / minor polish]

## Estimated Effort

<!-- Optional: Help with planning -->

- **Small**: < 1 hour (simple fix, 1-2 files)
- **Medium**: 1-4 hours (moderate change, 3-5 files)
- **Large**: > 4 hours (significant feature, 5+ files, complex logic)

---

## Labels to Add

- `bug` — Something isn't working
- `enhancement` — New feature or request
- `documentation` — Improvements or additions to documentation
- `good first issue` — Good for newcomers
- `help wanted` — Extra attention is needed
- `priority: high` — High priority
- `agent-friendly` — Well-suited for AI coding agents
- `backend` — Backend/Python related
- `frontend` — Frontend/Next.js related
- `security` — Security related
- `performance` — Performance improvement

---

## Example Issues

### Example 1: Bug Fix

**Title**: `fix(backend): CORS error when accessing API from custom domain`

```markdown
## Goal

Fix CORS error when accessing API from custom domain mon.go7s.net

## Problem/Context

- **Current**: API calls from mon.go7s.net fail with CORS error
- **Expected**: API should accept requests from custom domains
- **Impact**: Blocks production deployment; affects all custom domain users

## Files Likely Affected

- `backend/security.py` — CORS configuration
- `backend/.env.example` — document env var
- `CUSTOM-DOMAIN-GUIDE.md` — add troubleshooting

## Acceptance Criteria

- [ ] Add ALLOWED_FRONTEND_DOMAINS env var to security.py
- [ ] Verify CORS headers include custom domain
- [ ] Update .env.example with example
- [ ] Update docs with CORS section
- [ ] All tests pass: pytest tests/test_security.py -v

## Non-Goals

- Do NOT rewrite entire CORS system
- Do NOT touch WebSocket CORS (same config applies)

## Testing Instructions

1. Set ALLOWED_FRONTEND_DOMAINS=mon.go7s.net
2. curl -H "Origin: https://mon.go7s.net" http://localhost:9083/api/servers
3. Expected: Response includes correct CORS header

## Priority

🟡 **High** — Blocks production deployment
```
````

### Example 2: Feature

**Title**: `feat(frontend): add first-run admin setup page`

```markdown
## Goal

Add /setup page for creating first admin user on fresh install

## Problem/Context

- **Current**: Default admin (admin/admin123) auto-created
- **Expected**: User creates custom admin via setup wizard
- **Impact**: Improves security; better UX for new installs

## Files Likely Affected

- `frontend-next/src/app/[locale]/(auth)/setup/page.tsx` — new page
- `frontend-next/middleware.ts` — redirect logic
- `backend/central_api.py` — setup endpoints
- `backend/user_management.py` — skip default admin

## Acceptance Criteria

- [ ] GET /api/setup/status returns {needs_setup: boolean}
- [ ] POST /api/setup/initialize creates first admin
- [ ] Frontend /setup page with username, email, password fields
- [ ] Middleware redirects to /setup when needs_setup=true
- [ ] After setup, user logged in and redirected to dashboard
- [ ] Tests pass, lint clean

## Non-Goals

- Do NOT add password reset flow (separate issue)
- Do NOT add 2FA (future enhancement)

## Testing Instructions

1. Delete data/servers.db
2. Start services: ./start-all.sh
3. Visit http://localhost:9081
4. Should redirect to /setup
5. Create admin user
6. Should login and see dashboard

## Priority

🟢 **Medium** — Nice to have for v2.4

## Estimated Effort

**Large** — 4-6 hours (backend + frontend + tests)
```

### Example 3: Documentation

**Title**: `docs: add Caddy examples to CUSTOM-DOMAIN-GUIDE.md`

```markdown
## Goal

Add Caddy reverse proxy examples to CUSTOM-DOMAIN-GUIDE.md

## Problem/Context

- **Current**: Guide only has Nginx examples
- **Expected**: Include Caddy examples for users who prefer it
- **Impact**: Helps Caddy users deploy with custom domains

## Files Likely Affected

- `CUSTOM-DOMAIN-GUIDE.md` — add Caddy section

## Acceptance Criteria

- [ ] Add "Caddy Configuration" section after Nginx
- [ ] Include basic Caddyfile with all necessary directives
- [ ] Show WebSocket proxying configuration
- [ ] Add link from README.md to guide
- [ ] No broken links

## Non-Goals

- Do NOT remove Nginx examples
- Do NOT add Apache examples (separate issue if needed)

## Testing Instructions

1. Review Caddyfile syntax
2. Check that all endpoints covered (/, /api/_, /ws/_)
3. Verify no broken links: grep -r "old-link" docs/

## Priority

🔵 **Low** — Nice to have

## Estimated Effort

**Small** — < 1 hour (docs only)
```

---

## Tips for Writing Agent-Friendly Issues

✅ **Do:**

- Be specific and actionable
- Include file paths
- List acceptance criteria as checkboxes
- Explicitly state non-goals
- Provide testing instructions
- Use examples and context

❌ **Don't:**

- Write vague descriptions ("fix bug", "improve performance")
- Omit testing steps
- Mix multiple unrelated changes
- Skip non-goals section
- Assume agent knows your context
- Leave acceptance criteria ambiguous

**Remember**: A well-written issue saves time and produces better results!
