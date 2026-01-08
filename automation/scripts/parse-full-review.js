#!/usr/bin/env node

/**
 * Parse Full Review Results and Generate Report
 * 
 * This script reads the full-review-data.json file and generates
 * a comprehensive markdown report in automation/FULL_REVIEW_REPORT.md
 */

const fs = require('fs');
const path = require('path');

// Get data file path from command line argument or use default
const dataFilePath = process.argv[2] || 'full-review-data.json';
const outputPath = path.join(__dirname, '..', 'FULL_REVIEW_REPORT.md');

// Read and parse the data file
let data;
try {
  const rawData = fs.readFileSync(dataFilePath, 'utf8');
  data = JSON.parse(rawData);
} catch (error) {
  console.error(`Error reading data file: ${error.message}`);
  process.exit(1);
}

// Generate the markdown report
const report = generateReport(data);

// Write the report to file
try {
  fs.writeFileSync(outputPath, report, 'utf8');
  console.log(`✅ Report successfully generated at: ${outputPath}`);
} catch (error) {
  console.error(`Error writing report file: ${error.message}`);
  process.exit(1);
}

/**
 * Generate the full markdown report
 */
function generateReport(data) {
  const timestamp = new Date().toISOString();
  const dateStr = new Date().toLocaleString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
    timeZoneName: 'short'
  });

  let report = `# 🔍 Full Review Report

**Generated:** ${dateStr}  
**Repository:** ${data.repository}  
**Workflow Run:** [#${data.workflowRunNumber}](https://github.com/${data.repository}/actions/runs/${data.workflowRunId})

---

## 📊 Executive Summary

`;

  // Calculate overall status
  const criticalIssues = [];
  const warnings = [];
  
  // Frontend checks
  if (data.frontend.lint.errors > 0) {
    criticalIssues.push(`Frontend has ${data.frontend.lint.errors} linting error(s)`);
  }
  if (data.frontend.lint.warnings > 0) {
    warnings.push(`Frontend has ${data.frontend.lint.warnings} linting warning(s)`);
  }
  if (!data.frontend.typecheck.success) {
    criticalIssues.push('Frontend TypeScript check failed');
  }
  if (!data.frontend.build.success) {
    criticalIssues.push('Frontend build failed');
  }

  // Backend checks
  if (data.backend.lint.errors > 0) {
    criticalIssues.push(`Backend has ${data.backend.lint.errors} linting error(s)`);
  }
  if (data.backend.lint.warnings > 0) {
    warnings.push(`Backend has ${data.backend.lint.warnings} linting warning(s)`);
  }
  if (!data.backend.test.success) {
    warnings.push('Backend tests failed or had issues');
  }
  if (!data.backend.build.success) {
    criticalIssues.push('Backend build failed');
  }

  // Security checks
  if (data.security.trivy.critical > 0) {
    criticalIssues.push(`${data.security.trivy.critical} CRITICAL security vulnerabilities found`);
  }
  if (data.security.trivy.high > 0) {
    warnings.push(`${data.security.trivy.high} HIGH security vulnerabilities found`);
  }
  if (data.security.gitleaks.secretsFound > 0) {
    criticalIssues.push(`${data.security.gitleaks.secretsFound} potential secret(s) detected`);
  }

  // Overall status
  if (criticalIssues.length === 0 && warnings.length === 0) {
    report += `### ✅ Overall Status: HEALTHY\n\nNo critical issues or warnings detected.\n\n`;
  } else if (criticalIssues.length > 0) {
    report += `### ⚠️ Overall Status: NEEDS ATTENTION\n\n**Critical Issues (${criticalIssues.length}):**\n`;
    criticalIssues.forEach(issue => {
      report += `- ❌ ${issue}\n`;
    });
    report += '\n';
    
    if (warnings.length > 0) {
      report += `**Warnings (${warnings.length}):**\n`;
      warnings.forEach(warning => {
        report += `- ⚠️ ${warning}\n`;
      });
      report += '\n';
    }
  } else {
    report += `### ⚠️ Overall Status: MINOR ISSUES\n\n**Warnings (${warnings.length}):**\n`;
    warnings.forEach(warning => {
      report += `- ⚠️ ${warning}\n`;
    });
    report += '\n';
  }

  // Quick Stats Table
  report += `## 📈 Quick Statistics

| Category | Metric | Value |
|----------|--------|-------|
| 🎨 **Frontend** | Lint Errors | ${data.frontend.lint.errors} |
| 🎨 **Frontend** | Lint Warnings | ${data.frontend.lint.warnings} |
| 🎨 **Frontend** | TypeScript Check | ${data.frontend.typecheck.success ? '✅ Passed' : '❌ Failed'} |
| 🎨 **Frontend** | Build Status | ${data.frontend.build.success ? '✅ Passed' : '❌ Failed'} |
| ⚙️ **Backend** | Lint Errors | ${data.backend.lint.errors} |
| ⚙️ **Backend** | Lint Warnings | ${data.backend.lint.warnings} |
| ⚙️ **Backend** | Tests | ${data.backend.test.success ? '✅ Passed' : '⚠️ Had Issues'} |
| ⚙️ **Backend** | Build Status | ${data.backend.build.success ? '✅ Passed' : '❌ Failed'} |
| 🔒 **Security** | Total Vulnerabilities | ${data.security.trivy.total} |
| 🔒 **Security** | Critical Vulns | ${data.security.trivy.critical} |
| 🔒 **Security** | High Vulns | ${data.security.trivy.high} |
| 🔒 **Security** | Medium Vulns | ${data.security.trivy.medium} |
| 🔒 **Security** | Low Vulns | ${data.security.trivy.low} |
| 🔒 **Security** | Secrets Found | ${data.security.gitleaks.secretsFound} |

---

`;

  // Detailed Sections
  report += `## 🎨 Frontend Analysis

### Linting
- **Errors:** ${data.frontend.lint.errors}
- **Warnings:** ${data.frontend.lint.warnings}
- **Status:** ${data.frontend.lint.errors === 0 ? '✅ No errors' : '❌ Needs attention'}

### TypeScript Type Checking
- **Status:** ${data.frontend.typecheck.success ? '✅ Passed' : '❌ Failed'}

### Build
- **Status:** ${data.frontend.build.success ? '✅ Passed' : '❌ Failed'}

${data.frontend.lint.errors > 0 || data.frontend.lint.warnings > 0 ? `
#### 🔧 Recommended Actions
- Review and fix linting errors in the frontend codebase
- Address TypeScript type errors if any
- Ensure all imports and dependencies are properly resolved
` : ''}

---

## ⚙️ Backend Analysis

### Linting
- **Errors:** ${data.backend.lint.errors}
- **Warnings:** ${data.backend.lint.warnings}
- **Status:** ${data.backend.lint.errors === 0 ? '✅ No errors' : '❌ Needs attention'}

### Tests
- **Status:** ${data.backend.test.success ? '✅ Passed' : '⚠️ Had Issues'}
- **Note:** Test failures may be expected in some cases

### Build
- **Status:** ${data.backend.build.success ? '✅ Passed' : '❌ Failed'}

${data.backend.lint.errors > 0 || data.backend.lint.warnings > 0 ? `
#### 🔧 Recommended Actions
- Review and fix linting errors in the backend codebase
- Address any failing tests
- Ensure all dependencies are properly installed
` : ''}

---

## 🔒 Security Analysis

### Trivy Vulnerability Scan
- **Total Vulnerabilities:** ${data.security.trivy.total}
- **Critical:** ${data.security.trivy.critical} ${data.security.trivy.critical > 0 ? '🚨' : ''}
- **High:** ${data.security.trivy.high} ${data.security.trivy.high > 0 ? '⚠️' : ''}
- **Medium:** ${data.security.trivy.medium}
- **Low:** ${data.security.trivy.low}

### Gitleaks Secret Scanning
- **Secrets Detected:** ${data.security.gitleaks.secretsFound}
- **Status:** ${data.security.gitleaks.secretsFound === 0 ? '✅ No secrets found' : '⚠️ Secrets detected - review required'}

${data.security.trivy.critical > 0 || data.security.trivy.high > 0 || data.security.gitleaks.secretsFound > 0 ? `
#### 🚨 Security Recommendations
${data.security.trivy.critical > 0 ? '- **URGENT:** Address critical vulnerabilities immediately\n' : ''}${data.security.trivy.high > 0 ? '- Review and patch high-severity vulnerabilities\n' : ''}${data.security.gitleaks.secretsFound > 0 ? '- Review detected secrets and remove them from git history if confirmed\n' : ''}- Update dependencies to latest secure versions
- Review security scan artifacts for detailed information
` : ''}

---

## 📸 UI Snapshots

${data.uiSnapshots.enabled ? `
- **Status:** ✅ Enabled
- **Result:** ${data.uiSnapshots.testsRun}
- UI screenshots and E2E test results are available in workflow artifacts
` : `
- **Status:** ⏭️ Skipped
- UI snapshots were not captured in this run
`}

---

## 🎯 Action Items

### High Priority
${criticalIssues.length > 0 ? criticalIssues.map(issue => `- [ ] ${issue}`).join('\n') : '- [x] No high-priority issues'}

### Medium Priority
${warnings.length > 0 ? warnings.map(warning => `- [ ] ${warning}`).join('\n') : '- [x] No medium-priority issues'}

### Continuous Improvement
- [ ] Review and update documentation
- [ ] Improve test coverage
- [ ] Update dependencies
- [ ] Monitor security advisories

---

## 📚 Additional Resources

- **Full Lint Results:** Check workflow artifacts
- **Test Results:** Check workflow artifacts
- **Security Scans:** Check workflow artifacts
- **UI Screenshots:** Check workflow artifacts (if enabled)

---

## 🤖 Workflow Information

- **Run ID:** ${data.workflowRunId}
- **Run Number:** ${data.workflowRunNumber}
- **Timestamp:** ${timestamp}
- **Repository:** ${data.repository}

---

<sub>🤖 Auto-generated by Full Review Workflow</sub>
`;

  return report;
}
