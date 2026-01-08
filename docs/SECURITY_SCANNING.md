# Security Scanning Guide

**Version:** 1.0  
**Last Updated:** January 2026  
**Maintained By:** DevSecOps Team

---

## 📋 Overview

This document describes the automated security scanning tools and processes used in the Server Monitor project. These tools help identify vulnerabilities, insecure code patterns, and supply chain risks.

---

## 🔍 Automated Security Scans

### 1. CodeQL Analysis

**What it does:** Static analysis to find security vulnerabilities and code quality issues in Python and JavaScript/TypeScript code.

**When it runs:**
- On every push to `main` and `develop` branches
- On every pull request
- Nightly at 2 AM UTC
- Can be triggered manually via workflow dispatch

**Workflow:** `.github/workflows/codeql.yml`

**Languages covered:**
- Python (backend)
- JavaScript/TypeScript (frontend-next)

**Query suites:**
- `security-extended` - Comprehensive security checks

**How to view results:**
1. Go to repository **Security** tab
2. Click **Code scanning alerts**
3. Filter by **CodeQL** tool
4. Review findings and dismiss false positives

**Configuration:**
- No additional configuration needed
- GitHub automatically manages CodeQL databases
- Results appear in Security tab

---

### 2. Dependency Review

**What it does:** Reviews dependency changes in pull requests to identify:
- Known vulnerabilities (CVEs)
- License compliance issues
- Malicious packages

**When it runs:**
- On every pull request to `main` and `develop` branches

**Workflow:** `.github/workflows/dependency-review.yml`

**Configuration:**
- **Fail on severity:** High or Critical
- **Allowed licenses:** MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Python-2.0
- **Denied licenses:** GPL-3.0, AGPL-3.0
- **Comments on PR:** Always

**How to interpret:**
- ✅ **Pass**: No high/critical vulnerabilities, licenses OK
- ⚠️ **Warning**: Moderate vulnerabilities found
- ❌ **Fail**: High/critical vulnerabilities or license issues

**Remediation:**
```bash
# For Python dependencies
pip install --upgrade <package>
# Update backend/requirements.txt

# For Node dependencies
npm update <package>
# Or npm audit fix
```

---

### 3. Security Scan (pip-audit, npm audit, bandit)

**What it does:** Comprehensive security scanning of dependencies and code.

**When it runs:**
- On every push to `main` and `develop` branches
- On every pull request
- Nightly at 3 AM UTC
- Can be triggered manually

**Workflow:** `.github/workflows/security-scan.yml`

#### 3.1 Python Dependency Audit (pip-audit)

**Scans:** `backend/requirements.txt`

**Checks:**
- Known vulnerabilities in Python packages
- Using PyPI Advisory Database
- Provides CVE IDs and fix versions

**Output:**
- JSON results uploaded as artifact
- Summary in workflow run
- Lists vulnerable packages and remediation steps

**Remediation:**
```bash
# Install pip-audit locally
pip install pip-audit

# Check backend dependencies
pip-audit -r backend/requirements.txt

# Update vulnerable package
pip install --upgrade <package>==<safe_version>
# Update backend/requirements.txt
```

**Example output:**
```
Found 2 vulnerabilities in 1 package
Name     Version  ID              Fix Versions
-------- -------- --------------- ------------
paramiko 2.12.0   GHSA-xxx-xxx    >=3.0.0
paramiko 2.12.0   CVE-2023-xxxxx  >=2.12.1
```

#### 3.2 Node.js Dependency Audit (npm audit)

**Scans:** `frontend-next/package-lock.json`

**Checks:**
- Known vulnerabilities in npm packages
- Using npm registry advisory database
- Provides severity levels and fix information

**Output:**
- JSON results uploaded as artifact
- Vulnerability summary by severity
- Lists affected packages

**Remediation:**
```bash
cd frontend-next

# Check for vulnerabilities
npm audit

# Attempt automatic fix
npm audit fix

# For breaking changes
npm audit fix --force

# Manual update if needed
npm update <package>
```

**Example output:**
```
# npm audit report

lodash  <4.17.21
Severity: high
Prototype Pollution - https://github.com/advisories/GHSA-xxx
fix available via `npm audit fix`
```

#### 3.3 Python Security Scan (Bandit)

**Scans:** `backend/` directory (excluding tests)

**Checks:**
- Common security issues in Python code:
  - SQL injection risks
  - Hardcoded secrets
  - Weak cryptography
  - Command injection
  - Path traversal
  - Insecure deserialization

**Severity levels:**
- Low (L)
- Medium (M)
- High (H)

**Confidence levels:**
- Low (L)
- Medium (M)
- High (H)

**Configuration:**
- Only reports Low-Low severity and above (`-ll`)
- Excludes test directories

**Output:**
- JSON results uploaded as artifact
- Text summary in workflow run
- Lists issues by file and line number

**Remediation:**
1. Review each finding
2. Assess if it's a real vulnerability or false positive
3. Fix real vulnerabilities
4. For false positives, add inline comment:
   ```python
   # nosec B303
   ```

**Example output:**
```
>> Issue: [B608:hardcoded_sql_expressions] Possible SQL injection vector through string-based query construction.
   Severity: Medium   Confidence: Low
   Location: backend/database.py:145
   More Info: https://bandit.readthedocs.io/en/latest/plugins/b608_hardcoded_sql_expressions.html
```

---

## 🛡️ GitHub Secret Scanning

### What it does

GitHub automatically scans repositories for:
- API keys
- Tokens
- Passwords
- Private keys
- Database connection strings
- OAuth tokens

### How to enable

Secret scanning is **enabled by default** for public repositories. For private repositories:

1. Go to repository **Settings**
2. Navigate to **Security** → **Code security and analysis**
3. Enable **Secret scanning**
4. Enable **Push protection** (prevents commits with secrets)

### How to view alerts

1. Go to repository **Security** tab
2. Click **Secret scanning alerts**
3. Review any detected secrets
4. Take action to rotate/revoke exposed secrets

### Prevention

**Use environment variables:**
```bash
# ❌ Bad - Hardcoded secret
JWT_SECRET = "hardcoded-secret-key"

# ✅ Good - Environment variable
JWT_SECRET = os.getenv("JWT_SECRET")
```

**Use `.env` files (not committed):**
```bash
# .gitignore should include:
.env
.env.local
config.env
```

**Verify before commit:**
```bash
# Check for potential secrets
git diff | grep -i "password\|secret\|key\|token"
```

---

## 📊 Dependabot

### What it does

Dependabot automatically:
- Monitors dependencies for vulnerabilities
- Creates pull requests to update vulnerable dependencies
- Keeps dependencies up-to-date

### How to configure

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "python"
    
  # Node.js dependencies
  - package-ecosystem: "npm"
    directory: "/frontend-next"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "javascript"
    
  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "github-actions"
```

### How it works

1. Dependabot scans dependencies daily
2. Creates PR when update available
3. Runs CI checks on PR
4. Review and merge if tests pass

---

## 🔒 Supply Chain Security Best Practices

### 1. Pin Dependencies

**Python (`requirements.txt`):**
```
# ✅ Good - Pinned versions
paramiko==3.0.0
PyJWT==2.8.0
cryptography==41.0.0

# ⚠️ Acceptable - Minor version pinning
paramiko>=3.0.0,<4.0.0

# ❌ Bad - Unpinned
paramiko
```

**Node.js (`package.json`):**
```json
{
  "dependencies": {
    "next": "14.2.35",  // ✅ Exact version
    "react": "^18.2.0"   // ⚠️ Caret allows patches
  }
}
```

**Always commit `package-lock.json`** to ensure reproducible builds.

### 2. Verify Package Integrity

**npm:**
```bash
# Verify checksums
npm ci

# Audit before install
npm audit
npm install
```

**pip:**
```bash
# Use hash verification (optional)
pip install --require-hashes -r requirements.txt

# Generate hashes
pip-compile --generate-hashes requirements.in
```

### 3. Regular Updates

- **Weekly:** Review Dependabot PRs
- **Monthly:** Run full dependency audit
- **Immediately:** Apply critical security patches

### 4. Monitor Advisories

Subscribe to security advisories:
- [GitHub Advisory Database](https://github.com/advisories)
- [PyPI Security Advisories](https://github.com/pypa/advisory-database)
- [npm Security Advisories](https://github.com/advisories?query=ecosystem%3Anpm)

### 5. SBOM Generation

Generate Software Bill of Materials for transparency:

**Python:**
```bash
pip install cyclonedx-bom
cyclonedx-py -r -i backend/requirements.txt -o sbom-python.json
```

**Node.js:**
```bash
npx @cyclonedx/cyclonedx-npm --output-file sbom-node.json
```

---

## 🚨 Responding to Security Findings

### Severity Levels

**Critical:**
- **Action:** Fix immediately (within 24 hours)
- **Examples:** Remote code execution, authentication bypass
- **Process:** Create hotfix, deploy ASAP

**High:**
- **Action:** Fix within 7 days
- **Examples:** SQL injection, XSS, sensitive data exposure
- **Process:** Create patch release

**Moderate:**
- **Action:** Fix within 30 days
- **Examples:** Information disclosure, DoS
- **Process:** Include in next minor release

**Low:**
- **Action:** Fix when convenient
- **Examples:** Minor information leaks, low-impact bugs
- **Process:** Include in upcoming release

### Response Workflow

1. **Assess**
   - Verify the vulnerability is real (not false positive)
   - Determine actual impact on your deployment
   - Check if vulnerable code path is reachable

2. **Triage**
   - Assign severity based on actual risk
   - Determine timeline for fix
   - Identify who should fix it

3. **Remediate**
   - Update dependency to safe version
   - Or apply code fix if no update available
   - Test fix thoroughly
   - Run security scans again

4. **Verify**
   - Confirm vulnerability is resolved
   - Re-run security scans
   - Check for regressions

5. **Document**
   - Update CHANGELOG
   - Document in release notes
   - Add to security advisory (if public)

6. **Deploy**
   - Release patch/hotfix
   - Notify users to update
   - Monitor for issues

---

## 📈 Security Metrics

Track these metrics to measure security posture:

- **Mean Time To Remediate (MTTR):** Average time to fix vulnerabilities
- **Open Vulnerabilities:** Current count by severity
- **False Positive Rate:** % of findings that are false positives
- **Dependency Freshness:** % of dependencies that are up-to-date
- **Scan Coverage:** % of codebase scanned

**Target goals:**
- Critical: MTTR < 24 hours
- High: MTTR < 7 days
- Moderate: MTTR < 30 days
- Open Critical: 0
- Open High: < 3
- Dependency Freshness: > 90%

---

## 🔧 Local Security Scanning

Run security scans locally before pushing:

```bash
# Python dependency audit
pip install pip-audit
pip-audit -r backend/requirements.txt

# Python security scan
pip install bandit
bandit -r backend -x tests -ll

# Node.js dependency audit
cd frontend-next
npm audit

# Check for secrets
git secrets --scan

# Or use pre-commit hooks
pip install pre-commit
pre-commit install
```

---

## 📚 Additional Resources

### Documentation
- [GitHub Security Features](https://docs.github.com/en/code-security)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [pip-audit Guide](https://pypi.org/project/pip-audit/)
- [npm audit Documentation](https://docs.npmjs.com/cli/v8/commands/npm-audit)
- [Bandit Documentation](https://bandit.readthedocs.io/)

### Security Databases
- [GitHub Advisory Database](https://github.com/advisories)
- [CVE Database](https://cve.mitre.org/)
- [National Vulnerability Database](https://nvd.nist.gov/)
- [PyPI Advisory Database](https://github.com/pypa/advisory-database)
- [npm Security Advisories](https://www.npmjs.com/advisories)

### Tools
- [Safety](https://pyup.io/safety/) - Python dependency checker
- [Snyk](https://snyk.io/) - Multi-language security scanner
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
- [Trivy](https://github.com/aquasecurity/trivy) - Container & dependency scanner

---

## ❓ FAQ

**Q: Should I fix all findings from security scans?**
A: Not necessarily. Assess each finding:
- Is it a true positive?
- Is the vulnerable code reachable?
- What's the actual impact?
- Is there a workaround?

Focus on real, exploitable vulnerabilities first.

**Q: How do I handle false positives?**
A: 
1. Verify it's actually a false positive
2. Document why it's false positive
3. Suppress with inline comments (bandit: `# nosec`)
4. Or configure tool to ignore specific issues

**Q: Can I disable security scans?**
A: Not recommended, but you can:
- Adjust frequency (e.g., only nightly)
- Lower sensitivity (fewer queries)
- Continue-on-error for non-blocking

Security is always a trade-off between safety and development velocity.

**Q: How often should I update dependencies?**
A: 
- **Critical security patches:** Immediately
- **High security patches:** Within 1 week
- **Regular updates:** Monthly or quarterly
- **Major versions:** When ready (test thoroughly)

**Q: What if a vulnerability has no fix?**
A:
1. Check if there's a workaround
2. Consider alternative package
3. Temporarily accept risk and document
4. Monitor for fixes
5. Implement additional controls (WAF, rate limiting, etc.)

---

**Document Version:** 1.0  
**Last Updated:** January 2026  
**Next Review:** July 2026
