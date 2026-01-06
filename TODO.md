# TODO List - Server Monitor Dashboard Development

**Last Updated**: 2026-01-06

---

## 🔥 High Priority (v2.1 Release)

### 1. Database Persistence ⭐⭐⭐
- [ ] Setup SQLite database schema
- [ ] Create migration script
- [ ] Convert deque to database writes
- [ ] Add database read queries
- [ ] Test with 7 days of data
- [ ] Add cleanup job (auto-delete old data)
- [ ] Update API endpoints to use database
- [ ] Performance testing
- **Estimated Time**: 8-10 hours
- **Files**: `backend/database.py`, `backend/migrations/`

### 2. Authentication System ⭐⭐⭐
- [ ] Design login page UI
- [ ] Create user table in database
- [ ] Implement password hashing (bcrypt)
- [ ] Add JWT token generation
- [ ] Add login endpoint `/api/auth/login`
- [ ] Add logout endpoint `/api/auth/logout`
- [ ] Protect API endpoints (middleware)
- [ ] Add session management
- [ ] Create default admin user
- [ ] Add "Remember Me" option
- **Estimated Time**: 10-12 hours
- **Files**: `backend/auth.py`, `frontend/login.html`

### 3. Export Data Feature ⭐⭐
- [ ] Add export button to UI
- [ ] Implement CSV export
- [ ] Implement JSON export
- [ ] Implement Excel export (openpyxl)
- [ ] Add date range selector
- [ ] Add metric selector (CPU, RAM, etc.)
- [ ] Endpoint: `/api/export?format=csv&from=...&to=...`
- [ ] Add download with filename
- **Estimated Time**: 6-8 hours
- **Files**: `backend/export.py`, `frontend/dashboard.html`

---

## ⚠️ Medium Priority (v2.2 Release)

### 4. Email Alerts ⭐⭐
- [ ] Design alert configuration UI
- [ ] Add SMTP settings form
- [ ] Create email templates
- [ ] Implement email sending (smtplib)
- [ ] Add threshold configuration
- [ ] Add alert rules (CPU > 90% for 5 min, etc.)
- [ ] Add email queue system
- [ ] Add alert history log
- [ ] Test with Gmail, Outlook
- **Estimated Time**: 8-10 hours
- **Files**: `backend/alerts.py`, `backend/email.py`

### 5. WebSocket Real-time Updates ⭐⭐
- [ ] Research Python WebSocket library (websockets/aiohttp)
- [ ] Implement WebSocket server
- [ ] Update frontend to use WebSocket
- [ ] Add reconnection logic
- [ ] Add fallback to polling
- [ ] Add connection status indicator
- [ ] Performance testing
- **Estimated Time**: 12-15 hours
- **Files**: `backend/websocket.py`, `frontend/dashboard.html`

### 6. Custom Metrics ⭐
- [ ] Design custom metric input form
- [ ] Add custom metric storage
- [ ] Support script-based metrics
- [ ] Support API endpoint metrics
- [ ] Add custom charts
- [ ] Add metric templates
- **Estimated Time**: 10-12 hours
- **Files**: `backend/custom_metrics.py`

---

## 💡 Low Priority (v3.0 Release)

### 7. Web Terminal Emulator
- [ ] Install xterm.js
- [ ] Setup node-pty backend
- [ ] Create terminal page
- [ ] Add authentication check
- [ ] Add terminal session management
- [ ] Add multiple terminal tabs
- [ ] Security hardening
- **Estimated Time**: 15-20 hours
- **Dependencies**: Node.js, xterm.js, node-pty

### 8. Multi-server Monitoring
- [ ] Design agent architecture
- [ ] Create agent script
- [ ] Add server management UI
- [ ] Add server list page
- [ ] Add overview dashboard
- [ ] Add agent-server communication
- [ ] Add server health checks
- **Estimated Time**: 20-25 hours
- **Files**: New agent architecture

### 9. Plugin System
- [ ] Design plugin API
- [ ] Create plugin loader
- [ ] Add plugin directory structure
- [ ] Create example plugins
- [ ] Add plugin management UI
- [ ] Add plugin marketplace (future)
- **Estimated Time**: 15-20 hours
- **Files**: `backend/plugins/`

---

## 🐛 Bug Fixes & Improvements

### Known Issues:
- [ ] Charts show "0" on first load (need 2+ data points)
- [ ] Docker tab empty if Docker not installed (add better message)
- [ ] Network speed calculation incorrect on first run
- [ ] Process kill requires confirmation every time (add "Don't ask again")
- [ ] Mobile view: Service control buttons too small
- [ ] Alert notifications don't persist across page refresh

### Performance Improvements:
- [ ] Add caching for API responses
- [ ] Lazy load log viewer (only when tab clicked)
- [ ] Optimize chart rendering (use requestAnimationFrame)
- [ ] Add service worker for offline mode
- [ ] Minify JavaScript code
- [ ] Compress API responses (gzip)

### UI/UX Improvements:
- [ ] Add loading spinners
- [ ] Add empty state messages
- [ ] Add error state messages
- [ ] Improve mobile navigation
- [ ] Add keyboard shortcuts
- [ ] Add tooltips for icons
- [ ] Add "Copy to clipboard" for commands
- [ ] Dark/Light theme toggle

---

## 🔒 Security Tasks

- [ ] Add HTTPS support (SSL/TLS)
- [ ] Change CORS from `*` to specific origin
- [ ] Add rate limiting to API endpoints
- [ ] Add input sanitization
- [ ] Add CSRF protection
- [ ] Add SQL injection prevention (use parameterized queries)
- [ ] Add XSS prevention (escape HTML)
- [ ] Add security headers (CSP, X-Frame-Options, etc.)
- [ ] Add brute force protection for login
- [ ] Add API key authentication option
- [ ] Regular security audit

---

## 📝 Documentation Tasks

- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Add development setup guide
- [ ] Add contribution guidelines
- [ ] Add code style guide
- [ ] Add architecture diagram
- [ ] Add deployment guide
- [ ] Add troubleshooting guide
- [ ] Add FAQ
- [ ] Add video tutorial
- [ ] Add blog post/announcement

---

## 🧪 Testing Tasks

### Unit Tests:
- [ ] Test API endpoints
- [ ] Test database operations
- [ ] Test authentication
- [ ] Test export functions
- [ ] Test alert system

### Integration Tests:
- [ ] Test full user flow
- [ ] Test browser compatibility
- [ ] Test mobile devices
- [ ] Test different screen sizes
- [ ] Test with different data volumes

### Performance Tests:
- [ ] Load testing (100+ concurrent users)
- [ ] Stress testing (1000+ requests/sec)
- [ ] Memory leak testing
- [ ] Database performance testing

---

## 🚀 Deployment Tasks

- [ ] Create production deployment script
- [ ] Setup CI/CD pipeline
- [ ] Create Docker container
- [ ] Create docker-compose.yml
- [ ] Add automated backups
- [ ] Add health checks
- [ ] Add monitoring/alerting for dashboard itself
- [ ] Create rollback procedure

---

## 📦 Dependencies to Add

### Python (Backend):
- [ ] `sqlite3` (built-in) - Database
- [ ] `bcrypt` - Password hashing
- [ ] `PyJWT` - JWT tokens
- [ ] `openpyxl` - Excel export
- [ ] `websockets` - WebSocket server
- [ ] `pytest` - Testing
- [ ] `black` - Code formatting
- [ ] `flake8` - Linting

### JavaScript (Frontend):
- [ ] None yet (pure vanilla JS)
- [ ] Maybe: `xterm.js` for terminal (if implemented)

---

## 🎯 Milestones

### Milestone 1: v2.1 - Persistence & Auth (ETA: 2 weeks)
- ✅ Development environment setup
- ⏳ Database persistence
- ⏳ Authentication system
- ⏳ Export data feature
- ⏳ Testing & bug fixes
- ⏳ Documentation update

### Milestone 2: v2.2 - Real-time & Alerts (ETA: 3 weeks)
- ⏳ Email alerts
- ⏳ WebSocket updates
- ⏳ Custom metrics
- ⏳ UI/UX improvements

### Milestone 3: v3.0 - Advanced Features (ETA: 6 weeks)
- ⏳ Web terminal
- ⏳ Multi-server monitoring
- ⏳ Plugin system
- ⏳ Security hardening

---

## 🤝 Contribution Guidelines

If you want to contribute:

1. Pick a task from this TODO list
2. Create a branch: `git checkout -b feature/task-name`
3. Make changes in `/opt/server-monitor-dev/`
4. Test thoroughly on dev ports (9081, 9083)
5. Update CHANGELOG.md
6. Commit: `git commit -m "Add: feature description"`
7. Test on production backup before deploying
8. Deploy to production only after approval

---

## 📊 Progress Tracking

- **Total Tasks**: ~80+ tasks
- **Completed**: 0 (fresh start)
- **In Progress**: 0
- **Blocked**: 0

**Legend:**
- ✅ Completed
- ⏳ In Progress
- ❌ Blocked
- 💀 Cancelled
- 🔥 Urgent

---

**Note**: This is a living document. Update as tasks are completed or priorities change.

**Last Review**: 2026-01-06
