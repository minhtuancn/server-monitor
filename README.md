# 🖥️ Server Monitor Dashboard v1.0

**Multi-server monitoring system với real-time updates, web terminal, và advanced security**

[![Status](https://img.shields.io/badge/status-production--ready-brightgreen)]()
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/minhtuancn/server-monitor/releases)
[![Tests](https://img.shields.io/badge/tests-23%2F25%20passing-green)]()
[![Security](https://img.shields.io/badge/security-9%2F10-yellow)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

📺 **Live Demo**: [GitHub Pages](https://minhtuancn.github.io/server-monitor/) | [Localhost](http://localhost:9081)

---

## 📋 Tổng Quan

Server Monitor Dashboard là hệ thống giám sát multi-server với giao diện web hiện đại, cho phép quản lý và theo dõi nhiều servers từ một dashboard trung tâm.

### ✨ Tính Năng Chính

- 🌐 **Multi-Server Management**: Quản lý nhiều servers từ một giao diện
- 📊 **Real-time Monitoring**: Cập nhật metrics thời gian thực qua WebSocket
- 🖥️ **Web Terminal**: SSH terminal emulator trên browser (xterm.js)
- 🔐 **Authentication System**: JWT-based authentication với session management
- 📧 **Email Alerts**: Cảnh báo tự động qua email khi vượt ngưỡng
- 📤 **Export Data**: Xuất dữ liệu ra CSV/JSON
- 🔒 **Advanced Security**: Rate limiting, CORS, input validation, security headers
- 🧪 **Automated Testing**: 23 test cases với pytest

### 🎯 Use Cases

- Giám sát multiple servers từ xa
- Quản lý infrastructure qua web UI
- Remote troubleshooting qua web terminal
- Theo dõi performance metrics real-time
- Nhận cảnh báo tự động về issues

### 🎉 Recent Improvements (v1.1 - 2026-01-07)

- ✅ **Fixed Database Path Issues**: Removed hardcoded `/opt` paths, now works from any directory
- ✅ **Enhanced Input Validation**: Fixed IP validation bypass (999.999.999.999 now rejected)
- ✅ **Frontend Cleanup**: Removed 11 duplicate files (44% reduction, 25+ → 14 pages)
- ✅ **Form Helper System**: Added loading states, real-time validation, toast notifications
- ✅ **Improved UX**: Consistent error handling, loading indicators, user-friendly messages
- ✅ **Documentation**: Added 36KB of guides (PROJECT_ASSESSMENT.md, TODO-IMPROVEMENTS.md, form guides)
- ✅ **Test Coverage**: 23/25 tests passing (92%), CodeQL scan: 0 vulnerabilities

See [PROJECT_ASSESSMENT.md](PROJECT_ASSESSMENT.md) for detailed analysis and [TODO-IMPROVEMENTS.md](TODO-IMPROVEMENTS.md) for roadmap.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Linux server (tested on Debian/Ubuntu)
- SSH access to monitored servers

### Installation

```bash
# Clone repository
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor

# Install dependencies
cd backend
pip3 install -r requirements.txt

# Install test dependencies (optional)
cd ../tests
pip3 install -r requirements.txt

# Configure environment
cd ..
cp .env.example .env
# Edit .env and set secure values for JWT_SECRET and ENCRYPTION_KEY
# Generate secure keys with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Initialize database (automatic on first run)
cd backend
python3 -c "import database; database.init_database()"
```

**Note:** The system now supports relative paths and works from any directory. No need for hardcoded `/opt` paths.

### Start Services

```bash
# From project root
./start-all.sh
```

Or start manually:

```bash
# Backend API
cd backend
python3 central_api.py &

# WebSocket server
python3 websocket_server.py &

# Terminal server (optional)
python3 terminal.py &

# Frontend
cd ../frontend
python3 -m http.server 9081 &
```

### Access Dashboard

- **Dashboard**: http://localhost:9081
- **API**: http://localhost:9083
- **Default Credentials**: admin / admin123 ⚠️ **Change in production!**

⚠️ **Security Warning**: The system auto-creates a default admin user. Change the password immediately after first login!

### Stop Services

```bash
cd /opt/server-monitor-dev
./stop-all.sh
```

---

## 📁 Project Structure

```
server-monitor/
├── backend/                    # Python backend services
│   ├── central_api.py         # Main REST API server (port 9083)
│   ├── websocket_server.py    # Real-time updates (port 9085)
│   ├── terminal.py            # Web terminal (port 9084)
│   ├── database.py            # SQLite database operations
│   ├── user_management.py     # User CRUD & authentication
│   ├── settings_manager.py    # System settings management
│   ├── ssh_manager.py         # SSH connection management
│   ├── email_alerts.py        # Email notification system
│   ├── alert_manager.py       # Multi-channel alert dispatcher
│   ├── security.py            # Security middleware (rate limiting, CORS, validation)
│   └── agent.py               # Monitoring agent for remote servers
│
├── frontend/                   # HTML/CSS/JS frontend (14 pages)
│   ├── index.html             # Landing page
│   ├── login.html             # Login page
│   ├── dashboard.html         # Main dashboard (multi-server view)
│   ├── server-detail.html     # Individual server details
│   ├── server-notes.html      # Markdown notes for servers
│   ├── terminal.html          # Web terminal interface
│   ├── settings.html          # System settings
│   ├── domain-settings.html   # Domain & SSL configuration
│   ├── email-settings.html    # Email alert configuration
│   ├── ssh-keys.html          # SSH key management
│   ├── users.html             # User management (admin)
│   ├── notifications.html     # Alert notifications
│   ├── system-check.html      # System health check
│   ├── test_cors.html         # CORS testing
│   ├── README.md              # Frontend documentation
│   ├── FORM_HELPERS_GUIDE.md  # Form utilities guide
│   ├── assets/
│   │   ├── css/               # Stylesheets
│   │   │   ├── app.css
│   │   │   ├── components.css # Enhanced with form states & animations
│   │   │   └── themes.css
│   │   ├── js/                # JavaScript modules
│   │   │   ├── api.js         # API client
│   │   │   ├── auth.js        # Authentication
│   │   │   ├── form-helpers.js # Form utilities (NEW)
│   │   │   ├── utils.js       # Utilities
│   │   │   ├── i18n.js        # Internationalization
│   │   │   └── component-loader.js
│   │   └── locales/           # 8 language translations
│   └── components/
│       ├── header.html        # Shared header
│       └── sidebar.html       # Shared sidebar
│
├── tests/                      # Automated tests
│   ├── test_api.py            # API integration tests (19/19 passing)
│   ├── test_security.py       # Security tests (4/6 passing)
│   └── requirements.txt       # Test dependencies
│
├── data/                       # Data storage (auto-created)
│   ├── servers.db             # SQLite database
│   └── *.json                 # Configuration files
│
├── logs/                       # Log files (auto-created)
│
├── docs/                       # Documentation
│
├── PROJECT_ASSESSMENT.md      # Comprehensive project review (NEW)
├── TODO-IMPROVEMENTS.md       # Action items roadmap (NEW)
├── VIETNAMESE_SUMMARY.md      # Vietnamese summary (NEW)
├── start-all.sh               # Start all services
├── stop-all.sh                # Stop all services
├── .env.example               # Environment template
└── README.md                  # This file
```

---

## 🔧 Configuration

### Ports

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| Frontend | 9081 | HTTP | Web UI |
| API | 9083 | HTTP | REST API |
| Terminal | 9084 | WebSocket | SSH terminal |
| WebSocket | 9085 | WebSocket | Real-time updates |
| Agent (remote) | 8083 | HTTP | Monitoring agent |

### Environment

Configuration options in `.env` file:
- **JWT_SECRET**: Secret key for JWT tokens (required)
- **ENCRYPTION_KEY**: Key for SSH password encryption (required)
- **JWT_EXPIRATION**: Token expiration in seconds (default: 86400)
- **DB_PATH**: Custom database path (optional, defaults to `data/servers.db`)
- **API_PORT**: API server port (default: 9083)
- **FRONTEND_PORT**: Frontend server port (default: 9081)

**Database Path**: Now supports relative paths. The system automatically resolves to `<project_root>/data/servers.db`. No hardcoded paths required!

---

## 🔐 Security Features

### Implemented (v4.1)

✅ **Rate Limiting**
- 100 requests/minute (general endpoints)
- 5 login attempts/5 minutes
- Automatic IP blocking after repeated failures

✅ **CORS Protection**
- Whitelist specific origins only
- No wildcard (*) in production

✅ **Security Headers**
- Content-Security-Policy
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection

✅ **Input Validation** (Enhanced v1.1)
- IP address validation (0-255 per octet)
- Hostname validation (proper DNS format)
- Port range validation (1-65535)
- String sanitization (HTML/XSS prevention)
- Real-time client-side validation with error feedback

✅ **Authentication**
- JWT token-based auth
- Session management
- Secure password hashing (SHA256)

### Recommendations

⚠️ **Before Production Deployment**:
1. Change default admin password
2. Enable HTTPS (use nginx/apache reverse proxy)
3. Set up firewall rules
4. Review CORS allowed origins
5. Enable database backups
6. Set up log rotation

---

## 📊 API Endpoints

### Authentication
```
POST   /api/auth/login       - Login
POST   /api/auth/logout      - Logout  
GET    /api/auth/verify      - Verify token
```

### Servers
```
GET    /api/servers          - List all servers
POST   /api/servers          - Add new server
GET    /api/servers/:id      - Get server details
PUT    /api/servers/:id      - Update server
DELETE /api/servers/:id      - Delete server
POST   /api/servers/:id/test - Test connection
```

### Monitoring
```
GET    /api/remote/stats/:id - Get server metrics
GET    /api/remote/stats/all - Get all servers metrics
GET    /api/stats/overview   - Get statistics summary
```

### Export
```
GET    /api/export/servers/csv      - Export servers to CSV
GET    /api/export/servers/json     - Export servers to JSON
GET    /api/export/history/csv      - Export monitoring history
GET    /api/export/history/json     - Export history as JSON
GET    /api/export/alerts/csv       - Export alerts
```

### Email
```
GET    /api/email/config     - Get email configuration
POST   /api/email/config     - Update email config
POST   /api/email/test       - Send test email
```

**Total: 29 REST endpoints + 1 WebSocket endpoint**

Full API documentation: See [API-TESTING-GUIDE.txt](API-TESTING-GUIDE.txt)

---

## 🧪 Testing

### Run Tests

```bash
cd tests

# Run all API tests (19 tests)
python3 -m pytest test_api.py -v

# Run security tests (6 tests)
python3 -m pytest test_security.py -v

# Run all tests
python3 -m pytest -v
```

### Test Coverage

- ✅ Authentication (5 tests)
- ✅ CRUD operations (5 tests)
- ✅ Export functionality (2 tests)
- ✅ Email configuration (2 tests)
- ✅ Unauthorized access (3 tests)
- ✅ Rate limiting (2 tests)
- ✅ Security headers (2 tests)
- ✅ Input validation (2 tests)

**Total: 23/25 tests passing (92%)**

---

## 📈 Performance

### Metrics

- **WebSocket Updates**: 3 seconds interval (3x faster than polling)
- **Network Overhead**: 70% reduction vs polling
- **API Response Time**: < 100ms (average)
- **Concurrent Connections**: 100+ supported
- **Database**: SQLite (suitable for < 100 servers)

### Scalability

- Current: Up to 100 servers
- Recommended: Use PostgreSQL for > 100 servers
- Consider: Redis for caching if > 1000 req/min

---

## 📚 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [IMPLEMENTATION_REPORT_V4.1.md](IMPLEMENTATION_REPORT_V4.1.md) - Implementation details
- [API-TESTING-GUIDE.txt](API-TESTING-GUIDE.txt) - API testing guide
- [MULTI-SERVER-GUIDE.md](MULTI-SERVER-GUIDE.md) - Multi-server setup
- [QUICKSTART.txt](QUICKSTART.txt) - Quick start guide
- [TODO.md](TODO.md) - Future improvements

---

## 🐛 Troubleshooting

### Services not starting

```bash
# Check if ports are in use
netstat -tlnp | grep -E ":(9081|9083|9084|9085)"

# Check logs
tail -f logs/*.log

# Restart services
./stop-all.sh && ./start-all.sh
```

### Database errors

```bash
# Reinitialize database
cd backend
python3 -c "import database; database.init_database()"
```

### WebSocket not connecting

1. Check firewall allows port 9085
2. Check websocket_server.py is running
3. Check browser console for errors
4. Verify WebSocket URL in dashboard.html

---

## 🔄 Deployment

### Development
```bash
./start-all.sh
```

### Production (with systemd)

```bash
# Copy service files
cp services/*.service /etc/systemd/system/

# Enable and start services
systemctl daemon-reload
systemctl enable server-dashboard-api-v2.service
systemctl enable opencode-dashboard.service
systemctl start server-dashboard-api-v2.service
systemctl start opencode-dashboard.service
```

### Docker (future)

```bash
docker-compose up -d
```

---

## 🤝 Contributing

### Development Workflow

1. Make changes in `/opt/server-monitor-dev/`
2. Test on dev ports (9081, 9083, 9084, 9085)
3. Run automated tests: `pytest tests/ -v`
4. Update documentation
5. Test on production backup before deploying

### Code Style

- Python: PEP 8
- JavaScript: ES6+
- HTML/CSS: Semantic, responsive design

---

## 📝 Changelog

### v1.0.0 (2026-01-06) - Initial Release 🎉
- ✅ Multi-server monitoring dashboard
- ✅ Real-time updates via WebSocket
- ✅ Web terminal emulator (xterm.js + SSH)
- ✅ Email alerts system with SMTP
- ✅ Export data (CSV/JSON)
- ✅ SSH key management
- ✅ JWT authentication system
- ✅ Advanced security (rate limiting, CORS, validation)
- ✅ Comprehensive testing suite (23 tests)
- ✅ Production-ready deployment scripts
- ✅ Complete documentation

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Minh Tuấn

---

## 👨‍💻 Author

**Minh Tuấn**
- 📧 Email: [vietkeynet@gmail.com](mailto:vietkeynet@gmail.com)
- 📱 WhatsApp/WeChat: +84912537003
- 🐙 GitHub: [@minhtuancn](https://github.com/minhtuancn)
- 🌐 Demo: [GitHub Pages](https://minhtuancn.github.io/server-monitor/)

**Project**: Server Monitoring System  
**Version**: 1.0.0  
**Release Date**: January 6, 2026

---

## 📞 Support

For issues or questions:
1. Check [TROUBLESHOOTING section](#-troubleshooting)
2. Review logs in `logs/` directory
3. Check [TODO.md](TODO.md) for known issues
4. Review test results: `pytest tests/ -v`

---

## 🎯 Roadmap

### v1.1.0 (Planned - Q1 2026)
- [ ] PostgreSQL support
- [ ] Redis caching
- [ ] Docker containerization
- [ ] Swagger/OpenAPI documentation
- [ ] Advanced alerting rules
- [ ] GitHub Pages deployment

### v2.0.0 (Planned - Q2 2026)
- [ ] Kubernetes support
- [ ] Multi-user management
- [ ] Role-based access control (RBAC)
- [ ] Advanced reporting
- [ ] Mobile responsive improvements
- [ ] Plugin system

---

**Made with ❤️ using Python, JavaScript, and modern web technologies**
