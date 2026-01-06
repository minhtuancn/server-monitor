# Server Monitor Dashboard - Development Version

**Thư mục phát triển**: `/opt/server-monitor-dev/`  
**Ngày tạo**: 06/01/2026  
**Version**: v2.1-dev (dựa trên v2.0 production)

---

## 🎯 Mục Đích

Thư mục này dùng để **phát triển tính năng mới** cho Server Monitor Dashboard, **tách biệt** với production code.

### Production (đang chạy):
- Backend: `/root/server_dashboard_api_v2.py`
- Frontend: `/var/www/html/index.html`
- Services: Running on ports 8081, 8083

### Development (thư mục này):
- Backend: `/opt/server-monitor-dev/backend/`
- Frontend: `/opt/server-monitor-dev/frontend/`
- Services: Sẽ chạy trên ports khác (9081, 9083)

---

## 📁 Cấu Trúc Thư Mục

```
/opt/server-monitor-dev/
├── backend/
│   ├── server_dashboard_api_v2.py    # API backend
│   └── status_webserver.py           # Web server
│
├── frontend/
│   ├── dashboard.html                # Dashboard v2 hiện tại
│   ├── dashboard-v2.html             # Backup
│   └── dashboard-v1.html             # Old version
│
├── services/
│   ├── server-dashboard-api-v2.service
│   └── opencode-dashboard.service
│
├── tests/
│   └── (chưa có test files)
│
├── docs/
│   └── (documentation cho dev)
│
└── README-DEV.md                      # File này
```

---

## 🚀 Chạy Development Server

### Cách 1: Chạy Trực Tiếp (Dev Mode)

**Backend API (port 9083):**
```bash
cd /opt/server-monitor-dev/backend/
# Sửa PORT trong file
sed -i 's/PORT = 8083/PORT = 9083/' server_dashboard_api_v2.py
# Chạy
python3 server_dashboard_api_v2.py
```

**Frontend (port 9081):**
```bash
cd /opt/server-monitor-dev/frontend/
# Chạy web server
python3 -m http.server 9081
```

### Cách 2: Tạo Dev Services

```bash
# Tạo service files mới cho dev
cp /opt/server-monitor-dev/services/server-dashboard-api-v2.service \
   /etc/systemd/system/server-dashboard-api-dev.service

cp /opt/server-monitor-dev/services/opencode-dashboard.service \
   /etc/systemd/system/opencode-dashboard-dev.service

# Sửa service files (đổi port, working directory)
# ... (xem hướng dẫn bên dưới)

# Enable và start
systemctl daemon-reload
systemctl enable server-dashboard-api-dev.service
systemctl start server-dashboard-api-dev.service
```

---

## 🛠️ Phát Triển Tính Năng Mới

### Tính Năng Có Thể Thêm:

#### 1. **Web Terminal Emulator** (Feature #15)
- Thư viện: xterm.js + node-pty
- File: `frontend/terminal.html`
- Endpoint: `/api/terminal/create`, `/api/terminal/send`

#### 2. **Authentication System**
- Login form
- JWT tokens
- Session management
- API key authentication

#### 3. **Database Persistence**
- SQLite hoặc PostgreSQL
- Lưu lịch sử dài hạn (7 ngày, 30 ngày)
- Query historical data

#### 4. **Real-time WebSocket**
- Thay vì polling 5s
- Push updates từ server
- Giảm network traffic

#### 5. **Email/Webhook Alerts**
- Gửi email khi CPU/RAM cao
- Webhook notifications
- Slack/Discord integration

#### 6. **Multi-server Monitoring**
- Monitor nhiều servers
- Dashboard tổng hợp
- Agent-based architecture

#### 7. **Custom Dashboards**
- Drag & drop widgets
- Save layout preferences
- Multiple dashboard views

#### 8. **Performance Optimization**
- Caching API responses
- Lazy loading components
- Service worker (offline mode)

#### 9. **Advanced Security**
- 2FA authentication
- Role-based access control (RBAC)
- Audit logging

#### 10. **Export/Import**
- Export data to CSV/JSON/Excel
- Import configuration
- Backup/restore settings

---

## 📝 Workflow Phát Triển

### 1. Tạo Branch/Feature Mới
```bash
# Create feature directory
mkdir -p /opt/server-monitor-dev/features/<feature-name>

# Copy base files
cp /opt/server-monitor-dev/backend/server_dashboard_api_v2.py \
   /opt/server-monitor-dev/features/<feature-name>/
```

### 2. Thay Đổi Code
- Edit files trong `/opt/server-monitor-dev/`
- Test locally trên dev ports (9081, 9083)

### 3. Test
```bash
# Test API
curl http://localhost:9083/api/health

# Test frontend
open http://localhost:9081/dashboard.html
```

### 4. Deploy lên Production
```bash
# Backup production first
cp /root/server_dashboard_api_v2.py /root/server_dashboard_api_v2.py.backup
cp /var/www/html/index.html /var/www/html/index.html.backup

# Copy dev to production
cp /opt/server-monitor-dev/backend/server_dashboard_api_v2.py /root/
cp /opt/server-monitor-dev/frontend/dashboard.html /var/www/html/index.html

# Restart services
systemctl restart server-dashboard-api-v2.service
systemctl restart opencode-dashboard.service
```

---

## 🔧 Cấu Hình Dev Environment

### Đổi Port cho Dev

**Backend (`backend/server_dashboard_api_v2.py`):**
```python
# Line 18: Đổi port
PORT = 9083  # Thay vì 8083
```

**Frontend (`frontend/dashboard.html`):**
```javascript
// Tìm dòng:
const API_URL = 'http://172.22.0.103:8083';

// Đổi thành:
const API_URL = 'http://172.22.0.103:9083';
```

### Tạo Dev Config File

```bash
cat > /opt/server-monitor-dev/dev-config.env << 'EOF'
# Development Configuration
API_PORT=9083
WEB_PORT=9081
API_HOST=0.0.0.0
DEBUG_MODE=true
LOG_LEVEL=debug
DATABASE_URL=sqlite:///dev-database.db
EOF
```

---

## 🧪 Testing

### Unit Tests
```bash
mkdir -p /opt/server-monitor-dev/tests/
cd /opt/server-monitor-dev/tests/

# Create test file
cat > test_api.py << 'EOF'
import unittest
import requests

class TestDashboardAPI(unittest.TestCase):
    BASE_URL = 'http://localhost:9083'
    
    def test_health(self):
        response = requests.get(f'{self.BASE_URL}/api/health')
        self.assertEqual(response.status_code, 200)
    
    def test_system_info(self):
        response = requests.get(f'{self.BASE_URL}/api/system')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('cpu', data)
        self.assertIn('memory', data)

if __name__ == '__main__':
    unittest.main()
EOF

# Run tests
python3 test_api.py
```

---

## 📊 Ý Tưởng Tính Năng Mới

### Priority 1 (Quan Trọng):
1. ✅ **Persistent Database** - Lưu lịch sử dài hạn
2. ✅ **Authentication** - Bảo mật dashboard
3. ✅ **WebSocket** - Real-time updates

### Priority 2 (Hữu Ích):
4. ⚠️ **Email Alerts** - Thông báo qua email
5. ⚠️ **Export Data** - Xuất báo cáo CSV/Excel
6. ⚠️ **Custom Metrics** - Thêm metrics tùy chỉnh

### Priority 3 (Nice to Have):
7. 💡 **Web Terminal** - Terminal trong browser
8. 💡 **Multi-server** - Monitor nhiều servers
9. 💡 **Dark/Light Mode Toggle** - Switch themes
10. 💡 **Plugins System** - Extensible architecture

---

## 🗂️ Git Workflow (Nếu Dùng Git)

```bash
cd /opt/server-monitor-dev/
git init
git add .
git commit -m "Initial dev version based on v2.0"

# Create feature branch
git checkout -b feature/database-persistence

# Make changes...
git add .
git commit -m "Add SQLite database support"

# Merge to main
git checkout main
git merge feature/database-persistence
```

---

## 📞 Development Notes

### Ports:
- **Production**: API 8083, Web 8081
- **Development**: API 9083, Web 9081
- **Testing**: API 9093, Web 9091

### Environment:
- **Production**: systemd services, auto-restart
- **Development**: manual start/stop, debug mode
- **Testing**: unit tests, integration tests

### Database:
- **Production**: In-memory (deque)
- **Development**: SQLite (dev-database.db)
- **Testing**: SQLite (test-database.db, reset after each test)

---

## 🚨 Lưu Ý Quan Trọng

1. **KHÔNG** deploy code chưa test lên production
2. **LUÔN** backup production code trước khi update
3. **KIỂM TRA** ports không conflict
4. **TEST** kỹ trên dev environment trước
5. **GHI CHÚ** thay đổi trong CHANGELOG.md
6. **UPDATE** version number khi release

---

## 📈 Roadmap

### Version 2.1 (Next Release):
- [ ] SQLite database persistence
- [ ] Basic authentication (username/password)
- [ ] Export data to CSV
- [ ] Email alerts

### Version 2.2:
- [ ] WebSocket real-time updates
- [ ] Multi-server monitoring
- [ ] Advanced RBAC

### Version 3.0:
- [ ] Web terminal emulator
- [ ] Plugin system
- [ ] REST API documentation (Swagger)

---

## 🔗 Liên Kết Hữu Ích

- Production Dashboard: http://172.22.0.103:8081/
- Dev Dashboard: http://172.22.0.103:9081/ (khi chạy)
- Production API: http://172.22.0.103:8083/
- Dev API: http://172.22.0.103:9083/ (khi chạy)

---

**Happy Coding! 🚀**

Thư mục này là nơi thử nghiệm an toàn. Hãy tự do thử nghiệm và phá vỡ mọi thứ ở đây!
