# Server Monitor - Release Process

**Version:** 1.0  
**Last Updated:** January 2026  
**Maintained By:** DevSecOps Team

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Release Types](#release-types)
3. [Pre-Release Checklist](#pre-release-checklist)
4. [Release Workflow](#release-workflow)
5. [Version Numbering](#version-numbering)
6. [Changelog Guidelines](#changelog-guidelines)
7. [Release Artifacts](#release-artifacts)
8. [Post-Release Actions](#post-release-actions)
9. [Hotfix Process](#hotfix-process)
10. [Rollback Procedure](#rollback-procedure)

---

## 🎯 Overview

This document defines the standardized release process for Server Monitor Dashboard. Following this process ensures consistent, high-quality releases with proper documentation and validation.

### Release Principles

- **Semantic Versioning**: Follow [semver](https://semver.org/) strictly
- **Documented Changes**: All changes must be in CHANGELOG.md
- **Validated Releases**: All releases must pass staging validation
- **Traceable**: All releases tagged in Git with detailed notes
- **Repeatable**: Process should be automatable and consistent

---

## 📦 Release Types

### Major Release (X.0.0)

Breaking changes, major architectural updates, or significant feature additions.

**Examples:**
- v1.0.0 → v2.0.0 (Next.js rewrite, breaking API changes)
- Database schema changes requiring migration
- Removal of deprecated features

**Validation Required:**
- Full staging validation
- Extended soak testing (1-2 weeks)
- User acceptance testing
- Migration testing from previous version

### Minor Release (x.Y.0)

New features, enhancements, or significant improvements with backward compatibility.

**Examples:**
- v2.1.0 → v2.2.0 (Observability features, audit export)
- New API endpoints
- New UI components
- Performance improvements

**Validation Required:**
- Full staging validation
- Upgrade testing
- Integration testing

### Patch Release (x.y.Z)

Bug fixes, security patches, or minor improvements.

**Examples:**
- v2.2.0 → v2.2.1 (Bug fixes)
- Security vulnerability patches
- Documentation corrections

**Validation Required:**
- Targeted testing of fixes
- Regression testing
- Quick staging validation

---

## ✅ Pre-Release Checklist

Before starting the release process, ensure all these items are complete:

### Code Quality

- [ ] All CI/CD checks passing
- [ ] No critical or high-severity security vulnerabilities
- [ ] Code review completed for all changes
- [ ] Tests passing with adequate coverage
- [ ] Linting passes without errors

### Documentation

- [ ] CHANGELOG.md updated with all changes
- [ ] Release notes drafted (`RELEASE_NOTES_vX.Y.Z.md`)
- [ ] README.md updated (if needed)
- [ ] API documentation updated (OpenAPI spec)
- [ ] Migration guide written (if breaking changes)

### Testing

- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Smoke tests passing
- [ ] Staging validation completed (`docs/STAGING_CHECKLIST.md`)
- [ ] Upgrade path tested (from previous version)
- [ ] Rollback tested

### Security

- [ ] Dependency vulnerabilities addressed
- [ ] Security scan passing (bandit, npm audit, pip-audit)
- [ ] CodeQL scan passing
- [ ] No secrets in code
- [ ] SBOM generated

---

## 🔄 Release Workflow

### Step 1: Version Bump Preparation

1. **Create Release Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b release/vX.Y.Z
   ```

2. **Update Version Numbers**

   Update version in these locations:
   
   - **README.md** (line 6):
     ```markdown
     [![Version](https://img.shields.io/badge/version-X.Y.Z-blue)](...)
     ```
   
   - **CHANGELOG.md** (top of file):
     ```markdown
     ## [X.Y.Z] - YYYY-MM-DD - Release Name
     ```
   
   - Create **RELEASE_NOTES_vX.Y.Z.md**:
     ```bash
     cp RELEASE_NOTES_v2.2.0.md RELEASE_NOTES_vX.Y.Z.md
     # Edit with new version details
     ```

3. **Update CHANGELOG.md**

   Ensure CHANGELOG.md follows [Keep a Changelog](https://keepachangelog.com/) format:
   
   ```markdown
   ## [X.Y.Z] - YYYY-MM-DD - Brief Description
   
   ### Added
   - New features
   
   ### Changed
   - Modifications to existing features
   
   ### Fixed
   - Bug fixes
   
   ### Security
   - Security improvements
   
   ### Deprecated
   - Features marked for removal
   
   ### Removed
   - Removed features
   ```

4. **Generate Release Notes**

   Create `RELEASE_NOTES_vX.Y.Z.md` with:
   - Overview and key highlights
   - Detailed feature descriptions
   - Breaking changes (if any)
   - Upgrade instructions
   - Known issues
   - Contributors

### Step 2: Staging Validation

1. **Deploy to Staging Environment**
   ```bash
   # On staging server
   curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/release/vX.Y.Z/scripts/install.sh | sudo bash -s -- --ref release/vX.Y.Z
   ```

2. **Run Staging Checklist**
   ```bash
   # Follow docs/STAGING_CHECKLIST.md
   # Document results
   ```

3. **Run Enhanced Smoke Tests**
   ```bash
   # Local smoke test
   ./scripts/smoke.sh --verbose
   
   # Staging smoke test
   ./scripts/smoke.sh \
     --base-url https://staging.example.com \
     --api-url https://staging.example.com \
     --auth-user admin \
     --auth-pass STAGING_PASSWORD \
     --verbose
   ```

4. **Performance Testing**
   - Load test critical endpoints
   - Monitor resource usage
   - Verify no memory leaks
   - Check WebSocket stability

### Step 3: Final Review

1. **Security Review**
   - Run CodeQL scan
   - Run pip-audit and npm audit
   - Review dependency changes
   - Verify SBOM generated

2. **Documentation Review**
   - Verify all docs are up-to-date
   - Check links are not broken
   - Review API documentation
   - Verify examples work

3. **Stakeholder Approval**
   - Technical lead sign-off
   - QA sign-off
   - DevOps sign-off
   - Security sign-off (for major/minor releases)

### Step 4: Create Git Tag

1. **Merge Release Branch to Main**
   ```bash
   git checkout main
   git merge release/vX.Y.Z
   git push origin main
   ```

2. **Create Annotated Tag**
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z - Brief Description"
   git push origin vX.Y.Z
   ```

### Step 5: GitHub Release

1. **Navigate to GitHub Releases**
   - Go to: https://github.com/minhtuancn/server-monitor/releases
   - Click "Draft a new release"

2. **Fill Release Information**
   
   **Tag version:** `vX.Y.Z` (select existing tag)
   
   **Release title:** `Server Monitor vX.Y.Z - Release Name`
   
   **Description:** (use template below)
   
   ```markdown
   # Server Monitor vX.Y.Z - Release Name
   
   **Release Date:** YYYY-MM-DD  
   **Type:** [Major/Minor/Patch] Release
   
   ## 🎯 Overview
   
   [Brief description of the release]
   
   ## ✨ Highlights
   
   - Key feature 1
   - Key feature 2
   - Key feature 3
   
   ## 📦 What's Changed
   
   ### Added
   - New feature descriptions
   
   ### Changed
   - Modification descriptions
   
   ### Fixed
   - Bug fix descriptions
   
   ## 🔒 Security
   
   - Security improvements
   - Vulnerability fixes (if any)
   
   ## ⬆️ Upgrade Instructions
   
   **From vX.Y.Z:**
   ```bash
   sudo /opt/server-monitor/scripts/smctl update vX.Y.Z
   ```
   
   **Fresh Installation:**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash -s -- --ref vX.Y.Z
   ```
   
   ## 📚 Documentation
   
   - [CHANGELOG](https://github.com/minhtuancn/server-monitor/blob/main/CHANGELOG.md)
   - [Release Notes](https://github.com/minhtuancn/server-monitor/blob/main/RELEASE_NOTES_vX.Y.Z.md)
   - [Installation Guide](https://github.com/minhtuancn/server-monitor/blob/main/README.md#-quick-start)
   - [API Documentation](http://localhost:9083/docs)
   
   ## 🛡️ Security
   
   - **SBOM:** See attached `sbom-python.json` and `sbom-node.json`
   - **Checksums:** See attached `checksums.txt`
   - **OpenAPI Spec:** See attached `openapi.yaml`
   
   ## 🙏 Contributors
   
   [List contributors if applicable]
   
   ## 📊 Full Changelog
   
   See [CHANGELOG.md](https://github.com/minhtuancn/server-monitor/blob/main/CHANGELOG.md#XYZ---yyyy-mm-dd)
   ```

3. **Attach Release Artifacts**
   
   Generate and attach:
   
   ```bash
   # Generate OpenAPI spec
   curl http://localhost:9083/api/openapi.yaml > openapi-vX.Y.Z.yaml
   
   # Generate checksums
   sha256sum scripts/install.sh > install.sh.sha256
   
   # Generate SBOM (for v2.3.0+, see below for instructions)
   # Python SBOM using pip-audit or cyclonedx-bom
   pip-audit --format json > sbom-python.json
   # OR
   cyclonedx-bom -i pyproject.toml -o sbom-python.json
   
   # Node.js SBOM using cyclonedx-bom
   cd frontend-next
   npx @cyclonedx/cyclonedx-npm --output-file ../sbom-node.json
   cd ..
   
   # Create checksums file
   cat > checksums.txt << EOF
   # Server Monitor vX.Y.Z - File Checksums
   
   $(sha256sum scripts/install.sh)
   $(sha256sum docs/openapi.yaml)
   $(sha256sum RELEASE_NOTES_vX.Y.Z.md 2>/dev/null || echo "")
   EOF
   ```
   
   Upload files:
   - `openapi-vX.Y.Z.yaml`
   - `install.sh.sha256`
   - `checksums.txt`
   - `sbom-python.json` (recommended for v2.3.0+)
   - `sbom-node.json` (recommended for v2.3.0+)

4. **Publish Release**
   - Review all information
   - Click "Publish release"
   - Verify release appears on releases page

### Step 6: Post-Release Verification

1. **Test Installation from Release**
   ```bash
   # On clean server
   curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/vX.Y.Z/scripts/install.sh | sudo bash -s -- --ref vX.Y.Z
   
   # Verify checksum
   curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/vX.Y.Z/scripts/install.sh > /tmp/install.sh
   curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/vX.Y.Z/scripts/install.sh.sha256 > /tmp/install.sh.sha256
   cd /tmp && sha256sum -c install.sh.sha256
   ```

2. **Monitor Initial Deployments**
   - Watch for bug reports
   - Monitor error rates
   - Check performance metrics
   - Review user feedback

---

## 🔢 Version Numbering

Server Monitor follows [Semantic Versioning 2.0.0](https://semver.org/):

**Format:** `MAJOR.MINOR.PATCH`

### Increment Rules

**MAJOR** version when:
- Making incompatible API changes
- Breaking changes to configuration
- Database schema changes requiring manual migration
- Removing features

**MINOR** version when:
- Adding functionality in a backward-compatible manner
- New features or endpoints
- Significant improvements
- Deprecating features (but not removing)

**PATCH** version when:
- Making backward-compatible bug fixes
- Security patches
- Documentation updates
- Performance improvements without API changes

### Version Examples

- `2.0.0` → First Next.js version (major rewrite)
- `2.1.0` → OpenAPI documentation (new features)
- `2.2.0` → Observability & reliability (new features)
- `2.2.1` → Bug fixes (patch)
- `3.0.0` → Breaking API changes (major)

---

## 📝 Changelog Guidelines

### Format

Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [X.Y.Z] - YYYY-MM-DD - Brief Description

### Added
- New feature 1
- New feature 2

### Changed
- Modified existing feature 1
- Updated dependency X to vY

### Deprecated
- Feature X will be removed in v3.0.0

### Removed
- Removed deprecated feature Y

### Fixed
- Fixed bug #123: Description
- Fixed security issue CVE-YYYY-NNNNN

### Security
- Security improvement 1
- Patched vulnerability in dependency X
```

### Best Practices

1. **Group Changes Logically**
   - Group related changes together
   - Use subsections for major features

2. **Be Specific**
   - ❌ "Fixed bugs"
   - ✅ "Fixed memory leak in WebSocket connection pool"

3. **Include References**
   - Link to issues: `#123`
   - Link to PRs: `PR #456`
   - Link to CVEs: `CVE-2024-12345`

4. **User-Focused Language**
   - Write for users, not developers
   - Explain impact, not just technical details

5. **Breaking Changes**
   - Clearly mark breaking changes
   - Provide migration instructions

### Example Entry

```markdown
## [2.2.0] - 2026-01-07 - Observability & Reliability

### 🚀 Production Observability & Enhanced Reliability

This release brings comprehensive observability, enhanced security, and 
system reliability features with zero breaking changes.

### Added

**Observability & Monitoring**
- Health check endpoint (`GET /api/health`) for liveness probes
- Readiness check endpoint (`GET /api/ready`) with validation (#45)
- Metrics endpoint (`GET /api/metrics`) supporting Prometheus and JSON formats
- Request correlation via `X-Request-Id` header
- Structured JSON logging across all services

**Security Enhancements**
- Startup secret validation for production environments
- Task safety policy engine with denylist/allowlist modes
- Audit log retention & cleanup (90-day default)
- Audit log export endpoints (CSV/JSON) (#46)

**Reliability & Recovery**
- Graceful shutdown for all services (SIGTERM/SIGINT handlers)
- Task recovery on startup for interrupted tasks
- Terminal session recovery
- Enhanced error handling

### Changed
- All services now output structured JSON logs
- Enhanced startup with recovery statistics
- Improved shutdown behavior (no orphaned processes)
- Metrics collector tracks more system state

### Fixed
- Tasks stuck in 'running' state after service restart (#42)
- Terminal sessions not marked closed on crash (#43)
- No graceful cleanup on SIGTERM
- Audit logs growing indefinitely (#44)

### Configuration
New environment variables (all optional, backward compatible):
- `AUDIT_RETENTION_DAYS=90`
- `AUDIT_CLEANUP_ENABLED=true`
- `AUDIT_CLEANUP_INTERVAL_HOURS=24`
- `TASK_POLICY_MODE=denylist`

See [RELEASE_NOTES_v2.2.0.md](docs/product/RELEASE_NOTES_v2.2.0.md) for details.
```

---

## 📦 Release Artifacts

### Required Artifacts

Every release must include:

1. **Git Tag**
   - Annotated tag with description
   - Format: `vX.Y.Z`

2. **GitHub Release**
   - Release notes
   - Installation instructions
   - Upgrade instructions

3. **OpenAPI Specification**
   - Current API spec in YAML format
   - Versioned filename: `openapi-vX.Y.Z.yaml`

4. **Checksums**
   - SHA256 checksums for scripts
   - File: `checksums.txt`

### Optional Artifacts

Recommended for major/minor releases:

1. **SBOM (Software Bill of Materials)**
   - Python dependencies SBOM
   - Node.js dependencies SBOM

2. **Security Report**
   - Vulnerability scan results
   - Dependency audit summary

3. **Performance Report**
   - Benchmark results
   - Comparison with previous version

---

## 🚀 Post-Release Actions

After publishing a release:

### 1. Update Documentation Sites

- [ ] Update GitHub Pages (if applicable)
- [ ] Update wiki pages
- [ ] Update external documentation

### 2. Announcements

- [ ] Post on project forums/discussions
- [ ] Update project website
- [ ] Notify stakeholders
- [ ] Social media announcement (if applicable)

### 3. Monitoring

- [ ] Monitor error rates in production
- [ ] Watch for new issues reported
- [ ] Track adoption metrics
- [ ] Monitor performance metrics

### 4. Cleanup

- [ ] Delete release branch (if not needed)
- [ ] Close milestone (if using milestones)
- [ ] Archive old staging environments

### 5. Plan Next Release

- [ ] Review feedback from release
- [ ] Plan features for next version
- [ ] Update roadmap
- [ ] Create next milestone

---

## 🔥 Hotfix Process

For critical bugs or security issues requiring immediate release:

### 1. Assess Severity

Hotfix warranted if:
- Security vulnerability (high/critical)
- Data loss bug
- Service unavailable
- Critical functionality broken

### 2. Quick Release Process

```bash
# Create hotfix branch from latest release tag
git checkout vX.Y.Z
git checkout -b hotfix/vX.Y.Z+1

# Make minimal fix
# ... edit files ...

# Test fix
./scripts/smoke.sh --verbose

# Update CHANGELOG.md
# Add hotfix entry

# Update version (patch bump)
# Update README.md badge to vX.Y.Z+1

# Commit
git commit -am "hotfix: [Brief description]"

# Merge to main
git checkout main
git merge hotfix/vX.Y.Z+1
git push origin main

# Tag hotfix
git tag -a vX.Y.Z+1 -m "Hotfix vX.Y.Z+1 - [Description]"
git push origin vX.Y.Z+1

# Create GitHub release (expedited process)
# Notify users immediately
```

### 3. Communication

- Immediate notification to users
- Clear description of issue and fix
- Upgrade instructions
- Workaround (if applicable)

---

## ⏮️ Rollback Procedure

If a release has critical issues:

### 1. Assess Impact

Determine if rollback is necessary:
- Is the bug reproducible?
- What is the blast radius?
- Can it be fixed quickly with a hotfix?
- Is user data at risk?

### 2. Execute Rollback

**For users:**
```bash
# Using rollback script
sudo /opt/server-monitor/scripts/rollback.sh vX.Y.Z-1

# Or manual rollback
sudo systemctl stop server-monitor-*
cd /opt/server-monitor
sudo git fetch origin
sudo git checkout vX.Y.Z-1
sudo systemctl start server-monitor-*
```

**For maintainers:**
```bash
# Do NOT delete tags or releases
# Instead, create a new patch release fixing the issue

# Or if necessary, mark release as pre-release
# Edit GitHub release → Check "This is a pre-release"
```

### 3. Post-Rollback Actions

- [ ] Notify users of rollback
- [ ] Document issue thoroughly
- [ ] Create hotfix or patch release
- [ ] Update documentation
- [ ] Conduct post-mortem

---

## 🔐 Security Releases

For releases containing security fixes:

### 1. Embargo Period

- Develop fix privately
- Do not disclose vulnerability publicly
- Notify major users privately (if applicable)
- Coordinate disclosure date

### 2. Release Process

- Follow standard release process
- Add `### Security` section to CHANGELOG
- Include CVE numbers (if assigned)
- Provide clear impact assessment
- Include mitigation steps

### 3. Post-Release

- Public disclosure after release available
- Update security advisories
- Notify security mailing lists
- Request CVE assignment (if needed)

---

## 📋 Release Checklist Template

Use this checklist for each release:

```markdown
## Release vX.Y.Z Checklist

### Pre-Release
- [ ] All CI checks passing
- [ ] CHANGELOG.md updated
- [ ] RELEASE_NOTES_vX.Y.Z.md created
- [ ] README.md version badge updated
- [ ] Staging validation completed
- [ ] Security scans passing
- [ ] Tests passing
- [ ] Documentation reviewed

### Release
- [ ] Release branch created
- [ ] Version numbers updated
- [ ] Merged to main
- [ ] Git tag created and pushed
- [ ] GitHub release published
- [ ] Artifacts attached
- [ ] Checksums generated

### Post-Release
- [ ] Installation tested from release
- [ ] Announcements made
- [ ] Monitoring in place
- [ ] Documentation sites updated
- [ ] Release branch cleaned up

### Sign-Off
- [ ] Technical Lead: _______________
- [ ] QA: _______________
- [ ] DevOps: _______________
- [ ] Security: _______________ (major/minor only)
```

---

## 📚 References

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)
- Project CHANGELOG: [CHANGELOG.md](../CHANGELOG.md)
- Staging Checklist: [STAGING_CHECKLIST.md](STAGING_CHECKLIST.md)

---

**Document Version:** 1.0  
**Last Updated:** January 2026  
**Next Review:** July 2026
