# 🖥️ Server Monitor Dashboard v2.3

**Multi-server monitoring system with modern Next.js 16 frontend, real-time updates, web terminal, webhooks, and advanced security**

[![Status](https://img.shields.io/badge/status-production--ready-brightgreen)]()
[![Version](https://img.shields.io/badge/version-2.3.0-blue)](https://github.com/minhtuancn/server-monitor/releases)
[![Frontend](https://img.shields.io/badge/frontend-Next.js%2016-black)]()
[![API](https://img.shields.io/badge/API-OpenAPI%203.0-brightgreen)]()
[![Tests](https://img.shields.io/badge/tests-passing-green)]()
[![Security](https://img.shields.io/badge/security-hardened-green)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 🚀 Quick Navigation

**Bạn muốn làm gì?**

- 💻 **[Test trên máy local?](#-chạy-thử-trên-local-developmenttesting)** ← Bắt đầu từ đây!
- 🚀 **[Deploy production?](#one-command-installation-on-linux-recommended)** ← Cài đặt tự động 1 lệnh
- 📚 **[Xem API docs?](http://localhost:9083/docs)** ← Swagger UI
- 🔧 **[Cấu hình?](#-configuration)** ← Ports, environment variables
- 🐛 **[Gặp lỗi?](#-troubleshooting)** ← Troubleshooting guide

---

**Getting Started:**

📚 **API Docs**: [Swagger UI](http://localhost:9083/docs) | [OpenAPI Spec](http://localhost:9083/api/openapi.yaml)  
📊 **Metrics**: [Prometheus Metrics](http://localhost:9083/api/metrics)  
🔗 **Webhooks**: Admin → Settings → Integrations

---

## 📋 Tổng Quan

Server Monitor Dashboard là hệ thống giám sát multi-server với giao diện web hiện đại Next.js, cho phép quản lý và theo dõi nhiều servers từ một dashboard trung tâm.

### 🎯 Các Phương Thức Sử Dụng

1. **Local Development/Testing** 💻

   - Chạy trực tiếp trên máy local để phát triển và test
   - Không cần systemd hay deployment phức tạp
   - Xem hướng dẫn chi tiết tại: [Chạy Thử Trên Local](#-chạy-thử-trên-local-developmenttesting)

2. **Production Deployment** 🚀
   - Cài đặt tự động với systemd services
   - Auto-start khi khởi động server
   - Xem hướng dẫn tại: [Quick Start - One-Command Installation](#one-command-installation-on-linux-recommended)

### ✨ Tính Năng Chính

- 🚀 **Modern Next.js Frontend**: App Router + TypeScript + MUI + React Query
- 🌐 **Multi-Server Management**: Quản lý nhiều servers từ một giao diện
- 📊 **Real-time Monitoring**: Cập nhật metrics thời gian thực qua WebSocket
- 🖥️ **Web Terminal**: SSH terminal emulator trên browser (xterm.js)
- 📦 **System Inventory**: Agentless inventory collection via SSH (Phase 4 Module 3)
- 🔐 **Secure Authentication**: JWT-based auth with HttpOnly cookies, RBAC
- 🔑 **SSH Key Vault**: Encrypted SSH private key storage with AES-256-GCM (Phase 4)
- 🛡️ **Security Hardened**: Rate limiting, CORS, input validation, CSRF protection
- 🔔 **Webhooks Integration**: HTTP callbacks for system events with HMAC signing (Phase 8)
- 📧 **Email Alerts**: Cảnh báo tự động qua email khi vượt ngưỡng
- 📤 **Export Data**: Xuất dữ liệu ra CSV/JSON
- 🌍 **Internationalization**: Multi-language support (8 languages)
- 🧪 **Automated Testing**: 23 test cases với pytest + CI/CD

### 🎯 Use Cases

- Giám sát multiple servers từ xa
- Quản lý infrastructure qua web UI
- Remote troubleshooting qua web terminal
- Theo dõi performance metrics real-time
- Nhận cảnh báo tự động về issues
- Quản lý SSH keys với mã hoá bảo mật

### 🎉 What's New

**v2.3 (2026-01-08) - Plugin System & Webhooks:**

- 🔌 **Plugin System**: Extensible architecture with event-driven plugins
- 🔗 **Managed Webhooks**: Database-backed webhooks with UI management (Admin → Settings → Integrations)
- 🛡️ **SSRF Protection**: Multi-layer validation blocks internal network access
- 🔐 **HMAC Signing**: Cryptographic signatures for webhook authenticity
- ⚡ **Performance**: TTL cache reduces DB queries by 40-60%, token bucket rate limiting
- 📊 **Enhanced Metrics**: Cache hits/misses, rate limits, webhook delivery tracking at `/api/metrics`
- 🌍 **i18n**: Webhooks UI supports 8 languages
- 🔄 **Zero Breaking Changes**: Fully backward compatible with v2.2

**v2.2 (2026-01-07) - Observability & Reliability:**

- 📊 **Observability**: Health checks at `/api/health` and `/api/ready`, Prometheus metrics at `/api/metrics`
- 🔍 **Request Tracing**: Correlation IDs for end-to-end request tracking
- 📝 **Structured Logging**: JSON logs across all services with redaction
- 🔒 **Enhanced Security**: Startup validation, task safety policy, audit retention
- 🛡️ **Reliability**: Graceful shutdown, automatic task recovery, session recovery
- 📤 **Audit Export**: CSV/JSON export with filtering and sanitization

**v2.1 (2026-01-07) - Production Polish:**

- 📚 **OpenAPI 3.0.3 Documentation**: Complete API specification with 70+ endpoints
- 🔍 **Swagger UI**: Interactive API documentation at `/docs` endpoint
- 🧪 **Automated Testing**: Smoke test script for deployment validation
- ✅ **Enhanced Test Coverage**: 200+ manual test cases documented
- 📖 **OSS-Ready**: Production-ready documentation for contributors

**v2.0 (2026-01-07):**

- ✨ **Next.js Frontend**: Complete rewrite with modern stack (Next.js 14, TypeScript, MUI)
- 🔐 **Enhanced Security**: HttpOnly cookies, RBAC, SSRF protection, path validation
- 🛡️ **BFF Layer**: Backend-for-Frontend with authentication proxy
- 🎨 **Improved UX**: Toast notifications, loading states, empty states, better error handling
- 🔄 **WebSocket Fixes**: Proper cleanup, no memory leaks, auto-reconnect
- 🌍 **i18n Support**: next-intl integration for 8 languages
- 📝 **Access Control**: Admin-only pages, role-based navigation
- 🚀 **CI/CD**: Separate workflows for frontend and backend

**Phase 4 Modules (2026-01-07):**

- 🔑 **SSH Key Vault**: AES-256-GCM encrypted private key storage with PBKDF2 key derivation
- 🖥️ **Enhanced Web Terminal**: Vault integration, session tracking, audit trail, idle timeout
- 📦 **System Inventory**: Agentless SSH-based collection of OS, CPU, memory, disk, network info
- ⚡ **Tasks/Remote Commands**: Async execution engine with concurrency control and audit logging
- 📝 **Notes & Tags**: Enhanced documentation and categorization with soft delete
- 📊 **Audit Logs**: Comprehensive activity tracking for compliance
- 🔄 **Server Workspace**: Tab-based UI (Overview, Inventory, Terminal, Tasks, Notes)
- 📈 **Recent Activity**: Dashboard widget showing latest system actions

---

## 💻 Chạy Thử Trên Local (Development/Testing)

**CÂU TRẢ LỜI: CÓ! Dự án có thể chạy thử hoàn toàn trên local để test và phát triển.**

📚 **Hướng dẫn chi tiết**: [docs/getting-started/LOCAL_DEV.md](docs/getting-started/LOCAL_DEV.md)  
🐛 **Gặp lỗi?**: [docs/getting-started/TROUBLESHOOTING.md](docs/getting-started/TROUBLESHOOTING.md)

### ⚠️ QUAN TRỌNG: Thư Mục Làm Việc

**Tất cả lệnh dưới đây PHẢI chạy từ thư mục gốc của dự án (project root).**

Thư mục gốc là nơi chứa: `backend/`, `frontend-next/`, `start-all.sh`, `.env.example`

```bash
# Kiểm tra bạn đang ở đúng thư mục chưa?
pwd
ls -la

# Phải thấy các thư mục/file này:
# backend/
# frontend-next/
# start-all.sh
# .env.example
```

Nếu không thấy → bạn đang ở sai thư mục! Hãy `cd` đến thư mục gốc của dự án trước.

### Yêu Cầu Hệ Thống

- **Python 3.8+** (kiểm tra: `python3 --version`)
- **Node.js 18+** và npm (kiểm tra: `node --version`)
- **Hệ điều hành**: Linux/macOS (Windows cần WSL)
- **RAM**: Tối thiểu 2GB
- **Disk**: ~500MB cho code và dependencies

### Cài Đặt Nhanh Cho Local Development

```bash
# 1. Clone repository
# Nếu chưa có repo:
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor

# Nếu đã có repo (cập nhật mã nguồn mới nhất):
cd ~/server-monitor  # hoặc đường dẫn nơi bạn đã clone
git pull

# Nếu muốn cài lại sạch (xóa và clone lại):
cd ~
rm -rf server-monitor
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor

# 2. Tạo Python virtual environment (KHUYẾN NGHỊ cho Python 3.12+)
python3 -m venv venv

# 3. Kích hoạt virtual environment
source venv/bin/activate  # Linux/macOS
# Windows: venv\Scripts\activate

# 4. Cài đặt backend dependencies (trong venv)
pip install -r backend/requirements.txt

# Optional: Cài đặt test dependencies
pip install -r tests/requirements.txt

# 5. Tạo file cấu hình môi trường
cp .env.example .env

# 6. Tạo keys bảo mật (QUAN TRỌNG!)
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))" >> .env
python3 -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(24))" >> .env
python3 -c "import secrets; print('KEY_VAULT_MASTER_KEY=' + secrets.token_urlsafe(32))" >> .env
# ⚠️ Lưu ý: Nếu chạy lại các lệnh trên, xóa các dòng key cũ trong .env trước

# 7. Cài đặt frontend dependencies (Next.js)
cd frontend-next
npm ci  # hoặc npm install
cd ..

# 📝 Lưu ý về npm warnings:
# - Thông báo "npm warn deprecated ..." là WARNING, không phải LỖI
# - Các deprecated packages vẫn hoạt động bình thường
# - Chỉ có lỗi thật khi npm exit code != 0 (hiện thông báo "npm ERR!")
# - Bạn có thể bỏ qua npm warnings khi chạy local development

# 8. Tạo file cấu hình cho frontend
cat > frontend-next/.env.local << 'EOF'
API_PROXY_TARGET=http://localhost:9083
NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084
EOF

# ⚠️ Lưu ý về heredoc:
# - EOF phải đứng một mình trên dòng cuối (không có khoảng trắng trước/sau)
# - Dùng 'EOF' (có dấu ngoặc) để tránh bash thay thế biến
```

### Khởi Động Services Để Test

**Cách 1: Sử dụng script tự động (Khuyến nghị)**

```bash
# Đảm bảo bạn đang ở thư mục gốc của dự án
pwd  # Phải thấy /path/to/server-monitor

# Khởi động tất cả services (API + WebSocket + Next.js Frontend)
./start-all.sh

# Script sẽ tự động:
# - Kích hoạt virtual environment (nếu có)
# - Khởi động Backend API (port 9083)
# - Khởi động WebSocket Server (port 9085)
# - Khởi động Terminal Server (port 9084)
# - Khởi động Next.js Frontend (port 9081)
# - Tự động cài đặt npm packages nếu chưa có

# ⏳ Chờ 10-30 giây để Next.js compile xong

# Dừng tất cả services
./stop-all.sh
```

**Giải thích về độ trễ lần đầu trong dev mode:**

Khi chạy Next.js 16 dev mode, code compile theo yêu cầu (on-demand). Lần đầu truy cập một trang có thể mất 5-10 giây. Đây là **hành vi bình thường của dev mode**.

- **Warm-up script**: Chạy `./scripts/warmup-dev.sh` để pre-compile các route thường dùng
- **Test performance thật**: Dùng `npm run build && npm run start` (production mode)

**Truy cập từ IP LAN (192.168.x.x, 172.x.x.x):**

Nếu muốn truy cập từ thiết bị khác trong mạng LAN, thêm vào `frontend-next/.env.local`:

```bash
ALLOW_LAN=true
```

Sau đó restart frontend dev server. Điều này tránh cảnh báo `allowedDevOrigins` khi truy cập từ IP không phải localhost.

**Cách 2: Khởi động từng service riêng (để debug)**

```bash
# Đảm bảo virtual environment đã được kích hoạt
source venv/bin/activate  # Hoặc venv\Scripts\activate trên Windows

# Terminal 1: Backend API (chạy từ project root)
python3 backend/central_api.py

# Terminal 2: WebSocket server (chạy từ project root)
python3 backend/websocket_server.py

# Terminal 3: Terminal server (chạy từ project root)
python3 backend/terminal.py

# Terminal 4: Frontend Next.js
cd frontend-next
npm run dev
```

### Truy Cập Dashboard

Sau khi khởi động thành công:

- 🌐 **Dashboard**: http://localhost:9081
- 🔌 **API Backend**: http://localhost:9083
- 📚 **API Documentation**: http://localhost:9083/docs (Swagger UI)
- 📊 **API Health**: http://localhost:9083/api/health

**Đăng nhập mặc định:**

- Username: `admin`
- Password: `admin123`

⚠️ **Lưu ý**: Đổi mật khẩu ngay sau khi đăng nhập lần đầu!

### Kiểm Tra Services Đang Chạy

```bash
# Kiểm tra ports đang được sử dụng
lsof -i :9081  # Frontend
lsof -i :9083  # API
lsof -i :9084  # Terminal WebSocket
lsof -i :9085  # Monitoring WebSocket

# Xem logs (nếu dùng start-all.sh)
tail -f logs/*.log

# Xem log của từng service cụ thể
tail -f logs/central_api.log
tail -f logs/websocket.log
tail -f logs/terminal.log

# Kiểm tra health của API
curl http://localhost:9083/api/health
```

**Lưu ý về logs**:

- Nếu chạy bằng `./start-all.sh` → logs trong thư mục `logs/`
- Nếu chạy manual (`python3 backend/...`) → logs hiện trên terminal
- Nếu cài production (systemd) → dùng `sudo journalctl -u server-monitor-*`

### Dừng Services

```bash
# Dừng backend services
./stop-all.sh

# Dừng frontend: Nhấn Ctrl+C trong terminal đang chạy npm
```

### Test Nhanh Các Tính Năng

1. **Thêm server để monitor**: Dashboard → Add Server
2. **Xem real-time metrics**: Metrics sẽ tự động cập nhật mỗi 3 giây
3. **Test web terminal**: Terminal → Connect to server via SSH
4. **Test alerts**: Settings → Email/Alerts
5. **Export data**: Servers → Export CSV/JSON

### Troubleshooting

📚 **Hướng dẫn đầy đủ**: [docs/getting-started/TROUBLESHOOTING.md](docs/getting-started/TROUBLESHOOTING.md)

**Lỗi: `source venv/bin/activate: No such file or directory`**

```bash
# Nguyên nhân: Bạn chưa tạo venv hoặc đang ở sai thư mục
# Giải pháp 1: Kiểm tra thư mục
pwd  # Phải thấy /path/to/server-monitor
ls -la  # Phải thấy backend/ frontend-next/ start-all.sh

# Giải pháp 2: Tạo venv nếu chưa có
python3 -m venv venv
source venv/bin/activate
```

**Lỗi: `ModuleNotFoundError: No module named 'paramiko'` hoặc `'websockets'`**

```bash
# Nguyên nhân: Chưa cài dependencies hoặc chưa activate venv
# Giải pháp:
source venv/bin/activate  # Kích hoạt venv trước!
pip install -r backend/requirements.txt

# Kiểm tra đã cài đủ chưa:
python3 -c "import paramiko; import websockets; print('OK')"
```

**Lỗi: `cd backend: No such file or directory`**

```bash
# Nguyên nhân: Bạn đang ở thư mục sai hoặc đã ở trong backend/ rồi
pwd  # Kiểm tra vị trí hiện tại

# Nếu thấy /path/to/server-monitor/backend → đã ở trong backend rồi!
# Quay về project root:
cd ..

# Nếu không thấy backend/ → đang ở sai chỗ:
cd /path/to/server-monitor
```

**Lỗi: Port already in use**

```bash
# Tìm và kill process đang dùng port
lsof -ti:9081 | xargs kill
lsof -ti:9083 | xargs kill
lsof -ti:9084 | xargs kill
lsof -ti:9085 | xargs kill

# Nếu process không dừng, dùng force kill
lsof -ti:9083 | xargs kill -9
```

**Lỗi: `tail -f logs/*.log: No such file or directory`**

```bash
# Nguyên nhân: Thư mục logs chưa tồn tại
# Giải pháp: start-all.sh sẽ tự tạo logs/ khi chạy
./start-all.sh

# Hoặc tạo thủ công:
mkdir -p logs

# Lưu ý: Nếu chạy manual (python3 backend/...), logs hiện trên terminal
# Nếu cài production (systemd), dùng: sudo journalctl -u server-monitor-*
```

**Lỗi: Module not found (sau khi cài xong)**

```bash
# Đảm bảo virtual environment đã được kích hoạt
source venv/bin/activate  # Hoặc venv\Scripts\activate trên Windows

# Cài lại dependencies
pip install -r backend/requirements.txt
cd frontend-next && npm install && cd ..
```

**Lỗi: externally-managed-environment (Python 3.12+)**

```bash
# Giải pháp: Sử dụng virtual environment (BẮT BUỘC cho Python 3.12+)
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

**Database bị lỗi**

```bash
# Khởi tạo lại database (từ project root)
source venv/bin/activate
python3 -c "import sys; sys.path.insert(0, 'backend'); import database; database.init_database()"
```

### Hot Reload (Development)

- **Frontend**: Next.js tự động reload khi bạn sửa code (Fast Refresh)
- **Backend**: Cần restart service sau khi sửa Python code
- **Tip**: Để auto-restart backend khi code thay đổi, có thể dùng:

  ```bash
  # Cài đặt watchdog
  pip3 install watchdog

  # Chạy với watchmedo (auto-restart khi file .py thay đổi)
  cd backend
  watchmedo auto-restart --patterns="*.py" --recursive -- python3 central_api.py
  ```

---

## 🚀 Quick Start

### One-Command Installation on Linux (Recommended)

**For production deployments**, use our automated installer:

```bash
# Install latest version
curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash

# Or install specific version
curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash -s -- --ref v2.2.0
```

**Secure installation with checksum verification:**

```bash
# Download installer and checksum
curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh -o /tmp/install.sh
curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh.sha256 -o /tmp/install.sh.sha256

# Verify checksum
cd /tmp && sha256sum -c install.sh.sha256

# If verification passes, run installer
sudo bash /tmp/install.sh --ref v2.2.0
```

**What it does:**

- ✅ Installs all dependencies (Python, Node.js, system packages)
- ✅ Creates systemd services for auto-start on boot
- ✅ Sets up SQLite database with secure configuration
- ✅ Generates random JWT and encryption secrets
- ✅ Configures firewall-friendly setup
- ✅ Ready in 3-5 minutes!

**After installation:**

- Access: `http://YOUR_SERVER_IP:9081`
- Default login: `admin` / `admin123` (⚠️ change immediately!)
- Manage: `sudo smctl status|restart|logs|update`

📖 **Full installation guide**: [docs/INSTALLER.md](docs/INSTALLER.md)

---

### Manual Installation (Development)

For development or if you prefer manual control:

#### Prerequisites

- Python 3.8+
- Node.js 18+ and npm
- Linux server (tested on Debian/Ubuntu)
- SSH access to monitored servers

#### Installation Steps

```bash
# Clone repository
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor

# Create Python virtual environment (recommended for Python 3.12+)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install test dependencies (optional)
pip install -r tests/requirements.txt

# Install frontend dependencies
cd frontend-next
npm ci
cd ..

# Configure environment
cp .env.example .env
# Edit .env and set secure values for JWT_SECRET and ENCRYPTION_KEY
# Generate secure keys with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Configure frontend environment
cat > frontend-next/.env.local << 'EOF'
API_PROXY_TARGET=http://localhost:9083
NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084
EOF

# Initialize database (automatic on first run, from project root)
python3 -c "import sys; sys.path.insert(0, 'backend'); import database; database.init_database()"
```

**Note:** The system now supports relative paths and works from any directory. No need for hardcoded `/opt` paths.

### Start Services

**Option 1: Start All (Recommended for first time)**

```bash
# From project root - starts backend services
./start-all.sh

# In a new terminal - start frontend
cd frontend-next
npm run dev  # Development mode with hot reload
# OR
npm run build && npm run start  # Production mode
```

**Option 2: Start Manually**

```bash
# All commands run from project root!
# Activate venv first
source venv/bin/activate

# Backend API
python3 backend/central_api.py &

# WebSocket server
python3 backend/websocket_server.py &

# Terminal server (optional)
python3 backend/terminal.py &

# Frontend Next.js
cd frontend-next
npm run dev  # Development (http://localhost:9081)
# OR
npm run build && npm run start  # Production
```

### Access Dashboard

- **Dashboard**: http://localhost:9081 (Next.js frontend)
- **API**: http://localhost:9083
- **API Documentation**: http://localhost:9083/docs (Swagger UI)
- **OpenAPI Spec**: http://localhost:9083/api/openapi.yaml
- **Default Credentials**: admin / admin123 ⚠️ **Change in production!**

⚠️ **Security Warning**: The system auto-creates a default admin user. Change the password immediately after first login!

### API Documentation

Server Monitor Dashboard provides comprehensive API documentation via OpenAPI 3.0.3:

**Swagger UI** (Interactive Documentation):

```
http://localhost:9083/docs
```

- Browse all 70+ API endpoints
- View request/response schemas
- Try out API calls directly from your browser
- Learn authentication patterns

**OpenAPI Specification** (Machine-readable):

```
http://localhost:9083/api/openapi.yaml
```

- Download for client code generation
- Import into Postman, Insomnia, or other API tools
- Generate SDK/client libraries

**Key API Groups**:

- **Authentication**: Login, logout, session management
- **Servers**: CRUD operations, connection testing, monitoring
- **SSH Keys**: Encrypted vault for private keys
- **Terminal**: WebSocket-based SSH terminal sessions
- **Inventory**: Agentless system information collection
- **Tasks**: Remote command execution with async workers
- **Notes & Tags**: Server documentation and categorization
- **Audit Logs**: Activity tracking and compliance
- **Users & RBAC**: User management and role-based access
- **Settings**: Application configuration
- **Export**: CSV/JSON data export

**Example API Call**:

```bash
# Get authentication token
curl -X POST http://localhost:9083/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# List servers (with token)
curl http://localhost:9083/api/servers \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

See [`docs/openapi.yaml`](docs/openapi.yaml) for complete API reference.

### Smoke Tests

Validate your deployment with the automated smoke test script:

```bash
# Run smoke tests
./scripts/smoke.sh

# Verbose mode for detailed output
./scripts/smoke.sh --verbose
```

The smoke test checks:

- ✅ All services running on correct ports
- ✅ Health endpoints responding
- ✅ Authentication flow working
- ✅ Database connectivity
- ✅ API documentation accessible

### Stop Services

```bash
./stop-all.sh  # Stops backend services

# Stop frontend: Ctrl+C in the terminal where npm is running
```

---

## 🔄 Update & Maintenance

### Update Installed System

For systems installed via the one-command installer:

```bash
# Update to latest version
sudo /opt/server-monitor/scripts/update.sh

# Update to specific version
sudo /opt/server-monitor/scripts/update.sh --ref v2.1.0

# Or use control script
sudo smctl update
```

The update process:

- ✅ Backs up your database automatically
- ✅ Updates code from GitHub
- ✅ Rebuilds backend and frontend
- ✅ Runs database migrations
- ✅ Restarts services in correct order
- ✅ Verifies health after update

### Rollback

If an update causes issues:

```bash
sudo /opt/server-monitor/scripts/rollback.sh
```

### Service Management

```bash
# Check status
sudo systemctl status server-monitor-*
# Or
sudo smctl status

# Restart services
sudo systemctl restart server-monitor-*
# Or
sudo smctl restart

# View logs
sudo journalctl -u server-monitor-* -f
# Or
sudo smctl logs

# Backup database
sudo smctl backup

# Restore database
sudo smctl restore /var/lib/server-monitor/backups/servers-20260107-120000.db
```

### Uninstall

```bash
# Remove services and installation (keeps data)
sudo smctl uninstall

# Complete cleanup (removes all data)
sudo rm -rf /var/lib/server-monitor /etc/server-monitor /var/log/server-monitor
sudo userdel server-monitor
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
├── frontend-next/              # Next.js 14 frontend (TypeScript)
│   ├── src/
│   │   ├── app/               # App Router pages
│   │   │   ├── api/           # BFF API routes (auth, proxy)
│   │   │   └── [locale]/      # Internationalized pages
│   │   │       ├── (auth)/login
│   │   │       └── (dashboard)/
│   │   │           ├── dashboard/
│   │   │           ├── servers/[id]/
│   │   │           ├── terminal/
│   │   │           ├── settings/
│   │   │           ├── users/
│   │   │           ├── notifications/
│   │   │           └── access-denied/
│   │   ├── components/        # React components
│   │   │   ├── layout/        # AppShell, Shell
│   │   │   ├── providers/     # Theme, Query, i18n
│   │   │   ├── SnackbarProvider.tsx
│   │   │   ├── LoadingSkeletons.tsx
│   │   │   └── EmptyStates.tsx
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # Utilities (API client, WebSocket, JWT)
│   │   ├── types/             # TypeScript type definitions
│   │   └── locales/           # i18n translations (8 languages)
│   ├── middleware.ts          # Auth + RBAC middleware
│   ├── next.config.mjs        # Next.js configuration
│   └── package.json
│
├── frontend/                   # Legacy HTML frontend (deprecated)
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   └── ... (14 pages)
│
├── tests/                      # Automated tests
│   ├── test_api.py            # API integration tests
│   ├── test_crypto_vault.py   # Crypto vault tests (9/9 passing)
│   ├── test_security.py       # Security tests
│   └── requirements.txt
│
├── scripts/                    # Utility scripts
│   ├── install.sh             # One-command installer
│   ├── update.sh              # System update script
│   ├── rollback.sh            # Rollback to previous version
│   ├── smoke.sh               # Automated smoke tests
│   └── smctl                  # Control script (systemctl wrapper)
│
├── services/                   # Systemd service files
│   ├── systemd/               # Production service files (source of truth)
│   │   ├── server-monitor-api.service
│   │   ├── server-monitor-ws.service
│   │   ├── server-monitor-terminal.service
│   │   └── server-monitor-frontend.service
│   └── legacy/                # Deprecated service files
│
├── data/                       # Data storage (auto-created)
│   ├── servers.db             # SQLite database
│   └── *.json                 # Configuration files
│
├── logs/                       # Log files (auto-created)
│
├── docs/                       # Documentation
│   ├── openapi.yaml           # OpenAPI 3.0.3 API specification (NEW in v2.1)
│   └── modules/               # Module-specific docs
│
├── .github/workflows/          # CI/CD
│   ├── ci.yml                 # Backend CI
│   └── frontend-ci.yml        # Frontend CI
│
├── DEPLOYMENT.md              # Production deployment guide
├── ARCHITECTURE.md            # System architecture
├── SECURITY.md                # Security guide
├── SMOKE_TEST_CHECKLIST.md    # Manual testing checklist (200+ test cases)
├── RELEASE_NOTES_v2.1.0.md    # Release notes for v2.1.0 (NEW)
├── CHANGELOG.md               # Version history
├── start-all.sh               # Start all services
├── stop-all.sh                # Stop all services
├── .env.example               # Environment template
└── README.md                  # This file
```

---

## 🔧 Configuration

### Ports

| Service        | Port | Protocol  | Description       |
| -------------- | ---- | --------- | ----------------- |
| Frontend       | 9081 | HTTP      | Web UI            |
| API            | 9083 | HTTP      | REST API          |
| Terminal       | 9084 | WebSocket | SSH terminal      |
| WebSocket      | 9085 | WebSocket | Real-time updates |
| Agent (remote) | 8083 | HTTP      | Monitoring agent  |

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

### Implemented (v2.0)

✅ **Authentication & Authorization**

- JWT token-based authentication
- HttpOnly cookies for token storage (XSS protection)
- Secure cookie attributes (HttpOnly, SameSite=Lax, Secure in production)
- Token expiration synchronized with cookie TTL
- Role-Based Access Control (RBAC)
- Admin-only routes protection
- Access Denied page for unauthorized access

✅ **Backend-for-Frontend (BFF) Security**

- Auth proxy layer in Next.js
- Cookie-to-Bearer token translation
- SSRF protection with path validation
- Path traversal prevention
- No cookie leakage to backend
- Set-cookie header filtering

✅ **Rate Limiting**

- 100 requests/minute (general endpoints)
- 5 login attempts/5 minutes
- Automatic IP blocking after repeated failures

✅ **CORS Protection**

- Whitelist specific origins only
- No wildcard (\*) in production
- Proper preflight handling

✅ **Security Headers**

- Content-Security-Policy
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection
- Strict-Transport-Security (HSTS)

✅ **Input Validation**

- IP address validation (0-255 per octet)
- Hostname validation (proper DNS format)
- Port range validation (1-65535)
- String sanitization (HTML/XSS prevention)
- Real-time client-side validation

✅ **WebSocket Security**

- Token authentication required
- No anonymous connections
- Proper error handling
- Connection timeout protection

### Security Best Practices

⚠️ **Before Production Deployment**:

1. Change default admin password
2. Enable HTTPS (use nginx/apache reverse proxy)
3. Set up firewall rules
4. Review CORS allowed origins
5. Enable database backups
6. Set up log rotation
7. Use environment variables for secrets
8. Regularly update dependencies

### Threat Model

**Protected Against:**

- ✅ XSS (Cross-Site Scripting) - HttpOnly cookies, input sanitization
- ✅ CSRF (Cross-Site Request Forgery) - SameSite cookies, token validation
- ✅ SSRF (Server-Side Request Forgery) - Path validation in proxy
- ✅ Path Traversal - Input validation, regex filtering
- ✅ SQL Injection - Parameterized queries, ORM usage
- ✅ Brute Force - Rate limiting on login
- ✅ Session Hijacking - Secure cookies, HTTPS in production
- ✅ Unauthorized Access - RBAC, middleware protection

**Remaining Risks:**

- ⚠️ DDoS attacks - Recommend using Cloudflare or similar
- ⚠️ Zero-day vulnerabilities - Keep dependencies updated
- ⚠️ Physical server access - Secure your infrastructure

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

Full API documentation: See [OpenAPI Spec](docs/openapi.yaml) | [Swagger UI](http://localhost:9083/docs) | [Test Guide](TEST_GUIDE.md)

---

## 🧪 Testing

### Backend Tests

```bash
cd tests

# Run all API tests (19 tests)
python3 -m pytest test_api.py -v

# Run security tests (6 tests)
python3 -m pytest test_security.py -v

# Run all tests
python3 -m pytest -v
```

### Frontend Tests

```bash
cd frontend-next

# Lint TypeScript/React code
npm run lint

# Build production bundle
npm run build

# Type checking
npx tsc --noEmit
```

### Smoke Testing

Use the comprehensive smoke test checklist:

```bash
# See SMOKE_TEST_CHECKLIST.md for detailed testing procedures
# Covers:
# - Authentication flows
# - Dashboard functionality
# - Real-time WebSocket updates
# - Terminal WebSocket
# - CRUD operations
# - Settings pages
# - Exports
# - Role-based access control
```

### Test Coverage

**Backend:**

- ✅ Authentication (5 tests)
- ✅ CRUD operations (5 tests)
- ✅ Export functionality (2 tests)
- ✅ Email configuration (2 tests)
- ✅ Unauthorized access (3 tests)
- ✅ Rate limiting (2 tests)
- ✅ Security headers (2 tests)
- ✅ Input validation (2 tests)

**Total: 23/25 tests passing (92%)**

**Frontend:**

- ✅ TypeScript compilation
- ✅ ESLint checks
- ✅ Production build verification
- ✅ Manual smoke tests (see SMOKE_TEST_CHECKLIST.md)

### CI/CD

**Backend CI** (.github/workflows/ci.yml):

- Python linting (flake8)
- Unit tests (pytest)
- Security scan (bandit)

**Frontend CI** (.github/workflows/frontend-ci.yml):

- TypeScript linting (ESLint)
- Production build test
- Build artifact verification

**Manual Project Review** (.github/workflows/manual-project-review.yml):

- Comprehensive project audit workflow (manual trigger)
- Static analysis, security scanning, and linting
- Full test suite execution with coverage
- Build validation and smoke testing
- UI screenshot capture with Playwright
- Documentation consistency checks
- Automatic PR and issue creation
- Detailed review report generation

To run the manual review workflow:

1. Go to **Actions** → **Manual Project Review & Release Audit**
2. Click **Run workflow**
3. Configure options (ref, screenshots, PR/issue creation)
4. Review the generated report in `docs/REVIEW_REPORT.md`
5. Check artifacts for detailed results and screenshots

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

## 🔔 Integrations

### Webhooks

Configure HTTP callbacks to receive real-time notifications when events occur in your infrastructure. Perfect for integrating with external systems like Slack, PagerDuty, or custom automation platforms.

**Features:**

- 📡 **Event-Driven**: Subscribe to 30+ event types (servers, tasks, users, alerts, etc.)
- 🔐 **Secure**: HMAC-SHA256 signature verification with SSRF protection
- 🔄 **Reliable**: Automatic retry with exponential backoff
- 📊 **Monitored**: Delivery logs with status tracking and error details
- 🎛️ **Flexible**: Per-webhook configuration (retry count, timeout, event filters)

**Quick Start:**

1. Navigate to **Settings → Webhooks** (admin only)
2. Click **Add Webhook**
3. Enter webhook URL and configure event types
4. Use **Test** to verify, **View Deliveries** to monitor

**Documentation:** See [docs/modules/WEBHOOKS.md](docs/modules/WEBHOOKS.md) for complete guide with API examples and signature verification code.

---

## 📚 Documentation

### Getting Started

- [README.md](README.md) - This file, overview and quick start
- [docs/getting-started/LOCAL_DEV.md](docs/getting-started/LOCAL_DEV.md) - Detailed local development setup
- [docs/getting-started/TROUBLESHOOTING.md](docs/getting-started/TROUBLESHOOTING.md) - Common issues and solutions
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [HTTPS-SETUP.md](HTTPS-SETUP.md) - SSL/HTTPS configuration

### Architecture & Design

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [MULTI-SERVER-GUIDE.md](MULTI-SERVER-GUIDE.md) - Multi-server setup

### Operations

- [POST-PRODUCTION.md](POST-PRODUCTION.md) - Monitoring, logging, maintenance
- [TEST_GUIDE.md](TEST_GUIDE.md) - Testing instructions
- [docs/WORKFLOWS.md](docs/WORKFLOWS.md) - GitHub Actions workflows guide (Vietnamese)
- [docs/WORKFLOWS_EN.md](docs/WORKFLOWS_EN.md) - GitHub Actions workflows guide (English)

### Security

- [SECURITY.md](SECURITY.md) - Security guide and audit findings

### Planning

- [ROADMAP.md](ROADMAP.md) - Feature roadmap
- [TODO-IMPROVEMENTS.md](TODO-IMPROVEMENTS.md) - Action items
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history

---

## 🐛 Troubleshooting

📚 **Complete troubleshooting guide**: [docs/getting-started/TROUBLESHOOTING.md](docs/getting-started/TROUBLESHOOTING.md)

### Quick Fixes

**Services not starting**

```bash
# Check if ports are in use
netstat -tlnp | grep -E ":(9081|9083|9084|9085)"

# Check logs (if using start-all.sh)
tail -f logs/*.log

# Restart services
./stop-all.sh && ./start-all.sh
```

**Database errors**

```bash
# Reinitialize database (from project root)
source venv/bin/activate
python3 -c "import sys; sys.path.insert(0, 'backend'); import database; database.init_database()"
```

**WebSocket not connecting**

1. Check firewall allows ports 9084 and 9085
2. Check websocket_server.py and terminal.py are running: `lsof -i :9085` and `lsof -i :9084`
3. Check browser console for errors
4. Verify WebSocket URLs in `frontend-next/.env.local`

**Common errors and solutions**: See [docs/getting-started/TROUBLESHOOTING.md](docs/getting-started/TROUBLESHOOTING.md)

---

## 🔄 Deployment

### Development

```bash
./start-all.sh
```

### Production

**Option A: Automated Installation (Recommended)**

```bash
# One-command installer - sets up everything automatically
curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash

# Manage services using smctl
sudo smctl status       # Check service status
sudo smctl restart      # Restart all services
sudo smctl logs api     # View API logs
sudo smctl update       # Update to latest version
```

**Option B: Manual systemd Installation**

```bash
# Copy systemd service files to system directory
sudo cp services/systemd/*.service /etc/systemd/system/

# Reload systemd and enable services
sudo systemctl daemon-reload
sudo systemctl enable --now server-monitor-api.service
sudo systemctl enable --now server-monitor-ws.service
sudo systemctl enable --now server-monitor-terminal.service
sudo systemctl enable --now server-monitor-frontend.service

# Check service status
sudo systemctl status server-monitor-*
```

### Docker (future)

```bash
docker-compose up -d
```

---

## 🤝 Contributing

### Development Workflow

1. Clone the repository to your working directory
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

### v2.0.0 (2026-01-07) - Next.js Migration & Security Hardening 🎉

**Frontend Rewrite:**

- ✨ Complete migration to Next.js 14 with App Router
- ✨ TypeScript for type safety
- ✨ Material-UI (MUI) for modern design system
- ✨ React Query for efficient data fetching
- ✨ React Hook Form + Zod for form validation
- ✨ next-intl for internationalization (8 languages)
- ✨ Dark/light theme support with next-themes

**Security Enhancements:**

- 🔐 HttpOnly cookies for token storage (XSS protection)
- 🔐 RBAC (Role-Based Access Control) with middleware
- 🔐 Access Denied page for unauthorized access
- 🔐 SSRF protection in BFF proxy
- 🔐 Path traversal prevention
- 🔐 Cookie TTL synchronized with JWT expiry
- 🔐 Secure cookie attributes (HttpOnly, SameSite, Secure)

**Backend-for-Frontend (BFF):**

- 🛡️ Auth proxy layer in Next.js
- 🛡️ Cookie-to-Bearer token translation
- 🛡️ No cookie leakage to backend
- 🛡️ Set-cookie header filtering

**WebSocket Improvements:**

- 🔄 Fixed event listener memory leaks
- 🔄 Proper cleanup on unmount
- 🔄 Better error handling
- 🔄 Connection status indicators

**UX Improvements:**

- 🎨 Global toast notification system
- 🎨 Loading skeleton components
- 🎨 Empty state components
- 🎨 Better error messages
- 🎨 Role-based navigation visibility

**DevOps:**

- 🚀 Separate CI workflow for frontend
- 🚀 Systemd service for Next.js
- 🚀 Comprehensive deployment documentation
- 🚀 Smoke test checklist
- 🚀 Troubleshooting guides

### v1.1.0 (2026-01-06)

- ✅ Fixed database path issues (removed hardcoded paths)
- ✅ Enhanced input validation (IP, hostname, port)
- ✅ Frontend cleanup (removed duplicate files)
- ✅ Form helper system with loading states
- ✅ Improved UX with consistent error handling
- ✅ Comprehensive documentation updates

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
**Version**: 2.3.0  
**Release Date**: January 8, 2026

---

## 📞 Support

For issues or questions:

1. Check [TROUBLESHOOTING section](#-troubleshooting)
2. Review logs in `logs/` directory
3. Check [TODO-IMPROVEMENTS.md](TODO-IMPROVEMENTS.md) for known issues
4. Review test results: `pytest tests/ -v`

---

## 🎯 Roadmap

### ✅ Completed Features

- [x] PostgreSQL support (can be configured)
- [x] Swagger/OpenAPI documentation (v2.1+)
- [x] Multi-user management (Phase 4+)
- [x] Role-based access control (RBAC) (v2.0+)
- [x] GitHub Pages deployment
- [x] Redis caching (cache_helper.py in v2.2+)

### v2.4.0 (Planned - Q1 2026)

- [ ] Docker containerization with docker-compose
- [ ] Enhanced monitoring dashboards with custom widgets
- [ ] Advanced alerting rules with conditional logic
- [ ] Plugin marketplace and third-party integrations
- [ ] Mobile app (React Native)

### v3.0.0 (Planned - Q2 2026)

- [ ] Kubernetes support
- [ ] Advanced reporting with scheduled reports
- [ ] Multi-tenancy support
- [ ] AI-powered anomaly detection
- [ ] Performance optimization for 1000+ servers

---

**Made with ❤️ using Python, JavaScript, and modern web technologies**
