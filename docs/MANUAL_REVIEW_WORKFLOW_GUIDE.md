# Manual Project Review & Release Audit - Usage Guide

This document provides instructions on how to use the **Manual Project Review & Release Audit** workflow to perform comprehensive audits of the server-monitor project.

## Overview

The Manual Project Review workflow is a GitHub Actions workflow that can be triggered manually to:

- Run comprehensive static analysis and security scans
- Execute all unit and integration tests
- Build and smoke test the application
- Capture UI screenshots for documentation
- Validate documentation consistency
- Generate a detailed review report
- Automatically create a PR with findings
- Create a follow-up issue with actionable tasks

## When to Run

Run this workflow:

- **Before a major release** - To ensure code quality and catch issues
- **After significant feature additions** - To validate the changes don't break existing functionality
- **During code reviews** - To get an automated, comprehensive assessment
- **Periodically (monthly/quarterly)** - As part of regular maintenance
- **When updating documentation** - To ensure screenshots and docs are up-to-date

## How to Run

### Using GitHub UI

1. Navigate to your repository on GitHub
2. Click on the **Actions** tab
3. Select **Manual Project Review & Release Audit** from the workflows list
4. Click **Run workflow** button (top right)
5. Configure the workflow inputs:
   - **ref**: Branch, tag, or SHA to review (default: `main`)
   - **create_pr**: Whether to create a PR with results (default: `true`)
   - **create_issue**: Whether to create a follow-up issue (default: `true`)
   - **base_url**: Base URL for frontend testing (default: `http://127.0.0.1:9081`)
   - **include_ui_screenshots**: Capture UI screenshots (default: `true`)
   - **smoke_auth_user**: Username for authenticated tests (default: `admin`)
   - **smoke_auth_pass**: Password for authenticated tests (default: `admin123`)
   - **issue_labels**: Labels for the created issue (default: `audit,automation`)
   - **pr_title**: Title for the created PR
6. Click **Run workflow** to start

### Using GitHub CLI

```bash
# Run with default options
gh workflow run manual-project-review.yml

# Run with custom options
gh workflow run manual-project-review.yml \
  --ref main \
  -f create_pr=true \
  -f create_issue=true \
  -f include_ui_screenshots=true

# Run for a specific branch
gh workflow run manual-project-review.yml \
  --ref feature/new-feature \
  -f create_pr=true
```

## Workflow Jobs

The workflow consists of 7 jobs that run sequentially:

### 1. Static Analysis & Linting (15 min timeout)
- Python linting with flake8
- Security scanning with bandit
- Frontend ESLint checks
- TypeScript type checking
- OpenAPI specification validation

### 2. Unit & Integration Tests (20 min timeout)
- Runs full pytest suite
- Generates test results
- Reports test coverage

### 3. Boot & Smoke Testing (25 min timeout)
- Starts backend services (API, WebSocket, Terminal)
- Builds and starts Next.js frontend
- Runs comprehensive smoke tests
- Collects service logs

### 4. UI Screenshot Capture (20 min timeout)
- Installs Playwright with Chromium
- Captures screenshots of key pages:
  - Homepage
  - Dashboard
  - Server List
  - Webhook Settings
  - Audit Logs
  - User Profile
  - Security Settings
- Saves screenshots to `docs/screenshots/`

### 5. Documentation Consistency (10 min timeout)
- Validates documentation files exist
- Checks for broken internal links
- Validates OpenAPI YAML syntax
- Checks for TODO items in docs

### 6. Generate Review Report (10 min timeout)
- Collects all job results
- Generates comprehensive `docs/REVIEW_REPORT.md`
- Includes findings, suggestions, and checklist

### 7. Create PR & Issue (10 min timeout)
- Creates automation branch with timestamp
- Commits review report and screenshots
- Opens PR with detailed description
- Creates follow-up issue with checklist
- Links PR and issue together

## Artifacts

The workflow generates several artifacts that are available for download:

- **lint-results**: Linting and security scan outputs
- **test-results**: Test execution logs
- **smoke-test-results**: Smoke test logs and service logs
- **ui-screenshots**: Captured UI screenshots and summary
- **doc-check-results**: Documentation validation results
- **review-report**: Final comprehensive report

Artifacts are retained for 30-90 days depending on the type.

## Output Files

After the workflow completes, the following files are created:

- `docs/REVIEW_REPORT.md` - Comprehensive review report
- `docs/screenshots/*.png` - UI screenshots
- `docs/screenshots/screenshot-summary.md` - Screenshot summary

If PR creation is enabled, these files are committed to a new branch and a PR is opened.

## Reviewing Results

### Step 1: Check Workflow Summary

After the workflow completes, review the GitHub Actions summary page which includes:
- Quick status of all jobs
- Excerpts from key results
- Links to artifacts

### Step 2: Download Artifacts

Download artifacts for detailed inspection:
- Test results for test failures
- Lint results for code quality issues
- Screenshots to verify UI state

### Step 3: Review the Generated Report

The `docs/REVIEW_REPORT.md` file contains:
- Executive summary with quick status
- Detailed CI results
- Module coverage analysis
- Findings and issues
- Suggested next steps
- Release checklist
- Copilot Agent prompt for follow-up work

### Step 4: Review the PR (if created)

The automatically created PR includes:
- Review report
- Updated screenshots
- Documentation updates
- Links to workflow run and artifacts

### Step 5: Check the Follow-up Issue (if created)

The issue contains:
- Checklist of follow-up actions
- Links to PR and artifacts
- Copilot Agent task prompt
- Priority-ordered action items

## Integration with Copilot Agent

The review report includes a "Copilot Agent Task Prompt" section that can be used to delegate follow-up work:

1. Copy the prompt from the review report
2. Create a new issue or comment
3. Tag @copilot with the prompt
4. Copilot will analyze the findings and create focused PRs

Example prompt:
```
Review the automated project review report at docs/REVIEW_REPORT.md and address the following:

1. Fix any failing tests identified in the test results
2. Address security issues found by bandit scan
3. Update documentation based on the findings
4. Add missing tests for modules with low coverage
5. Clean up TODO/FIXME comments in the codebase

Create focused PRs for each major issue found. Ensure all changes maintain backward compatibility and don't break existing functionality.
```

## Troubleshooting

### Workflow Fails on Static Analysis
- Check lint-results artifact for specific errors
- Address Python/TypeScript linting issues
- Fix security issues identified by bandit

### Tests Fail
- Download test-results artifact
- Review test failures
- May be expected if tests are environment-specific

### Smoke Tests Fail
- Check smoke-test-results artifact
- Review service logs
- Ensure all services started properly
- May fail if ports are in use

### Screenshot Capture Fails
- Check if frontend is accessible
- Verify authentication credentials
- Review screenshot-results.txt in artifacts
- Screenshots failures don't block the workflow

### PR/Issue Creation Fails
- Check workflow logs
- Ensure proper permissions are set
- Verify GitHub token has required scopes

## Best Practices

1. **Run before releases** - Always run a full review before tagging a release
2. **Review artifacts** - Don't just rely on pass/fail, review detailed outputs
3. **Update screenshots** - Keep UI screenshots current for documentation
4. **Act on findings** - Use the follow-up issue to track action items
5. **Regular cadence** - Run monthly for proactive issue detection
6. **Clean up PRs** - Close automation PRs after extracting useful information

## Customization

The workflow can be customized by editing `.github/workflows/manual-project-review.yml`:

- Adjust timeouts for jobs
- Modify screenshot pages list in `scripts/ui-snapshots.mjs`
- Update report template in `scripts/generate-review-report.sh`
- Add custom validation steps
- Configure different artifact retention periods

## Security Considerations

- The workflow uses minimal permissions by default
- Permissions are elevated per-job as needed
- Secrets should not be hardcoded (use GitHub Secrets)
- Review logs to ensure no sensitive data is exposed
- Artifacts may contain sensitive information - use appropriate retention periods

## Support

For issues or questions:
- Check workflow run logs
- Review this guide
- Open an issue in the repository
- Contact the development team

---

**Last Updated:** 2026-01-08  
**Version:** 1.0.0
