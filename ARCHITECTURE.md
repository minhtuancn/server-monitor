# Server Monitor Dashboard v4.0 - Architecture

## 📱 Giao Diện Chính (Main UI Hierarchy)

### Level 0: Public Access
- **index.html** → Auto redirect đến multi-server-dashboard.html
- **login.html** → Trang đăng nhập (bắt buộc)

### Level 1: Authenticated Dashboard (Main Interface)
**🏠 multi-server-dashboard.html** - GIAO DIỆN CHÍNH
- Overview tất cả servers
- Quick actions
- Statistics cards
- Server grid với search/filter
- Navigation menu đầy đủ

### Level 2: Sub Pages (Accessible from Main Dashboard)
1. **server-detail.html?id=X** - Chi tiết 1 server
   - Real-time monitoring
   - Charts (CPU, Memory, Network)
   - Tabs: Overview, Processes, Network, Logs
   - Quick actions

2. **ssh-keys.html** - Quản lý SSH Keys
   - List/Add/Edit/Delete SSH keys
   - Test connection
   - Notes for each key

3. **email-settings.html** - Cấu hình Email Alerts
   - SMTP settings
   - Test email
   - Enable/Disable alerts

4. **terminal.html?server=X** - Web Terminal
   - SSH terminal emulator
   - Command execution
   - Real-time output

5. **dashboard-v2.html** - Dark Theme Dashboard (Alternative)
   - Modern dark UI
   - Advanced charts
   - Tab-based navigation

## 🔐 Authentication Flow

```
User → index.html 
  ↓
Check authToken in localStorage
  ↓
  NO → login.html → Enter credentials → API /auth/login → Get token → Save to localStorage
  ↓
  YES → multi-server-dashboard.html (MAIN)
    ↓
    Navigation Menu:
    - Servers (main view)
    - SSH Keys
    - Email Settings
    - Export Data
    - Logout
```

## 🎨 Navigation Menu Structure

### Main Dashboard Header
```
┌─────────────────────────────────────────────────────────────┐
│ 🏠 Server Monitor v4.0     [🔑SSH][📧Email][🔄Refresh][👤User]│
└─────────────────────────────────────────────────────────────┘
│ Search... [🔍]  [Filter ▼]  [+ Add Server]                  │
└─────────────────────────────────────────────────────────────┘
│                                                               │
│  Statistics Cards: Total | Online | Offline | Alerts         │
│                                                               │
│  Server Grid (Cards with actions)                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                        │
│  │ Server1 │ │ Server2 │ │ Server3 │                        │
│  │ 🟢 UP   │ │ 🔴 DOWN │ │ 🟢 UP   │                        │
│  └─────────┘ └─────────┘ └─────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Server Actions (Dropdown Menu)
- 👁️ View Details → server-detail.html
- ✏️ Edit Server → Modal
- 🖥️ Open Terminal → terminal.html
- 🔄 Refresh Stats
- 🗑️ Delete Server

## 📊 API Endpoints Structure

### Authentication
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/verify

### Servers
- GET /api/servers - List all
- POST /api/servers - Add new
- GET /api/servers/{id} - Get details
- PUT /api/servers/{id} - Update
- DELETE /api/servers/{id} - Delete
- POST /api/servers/test - Test connection

### Monitoring
- GET /api/remote/stats/{id} - Get server stats
- GET /api/remote/stats/all - Get all servers stats
- POST /api/remote/agent/deploy/{id} - Deploy agent
- POST /api/remote/agent/start/{id} - Start agent
- GET /api/remote/agent/status/{id} - Check agent status

### SSH Keys (NEW)
- GET /api/ssh-keys - List all keys
- POST /api/ssh-keys - Add key
- GET /api/ssh-keys/{id} - Get key
- PUT /api/ssh-keys/{id} - Update key
- DELETE /api/ssh-keys/{id} - Delete key
- POST /api/ssh-keys/{id}/test - Test key

### Email Alerts
- GET /api/email/config - Get email config
- POST /api/email/config - Save config
- POST /api/email/test - Test email
- POST /api/email/send-alert - Send alert

### Export
- GET /api/export/servers?format=csv|json
- GET /api/export/history?format=csv|json
- GET /api/export/alerts/csv

### Statistics
- GET /api/stats/overview - Dashboard stats
- GET /api/alerts - Get alerts

## 🔒 Security Layers

1. **Frontend Security**
   - Check authToken before rendering
   - Redirect to login if no token
   - Store token in localStorage (httpOnly not available in SPA)

2. **Backend Security**
   - Verify token on every request (except public endpoints)
   - Token expires after 7 days
   - Password hashing (SHA256)
   - SSH password encryption (XOR + base64)

3. **API Security**
   - CORS enabled
   - Authorization header required
   - Role-based access (admin/public)
   - Session cleanup (expired tokens)

## 📁 File Structure

```
/opt/server-monitor-dev/
├── backend/
│   ├── central_api.py         # Main API server (35+ endpoints)
│   ├── database.py            # SQLite + CRUD functions
│   ├── ssh_manager.py         # SSH connection pool
│   ├── email_alerts.py        # Email system
│   ├── terminal.py            # WebSocket terminal
│   └── agent.py               # Monitoring agent
├── frontend/
│   ├── index.html             # Landing page (redirect)
│   ├── login.html             # Authentication
│   ├── multi-server-dashboard.html  # 🏠 MAIN DASHBOARD
│   ├── server-detail.html     # Server details
│   ├── ssh-keys.html          # SSH key management
│   ├── email-settings.html    # Email config
│   ├── terminal.html          # Web terminal
│   └── dashboard-v2.html      # Alternative dark theme
├── data/
│   └── servers.db             # SQLite database
└── logs/
    ├── api.log
    ├── terminal.log
    └── web.log
```

## 🚀 Deployment Ports

### Development
- Frontend: http://172.22.0.103:9081
- API: http://172.22.0.103:9083
- Terminal WS: ws://172.22.0.103:9084

### Production
- Frontend: http://172.22.0.103:8081
- API: http://172.22.0.103:8083
- Terminal WS: ws://172.22.0.103:8084

## 🎯 User Journey

1. **First Visit**
   ```
   User → index.html → login.html → multi-server-dashboard.html
   ```

2. **Regular User**
   ```
   User → index.html (auto redirect) → multi-server-dashboard.html (if token valid)
   ```

3. **View Server Details**
   ```
   Dashboard → Click "View Details" → server-detail.html?id=X
   ```

4. **Manage SSH Keys**
   ```
   Dashboard → Click "SSH Keys" button → ssh-keys.html
   ```

5. **Open Terminal**
   ```
   Dashboard → Server card → Actions → Terminal → terminal.html?server=X
   ```

## 🔑 Default Credentials

```
Username: admin
Password: admin123
```

⚠️ **IMPORTANT**: Change default password in production!
