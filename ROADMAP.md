# Server Monitor - Roadmap

**⚠️ This document has moved!**

The roadmap is now maintained at: **[docs/product/ROADMAP.md](docs/product/ROADMAP.md)**

Please update your bookmarks.

---

## Quick Links

- **Roadmap (Version-based)**: [docs/product/ROADMAP.md](docs/product/ROADMAP.md)
- **Tasks (Now/Next/Later)**: [docs/product/TASKS.md](docs/product/TASKS.md)
- **Documentation Index**: [docs/README.md](docs/README.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Agent Workflow**: [AGENTS.md](AGENTS.md)

---

The new roadmap includes:

- Clear version-based planning (v2.4, v2.5, v3.0)
- Scope and non-goals for each release
- Acceptance criteria
- Decision log
- Migration guides for breaking changes
- [ ] Audit logging
- [ ] Advanced reporting dashboard
- [ ] Server grouping and tagging improvements

**Integration:**

- [ ] Webhook notifications
- [ ] SSO integration (SAML/OAuth2)
- [ ] API key management
- [ ] External monitoring tool integration

---

## 📊 Feature Priority Matrix

| Feature                 | Priority | Complexity | Status  |
| ----------------------- | -------- | ---------- | ------- |
| Fix security tests      | High     | Low        | Pending |
| Docker support          | High     | Medium     | Pending |
| API documentation       | High     | Medium     | Pending |
| Configurable thresholds | Medium   | Low        | Pending |
| PostgreSQL support      | Medium   | High       | Planned |
| 2FA authentication      | Medium   | Medium     | Planned |
| Prometheus metrics      | Low      | Medium     | Planned |
| Plugin system           | Low      | High       | Future  |

---

## 🔒 Security Roadmap

### Completed ✅

- JWT token authentication
- Password hashing (SHA256 + salt)
- Rate limiting (100 req/min, 5 login/5min)
- CORS with whitelist
- Security headers (CSP, X-Frame-Options, etc.)
- Input validation (IP, hostname, port)
- SQL injection prevention
- XSS prevention

### Planned

- [ ] HTTPS enforcement documentation
- [ ] Session timeout warnings
- [ ] Audit logging for sensitive operations
- [ ] 2FA/MFA support
- [ ] IP whitelist/blacklist
- [ ] API key authentication option

---

## 🧪 Testing Roadmap

### Current Coverage

- Backend API tests: 19/19 (100%)
- Security tests: 4/6 (67%)
- Total: 23/25 (92%)

### Planned

- [ ] WebSocket integration tests
- [ ] SSH terminal tests
- [ ] Email alert tests
- [ ] E2E tests (Playwright)
- [ ] Load/performance tests
- [ ] Accessibility tests

---

## 📝 Documentation Roadmap

### Completed ✅

- README.md - Installation & usage
- ARCHITECTURE.md - System design
- HTTPS-SETUP.md - SSL configuration
- CONTRIBUTING.md - Contribution guide
- TEST_GUIDE.md - Testing instructions
- CHANGELOG.md - Version history

### Planned

- [ ] DEPLOYMENT.md - Production deployment guide
- [ ] API.md - Complete API documentation
- [ ] TROUBLESHOOTING.md - Common issues
- [ ] SECURITY.md - Security best practices

---

## 🚨 Known Issues

1. **Rate limiting interferes with tests** - Sequential tests may hit rate limits
2. **WebSocket reconnection** - Not automatically reconnecting after disconnect
3. **Session timeout** - No warning before token expiration

See [TODO-IMPROVEMENTS.md](TODO-IMPROVEMENTS.md) for detailed action items.

---

## 💡 Future Considerations

These are ideas for future versions, not committed features:

- Mobile application (React Native/Flutter)
- GraphQL API option
- Microservices architecture
- Event sourcing for audit trail
- Machine learning for anomaly detection
- Custom dashboard builder

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Priority areas for contribution:

1. Bug fixes
2. Test coverage improvements
3. Documentation updates
4. Security enhancements
5. Performance optimizations

---

## 📞 Contact

**Minh Tuấn**

- 📧 Email: [vietkeynet@gmail.com](mailto:vietkeynet@gmail.com)
- 🐙 GitHub: [@minhtuancn](https://github.com/minhtuancn)

---

**Last Updated:** 2026-01-07
