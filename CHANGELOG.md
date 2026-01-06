# Changelog - Server Monitor Dashboard

All notable changes to this project will be documented in this file.

---

## [v2.0] - 2026-01-06 (PRODUCTION)

### ✅ Added (14 Features)
- Network Monitoring with bandwidth charts
- Historical Charts (30 minutes, 4 metrics)
- Alert System with browser notifications
- Disk I/O Statistics
- Docker Container Management
- Quick Actions Panel
- System Logs Viewer (4 log files)
- Security Dashboard (SSH, firewall, sessions)
- Service Status & Control
- Advanced Process Manager
- Scheduled Tasks Viewer (cron jobs)
- Hardware Information (CPU, temp)
- Mobile Responsive Design
- Quick Stats Widgets

### 🔧 Technical
- Backend: Python 3 (22KB, 635 lines)
- Frontend: Single HTML file (58KB)
- Database: In-memory (Python deque, 360 points)
- Services: 2 systemd services
- Ports: API 8083, Web 8081
- RAM Usage: ~32MB total

### 🐛 Fixed
- CORS issue (API_URL changed to IP instead of localhost)
- Chart initialization (added 10s warmup)
- Process kill confirmation modal

### 📝 Documentation
- DASHBOARD_V2_GUIDE.md
- DASHBOARD_V2_SUMMARY.txt
- WATCHDOG_EXPLAINED.md
- README.md (English)
- HUONG_DAN.txt (Vietnamese)

---

## [v2.1-dev] - 2026-01-06 (DEVELOPMENT)

### 🎯 Planned Features

#### High Priority:
- [ ] SQLite database for persistent history
- [ ] Authentication system (login/logout)
- [ ] Export data to CSV/JSON/Excel
- [ ] Email alerts configuration
- [ ] WebSocket for real-time updates

#### Medium Priority:
- [ ] Custom metrics/widgets
- [ ] Dark/Light theme toggle
- [ ] Advanced filtering & search
- [ ] Scheduled reports
- [ ] API rate limiting

#### Low Priority:
- [ ] Web terminal emulator (xterm.js)
- [ ] Multi-server monitoring
- [ ] Plugin system
- [ ] Swagger API documentation

### 🚧 In Development
- Development environment setup (/opt/server-monitor-dev/)
- Test framework structure
- Dev ports configuration (9081, 9083)

---

## [v1.0] - 2026-01-05

### Initial Release
- Basic CPU/RAM monitoring
- Process list
- Simple HTML interface (20KB)
- No charts, no Docker, no security features

---

## Version History

| Version | Date | Status | Features | Size |
|---------|------|--------|----------|------|
| v1.0 | 2026-01-05 | Deprecated | 3 | 20KB |
| v2.0 | 2026-01-06 | **Production** | 14 | 58KB |
| v2.1-dev | 2026-01-06 | Development | TBD | TBD |

---

## Breaking Changes

### v2.0 (from v1.0)
- Complete rewrite
- API structure changed
- New port numbers
- In-memory database (no persistence from v1.0)

### v2.1-dev (from v2.0)
- Will add database (breaking change in data structure)
- Authentication required (breaking change in API access)
- WebSocket replaces polling (breaking change in frontend)

---

## Migration Guide

### From v1.0 to v2.0
1. Backup v1.0: `cp /var/www/html/index.html /var/www/html/index-v1.html`
2. Stop old services (if any)
3. Deploy v2.0 files
4. Start new services
5. Update bookmarks to new URL

### From v2.0 to v2.1 (Future)
1. Export data if needed (no persistence in v2.0)
2. Create database: `python3 migrate.py`
3. Update config files
4. Restart services
5. Login with default credentials

---

## Development Notes

### v2.0 Production
- Location: `/root/`, `/var/www/html/`
- Backup: Available (full backup created)
- Stable: Yes
- Support: Active

### v2.1 Development
- Location: `/opt/server-monitor-dev/`
- Ports: 9081, 9083 (dev), 9091, 9093 (test)
- Status: Active development
- ETA: TBD

---

## Contributors

- OpenCode AI Assistant (Initial development)
- (Add your name here when contributing)

---

## License

MIT License (or specify your license)

---

**Last Updated**: 2026-01-06
