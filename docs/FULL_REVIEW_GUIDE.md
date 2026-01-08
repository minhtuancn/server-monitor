# Full Review Workflow Guide

## Overview

The **Full Review - Manual Project Audit** workflow is a comprehensive automated quality audit tool for the server-monitor project. It performs static analysis, security scanning, testing, and generates detailed reports.

## Features

### 1. Frontend Checks (Next.js)
- **Linting**: ESLint analysis of frontend code
- **Type Checking**: TypeScript type validation
- **Build**: Production build verification

### 2. Backend Checks (Python)
- **Linting**: flake8 Python code analysis
- **Security Scanning**: bandit security vulnerability detection
- **Testing**: Optional pytest test execution
- **Import Validation**: Ensures all Python modules import correctly

### 3. Security Scans
- **Trivy**: Filesystem vulnerability scanning (detects vulnerabilities in dependencies)
- **Gitleaks**: Secret detection in git history

### 4. UI Snapshots (Optional)
- **Playwright**: Captures screenshots of the application UI
- Provides visual regression testing capabilities

### 5. Automated Reporting
- Generates comprehensive markdown reports
- Creates/updates GitHub issues with findings
- Optionally creates PRs with documentation

## How to Run

### Via GitHub Actions UI

1. Navigate to the **Actions** tab in GitHub
2. Select **🔍 Full Review - Manual Project Audit** from the workflows list
3. Click **Run workflow** button
4. Configure the options (see below)
5. Click **Run workflow** to start

### Workflow Options

| Option | Description | Default |
|--------|-------------|---------|
| `create_issue` | Create or update a GitHub issue with findings | `true` |
| `create_pr` | Create a pull request with the report and documentation | `false` |
| `include_ui_snapshots` | Run Playwright tests and capture UI screenshots | `true` |
| `include_security_scans` | Run Trivy and Gitleaks security scans | `true` |
| `stale_days_threshold` | Days threshold for stale branch reporting | `30` |
| `run_backend_tests` | Run backend pytest tests (requires database setup) | `true` |

### Recommended Configurations

#### Quick Review (Faster)
- `create_issue`: `true`
- `create_pr`: `false`
- `include_ui_snapshots`: `false`
- `include_security_scans`: `true`
- `run_backend_tests`: `false`

#### Full Audit (Comprehensive)
- `create_issue`: `true`
- `create_pr`: `true`
- `include_ui_snapshots`: `true`
- `include_security_scans`: `true`
- `run_backend_tests`: `true`

#### Security Focus
- `create_issue`: `true`
- `create_pr`: `false`
- `include_ui_snapshots`: `false`
- `include_security_scans`: `true`
- `run_backend_tests`: `false`

## Understanding the Report

### Report Structure

The generated report (`automation/FULL_REVIEW_REPORT.md`) includes:

1. **Executive Summary**
   - Overall project health status
   - Critical issues and warnings count
   - Quick assessment of major problems

2. **Quick Statistics Table**
   - Metrics for frontend (errors, warnings, build status)
   - Metrics for backend (errors, warnings, test status)
   - Security metrics (vulnerabilities, secrets)

3. **Detailed Analysis**
   - **Frontend Analysis**: Linting, type checking, build results
   - **Backend Analysis**: Linting, security scan, test results
   - **Security Analysis**: Trivy and Gitleaks findings
   - **UI Snapshots**: Screenshot capture status

4. **Action Items**
   - Prioritized list of issues (High, Medium, Low)
   - Continuous improvement suggestions

### Status Indicators

- ✅ **HEALTHY**: No issues detected
- ⚠️ **NEEDS ATTENTION**: Critical issues found
- ⚠️ **MINOR ISSUES**: Only warnings, no critical errors
- 🚨 **CRITICAL**: Security vulnerabilities or major failures

### Interpreting Results

#### Frontend Metrics
- **Lint Errors**: Must be fixed (code quality issues)
- **Lint Warnings**: Should be addressed (potential issues)
- **TypeScript Errors**: Type safety violations that must be fixed
- **Build Failures**: Prevent deployment, must be resolved

#### Backend Metrics
- **Lint Errors**: Code quality violations
- **Security Issues**: Potential vulnerabilities (review with bandit)
- **Test Failures**: Breaking changes or bugs
- **Import Errors**: Missing dependencies or syntax errors

#### Security Metrics
- **Critical Vulnerabilities**: Immediate action required
- **High Vulnerabilities**: Should be patched soon
- **Medium/Low**: Address during regular maintenance
- **Secrets Found**: Review and remove from git history

## Artifacts

The workflow generates several artifacts:

### Downloadable Artifacts
- **full-review-results**: Contains all output files
  - `FULL_REVIEW_REPORT.md`: Main report
  - `frontend-lint.txt`: Frontend linting output
  - `backend-lint.txt`: Backend linting output
  - `trivy-results.txt`: Security scan results
  - And more...

- **ui-snapshots**: UI screenshots (if enabled)
  - Login page screenshot
  - Dashboard screenshot
  - Other captured pages

### Retention
- Artifacts are retained for **90 days**
- Screenshots are retained for **30 days**

## GitHub Issue Integration

When `create_issue` is enabled:

- Searches for existing issue titled "🔍 Full Review - Remaining Work"
- Updates the existing issue if found
- Creates a new issue if not found
- Labels: `automated`, `project-review`, `technical-debt`

The issue includes:
- Full report content
- Link to workflow run
- Direct links to artifacts
- Auto-generated timestamp

## Pull Request Integration

When `create_pr` is enabled:

- Creates a new branch: `automation/full-review/YYYY-MM-DD`
- Commits the report and screenshots
- Creates a PR against the `main` branch
- PR Title: `chore: full review report YYYY-MM-DD`
- Includes link to workflow run

## Workflow Duration

Typical execution times:

| Configuration | Duration |
|--------------|----------|
| Quick Review | 5-10 minutes |
| Full Audit | 15-25 minutes |
| With UI Snapshots | 20-30 minutes |

## Troubleshooting

### Common Issues

#### 1. Frontend Build Fails
- Check Node.js version compatibility
- Verify all dependencies are installed
- Review TypeScript errors

#### 2. Backend Tests Fail
- Database initialization issues
- Missing environment variables
- Test database connection problems

#### 3. UI Snapshots Fail
- Services not starting properly
- Network connectivity issues
- Playwright installation problems

#### 4. Security Scan False Positives
- Review Trivy results for context
- Check if vulnerabilities are in dev dependencies
- Verify Gitleaks findings aren't test data

### Getting Help

1. Review the workflow logs in GitHub Actions
2. Download and examine the artifacts
3. Check the generated report for specific errors
4. Look at individual step outputs for details

## Best Practices

### When to Run

- **Before releases**: Ensure code quality before deploying
- **Weekly/Monthly**: Regular project health checks
- **After major changes**: Validate large refactors
- **Security audits**: Periodic vulnerability scans

### Following Up

1. **Review the report**: Read the executive summary first
2. **Prioritize**: Address critical issues before warnings
3. **Create focused PRs**: Don't fix everything at once
4. **Track progress**: Use the issue to monitor improvements
5. **Re-run after fixes**: Verify improvements with another run

### Integration with Development

- Use findings to improve CI/CD pipelines
- Add failing checks to pre-commit hooks
- Update coding standards based on common issues
- Share reports with the team for awareness

## Advanced Usage

### Running Locally

The report generation script can be run manually:

```bash
# Create a data file
cat > full-review-data.json << EOF
{
  "workflowRunId": "123456",
  "workflowRunNumber": "1",
  "repository": "owner/repo",
  "frontend": { /* ... */ },
  "backend": { /* ... */ },
  "security": { /* ... */ }
}
EOF

# Generate report
node automation/scripts/parse-full-review.js full-review-data.json

# View report
cat automation/FULL_REVIEW_REPORT.md
```

### Customizing the Workflow

To adapt the workflow for your needs:

1. **Modify checks**: Edit `.github/workflows/full-review.yml`
2. **Add new metrics**: Update `parse-full-review.js`
3. **Change thresholds**: Adjust failure conditions
4. **Add new scans**: Integrate additional tools

### Scheduling Automatic Runs

Add a schedule trigger to run automatically:

```yaml
on:
  workflow_dispatch:
    # ... existing inputs ...
  schedule:
    - cron: '0 0 * * 1'  # Run every Monday at midnight UTC
```

## Security Considerations

- Workflow has minimal permissions by default
- Write access only granted for PR/issue creation
- Secrets never exposed in reports or logs
- All scans run in isolated containers

## Contributing

To improve the Full Review workflow:

1. Test changes locally first
2. Update documentation
3. Add new features incrementally
4. Ensure backward compatibility
5. Update this guide with new features

---

**Last Updated**: January 2026  
**Workflow Version**: 1.0  
**Maintainer**: GitHub Actions Bot
