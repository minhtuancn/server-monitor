# Server Monitor Documentation Index

**This is the single source of truth for all project documentation.**

Last Updated: 2026-01-09

---

## 📚 Documentation Structure

### Getting Started

**Quick Start & Installation**

- [/README.md](/README.md) — Project overview, quick navigation
- [QUICK_START.md](getting-started/QUICK_START.md) — Local development setup (5 min)
- [FIRST_RUN.md](getting-started/FIRST_RUN.md) — First-run setup wizard
- [TROUBLESHOOTING.md](getting-started/TROUBLESHOOTING.md) — Common issues & solutions
- [CUSTOM_DOMAIN.md](operations/CUSTOM_DOMAIN.md) — Deploy with custom domain (mon.go7s.net)
- [HTTPS_SETUP.md](security/HTTPS_SETUP.md) — SSL/TLS certificate setup
- [DEPLOYMENT.md](operations/DEPLOYMENT.md) — Production deployment guide
- [DOCKER.md](getting-started/DOCKER.md) — Docker Compose setup (future)

**Configuration**

- [/backend/.env.example](/backend/.env.example) — Backend environment variables
- [/frontend-next/.env.example](/frontend-next/.env.example) — Frontend environment variables
- [MULTI_SERVER.md](getting-started/MULTI_SERVER.md) — Managing multiple servers
- [QUICK_REFERENCE.md](getting-started/QUICK_REFERENCE.md) — Quick reference guide
- [OFFLINE_MODE.md](operations/OFFLINE_MODE.md) — Running without internet

---

### Architecture & Design

**System Design**

- [ARCHITECTURE.md](architecture/ARCHITECTURE.md) — High-level system architecture
- [COMPONENTS.md](architecture/COMPONENTS.md) — Component descriptions
- [EVENT_MODEL.md](architecture/EVENT_MODEL.md) — Event-driven architecture
- [PLUGIN_SYSTEM.md](architecture/PLUGIN_SYSTEM.md) — Plugin architecture

**Technical Specs**

- [/docs/PROJECT_SPECIFICATION.md](PROJECT_SPECIFICATION.md) — Complete feature list
- [API.md](architecture/API.md) — API design principles
- [DATABASE.md](architecture/DATABASE.md) — Database schema
- [WEBSOCKET.md](architecture/WEBSOCKET.md) — Real-time updates architecture

---

### Development

**For Developers**

- [/AGENTS.md](/AGENTS.md) — **AI Agent workflow rules** (must-read!)
- [CONTRIBUTING.md](templates/CONTRIBUTING.md) — How to contribute
- [CODE_STYLE.md](development/CODE_STYLE.md) — Coding standards
- [TESTING.md](development/TESTING.md) — Testing strategy
- [TEST_GUIDE.md](operations/TEST_GUIDE.md) — Running tests

**Backend (Python)**

- [/backend/README.md](/backend/README.md) — Backend overview
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) — Implementation notes
- [API_REFERENCE.md](backend/API_REFERENCE.md) — API endpoint reference
- [/docs/openapi.yaml](openapi.yaml) — OpenAPI 3.0 spec

**Frontend (Next.js)**

- [/frontend-next/README.md](/frontend-next/README.md) — Frontend overview
- [WORKFLOWS.md](WORKFLOWS.md) — Frontend workflows
- [WORKFLOWS_EN.md](WORKFLOWS_EN.md) — Frontend workflows (English)
- [I18N_GUIDE.md](I18N_GUIDE.md) — Internationalization guide
- [COMPONENTS.md](frontend/COMPONENTS.md) — Component library

---

### Operations

**Running in Production**

- [BACKUP_RESTORE.md](operations/BACKUP_RESTORE.md) — Database backups & recovery
- [LOGGING.md](operations/LOGGING.md) — Log management & monitoring
- [UPGRADE_ROLLBACK.md](operations/UPGRADE_ROLLBACK.md) — Version upgrades & rollback
- [DEPLOYMENT.md](operations/DEPLOYMENT.md) — Production deployment details
- [SMOKE_TEST.md](operations/SMOKE_TEST.md) — Smoke testing checklist

**CI/CD & Release**

- [CI_WORKFLOWS.md](CI_WORKFLOWS.md) — GitHub Actions workflows
- [RELEASE_PROCESS.md](RELEASE_PROCESS.md) — How to release
- [STAGING_CHECKLIST.md](STAGING_CHECKLIST.md) — Pre-release checklist

---

### Security

**Security Model**

- [SECURITY.md](security/SECURITY.md) — Security policy & vulnerability reporting
- [PRODUCTION_SECURITY.md](security/PRODUCTION_SECURITY.md) — Production hardening checklist
- [HTTPS_SETUP.md](security/HTTPS_SETUP.md) — SSL certificate setup
- [SECURITY_MODEL.md](security/SECURITY_MODEL.md) — Authentication & authorization
- [SSH_KEY_MANAGEMENT.md](security/SSH_KEY_MANAGEMENT.md) — SSH key vault
- [WEBHOOKS_SECURITY.md](security/WEBHOOKS_SECURITY.md) — Webhook HMAC & SSRF

**Configuration**

- [CORS.md](security/CORS.md) — CORS configuration
- [RATE_LIMITING.md](security/RATE_LIMITING.md) — API rate limits

---

### Product

**Roadmap & Planning**

- [/docs/product/ROADMAP.md](product/ROADMAP.md) — **Version-based roadmap** (must-read!)
- [/docs/product/TASKS.md](product/TASKS.md) — **Task backlog** (Now/Next/Later)
- [/ROADMAP.md](/ROADMAP.md) — Stub → links to docs/product/ROADMAP.md
- [/TODO-IMPROVEMENTS.md](/TODO-IMPROVEMENTS.md) — Stub → links to docs/product/TASKS.md

**Release Notes**

- [CHANGELOG.md](product/CHANGELOG.md) — All releases changelog
- [RELEASE_NOTES_v2.3.0.md](product/RELEASE_NOTES_v2.3.0.md) — Version 2.3.0
- [RELEASE_NOTES_v2.2.0.md](product/RELEASE_NOTES_v2.2.0.md) — Version 2.2.0
- [RELEASE_NOTES_v2.1.0.md](product/RELEASE_NOTES_v2.1.0.md) — Version 2.1.0

---

### Templates

**For AI Agents & Contributors**

- [CONTRIBUTING.md](templates/CONTRIBUTING.md) — Contributing guidelines
- [AGENT_STATUS_REPORT.md](templates/AGENT_STATUS_REPORT.md) — Report format after work
- [PR_CHECKLIST.md](templates/PR_CHECKLIST.md) — Pull request checklist
- [ISSUE_TEMPLATE_AGENT_TASK.md](templates/ISSUE_TEMPLATE_AGENT_TASK.md) — Issue template for agents
- [REVIEW_REPORT.template.md](REVIEW_REPORT.template.md) — Code review template

---

### Reviews & Assessments

**Project Reviews**

- [FULL_REVIEW_GUIDE.md](FULL_REVIEW_GUIDE.md) — Complete review process
- [MANUAL_REVIEW_WORKFLOW_GUIDE.md](MANUAL_REVIEW_WORKFLOW_GUIDE.md) — Manual review workflow
- [REVIEW_REPORT.md](REVIEW_REPORT.md) — Latest review report
- [PROJECT_ASSESSMENT.md](PROJECT_ASSESSMENT.md) — Project assessment

**Historical**

- [IMPLEMENTATION-ONBOARDING-DOMAIN.md](/IMPLEMENTATION-ONBOARDING-DOMAIN.md) — Recent implementations
- Phase summaries (PHASE\*\_SUMMARY.md) — Historical development phases

---

## 📖 Reading Paths

### "I'm new, where do I start?"

1. [/README.md](/README.md) — Project overview
2. [QUICK_START.md](getting-started/QUICK_START.md) — Get it running locally
3. [/ARCHITECTURE.md](/ARCHITECTURE.md) — Understand the system
4. [/CONTRIBUTING.md](/CONTRIBUTING.md) — How to contribute

### "I'm an AI agent working on this repo"

1. **[/AGENTS.md](/AGENTS.md)** — **Start here!** Workflow rules & non-goals
2. [/docs/product/TASKS.md](product/TASKS.md) — Available tasks
3. [templates/ISSUE_TEMPLATE_AGENT_TASK.md](templates/ISSUE_TEMPLATE_AGENT_TASK.md) — How to understand issues
4. [templates/PR_CHECKLIST.md](templates/PR_CHECKLIST.md) — Before submitting PR
5. [templates/AGENT_STATUS_REPORT.md](templates/AGENT_STATUS_REPORT.md) — How to report back

### "I want to deploy to production"

1. [operations/CUSTOM_DOMAIN.md](operations/CUSTOM_DOMAIN.md) — Custom domain setup
2. [security/HTTPS_SETUP.md](security/HTTPS_SETUP.md) — SSL certificates
3. [operations/DEPLOYMENT.md](operations/DEPLOYMENT.md) — Production deployment
4. [security/PRODUCTION_SECURITY.md](security/PRODUCTION_SECURITY.md) — Security hardening
5. [operations/SMOKE_TEST.md](operations/SMOKE_TEST.md) — Verify deployment

### "I want to understand the codebase"

1. [architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md) — System design
2. [/backend/README.md](/backend/README.md) — Backend overview
3. [/frontend-next/README.md](/frontend-next/README.md) — Frontend overview
4. [backend/API_REFERENCE.md](backend/API_REFERENCE.md) — API endpoints
5. [openapi.yaml](openapi.yaml) — OpenAPI spec

### "I want to add a feature"

1. Check [product/ROADMAP.md](product/ROADMAP.md) — Is it planned?
2. Check [product/TASKS.md](product/TASKS.md) — Already in backlog?
3. Create issue using [templates/ISSUE_TEMPLATE_AGENT_TASK.md](templates/ISSUE_TEMPLATE_AGENT_TASK.md)
4. Follow [/AGENTS.md](/AGENTS.md) workflow rules
5. Submit PR with [templates/PR_CHECKLIST.md](templates/PR_CHECKLIST.md)

---

## 🚨 Documentation Rules

### Golden Rules

1. **All docs live in `docs/`** (except README, LICENSE, CONTRIBUTING, AGENTS)
2. **Update this index** when adding/moving docs
3. **No duplicate content** — consolidate or link
4. **Fix broken links** immediately after moving files
5. **Keep it current** — update dates and versions

### Adding New Documentation

```bash
# 1. Create doc in appropriate subdirectory
vim docs/security/NEW_FEATURE.md

# 2. Update this index
vim docs/README.md

# 3. Check for broken links
grep -r "old-path" .

# 4. Test links work
# (commit and view on GitHub or use Markdown preview)
```

### Moving Existing Documentation

```bash
# 1. Move file
git mv OLD_FILE.md docs/category/NEW_FILE.md

# 2. Create stub at old location (optional)
echo "# Old Title\n\nMoved to [docs/category/NEW_FILE.md](docs/category/NEW_FILE.md)" > OLD_FILE.md

# 3. Update all references
grep -r "OLD_FILE.md" .
# Update found files

# 4. Update this index
vim docs/README.md
```

---

## 🗑️ Archive & Historical Files

The following files have been moved to `docs/archive/` (historical reference):

### Implementation Summaries (Archived)

- `PHASE2_COMPLETION_REPORT.md` → `docs/archive/`
- `PHASE3_COMPLETION_SUMMARY.md` → `docs/archive/`
- `PHASE6_COMPLETION_SUMMARY.md` → `docs/archive/`
- `PHASE6_IMPLEMENTATION_SUMMARY.md` → `docs/archive/`
- `PHASE8_PROGRESS.md` → `docs/archive/`
- `DEVELOPMENT-COMPLETION-SUMMARY.md` → `docs/archive/`
- `ENTERPRISE_SUMMARY.md` → `docs/archive/`
- `SESSION-COMPLETION-REPORT.txt` → `docs/archive/`
- `PR_SUMMARY.md` → `docs/archive/`
- `VIETNAMESE_SUMMARY.md` → `docs/archive/`
- `UPDATE_SUMMARY_VI.md` → `docs/archive/`
- `ENTERPRISE_ROADMAP.md` → `docs/archive/`
- `README_v2.3.0.md` → `docs/archive/`

### Legacy Guides (Archived)

- `MULTI_SERVER_GUIDE_OLD.md` → `docs/archive/` (replaced by `docs/getting-started/MULTI_SERVER.md`)
- `UPGRADE_GUIDE_OLD.md` → `docs/archive/` (replaced by `docs/operations/UPGRADE_ROLLBACK.md`)

**All files preserved for historical reference but no longer in main documentation tree.**

---

## 📝 Style Guide

### Markdown Conventions

- **Headers**: Use ATX-style (`# Header`, not underline style)
- **Links**: Use relative paths from project root
- **Code blocks**: Always specify language (`python, `bash, ```typescript)
- **Lists**: Use `-` for unordered, `1.` for ordered
- **Emphasis**: `**bold**` for important, `_italic_` for emphasis, `` `code` `` for code

### Writing Style

- **Concise**: Get to the point quickly
- **Actionable**: Use imperative mood ("Run tests", not "Tests should be run")
- **Examples**: Include code examples where helpful
- **Links**: Link to code, issues, related docs
- **Dates**: Use ISO 8601 (2026-01-09)
- **Versions**: Semantic versioning (v2.3.1)

---

## 🔗 External Resources

- **GitHub Repo**: [github.com/minhtuancn/server-monitor](https://github.com/minhtuancn/server-monitor)
- **API Docs (Live)**: [http://localhost:9083/docs](http://localhost:9083/docs) (when running)
- **Swagger UI**: [http://localhost:9083/docs](http://localhost:9083/docs)
- **Metrics**: [http://localhost:9083/api/metrics](http://localhost:9083/api/metrics)

---

## 📧 Need Help?

- **Found a bug?** → Create issue with [templates/ISSUE_TEMPLATE_AGENT_TASK.md](templates/ISSUE_TEMPLATE_AGENT_TASK.md)
- **Have a question?** → Check [TROUBLESHOOTING.md](getting-started/TROUBLESHOOTING.md) first
- **Want to contribute?** → Read [templates/CONTRIBUTING.md](templates/CONTRIBUTING.md)
- **Security issue?** → See [security/SECURITY.md](security/SECURITY.md) for reporting

---

**Last Updated**: 2026-01-09  
**Maintained by**: Project maintainers  
**License**: MIT (see [/LICENSE](/LICENSE))
