# Server Monitor - Product Roadmap

**Version-based roadmap with clear outcomes, scope, and non-goals for each release.**

Last Updated: 2026-01-09

---

## Current Version: v2.3.1 (Production)

**Status**: ✅ Stable, production-ready  
**Release Date**: 2026-01-09

### What's Included

- Multi-server monitoring with real-time WebSocket updates
- Web terminal (SSH via xterm.js)
- JWT authentication with RBAC
- **NEW**: First-run admin setup (onboarding flow)
- **NEW**: Custom domain support (e.g., mon.go7s.net)
- Plugin system with webhooks
- Multi-channel alerts (Email, Telegram, Slack)
- SSH key vault with AES-256-GCM encryption
- Internationalization (8 languages)
- Next.js 16 frontend with App Router

### Known Issues

- None critical
- 2 security tests need review (not blockers)

---

## Upcoming Releases

### v2.4.0 — Stability & Testing (Target: Q1 2026)

**Outcome**: Rock-solid production system with comprehensive test coverage and improved UX.

**Scope**:

- **Testing**:
  - Fix remaining 2 security tests
  - Add E2E tests (Playwright) for critical flows
  - Add WebSocket integration tests
  - Add terminal (SSH) functionality tests
- **UI/UX Polish**:
  - Add breadcrumb navigation
  - Improve mobile responsive design
  - Add loading states to all async operations
  - Standardize error messages
- **Performance**:
  - Optimize database queries (add indexes)
  - Add response caching headers
  - Minify/compress frontend assets
- **Operations**:
  - Add database backup automation
  - Improve log aggregation
  - Add health check dashboard

**Non-Goals**:

- No new features (focus on stability)
- No architecture changes
- No new dependencies

**Acceptance Criteria**:

- [ ] All tests pass (100% success rate)
- [ ] E2E test suite covers login, dashboard, terminal
- [ ] Mobile dashboard usable on phone/tablet
- [ ] Database backup script runs nightly
- [ ] Health check dashboard shows all service status

---

### v2.5.0 — Enterprise Features (Target: Q2 2026)

**Outcome**: Multi-tenancy and advanced access control for enterprise deployments.

**Scope**:

- **Multi-Tenancy**:
  - Tenant isolation (data, users, servers)
  - Tenant admin role
  - Per-tenant configuration
- **Access Control**:
  - Enhanced RBAC with custom roles
  - Permission inheritance
  - Audit log for all actions
- **Security**:
  - Two-factor authentication (2FA/TOTP)
  - OAuth2 integration (Google, GitHub, Azure AD)
  - IP whitelist/blacklist per tenant
- **Monitoring**:
  - Prometheus metrics endpoint
  - Grafana dashboard templates
  - Distributed tracing (optional)

**Non-Goals**:

- No microservices split (monolith is fine)
- No Kubernetes yet (bare metal/VM focus)
- No GraphQL API (REST is sufficient)

**Acceptance Criteria**:

- [ ] Multiple tenants can coexist with isolated data
- [ ] Custom roles can be created via UI
- [ ] 2FA works with authenticator apps
- [ ] OAuth login works for at least 2 providers
- [ ] Audit log records all privileged actions
- [ ] Prometheus metrics exported

---

### v3.0.0 — Scalability & Cloud (Target: Q3 2026)

**Outcome**: Cloud-native deployment with horizontal scaling and managed database support.

**Scope**:

- **Database**:
  - PostgreSQL support (alongside SQLite)
  - Database migrations (Alembic)
  - Connection pooling
- **Infrastructure**:
  - Docker Compose for local dev
  - Kubernetes manifests (optional deployment)
  - Redis caching layer (optional)
  - Message queue (RabbitMQ/Redis for async tasks)
- **Scalability**:
  - Horizontal scaling (multiple API instances)
  - Distributed WebSocket (Redis pub/sub)
  - Load balancer support (sticky sessions)
- **Cloud Integrations**:
  - AWS deployment guide
  - Azure deployment guide
  - GCP deployment guide

**Non-Goals**:

- No vendor lock-in (cloud-agnostic)
- No removal of bare metal support
- No forced PostgreSQL migration (SQLite still supported)

**Breaking Changes**:

- Database connection string format changes
- Environment variable renames for consistency
- API versioning introduced (/api/v1/, /api/v2/)

**Migration Guide**:

- Migration script provided: `scripts/migrate_v2_to_v3.sh`
- Automatic backup before migration
- Rollback instructions included

**Acceptance Criteria**:

- [ ] PostgreSQL works as primary database
- [ ] Docker Compose brings up full stack
- [ ] Kubernetes manifests deploy successfully
- [ ] Redis caching improves API response time by 50%
- [ ] Horizontal scaling tested with 3+ API instances
- [ ] Migration script tested on real v2.x data

---

### v3.1.0 — Advanced Monitoring (Target: Q4 2026)

**Outcome**: Deep insights with custom metrics, alerting, and reporting.

**Scope**:

- **Custom Metrics**:
  - User-defined metric collectors
  - Plugin API for metric sources
  - Time-series data storage (InfluxDB integration)
- **Alerting**:
  - Alert rules engine (threshold, anomaly, pattern)
  - Alert aggregation (reduce noise)
  - Alert escalation policies
  - Snooze/acknowledge alerts
- **Reporting**:
  - Scheduled reports (daily, weekly, monthly)
  - Report templates (PDF, HTML, email)
  - Trend analysis charts
  - SLA tracking
- **Dashboards**:
  - Custom dashboard builder (drag-and-drop)
  - Dashboard templates library
  - Dashboard sharing (public links)

**Non-Goals**:

- No AI/ML predictions (future consideration)
- No mobile app (web-first)

**Acceptance Criteria**:

- [ ] Users can define custom metric collectors via UI
- [ ] Alert rules can be created without code
- [ ] Weekly reports emailed automatically
- [ ] Dashboard builder supports 10+ widget types
- [ ] Public dashboard links work without login

---

## Future Considerations (v4.0+)

Ideas under consideration for post-v3:

- **AI/ML Integration**:
  - Anomaly detection (auto-learn normal patterns)
  - Predictive alerts (forecast capacity issues)
  - Intelligent insights (root cause analysis suggestions)
- **Mobile App**:
  - iOS/Android native apps
  - Push notifications
  - Mobile-optimized dashboards
- **Advanced Integrations**:
  - ServiceNow, Jira, PagerDuty connectors
  - ChatOps (Slack/Teams commands)
  - Status page generation (public incident dashboard)
- **Developer Tools**:
  - GraphQL API (alongside REST)
  - SDK libraries (Python, Node.js, Go)
  - Terraform provider
- **Community Features**:
  - Plugin marketplace
  - Dashboard template sharing
  - Community forums

---

## Versioning Strategy

### Semantic Versioning (SemVer)

- **MAJOR.MINOR.PATCH** (e.g., v2.3.1)
  - **MAJOR**: Breaking changes (API changes, schema changes, migrations required)
  - **MINOR**: New features (backward-compatible)
  - **PATCH**: Bug fixes (backward-compatible)

### Release Cadence

- **Patch releases**: As needed (bug fixes, security)
- **Minor releases**: Quarterly (new features)
- **Major releases**: Annually (breaking changes)

### Long-Term Support (LTS)

- **v2.x**: Supported until v4.0 release (~ 2027)
- **v3.x**: Supported until v5.0 release (~ 2028)
- Security patches for all supported versions

---

## Decision Log

### Why Multi-Tenancy in v2.5?

- Enterprise customers requested it
- Enables SaaS deployment model
- Foundational for future growth

### Why PostgreSQL in v3.0?

- SQLite limitations for concurrent writes
- Enterprise requirement for managed databases
- Better performance for large datasets

### Why Not Mobile App Yet?

- Web-first focus (responsive design)
- Limited resources (focus on core features)
- PWA option available as interim solution

---

## Contributing to Roadmap

Have ideas? We'd love to hear them!

1. **Check existing issues**: See if already discussed
2. **Create feature request**: Use issue template
3. **Discuss in issue**: Gather feedback from community
4. **Vote with 👍**: Help us prioritize
5. **Submit PR**: Implement if you can!

**Process**:

- Feature requests → Backlog (docs/product/TASKS.md)
- Community vote & discuss
- Maintainers review & prioritize
- Approved features → Roadmap
- Implementation → PR → Release

---

## Resources

- **Tasks Backlog**: [docs/product/TASKS.md](TASKS.md)
- **Changelog**: [/CHANGELOG.md](/CHANGELOG.md)
- **Release Notes**: [docs/product/](.) (RELEASE_NOTES_vX.X.X.md)
- **Contributing**: [/CONTRIBUTING.md](/CONTRIBUTING.md)
- **Architecture**: [docs/architecture/ARCHITECTURE.md](../architecture/ARCHITECTURE.md)
