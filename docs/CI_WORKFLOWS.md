# CI/CD Workflows Documentation

This document explains all GitHub Actions workflows for the `server-monitor` project, when they run, what they do, and how to replicate checks locally.

## Overview

The project uses 6 workflows organized by purpose:
1. **Backend CI** - Fast Python linting and testing
2. **Frontend CI** - Fast Next.js linting, type checking, and building
3. **CodeQL Analysis** - Deep security analysis (main branch + nightly)
4. **Security Scan** - Dependency audits and security scanning
5. **Dependency Review** - PR-only dependency vulnerability checks
6. **Manual Project Review** - Comprehensive project audit (manual trigger)

## Workflow Details

### 1. Backend CI (`ci.yml`)

**Purpose**: Fast feedback on Python code quality and functionality

**Triggers**:
- Pull requests to `main` or `develop`
- Pushes to `main` or `develop`

**What it does**:
- **Lint Job**: Runs `flake8` on backend code to catch syntax errors and style issues
- **Test Job**: Runs pytest on unit tests (crypto, plugins, observability, webhooks, security)

**Features**:
- ✅ Pip dependency caching for faster runs
- ✅ Concurrency control (cancels old runs on new PR push)
- ✅ Minimal permissions (read-only)

**Run locally**:
```bash
# Linting
cd /path/to/server-monitor
pip install flake8
flake8 backend --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 backend --count --exit-zero --max-complexity=15 --max-line-length=150 --statistics

# Testing
pip install -r backend/requirements.txt
pip install -r tests/requirements.txt
export DB_PATH=/tmp/server-monitor-data/servers.db
export JWT_SECRET=test-secret-key
export ENCRYPTION_KEY=test-encryption-key
cd backend && python -c "import database; database.init_database()"
cd ../tests
pytest --tb=short -v test_crypto_vault.py test_plugin_system.py test_plugin_integration.py test_security.py test_observability.py test_webhooks.py
```

**Expected duration**: 3-5 minutes

---

### 2. Frontend CI (`frontend-ci.yml`)

**Purpose**: Fast feedback on Next.js frontend code quality

**Triggers**:
- Pull requests to `main` or `develop` (only when `frontend-next/**` changes)
- Pushes to `main` or `develop` (only when `frontend-next/**` changes)

**What it does**:
- Runs ESLint on TypeScript/React code
- Runs TypeScript type checking (`tsc --noEmit`)
- Builds the Next.js application to ensure no build errors

**Features**:
- ✅ npm dependency caching for faster runs
- ✅ Concurrency control (cancels old runs on new PR push)
- ✅ Path filtering (only runs when frontend changes)
- ✅ Minimal permissions (read-only)

**Run locally**:
```bash
cd /path/to/server-monitor/frontend-next
npm ci
npm run lint
npx tsc --noEmit
npm run build
```

**Expected duration**: 2-4 minutes

---

### 3. CodeQL Security Analysis (`codeql.yml`)

**Purpose**: Deep static security analysis to find vulnerabilities

**Triggers**:
- Pushes to `main` (not on PRs - too heavy)
- Daily schedule at 2 AM UTC
- Manual workflow dispatch

**What it does**:
- Analyzes Python backend code for security issues
- Analyzes JavaScript/TypeScript frontend code for security issues
- Uses `security-extended` query suite for comprehensive checks
- Uploads results to GitHub Security tab

**Features**:
- ✅ Concurrency control for main branch
- ✅ Proper security-events write permission
- ⚠️ Not run on PRs to save CI minutes (heavy analysis)

**Run locally**:
```bash
# CodeQL requires special setup, use GitHub CLI instead:
gh api repos/minhtuancn/server-monitor/code-scanning/alerts
```

**Expected duration**: 5-10 minutes

**Note**: Results appear in the "Security" tab under "Code scanning alerts"

---

### 4. Security Scan (`security-scan.yml`)

**Purpose**: Dependency vulnerability scanning and Python security checks

**Triggers**:
- Pull requests to `main` or `develop` - **lightweight mode** (Bandit only)
- Pushes to `main` - **full mode** (all scans)
- Nightly schedule at 3 AM UTC - **full mode** (all scans)
- Manual workflow dispatch

**What it does**:

**On Pull Requests** (lightweight):
- Runs Bandit Python security scanner (fails if issues found)

**On Push to Main / Schedule** (full):
- Runs `pip-audit` on backend dependencies
- Runs `npm audit` on frontend dependencies  
- Runs Bandit Python security scanner
- Uploads scan results as artifacts

**Features**:
- ✅ Concurrency control
- ✅ Conditional job execution (heavy scans only on schedule/main)
- ✅ Caching for pip and npm
- ✅ Fails PRs on security issues

**Run locally**:
```bash
# Bandit scan
pip install bandit[toml]
bandit -r backend -x tests -ll

# pip-audit (Python dependencies)
pip install pip-audit
pip-audit -r backend/requirements.txt --desc

# npm audit (Frontend dependencies)
cd frontend-next
npm audit
```

**Expected duration**: 
- PR: 1-2 minutes (Bandit only)
- Schedule/Main: 5-8 minutes (all scans)

---

### 5. Dependency Review (`dependency-review.yml`)

**Purpose**: Review dependency changes in pull requests for security issues

**Triggers**:
- Pull requests to `main` or `develop` only

**What it does**:
- Compares dependencies between base and PR branches
- Checks for known vulnerabilities in new/changed dependencies
- Checks license compatibility
- Posts summary comment on PR

**Features**:
- ✅ Concurrency control
- ✅ PR comments with results
- ✅ Fails on high/critical severity vulnerabilities
- ✅ License validation

**Configuration**:
- Fails on: high or critical severity
- Warns on: moderate severity
- Allowed licenses: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Python-2.0
- Denied licenses: GPL-3.0, AGPL-3.0

**Run locally**:
```bash
# This action requires GitHub API, cannot run locally
# Use GitHub web interface to see results on PRs
```

**Expected duration**: 1-2 minutes

---

## PR Checks Summary

When you open a pull request, expect these checks:

| Check | When | Duration | Purpose |
|-------|------|----------|---------|
| Backend CI | Always | 3-5 min | Python lint + tests |
| Frontend CI | If frontend changes | 2-4 min | TS/React lint + build |
| Dependency Review | Always | 1-2 min | Dependency security |
| Security Scan (Bandit) | Always | 1-2 min | Python security scan |
| **Total** | - | **5-10 min** | Fast feedback |

**Note**: CodeQL and full security scans run only on `main` branch and nightly to avoid slowing down PR workflows.

---

### 6. Manual Project Review & Release Audit (`manual-project-review.yml`)

**Purpose**: Comprehensive project audit for releases and major milestones

**Triggers**:
- Manual workflow dispatch only (not automatic)

**What it does**:
1. **Static Analysis & Linting** (15 min):
   - Python linting (flake8)
   - Security scanning (bandit)
   - Frontend ESLint and TypeScript checking
   - OpenAPI specification validation

2. **Unit & Integration Tests** (20 min):
   - Runs full pytest test suite
   - Generates test coverage reports

3. **Boot & Smoke Testing** (25 min):
   - Starts all backend services (API, WebSocket, Terminal)
   - Builds and starts Next.js frontend
   - Runs comprehensive smoke tests
   - Collects service logs

4. **UI Screenshot Capture** (20 min):
   - Captures screenshots of key pages using Playwright
   - Saves to `docs/screenshots/` for documentation
   - Generates screenshot summary

5. **Documentation Consistency** (10 min):
   - Validates all documentation files exist
   - Checks for broken internal links
   - Validates YAML syntax

6. **Generate Review Report** (10 min):
   - Aggregates all results
   - Creates comprehensive `docs/REVIEW_REPORT.md`
   - Includes findings, suggestions, and checklists

7. **Create PR & Issue** (10 min):
   - Creates automation branch with review results
   - Opens PR with findings
   - Creates follow-up issue with action items

**Features**:
- ✅ Fully configurable inputs (ref, PR/issue creation, screenshots)
- ✅ Comprehensive artifact collection
- ✅ Automatic PR and issue creation
- ✅ GitHub Step Summary for quick review
- ✅ Copilot Agent integration prompts

**Run via GitHub UI**:
1. Go to **Actions** → **Manual Project Review & Release Audit**
2. Click **Run workflow**
3. Configure options:
   - `ref`: Branch/tag to review (default: main)
   - `create_pr`: Create PR with results (default: true)
   - `create_issue`: Create follow-up issue (default: true)
   - `include_ui_screenshots`: Capture screenshots (default: true)
   - Authentication credentials for smoke tests
4. Click **Run workflow**

**Run via GitHub CLI**:
```bash
# Run with defaults
gh workflow run manual-project-review.yml

# Run with custom ref
gh workflow run manual-project-review.yml --ref develop

# Run without PR/issue creation
gh workflow run manual-project-review.yml \
  -f create_pr=false \
  -f create_issue=false
```

**Expected duration**: 60-90 minutes (varies based on enabled features)

**Artifacts generated**:
- lint-results (30 days retention)
- test-results (30 days retention)
- smoke-test-results (30 days retention)
- ui-screenshots (30 days retention)
- doc-check-results (30 days retention)
- review-report (90 days retention)

**When to use**:
- Before major releases
- After significant feature additions
- Monthly/quarterly maintenance reviews
- When updating documentation
- Before security audits

**Documentation**: See [docs/MANUAL_REVIEW_WORKFLOW_GUIDE.md](MANUAL_REVIEW_WORKFLOW_GUIDE.md) for complete guide.

---

## Scheduled Workflows

Nightly automated checks:

| Time (UTC) | Workflow | Purpose |
|------------|----------|---------|
| 2:00 AM | CodeQL Analysis | Deep security analysis |
| 3:00 AM | Security Scan (full) | Comprehensive dependency audits |

---

## Concurrency & Optimization

All workflows implement:
- **Concurrency control**: Automatically cancels old runs when new commits are pushed
- **Dependency caching**: Speeds up subsequent runs by caching pip/npm dependencies
- **Minimal permissions**: Each job has only the permissions it needs
- **Path filtering**: Frontend CI only runs when frontend files change

---

## Troubleshooting

### Backend tests fail
- Check if you have all test dependencies: `pip install -r tests/requirements.txt`
- Ensure environment variables are set (DB_PATH, JWT_SECRET, ENCRYPTION_KEY)
- Some integration tests may require a running API server

### Frontend build fails
- Check if you ran `npm ci` (not `npm install`)
- Ensure Node.js version 20 is used
- Check environment variables are provided for Next.js build

### Bandit finds security issues
- Review the specific issues in the workflow log
- Use `# nosec` comments only if you're certain the issue is a false positive
- Consider refactoring the code to address the security concern

### npm audit or pip-audit finds vulnerabilities
- Review the vulnerabilities in the scheduled run logs
- Check if updates are available: `npm audit fix` or update requirements.txt
- Evaluate if the vulnerability affects your use case

---

## Adding New Checks

If you need to add new checks:

1. **For fast checks (< 2 minutes)**: Add to Backend CI or Frontend CI
2. **For slow checks (> 2 minutes)**: Add to Security Scan with conditional execution
3. **For deep analysis**: Add to CodeQL or create a new scheduled workflow
4. Always add:
   - Concurrency control
   - Dependency caching
   - Minimal permissions
   - Clear documentation

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Dependency Review Action](https://github.com/actions/dependency-review-action)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [pip-audit Documentation](https://github.com/pypa/pip-audit)
