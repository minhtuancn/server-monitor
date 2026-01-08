# GitHub Actions Workflows - User Guide

## Overview

This repository uses GitHub Actions to automate CI/CD processes, security checks, and project reviews.

## Workflow List

### 1. Backend CI (`ci.yml`)
**Triggers:** Push and Pull Request to `main` or `develop`

**Functions:**
- Lint Python code with flake8
- Run unit tests for backend
- Check Python syntax

### 2. Frontend CI (`frontend-ci.yml`)
**Triggers:** Push and Pull Request to `main` or `develop` (only when `frontend-next/` changes)

**Functions:**
- Lint JavaScript/TypeScript code with ESLint
- Check TypeScript types
- Build Next.js application

### 3. CodeQL Security Analysis (`codeql.yml`)
**Triggers:**
- Push to `main`
- Schedule: Daily at 2 AM UTC
- Manual dispatch

**Functions:**
- Analyze code security with CodeQL
- Scan both Python and JavaScript/TypeScript
- Use `security-extended` queries

### 4. Dependency Review (`dependency-review.yml`)
**Triggers:** Pull Request to `main` or `develop`

**Functions:**
- Review new dependencies added in PR
- Check for vulnerabilities and licenses
- Comment results on PR

### 5. Security Scan (`security-scan.yml`)
**Triggers:**
- Push to `main`
- Pull Request to `main` or `develop`
- Schedule: Daily at 3 AM UTC
- Manual dispatch

**Functions:**
- Scan vulnerabilities in Python dependencies (pip-audit)
- Scan vulnerabilities in Node.js dependencies (npm audit)
- Scan security issues in code (bandit)

**Note:** `pip-audit` and `npm-audit` only run on main branch and schedule to avoid slowing down PR reviews.

### 6. Manual Project Review (`manual-project-review.yml`)
**Triggers:** Manual dispatch (workflow_dispatch)

**Functions:**
- Run full project review with static analysis, tests, smoke tests
- Capture UI screenshots
- Create PR with review report and screenshots
- Create Issue for follow-up

**Parameters:**
- `ref`: Branch/tag/SHA to review (default: `main`)
- `create_pr`: Create PR with review results (default: `true`)
- `create_issue`: Create follow-up issue (default: `true`)
- `base_url`: Base URL for frontend screenshots (default: `http://127.0.0.1:9081`)
- `include_ui_screenshots`: Capture UI screenshots (default: `true`)
- `smoke_auth_user`: Username for smoke tests (default: `admin`)
- `smoke_auth_pass`: Password for smoke tests (default: `admin123`)
- `issue_labels`: Labels for created issue (default: `audit,automation`)
- `pr_title`: Title for PR (default: `chore: automated review report + screenshots + docs refresh`)

## Changes Made (2026-01-08)

### Original Issue
The `manual-project-review.yml` workflow did not automatically create PR and Issue when the `ui-screenshots` job was skipped (when `include_ui_screenshots = false`).

### Solution
1. **Fixed job dependencies:**
   - Removed `ui-screenshots` from `needs` of `create-pr-and-issue` job
   - Only kept `generate-report` in needs list
   - Added condition check: `needs.generate-report.result != 'failure'`

2. **Improved error handling:**
   - Added `continue-on-error: true` for download artifacts step in `generate-report`
   - Screenshots download already had `continue-on-error: true`

3. **Fixed YAML syntax error in `security-scan.yml`:**
   - Fixed indentation of Python code in `pip-audit` job
   - Fixed indentation of Node.js code in `npm-audit` job
   - YAML parser requires proper indentation for heredoc code blocks

### Before Fix:
```yaml
needs: [generate-report, ui-screenshots]
if: |
  always() && 
  (github.event.inputs.create_pr == 'true' || github.event.inputs.create_issue == 'true')
```

### After Fix:
```yaml
needs: [generate-report]
if: |
  always() && 
  needs.generate-report.result != 'failure' &&
  (github.event.inputs.create_pr == 'true' || github.event.inputs.create_issue == 'true')
```

## How to Use Manual Project Review

### Method 1: Via GitHub UI
1. Go to **Actions** tab in the repository
2. Select **Manual Project Review & Release Audit** workflow
3. Click **Run workflow**
4. Choose options:
   - Branch to review
   - Create PR or not
   - Create Issue or not
   - Capture screenshots or not
5. Click **Run workflow** to start

### Method 2: Via GitHub CLI
```bash
gh workflow run manual-project-review.yml \
  -f ref=main \
  -f create_pr=true \
  -f create_issue=true \
  -f include_ui_screenshots=true
```

### Results
The workflow will:
1. Run all checks (lint, tests, smoke tests, etc.)
2. Create review report at `docs/REVIEW_REPORT.md`
3. Capture screenshots (if enabled) at `docs/screenshots/`
4. Create PR with review results and screenshots
5. Create Issue to track follow-up actions

## Best Practices

### When to Run Manual Project Review?
- Before releasing a new version
- After merging multiple PRs
- Periodically (weekly/monthly) to track quality
- When you need to audit the entire project

### How to Handle Results
1. Review the auto-created PR
2. Download artifacts to see details
3. Check Issue to track issues that need fixing
4. Create focused PRs for each issue found
5. Close PR after extracting actionable items

## Troubleshooting

### Workflow Failed
1. Check logs of failed job
2. Download artifacts to see details
3. Re-run workflow if failed due to network/timeout
4. Create issue if failed due to workflow bug

### PR/Issue Not Created
Check:
- Is `create_pr` or `create_issue` set to `true`?
- Did `generate-report` job succeed?
- Does workflow have `contents: write`, `pull-requests: write`, `issues: write` permissions?

### Workflow Takes Too Long
- Skip UI screenshots if not needed: `include_ui_screenshots=false`
- Check timeout of each job
- May need to increase timeout if tests take long

## Documentation Links
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Dependency Review Action](https://github.com/actions/dependency-review-action)

---

For Vietnamese version, see [WORKFLOWS.md](WORKFLOWS.md)
