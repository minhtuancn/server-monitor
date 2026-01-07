# Multi-Server Monitoring System - Quick Start Guide

**Version**: v3.0-dev  
**Date**: 2026-01-06  
**Type**: Multi-Server Central Monitoring

---

## 🎯 Tổng Quan

Hệ thống monitoring nhiều servers/LXC containers từ một Central Server thông qua SSH.

### Kiến Trúc:

```
┌─────────────────────────────────────────────┐
│        CENTRAL SERVER (Máy chủ trung tâm)  │
│  ┌──────────────────────────────────────┐  │
│  │  Backend API (Python + SQLite)        │  │
│  │  Port: 9083                            │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │  Frontend Dashboard (HTML/JS)         │  │
│  │  Port: 9081                            │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
              │ SSH Connections
    ┌─────────┼─────────┬─────────┐
    │         │         │         │
┌───▼────┐ ┌─▼──────┐ ┌▼──────┐ ┌▼──────┐
│ LXC #1 │ │ LXC #2 │ │ LXC #3│ │ LXC #N│
│ Agent  │ │ Agent  │ │ Agent │ │ Agent │
│:8083   │ │:8083   │ │:8083  │ │:8083  │
└────────┘ └────────┘ └───────┘ └───────┘
```

### Tính năng mới:

✅ **Monitor nhiều servers** từ một dashboard duy nhất  
✅ **SSH-based connection** - Bảo mật cao  
✅ **Quản lý servers** - Thêm/xóa/edit servers  
✅ **Real-time stats** từ tất cả servers  
✅ **Remote control** - Kill process, restart service qua SSH  
✅ **Auto-deploy agent** - Deploy script lên remote servers  
✅ **Alert system** - Cảnh báo khi servers offline/online  

---

## 📦 Cài Đặt

### Bước 1: Cài Dependencies

```bash
cd /opt/server-monitor-dev/backend/
pip3 install -r requirements.txt
```

**Dependencies:**
- `paramiko` - SSH library for Python

### Bước 2: Generate SSH Key (nếu chưa có)

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
```

Không cần passphrase (enter để bỏ qua).

### Bước 3: Copy SSH Public Key sang Remote Servers

```bash
ssh-copy-id root@<remote_server_ip>
```

Hoặc manual:

```bash
cat ~/.ssh/id_rsa.pub
# Copy output và paste vào remote server: ~/.ssh/authorized_keys
```

---

## 🚀 Khởi Động Central Server

### Cách 1: Sử dụng Start Script

```bash
cd /opt/server-monitor-dev/
./start-central.sh
```

### Cách 2: Manual

```bash
cd /opt/server-monitor-dev/backend/
python3 central_api.py
```

**Central Server sẽ chạy trên:**
- API: `http://localhost:9083`
- Frontend: `http://localhost:9081` (TODO)

---

## 📡 Deploy Agent lên Remote Servers

### Option 1: Sử dụng Deploy Script (Đơn giản nhất)

```bash
cd /opt/server-monitor-dev/
./deploy-agent.sh root@192.168.1.100
```

**Output:**
```
✅ SSH connection successful
✅ Python3 3.10.6
✅ Upload successful
✅ Agent is running successfully!
```

### Option 2: Manual Deploy

```bash
# 1. Upload agent script
scp /opt/server-monitor-dev/backend/agent.py root@192.168.1.100:/opt/agent.py

# 2. SSH vào remote server
ssh root@192.168.1.100

# 3. Chạy agent
nohup python3 /opt/agent.py > /tmp/agent.log 2>&1 &

# 4. Verify
curl http://localhost:8083/api/health
```

---

## 🎛️ Quản Lý Servers qua API

### 1. Lấy SSH Public Key

```bash
curl http://localhost:9083/api/ssh/pubkey
```

Copy key này và add vào remote servers.

### 2. Test SSH Connection

```bash
curl -X POST http://localhost:9083/api/servers/test \
  -H 'Content-Type: application/json' \
  -d '{
    "host": "192.168.1.100",
    "username": "root",
    "port": 22,
    "ssh_key_path": "~/.ssh/id_rsa"
  }'
```

**Response:**
```json
{"success": true, "message": "SSH connection successful"}
```

### 3. Thêm Server mới

```bash
curl -X POST http://localhost:9083/api/servers \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "LXC Container 1",
    "host": "192.168.1.100",
    "username": "root",
    "port": 22,
    "description": "Production LXC Container",
    "ssh_key_path": "~/.ssh/id_rsa",
    "agent_port": 8083,
    "tags": "lxc,production,web"
  }'
```

**Response:**
```json
{
  "success": true,
  "server_id": 1,
  "message": "Server LXC Container 1 added successfully"
}
```

### 4. Lấy Danh Sách Servers

```bash
curl http://localhost:9083/api/servers
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "LXC Container 1",
    "host": "192.168.1.100",
    "port": 22,
    "username": "root",
    "description": "Production LXC Container",
    "status": "online",
    "last_seen": "2026-01-06T10:30:00",
    "tags": "lxc,production,web"
  }
]
```

### 5. Lấy Stats từ Server

```bash
curl http://localhost:9083/api/remote/stats/1
```

**Response:** Toàn bộ monitoring data (CPU, RAM, processes, etc.)

### 6. Lấy Stats từ TẤT CẢ Servers

```bash
curl http://localhost:9083/api/remote/stats/all
```

### 7. Update Server

```bash
curl -X PUT http://localhost:9083/api/servers/1 \
  -H 'Content-Type: application/json' \
  -d '{
    "description": "Updated description",
    "tags": "lxc,staging"
  }'
```

### 8. Xóa Server

```bash
curl -X DELETE http://localhost:9083/api/servers/1
```

---

## 🎮 Remote Control qua SSH

### Kill Process trên Remote Server

```bash
curl -X POST http://localhost:9083/api/remote/action/1 \
  -H 'Content-Type: application/json' \
  -d '{
    "action_type": "kill_process",
    "action_data": {
      "pid": "1234"
    }
  }'
```

### Restart Service trên Remote Server

```bash
curl -X POST http://localhost:9083/api/remote/action/1 \
  -H 'Content-Type: application/json' \
  -d '{
    "action_type": "service_action",
    "action_data": {
      "service": "nginx.service",
      "action": "restart"
    }
  }'
```

### Docker Container Control

```bash
curl -X POST http://localhost:9083/api/remote/action/1 \
  -H 'Content-Type: application/json' \
  -d '{
    "action_type": "docker_action",
    "action_data": {
      "container": "my_container",
      "action": "restart"
    }
  }'
```

---

## 📊 API Endpoints Reference

### Server Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/servers` | Lấy danh sách tất cả servers |
| POST | `/api/servers` | Thêm server mới |
| GET | `/api/servers/<id>` | Lấy chi tiết server |
| PUT | `/api/servers/<id>` | Cập nhật server |
| DELETE | `/api/servers/<id>` | Xóa server |
| POST | `/api/servers/test` | Test SSH connection |

### Remote Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/remote/stats/<id>` | Lấy stats từ 1 server |
| GET | `/api/remote/stats/all` | Lấy stats từ TẤT CẢ servers |

### Remote Agent Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/remote/agent/deploy/<id>` | Deploy agent lên server |
| POST | `/api/remote/agent/start/<id>` | Start agent trên server |

### Remote Actions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/remote/action/<id>` | Execute remote action |

**Action types:**
- `kill_process` - Kill process by PID
- `service_action` - Start/stop/restart service
- `docker_action` - Docker container control

### Statistics & Alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats/overview` | Overview statistics |
| GET | `/api/alerts` | Lấy alerts |
| GET | `/api/ssh/pubkey` | Lấy SSH public key |

---

## 🔒 Security Best Practices

1. **SSH Keys only** - Không dùng password authentication
2. **Restricted keys** - Tạo SSH key riêng cho monitoring:
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/monitoring_key
   ```
3. **Limited permissions** - User monitoring chỉ có quyền đọc
4. **Firewall** - Chỉ allow SSH from Central Server IP
5. **Key rotation** - Thay đổi SSH keys định kỳ

---

## 🐛 Troubleshooting

### Problem: SSH connection failed

**Solution:**
```bash
# Test SSH manually
ssh -v root@192.168.1.100

# Check authorized_keys
ssh root@192.168.1.100 'cat ~/.ssh/authorized_keys'

# Copy key again
ssh-copy-id root@192.168.1.100
```

### Problem: Agent not running

**Solution:**
```bash
# SSH vào remote server
ssh root@192.168.1.100

# Check if agent is running
lsof -i:8083

# Check agent logs
cat /tmp/agent.log

# Restart agent
nohup python3 /opt/agent.py > /tmp/agent.log 2>&1 &
```

### Problem: Port 9083 already in use

**Solution:**
```bash
# Find process using port
lsof -i:9083

# Kill process
kill -9 $(lsof -t -i:9083)

# Restart central server
./start-central.sh
```

### Problem: paramiko not found

**Solution:**
```bash
pip3 install paramiko
```

---

## 📁 File Structure

```
/opt/server-monitor-dev/
├── backend/
│   ├── central_api.py          # Central API server
│   ├── agent.py                # Agent script for remote servers
│   ├── database.py             # SQLite database module
│   ├── ssh_manager.py          # SSH connection manager
│   ├── websocket_server.py     # WebSocket server
│   ├── terminal.py             # Web terminal service
│   ├── requirements.txt        # Python dependencies
│   └── legacy/                 # Deprecated files (not used)
│       ├── server_dashboard_api_v2.py  # Old single-server API
│       └── server_dashboard_api_v3.py  # Old backup
│
├── frontend/
│   ├── dashboard.html          # Old single-server UI
│   └── multi-dashboard.html    # TODO: Multi-server UI
│
├── frontend-next/              # Modern Next.js frontend
│   └── ...
│
├── data/
│   └── servers.db              # SQLite database (auto-created)
│
├── start-central.sh            # Start central server
├── deploy-agent.sh             # Deploy agent to remote
├── MULTI-SERVER-GUIDE.md       # This file
└── README-DEV.md               # Original dev guide
```

---

## 🎯 Next Steps

### TODO (Frontend):
- [ ] Create Multi-server Overview Dashboard UI
- [ ] Server Management UI (Add/Edit/Delete servers)
- [ ] Per-server Detail View
- [ ] Real-time updates (polling every 5s)

### TODO (Backend):
- [ ] WebSocket support for real-time updates
- [ ] Alert system (email/webhook)
- [ ] Historical data storage
- [ ] Authentication/Authorization

---

## 📞 Support

- Documentation: `/opt/server-monitor-dev/README-DEV.md`
- TODO List: `/opt/server-monitor-dev/TODO.md`
- Changelog: `/opt/server-monitor-dev/CHANGELOG.md`

---

**Happy Monitoring! 🚀**
