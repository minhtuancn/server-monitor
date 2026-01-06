# SERVER MONITOR V4.0 - TECHNICAL SPECIFICATION

## 📋 TABLE OF CONTENTS
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Database Schema](#database-schema)
4. [API Specification](#api-specification)
5. [Frontend Structure](#frontend-structure)
6. [Features Specification](#features-specification)
7. [Security Requirements](#security-requirements)
8. [Development Workflow](#development-workflow)

---

## 1. PROJECT OVERVIEW

### 1.1 Description
Multi-Server Monitoring Dashboard v4.0 - Professional server management platform with SSH key management, terminal access, network tools, and real-time monitoring.

### 1.2 Technology Stack
- **Backend**: Python 3.8+, FastAPI, SQLite
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Communication**: REST API, WebSocket
- **Authentication**: JWT tokens, session-based
- **SSH**: Paramiko library

### 1.3 Project Goals
- ✅ Professional-grade UI/UX consistency
- ✅ Comprehensive SSH key management
- ✅ Terminal with command snippets
- ✅ Network diagnostic tools
- ✅ Server grouping and organization
- ✅ Real-time agent installation feedback
- ✅ Complete documentation

---

## 2. SYSTEM ARCHITECTURE

### 2.1 Directory Structure
```
/opt/server-monitor-dev/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── servers.py        # Server management
│   │   │   ├── ssh_keys.py       # SSH key management
│   │   │   ├── groups.py         # Server groups
│   │   │   ├── snippets.py       # Terminal snippets
│   │   │   ├── network.py        # Network tools
│   │   │   └── users.py          # User management
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration
│   │   ├── database.py           # Database connection
│   │   ├── security.py           # Security utilities
│   │   └── ssh.py                # SSH operations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── server.py
│   │   ├── ssh_key.py
│   │   ├── group.py
│   │   └── snippet.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── ssh_service.py
│   │   ├── monitoring_service.py
│   │   ├── network_service.py
│   │   └── agent_service.py
│   ├── agent.py                  # Monitoring agent
│   ├── central_api.py            # Main API entry (LEGACY - to migrate)
│   └── requirements.txt
├── frontend/
│   ├── assets/
│   │   ├── css/
│   │   │   ├── app.css           # Main stylesheet
│   │   │   ├── components.css    # Reusable components
│   │   │   └── themes.css        # Theme variables
│   │   ├── js/
│   │   │   ├── auth.js           # Authentication module
│   │   │   ├── api.js            # API client
│   │   │   ├── utils.js          # Utilities
│   │   │   ├── components.js     # UI components
│   │   │   └── i18n.js           # Internationalization
│   │   └── images/
│   ├── components/               # Reusable HTML components
│   │   ├── header.html
│   │   ├── sidebar.html
│   │   └── footer.html
│   ├── pages/                    # Main application pages
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── servers.html
│   │   ├── ssh-keys.html
│   │   ├── terminal.html
│   │   ├── snippets.html
│   │   ├── groups.html
│   │   ├── network-tools.html
│   │   ├── profile.html
│   │   └── settings.html
│   └── index.html                # Entry point
├── data/
│   ├── servers.db                # SQLite database
│   └── ssh_keys/                 # SSH keys storage
├── logs/
│   ├── api.log
│   ├── agent.log
│   └── error.log
├── docs/
│   ├── README.md
│   ├── API.md
│   ├── DEVELOPMENT.md
│   ├── DEPLOYMENT.md
│   ├── ARCHITECTURE.md
│   ├── USER_GUIDE.md
│   └── PROJECT_SPECIFICATION.md  # This file
├── tests/
│   ├── backend/
│   │   ├── test_api.py
│   │   ├── test_ssh.py
│   │   └── test_services.py
│   └── frontend/
│       └── test_ui.js
├── scripts/
│   ├── migrate_db.py             # Database migrations
│   ├── backup.sh                 # Backup script
│   └── deploy.sh                 # Deployment script
├── .env.example
├── .gitignore
├── requirements.txt
├── start-dev.sh
├── start-prod.sh
└── README.md
```

### 2.2 Component Communication
```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS/WSS
       ▼
┌─────────────┐         ┌──────────────┐
│  Frontend   │◄───────►│   Backend    │
│  (Static)   │  REST   │   FastAPI    │
└─────────────┘         └──────┬───────┘
                               │
                    ┌──────────┼──────────┐
                    │          │          │
                    ▼          ▼          ▼
              ┌─────────┐ ┌────────┐ ┌────────┐
              │ SQLite  │ │  SSH   │ │ Agent  │
              │   DB    │ │Servers │ │ Remote │
              └─────────┘ └────────┘ └────────┘
```

---

## 3. DATABASE SCHEMA

### 3.1 Existing Tables (Extended)

#### admin_users
```sql
CREATE TABLE admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    theme VARCHAR(20) DEFAULT 'dark',          -- NEW
    language VARCHAR(10) DEFAULT 'vi',         -- NEW
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

#### servers
```sql
CREATE TABLE servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER DEFAULT 22,
    username VARCHAR(50) NOT NULL,
    ssh_key_path TEXT,
    ssh_password TEXT,
    description TEXT,
    tags TEXT,
    location VARCHAR(100),
    is_active BOOLEAN DEFAULT 1,
    agent_installed BOOLEAN DEFAULT 0,
    agent_port INTEGER DEFAULT 9090,
    last_check TIMESTAMP,
    last_metrics TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### sessions
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE CASCADE
);
```

### 3.2 New Tables

#### server_groups
```sql
CREATE TABLE server_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color VARCHAR(20) DEFAULT '#667eea',
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### server_group_members
```sql
CREATE TABLE server_group_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    server_id INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES server_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE,
    UNIQUE(group_id, server_id)
);
```

#### terminal_snippets
```sql
CREATE TABLE terminal_snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    command TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    is_public BOOLEAN DEFAULT 0,
    use_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE SET NULL
);
```

#### ssh_key_pairs
```sql
CREATE TABLE ssh_key_pairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    key_type VARCHAR(20) NOT NULL CHECK(key_type IN ('rsa', 'ed25519', 'ecdsa')),
    key_size INTEGER,
    public_key TEXT NOT NULL,
    private_key_path TEXT NOT NULL,
    passphrase_encrypted TEXT,
    fingerprint VARCHAR(100),
    comment TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP
);
```

#### ssh_key_deployments
```sql
CREATE TABLE ssh_key_deployments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id INTEGER NOT NULL,
    server_id INTEGER NOT NULL,
    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    FOREIGN KEY (key_id) REFERENCES ssh_key_pairs(id) ON DELETE CASCADE,
    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
);
```

#### network_scan_history
```sql
CREATE TABLE network_scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    scan_type VARCHAR(50) NOT NULL,
    result TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
);
```

#### agent_installation_logs
```sql
CREATE TABLE agent_installation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    log_data TEXT,
    error TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
);
```

### 3.3 Migration Strategy
```python
# migrations/001_add_user_settings.py
def upgrade(db):
    db.execute("ALTER TABLE admin_users ADD COLUMN theme VARCHAR(20) DEFAULT 'dark'")
    db.execute("ALTER TABLE admin_users ADD COLUMN language VARCHAR(10) DEFAULT 'vi'")

# migrations/002_create_groups.py
def upgrade(db):
    db.execute("""CREATE TABLE server_groups (...)""")
    db.execute("""CREATE TABLE server_group_members (...)""")
    
# ... etc
```

---

## 4. API SPECIFICATION

### 4.1 API Versioning
All new endpoints use `/api/v1/` prefix for versioning.

### 4.2 Authentication
**Method**: Bearer Token (JWT)
**Header**: `Authorization: Bearer <token>`

**Login Flow:**
```
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "password123"
}

Response:
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_at": "2024-01-07T12:00:00Z",
  "user": {
    "id": 1,
    "username": "admin",
    "theme": "dark",
    "language": "vi"
  }
}
```

### 4.3 Endpoint Specifications

#### 4.3.1 Authentication & Users

```yaml
POST /api/v1/auth/login
  Body: { username, password }
  Response: { token, user, expires_at }

POST /api/v1/auth/logout
  Headers: Authorization
  Response: { success }

GET /api/v1/auth/verify
  Headers: Authorization
  Response: { valid, user }

POST /api/v1/auth/refresh
  Headers: Authorization
  Response: { token, expires_at }

GET /api/v1/user/profile
  Headers: Authorization
  Response: { id, username, email, theme, language, created_at, last_login }

PUT /api/v1/user/profile
  Headers: Authorization
  Body: { email, theme, language }
  Response: { success, user }

POST /api/v1/user/change-password
  Headers: Authorization
  Body: { current_password, new_password }
  Response: { success }

GET /api/v1/user/settings
  Headers: Authorization
  Response: { theme, language, notifications, ... }

PUT /api/v1/user/settings
  Headers: Authorization
  Body: { theme, language, ... }
  Response: { success }
```

#### 4.3.2 Server Management

```yaml
GET /api/v1/servers
  Headers: Authorization
  Query: ?group_id=1&status=online&search=web
  Response: [{ id, name, host, status, metrics, ... }]

POST /api/v1/servers
  Headers: Authorization
  Body: { name, host, port, username, auth_method, ... }
  Response: { success, server }

GET /api/v1/servers/{id}
  Headers: Authorization
  Response: { id, name, host, metrics, groups, ... }

PUT /api/v1/servers/{id}
  Headers: Authorization
  Body: { name, description, ... }
  Response: { success, server }

DELETE /api/v1/servers/{id}
  Headers: Authorization
  Response: { success }

POST /api/v1/servers/{id}/test
  Headers: Authorization
  Response: { success, message, connection_time }
```

#### 4.3.3 SSH Key Management

```yaml
GET /api/v1/ssh-keys
  Headers: Authorization
  Response: [{ id, name, key_type, fingerprint, created_at, ... }]

POST /api/v1/ssh-keys
  Headers: Authorization
  Body: { name, key_type, key_size, passphrase, description }
  Response: { success, key }

POST /api/v1/ssh-keys/generate
  Headers: Authorization
  Body: { name, key_type, key_size, passphrase, comment }
  Response: { success, key_id, fingerprint, public_key }

POST /api/v1/ssh-keys/upload
  Headers: Authorization
  Body: FormData { name, private_key_file, public_key_file, passphrase }
  Response: { success, key }

POST /api/v1/ssh-keys/import
  Headers: Authorization
  Body: { name, private_key_content, public_key_content, passphrase }
  Response: { success, key }

GET /api/v1/ssh-keys/{id}
  Headers: Authorization
  Response: { id, name, key_type, public_key, fingerprint, ... }

GET /api/v1/ssh-keys/{id}/public
  Headers: Authorization
  Response: { public_key }

GET /api/v1/ssh-keys/{id}/private
  Headers: Authorization
  Response: { private_key }  # Requires additional auth

PUT /api/v1/ssh-keys/{id}
  Headers: Authorization
  Body: { name, description, passphrase }
  Response: { success }

DELETE /api/v1/ssh-keys/{id}
  Headers: Authorization
  Response: { success }

POST /api/v1/ssh-keys/{id}/deploy
  Headers: Authorization
  Body: { server_ids: [1, 2, 3] }
  Response: { success, deployed: [...], failed: [...] }

POST /api/v1/ssh-keys/{id}/test
  Headers: Authorization
  Body: { server_id }
  Response: { success, connection_time }

GET /api/v1/ssh-keys/{id}/deployments
  Headers: Authorization
  Response: [{ server_id, server_name, deployed_at, status }]
```

#### 4.3.4 Server Groups

```yaml
GET /api/v1/groups
  Headers: Authorization
  Response: [{ id, name, description, color, server_count }]

POST /api/v1/groups
  Headers: Authorization
  Body: { name, description, color, icon }
  Response: { success, group }

GET /api/v1/groups/{id}
  Headers: Authorization
  Response: { id, name, description, servers: [...] }

PUT /api/v1/groups/{id}
  Headers: Authorization
  Body: { name, description, color }
  Response: { success }

DELETE /api/v1/groups/{id}
  Headers: Authorization
  Response: { success }

POST /api/v1/groups/{id}/members
  Headers: Authorization
  Body: { server_ids: [1, 2, 3] }
  Response: { success, added_count }

DELETE /api/v1/groups/{id}/members/{server_id}
  Headers: Authorization
  Response: { success }

POST /api/v1/groups/{id}/bulk-action
  Headers: Authorization
  Body: { action: 'restart_agent', params: {...} }
  Response: { success, results: [...] }
```

#### 4.3.5 Terminal Snippets

```yaml
GET /api/v1/snippets
  Headers: Authorization
  Query: ?category=system&public=true
  Response: [{ id, name, command, category, use_count }]

POST /api/v1/snippets
  Headers: Authorization
  Body: { name, command, description, category, is_public }
  Response: { success, snippet }

GET /api/v1/snippets/{id}
  Headers: Authorization
  Response: { id, name, command, description, ... }

PUT /api/v1/snippets/{id}
  Headers: Authorization
  Body: { name, command, description, category }
  Response: { success }

DELETE /api/v1/snippets/{id}
  Headers: Authorization
  Response: { success }

POST /api/v1/snippets/{id}/execute
  Headers: Authorization
  Body: { server_id, variables: {...} }
  Response: { success, output, exit_code }

GET /api/v1/snippets/categories
  Headers: Authorization
  Response: [{ name, count }]
```

#### 4.3.6 Network Tools

```yaml
POST /api/v1/servers/{id}/scan-ports
  Headers: Authorization
  Body: { start_port: 1, end_port: 1000, timeout: 5 }
  Response: { success, open_ports: [...], scan_time }

POST /api/v1/servers/{id}/check-port
  Headers: Authorization
  Body: { port: 80, protocol: 'tcp' }
  Response: { success, open, service, banner }

GET /api/v1/servers/{id}/firewall-status
  Headers: Authorization
  Response: { success, firewall: 'iptables', active, rules: [...] }

POST /api/v1/servers/{id}/ping
  Headers: Authorization
  Body: { count: 4 }
  Response: { success, packets_sent, packets_received, avg_time }

POST /api/v1/servers/{id}/traceroute
  Headers: Authorization
  Body: { max_hops: 30 }
  Response: { success, hops: [...] }

POST /api/v1/servers/{id}/network-info
  Headers: Authorization
  Response: { success, interfaces: [...], routes: [...], dns: [...] }
```

#### 4.3.7 Agent Management

```yaml
POST /api/v1/servers/{id}/check-environment
  Headers: Authorization
  Response: { 
    success, 
    os: { name, version },
    python: { installed, version },
    packages: { pip, systemd, ... },
    disk_space: { available, required }
  }

POST /api/v1/servers/{id}/install-agent
  Headers: Authorization
  Body: { port: 9090, auto_start: true }
  Response: { success, job_id }

WebSocket /api/v1/servers/{id}/install-agent-stream
  Headers: Authorization
  Messages: { type: 'log', message: '...', timestamp }

POST /api/v1/servers/{id}/uninstall-agent
  Headers: Authorization
  Response: { success }

GET /api/v1/servers/{id}/agent-status
  Headers: Authorization
  Response: { installed, running, version, uptime }

POST /api/v1/servers/{id}/agent-action
  Headers: Authorization
  Body: { action: 'restart' | 'start' | 'stop' }
  Response: { success }
```

### 4.4 Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "AUTH_INVALID_TOKEN",
    "message": "Invalid or expired token",
    "details": null
  }
}
```

### 4.5 Rate Limiting
- **Authentication**: 5 requests per minute
- **API calls**: 100 requests per minute
- **WebSocket**: 10 connections per user

---

## 5. FRONTEND STRUCTURE

### 5.1 Shared CSS Variables (themes.css)
```css
:root {
  /* Dark Theme */
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
  --text-primary: #e2e8f0;
  --text-secondary: #cbd5e1;
  --text-muted: #94a3b8;
  --accent: #667eea;
  --accent-dark: #764ba2;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --info: #3b82f6;
  --border: #334155;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  
  /* Shadows */
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.5);
}
```

### 5.2 Component Library (components.css)
```css
/* Buttons */
.btn { /* base button styles */ }
.btn-primary { /* primary button */ }
.btn-success { /* success button */ }
.btn-danger { /* danger button */ }

/* Cards */
.card { /* base card */ }
.card-header { /* card header */ }
.card-body { /* card body */ }

/* Forms */
.form-group { /* form group */ }
.form-label { /* label */ }
.form-input { /* input field */ }
.form-select { /* dropdown */ }

/* Modals */
.modal { /* modal overlay */ }
.modal-content { /* modal container */ }
.modal-header { /* modal header */ }
.modal-body { /* modal body */ }

/* Tables */
.table { /* table styles */ }
.table-responsive { /* responsive wrapper */ }

/* Alerts */
.alert { /* base alert */ }
.alert-success { /* success alert */ }
.alert-danger { /* error alert */ }

/* Navigation */
.header { /* top header */ }
.sidebar { /* left sidebar */ }
.nav-item { /* nav menu item */ }

/* Utilities */
.text-center { text-align: center; }
.mt-4 { margin-top: var(--spacing-lg); }
.p-4 { padding: var(--spacing-lg); }
```

### 5.3 JavaScript Modules

#### auth.js
```javascript
export class AuthManager {
  constructor() {
    this.token = localStorage.getItem('auth_token');
    this.user = JSON.parse(localStorage.getItem('user') || 'null');
  }
  
  async login(username, password) { /* ... */ }
  async logout() { /* ... */ }
  async verifyToken() { /* ... */ }
  isAuthenticated() { /* ... */ }
  getUser() { /* ... */ }
  requireAuth() { /* redirect if not auth */ }
}
```

#### api.js
```javascript
export class APIClient {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.auth = new AuthManager();
  }
  
  async request(method, endpoint, data = null) {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.auth.token}`
    };
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method,
      headers,
      body: data ? JSON.stringify(data) : null
    });
    
    return await response.json();
  }
  
  get(endpoint) { return this.request('GET', endpoint); }
  post(endpoint, data) { return this.request('POST', endpoint, data); }
  put(endpoint, data) { return this.request('PUT', endpoint, data); }
  delete(endpoint) { return this.request('DELETE', endpoint); }
}
```

#### utils.js
```javascript
export function showToast(message, type = 'info') { /* ... */ }
export function formatDate(timestamp) { /* ... */ }
export function formatBytes(bytes) { /* ... */ }
export function debounce(func, wait) { /* ... */ }
export function copyToClipboard(text) { /* ... */ }
```

### 5.4 Page Template Structure
```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title - Server Monitor v4.0</title>
    <link rel="stylesheet" href="/assets/css/app.css">
</head>
<body>
    <!-- Header Component -->
    <div id="header-container"></div>
    
    <!-- Sidebar Component -->
    <div id="sidebar-container"></div>
    
    <!-- Main Content -->
    <main class="main-content">
        <div class="container">
            <!-- Page specific content -->
        </div>
    </main>
    
    <!-- Footer Component -->
    <div id="footer-container"></div>
    
    <!-- Scripts -->
    <script type="module">
        import { AuthManager } from '/assets/js/auth.js';
        import { APIClient } from '/assets/js/api.js';
        
        const auth = new AuthManager();
        auth.requireAuth(); // Redirect if not logged in
        
        const api = new APIClient(API_URL);
        
        // Page specific code
    </script>
</body>
</html>
```

---

## 6. FEATURES SPECIFICATION

### 6.1 User Profile & Settings

**Features:**
- View/Edit profile information
- Change password
- Theme selector (dark/light)
- Language selector (vi/en)
- Notification preferences

**UI Components:**
- Profile page
- User dropdown menu in header
- Settings modal

**API Endpoints:**
- GET /api/v1/user/profile
- PUT /api/v1/user/profile
- POST /api/v1/user/change-password
- GET/PUT /api/v1/user/settings

### 6.2 SSH Key Management (Advanced)

**Features:**
1. **Generate Key Pairs**
   - RSA (2048, 4096 bits)
   - ED25519
   - ECDSA
   - Optional passphrase
   - Custom comment

2. **Import Keys**
   - Upload file
   - Copy/paste content
   - Auto-detect key type

3. **Manage Keys**
   - List all keys
   - View public/private separately
   - Edit metadata
   - Delete keys
   - Test connection

4. **Deploy to Servers**
   - Select multiple servers
   - Bulk deployment
   - Deployment status tracking
   - Rollback option

5. **Convert Auth Method**
   - Password → Key
   - Auto-configure authorized_keys
   - Verify connection

**UI Components:**
- SSH Keys page
- Key generation modal
- Key upload modal
- Deployment modal
- Key viewer modal

**API Endpoints:**
- POST /api/v1/ssh-keys/generate
- POST /api/v1/ssh-keys/upload
- POST /api/v1/ssh-keys/import
- POST /api/v1/ssh-keys/{id}/deploy
- POST /api/v1/ssh-keys/{id}/test

### 6.3 Terminal Snippets

**Features:**
1. **Snippet Library**
   - System commands
   - Package management
   - Network diagnostics
   - Service management
   - Custom commands

2. **Management**
   - Create/Edit/Delete
   - Categorize
   - Mark as public/private
   - Track usage count

3. **Execution**
   - One-click execute
   - Variable substitution
   - Output display
   - Save to history

**UI Components:**
- Snippets library page
- Snippet editor modal
- Quick snippets panel in terminal
- Execution modal

**API Endpoints:**
- GET /api/v1/snippets
- POST /api/v1/snippets
- POST /api/v1/snippets/{id}/execute

**Example Snippets:**
```yaml
- name: "Check Disk Usage"
  category: "system"
  command: "df -h"

- name: "List Top Processes"
  category: "monitoring"
  command: "ps aux --sort=-%mem | head -10"

- name: "Install Package"
  category: "package"
  command: "apt-get install -y {{package_name}}"
  variables: ["package_name"]
```

### 6.4 Server Groups

**Features:**
1. **Group Management**
   - Create/Edit/Delete groups
   - Assign colors and icons
   - Add/Remove servers

2. **Organization**
   - Filter by group
   - Group-based dashboard
   - Group tags

3. **Bulk Actions**
   - Execute command on group
   - Deploy keys to group
   - Install agent on group
   - Monitor group health

**UI Components:**
- Groups management page
- Group selector in dashboard
- Group actions menu

**API Endpoints:**
- GET/POST /api/v1/groups
- POST /api/v1/groups/{id}/members
- POST /api/v1/groups/{id}/bulk-action

### 6.5 Network Tools

**Features:**
1. **Port Scanner**
   - Range scanning
   - Service detection
   - Banner grabbing
   - Results export

2. **Port Checker**
   - TCP/UDP check
   - Connection test
   - Response time

3. **Firewall Status**
   - iptables rules
   - firewalld status
   - Active connections

4. **Diagnostics**
   - Ping test
   - Traceroute
   - Network interfaces
   - Route table

**UI Components:**
- Network tools page
- Port scanner interface
- Results display

**API Endpoints:**
- POST /api/v1/servers/{id}/scan-ports
- POST /api/v1/servers/{id}/check-port
- GET /api/v1/servers/{id}/firewall-status
- POST /api/v1/servers/{id}/ping

### 6.6 Agent Installation with Feedback

**Features:**
1. **Pre-installation Checks**
   - OS compatibility
   - Python version
   - Required packages
   - Disk space
   - Network connectivity

2. **Installation Process**
   - Real-time log streaming
   - Progress indicator
   - Step-by-step status
   - Error handling

3. **Post-installation**
   - Service verification
   - Health check
   - Configuration summary

**UI Components:**
- Installation modal with terminal output
- Progress bar
- Status indicators

**API Endpoints:**
- POST /api/v1/servers/{id}/check-environment
- WebSocket /api/v1/servers/{id}/install-agent-stream

**Installation Steps:**
```
1. Environment Check
   ✓ OS: Ubuntu 22.04
   ✓ Python: 3.10.12
   ✓ Disk: 2.5GB available
   
2. Download Agent
   → Downloading agent.py...
   ✓ Downloaded (125KB)
   
3. Install Dependencies
   → pip install psutil fastapi uvicorn
   ✓ Dependencies installed
   
4. Configure Service
   → Creating systemd service...
   ✓ Service created
   
5. Start Agent
   → systemctl start server-monitor-agent
   ✓ Agent started on port 9090
   
6. Verify Connection
   → Testing connection...
   ✓ Agent responding
   
✓ Installation complete!
```

---

## 7. SECURITY REQUIREMENTS

### 7.1 Authentication
- Password hashing: bcrypt with salt
- JWT tokens with expiration
- Session timeout: 24 hours
- Refresh token mechanism
- Failed login attempts tracking

### 7.2 Authorization
- Role-based access control (RBAC)
- Resource-level permissions
- API rate limiting
- CORS configuration

### 7.3 Data Protection
- SSH keys encrypted at rest
- Passwords never stored in plaintext
- Sensitive data in environment variables
- Secure WebSocket connections (WSS)

### 7.4 Input Validation
- SQL injection prevention
- XSS protection
- Command injection prevention
- File upload validation

### 7.5 Audit Logging
- Login/logout events
- SSH key operations
- Server modifications
- Failed authentication attempts

---

## 8. DEVELOPMENT WORKFLOW

### 8.1 Git Workflow
```
main (production)
  ├── develop (staging)
  │   ├── feature/user-settings
  │   ├── feature/ssh-keys-advanced
  │   └── feature/network-tools
  └── hotfix/critical-bug
```

### 8.2 Code Review Process
1. Create feature branch
2. Implement feature
3. Write tests
4. Create pull request
5. Code review
6. Merge to develop
7. Test on staging
8. Merge to main

### 8.3 Testing Strategy
- Unit tests (backend)
- Integration tests (API)
- Manual testing (frontend)
- Security testing
- Performance testing

### 8.4 Deployment Process
1. Backup database
2. Stop services
3. Pull latest code
4. Run migrations
5. Install dependencies
6. Start services
7. Verify deployment
8. Monitor logs

---

## 9. SUCCESS CRITERIA

### 9.1 Technical Requirements
- ✅ All pages use unified UI theme
- ✅ Session management works across all pages
- ✅ All API endpoints respond < 200ms
- ✅ No console errors in browser
- ✅ Mobile responsive design
- ✅ Cross-browser compatibility

### 9.2 Feature Requirements
- ✅ User can change password
- ✅ User can customize theme/language
- ✅ SSH keys can be generated and deployed
- ✅ Terminal snippets work correctly
- ✅ Server groups organize servers
- ✅ Network tools provide accurate results
- ✅ Agent installation shows live progress

### 9.3 Documentation Requirements
- ✅ README.md is complete and clear
- ✅ API documentation is accurate
- ✅ Development guide helps new developers
- ✅ User guide explains all features
- ✅ Code is well-commented

### 9.4 Quality Requirements
- ✅ No critical bugs
- ✅ Code follows style guide
- ✅ Performance is acceptable
- ✅ Security best practices followed
- ✅ Error handling is comprehensive

---

## 10. TIMELINE & MILESTONES

### Week 1: Foundation
- ✅ Day 1-2: Shared components & database
- ✅ Day 3-4: UI rebuild (all pages)
- ✅ Day 5: User profile & settings

### Week 2: Core Features
- ✅ Day 1-2: SSH key management (full)
- ✅ Day 3: Terminal snippets
- ✅ Day 4: Server groups
- ✅ Day 5: Testing & bug fixes

### Week 3: Advanced Features
- ✅ Day 1-2: Network tools
- ✅ Day 3-4: Agent installation feedback
- ✅ Day 5: Final testing

### Week 4: Documentation & Polish
- ✅ Day 1-2: Complete documentation
- ✅ Day 3-4: Bug fixes & polish
- ✅ Day 5: Deployment & handoff

---

## APPENDIX A: GLOSSARY

- **Agent**: Monitoring software installed on remote servers
- **SSH Key Pair**: Public/private cryptographic key pair for authentication
- **Snippet**: Reusable command template
- **Group**: Collection of servers for organization
- **Session**: Authenticated user connection
- **Token**: JWT authentication credential

---

## APPENDIX B: REFERENCES

- FastAPI Documentation: https://fastapi.tiangolo.com
- Paramiko Documentation: http://www.paramiko.org
- SQLite Documentation: https://www.sqlite.org/docs.html
- JWT Best Practices: https://jwt.io/introduction

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-06  
**Author**: Development Team  
**Status**: APPROVED - Ready for Implementation
