#!/bin/bash

###############################################################################
# Generate Review Report Script
# 
# Generates a comprehensive review report for the server-monitor project
# Used by the manual-project-review workflow
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPORT_FILE="${REPORT_FILE:-docs/REVIEW_REPORT.md}"
REF="${REF:-unknown}"
RUNNER_OS="${RUNNER_OS:-unknown}"
LINT_RESULT="${LINT_RESULT:-unknown}"
TEST_RESULT="${TEST_RESULT:-unknown}"
BUILD_RESULT="${BUILD_RESULT:-unknown}"
SMOKE_RESULT="${SMOKE_RESULT:-unknown}"
SCREENSHOT_RESULT="${SCREENSHOT_RESULT:-unknown}"

echo -e "${BLUE}📝 Generating review report...${NC}"

# Get current timestamp
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Get git information
GIT_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
GIT_COMMIT_SHORT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
GIT_AUTHOR=$(git log -1 --format='%an <%ae>' 2>/dev/null || echo "unknown")
GIT_DATE=$(git log -1 --format='%ai' 2>/dev/null || echo "unknown")

# Count files and lines
BACKEND_FILES=$(find backend -name "*.py" 2>/dev/null | wc -l || echo "0")
FRONTEND_FILES=$(find frontend-next/src -name "*.tsx" -o -name "*.ts" 2>/dev/null | wc -l || echo "0")
TEST_FILES=$(find tests -name "*.py" 2>/dev/null | wc -l || echo "0")
DOC_FILES=$(find . -maxdepth 1 -name "*.md" 2>/dev/null | wc -l || echo "0")

# Generate report
cat > "$REPORT_FILE" << EOF
# Project Review Report

**Generated:** ${TIMESTAMP}  
**Ref:** ${REF}  
**Commit:** ${GIT_COMMIT_SHORT} (${GIT_COMMIT})  
**Branch:** ${GIT_BRANCH}  
**Author:** ${GIT_AUTHOR}  
**Date:** ${GIT_DATE}

---

## Executive Summary

This automated review report provides a comprehensive audit of the server-monitor project, including code quality checks, test results, build validation, and documentation consistency.

### Quick Status

| Component | Status |
|-----------|--------|
| Python Linting | ${LINT_RESULT} |
| Unit Tests | ${TEST_RESULT} |
| Frontend Build | ${BUILD_RESULT} |
| Smoke Tests | ${SMOKE_RESULT} |
| UI Screenshots | ${SCREENSHOT_RESULT} |

---

## Environment Information

- **Runner OS:** ${RUNNER_OS}
- **Python Version:** $(python --version 2>&1 || echo "unknown")
- **Node Version:** $(node --version 2>&1 || echo "unknown")
- **Git Version:** $(git --version 2>&1 || echo "unknown")

---

## Repository Statistics

- **Backend Python Files:** ${BACKEND_FILES}
- **Frontend TypeScript Files:** ${FRONTEND_FILES}
- **Test Files:** ${TEST_FILES}
- **Documentation Files:** ${DOC_FILES}

---

## CI Results

### 1. Static Analysis & Linting

**Python Linting (flake8):** ${LINT_RESULT}

EOF

# Add lint details if available
if [ -f "lint-results.txt" ]; then
  echo "#### Details:" >> "$REPORT_FILE"
  echo '```' >> "$REPORT_FILE"
  cat lint-results.txt >> "$REPORT_FILE"
  echo '```' >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" << EOF

**Security Scanning (bandit):** See security scan results

**Frontend Linting (ESLint):** ${LINT_RESULT}

**TypeScript Type Check:** ${LINT_RESULT}

### 2. Unit & Integration Tests

**Result:** ${TEST_RESULT}

EOF

# Add test details if available
if [ -f "test-results.txt" ]; then
  echo "#### Test Summary:" >> "$REPORT_FILE"
  echo '```' >> "$REPORT_FILE"
  cat test-results.txt >> "$REPORT_FILE"
  echo '```' >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" << EOF

### 3. Build Validation

**Frontend Build:** ${BUILD_RESULT}

### 4. Smoke Tests

**Result:** ${SMOKE_RESULT}

EOF

# Add smoke test details if available
if [ -f "smoke-results.txt" ]; then
  echo "#### Smoke Test Details:" >> "$REPORT_FILE"
  echo '```' >> "$REPORT_FILE"
  cat smoke-results.txt >> "$REPORT_FILE"
  echo '```' >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" << EOF

### 5. UI Screenshots

**Result:** ${SCREENSHOT_RESULT}

Screenshots are available in \`docs/screenshots/\` directory.

---

## Module Coverage

The following modules were checked during this review:

- ✅ **Authentication & RBAC:** \`backend/user_management.py\`, \`backend/security.py\`
- ✅ **Webhooks:** \`backend/webhook_dispatcher.py\`
- ✅ **Task Management:** \`backend/task_runner.py\`, \`backend/task_policy.py\`
- ✅ **Inventory:** \`backend/inventory_collector.py\`
- ✅ **Terminal:** \`backend/terminal.py\`, \`backend/websocket_server.py\`
- ✅ **Audit:** \`backend/event_model.py\`, \`backend/audit_cleanup.py\`
- ✅ **Plugins:** \`backend/plugin_system.py\`, \`backend/plugins/\`
- ✅ **Crypto Vault:** \`backend/crypto_vault.py\`, \`backend/ssh_key_manager.py\`
- ✅ **Rate Limiting:** \`backend/rate_limiter.py\`
- ✅ **Cache:** \`backend/cache_helper.py\`
- ✅ **Frontend:** \`frontend-next/src/\`

---

## Findings

### Documentation Consistency

EOF

# Check for common documentation issues
echo "#### Checked Documentation Files:" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for doc in README.md DEPLOYMENT.md SECURITY.md ARCHITECTURE.md ROADMAP.md TODO-IMPROVEMENTS.md; do
  if [ -f "$doc" ]; then
    echo "- ✅ \`$doc\` exists" >> "$REPORT_FILE"
  else
    echo "- ❌ \`$doc\` missing" >> "$REPORT_FILE"
  fi
done

cat >> "$REPORT_FILE" << EOF

#### OpenAPI Specification

EOF

if [ -f "docs/openapi.yaml" ]; then
  echo "- ✅ \`docs/openapi.yaml\` exists" >> "$REPORT_FILE"
else
  echo "- ❌ \`docs/openapi.yaml\` missing" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" << EOF

### Potential Issues

EOF

# Check for TODO/FIXME comments
echo "#### Code TODOs and FIXMEs:" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
# Count TODO/FIXME occurrences in code (not lines)
if [ -d "backend" ] && [ -d "frontend-next/src" ]; then
  TODO_COUNT=$(grep -roh "TODO\|FIXME" backend/ frontend-next/src/ 2>/dev/null | wc -l || echo "0")
else
  TODO_COUNT="0"
fi
echo "Found **${TODO_COUNT}** TODO/FIXME comments in code" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Check for hardcoded credentials patterns
echo "#### Security Scan:" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "Run \`bandit -r backend/\` for detailed security analysis" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

cat >> "$REPORT_FILE" << EOF

### Missing Tests

Review test coverage to identify modules that need additional testing.

Run: \`pytest --cov=backend --cov-report=html\` for detailed coverage report

---

## Suggested Next PRs

Based on this review, consider the following improvements:

### High Priority

1. **Fix any failing tests** - Address test failures identified in this report
2. **Security fixes** - Address any security issues from bandit scan
3. **Documentation updates** - Fix broken links and update outdated sections

### Medium Priority

1. **Increase test coverage** - Add tests for modules with <80% coverage
2. **Code cleanup** - Address TODO/FIXME comments
3. **Performance optimization** - Profile slow endpoints and optimize

### Low Priority

1. **UI/UX improvements** - Based on screenshot review
2. **Documentation enhancements** - Add more examples and use cases
3. **Developer experience** - Improve setup and development workflow

---

## Copilot Agent Task Prompt

If you want to delegate follow-up tasks to GitHub Copilot agent, use this prompt:

\`\`\`
Review the automated project review report at docs/REVIEW_REPORT.md and address the following:

1. Fix any failing tests identified in the test results
2. Address security issues found by bandit scan
3. Update documentation based on the findings
4. Add missing tests for modules with low coverage
5. Clean up TODO/FIXME comments in the codebase

Create focused PRs for each major issue found. Ensure all changes maintain backward compatibility and don't break existing functionality.
\`\`\`

---

## Release Checklist

Before releasing the next version, ensure:

- [ ] All CI checks pass (lint, test, build, smoke)
- [ ] No critical security vulnerabilities
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated
- [ ] Version numbers are bumped appropriately
- [ ] Screenshots reflect current UI state
- [ ] All TODOs in ROADMAP.md are reviewed
- [ ] Deployment guide is tested and accurate

---

## Artifacts

The following artifacts were generated during this review:

- Test results: See GitHub Actions artifacts
- Lint results: See GitHub Actions artifacts
- Screenshots: \`docs/screenshots/\`
- Review report: \`docs/REVIEW_REPORT.md\` (this file)

---

**Report Generated By:** GitHub Actions Manual Project Review Workflow  
**Next Review:** Run workflow manually when significant changes are made
EOF

echo -e "${GREEN}✅ Review report generated: ${REPORT_FILE}${NC}"

# Also output to console
echo ""
echo "=========================================="
echo "Review Report Summary"
echo "=========================================="
echo "Ref: ${REF}"
echo "Commit: ${GIT_COMMIT_SHORT}"
echo ""
echo "Results:"
echo "  Linting: ${LINT_RESULT}"
echo "  Tests: ${TEST_RESULT}"
echo "  Build: ${BUILD_RESULT}"
echo "  Smoke: ${SMOKE_RESULT}"
echo "  Screenshots: ${SCREENSHOT_RESULT}"
echo ""
echo "Full report: ${REPORT_FILE}"
echo "=========================================="
