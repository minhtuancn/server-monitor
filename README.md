# 🖥️ Server Monitor Dashboard v2.3

**Multi-server monitoring system with modern Next.js 16 frontend, real-time updates, web terminal, webhooks, and advanced security**

[![Status](https://img.shields.io/badge/status-production--ready-brightgreen)]()
[![Version](https://img.shields.io/badge/version-2.3.1-blue)](https://github.com/minhtuancn/server-monitor/releases)
[![Frontend](https://img.shields.io/badge/frontend-Next.js%2016-black)]()
[![API](https://img.shields.io/badge/API-OpenAPI%203.0-brightgreen)]()
[![Tests](https://img.shields.io/badge/tests-passing-green)]()
[![Security](https://img.shields.io/badge/security-hardened-green)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 🚀 Quick Start

### Local Development (5 minutes)
```bash
# Clone repository
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor

# Start all services
./start-dev.sh

# Access dashboard
open http://localhost:9081
```

**First-run setup**: Create admin account at `/setup` page.

### Production Deployment (1 command)
```bash
# One-command installation (Ubuntu/Debian)
./installer.sh

# Or with custom domain
CUSTOM_DOMAIN=mon.go7s.net ./start-all.sh
```

---

## ✨ Features

- 🚀 **Modern Stack**: Next.js 16 + TypeScript + React 19 + MUI v5
- 🌐 **Multi-Server**: Manage multiple servers from one dashboard
- 📊 **Real-time**: WebSocket updates every 3 seconds
- 🖥️ **Web Terminal**: SSH emulator in browser (xterm.js)
- 🔐 **Secure**: JWT auth, RBAC, HTTPS, encrypted SSH keys
- 🔔 **Alerts**: Email, Telegram, Slack, Webhooks with HMAC
- 🌍 **i18n**: 8 languages supported
- 📦 **Plugins**: Extensible event-driven architecture
- 🧪 **Tested**: 23 automated tests, CI/CD ready

---

## 📚 Documentation

### Getting Started
- [Quick Start Guide](docs/getting-started/QUICK_START.md) — Detailed setup instructions
- [Custom Domain Setup](CUSTOM-DOMAIN-GUIDE.md) — Deploy to mon.go7s.net or any domain
- [HTTPS Setup](HTTPS-SETUP.md) — SSL/TLS certificates
- [Troubleshooting](docs/getting-started/TROUBLESHOOTING.md) — Common issues

### For Developers
- **[AGENTS.md](AGENTS.md)** — **AI agents start here!** Workflow rules & best practices
- [Contributing](CONTRIBUTING.md) — How to contribute
- [Architecture](ARCHITECTURE.md) — System design
- [API Reference](http://localhost:9083/docs) — Swagger UI (when running)
- [Testing](TEST_GUIDE.md) — Running tests

### Operations
- [Deployment Guide](DEPLOYMENT.md) — Production deployment
- [Security Guide](SECURITY.md) — Security best practices
- [Backup & Restore](docs/operations/BACKUP_RESTORE.md) — Database backups
- [Upgrade Guide](UPGRADE_GUIDE.md) — Version upgrades

### Planning
- [Roadmap](docs/product/ROADMAP.md) — Version-based roadmap (v2.4-v3.1)
- [Tasks](docs/product/TASKS.md) — Task backlog (Now/Next/Later)
- [Changelog](CHANGELOG.md) — Release history

### Complete Index
- **[docs/README.md](docs/README.md)** — **Complete documentation index**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Next.js 16 Frontend (Port 9081)                        │
│  • App Router + TypeScript + MUI                       │
│  • Real-time dashboard + Web terminal                  │
└──────────────┬──────────────────────────────────────────┘
               │ HTTP/WebSocket
┌──────────────▼──────────────────────────────────────────┐
│ Python Backend (FastAPI)                                │
│  • Central API (9083) • WebSocket (9085)               │
│  • Terminal (9084)     • SQLite/PostgreSQL             │
└──────────────┬──────────────────────────────────────────┘
               │ SSH
┌──────────────▼──────────────────────────────────────────┐
│ Remote Servers (Agents)                                 │
│  • Collect metrics via SSH                             │
│  • Execute commands                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Use Cases

- **DevOps**: Monitor infrastructure from single dashboard
- **SysAdmins**: Remote troubleshooting via web terminal
- **Teams**: Multi-tenant server management
- **MSPs**: Monitor client servers with custom branding
- **Compliance**: Audit logs for all actions

---

## 🔒 Security

- JWT authentication with HttpOnly cookies
- Role-based access control (RBAC)
- AES-256-GCM encrypted SSH key vault
- Rate limiting & CORS protection
- CSRF protection
- Input validation & sanitization
- HTTPS/TLS support
- Webhook HMAC signing
- SSRF protection

See [SECURITY.md](SECURITY.md) for details.

---

## 🤝 Contributing

We welcome contributions! Please read:

1. **[AGENTS.md](AGENTS.md)** — Workflow rules (required for AI agents)
2. **[CONTRIBUTING.md](CONTRIBUTING.md)** — Contribution guidelines
3. **[docs/product/TASKS.md](docs/product/TASKS.md)** — Available tasks
4. **[docs/templates/](docs/templates/)** — PR/issue templates

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **Documentation**: [docs/README.md](docs/README.md)
- **API Docs**: [http://localhost:9083/docs](http://localhost:9083/docs) (Swagger UI)
- **GitHub**: [github.com/minhtuancn/server-monitor](https://github.com/minhtuancn/server-monitor)
- **Issues**: [github.com/minhtuancn/server-monitor/issues](https://github.com/minhtuancn/server-monitor/issues)

---

## 🎉 What's New in v2.3.1

- **First-Run Setup**: Guided admin account creation on fresh install
- **Custom Domain**: Deploy to any domain (e.g., mon.go7s.net) with full CORS support
- **Plugin System**: Event-driven extensible architecture
- **Webhooks**: Managed webhooks with HMAC signing & SSRF protection
- **Enhanced Security**: Rate limiting, encrypted SSH keys, audit logs
- **i18n**: 8 languages supported

See [CHANGELOG.md](CHANGELOG.md) for full release history.

---

**Made with ❤️ by the Server Monitor team**
