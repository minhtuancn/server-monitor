# 🚀 Multi-Server Monitoring System v3.0

**Hệ thống monitoring nhiều servers/LXC containers từ một Central Server**

## ✨ Tính năng chính

✅ **Monitor nhiều servers** - Quản lý unlimited servers từ một dashboard  
✅ **SSH-based** - Kết nối bảo mật qua SSH public key  
✅ **Real-time stats** - CPU, RAM, Disk, Network, Processes  
✅ **Remote control** - Kill processes, restart services qua SSH  
✅ **Auto-deploy agent** - Script tự động deploy lên remote servers  
✅ **Alert system** - Cảnh báo khi servers offline  
✅ **Database storage** - SQLite lưu danh sách servers  

## 📊 Kiến trúc

```
┌─────────────────────────────────┐
│   CENTRAL SERVER (Current)      │
│   - API: Port 9083              │
│   - Database: SQLite            │
│   - SSH Connection Pool         │
└─────────────┬───────────────────┘
              │ SSH Connections
    ┌─────────┼─────────┬─────────┐
    │         │         │         │
┌───▼────┐ ┌─▼──────┐ ┌▼──────┐ ┌▼──────┐
│ LXC #1 │ │ LXC #2 │ │ LXC #3│ │ LXC #N│
│ Agent  │ │ Agent  │ │ Agent │ │ Agent │
│:8083   │ │:8083   │ │:8083  │ │:8083  │
└────────┘ └────────┘ └───────┘ └───────┘
```

## 🎯 Quick Start

### 1. Cài đặt Dependencies

```bash
# Ubuntu/Debian
apt-get install python3-pip
pip3 install paramiko

# Test
python3 -c "import paramiko; print('✅ OK')"
```

### 2. Start Central Server

```bash
cd /opt/server-monitor-dev
./start-central.sh
```

Central Server chạy trên `http://localhost:9083`

### 3. Deploy Agent lên Remote Server

```bash
# Đảm bảo SSH key đã được setup
ssh-copy-id root@192.168.1.100

# Deploy agent
./deploy-agent.sh root@192.168.1.100
```

### 4. Add Server vào Central Database

```bash
curl -X POST http://localhost:9083/api/servers \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "LXC Container 1",
    "host": "192.168.1.100",
    "username": "root",
    "port": 22,
    "description": "Production LXC",
    "ssh_key_path": "~/.ssh/id_rsa",
    "agent_port": 8083
  }'
```

### 5. Get Monitoring Data

```bash
# From one server
curl http://localhost:9083/api/remote/stats/1 | jq

# From all servers
curl http://localhost:9083/api/remote/stats/all | jq
```

## 📁 Files Structure

```
/opt/server-monitor-dev/
├── 📄 docs/getting-started/MULTI_SERVER.md      ← This file
├── 📄 MULTI-SERVER-GUIDE.md       ← Detailed guide
├── 📄 SUMMARY.md                   ← Development summary
├── 📄 INSTALL.txt                  ← Quick install
│
├── 🗂️  backend/
│   ├── central_api.py              ← Central API server (NEW)
│   ├── agent.py                    ← Lightweight agent (NEW)
│   ├── database.py                 ← SQLite database (NEW)
│   ├── ssh_manager.py              ← SSH connections (NEW)
│   └── requirements.txt            ← Dependencies
│
├── 🗂️  data/
│   └── servers.db                  ← SQLite DB (auto-created)
│
├── 🚀 start-central.sh             ← Start central server
└── 🚀 deploy-agent.sh              ← Deploy agent script
```

## 🔧 API Endpoints

### Server Management
- `GET  /api/servers` - List servers
- `POST /api/servers` - Add server
- `PUT  /api/servers/<id>` - Update server
- `DELETE /api/servers/<id>` - Delete server
- `POST /api/servers/test` - Test SSH connection

### Remote Monitoring
- `GET /api/remote/stats/<id>` - Get server stats
- `GET /api/remote/stats/all` - Get all servers stats

### Remote Control
- `POST /api/remote/action/<id>` - Execute remote action
  - Kill process: `{"action_type": "kill_process", "action_data": {"pid": "1234"}}`
  - Restart service: `{"action_type": "service_action", "action_data": {"service": "nginx", "action": "restart"}}`
  - Docker control: `{"action_type": "docker_action", "action_data": {"container": "app", "action": "restart"}}`

### Agent Management
- `POST /api/remote/agent/deploy/<id>` - Deploy agent
- `POST /api/remote/agent/start/<id>` - Start agent

## 📚 Documentation

- **[MULTI-SERVER-GUIDE.md](MULTI-SERVER-GUIDE.md)** - Complete guide với examples
- **[SUMMARY.md](SUMMARY.md)** - Development summary & architecture
- **[INSTALL.txt](INSTALL.txt)** - Quick installation steps
- **[README-DEV.md](README-DEV.md)** - Original development guide

## ✅ Hoàn thành

- [x] Database module (SQLite)
- [x] SSH manager (connection pool)
- [x] Central API server (15 endpoints)
- [x] Lightweight agent (pure Python)
- [x] Deployment scripts
- [x] Documentation

## 🚧 TODO

- [ ] Frontend UI (multi-server dashboard)
- [ ] Server management UI
- [ ] Real-time polling
- [ ] WebSocket support
- [ ] Authentication
- [ ] Testing với nhiều LXC containers

## 🔐 Security

1. **SSH Key-based** - Không dùng password
2. **Public key** được hiển thị khi start: `./start-central.sh`
3. **Copy key** lên remote servers: `ssh-copy-id root@<host>`
4. **Test connection**: `POST /api/servers/test`

## 🐛 Troubleshooting

### Paramiko not found
```bash
pip3 install paramiko
```

### SSH connection failed
```bash
# Test manually
ssh root@192.168.1.100

# Copy key
ssh-copy-id root@192.168.1.100
```

### Port already in use
```bash
lsof -i:9083
kill -9 $(lsof -t -i:9083)
```

### Agent not running
```bash
ssh root@192.168.1.100
cat /tmp/agent.log
nohup python3 /opt/monitoring_agent.py > /tmp/agent.log 2>&1 &
```

## 📞 Examples

### Add multiple servers
```bash
for i in {100..105}; do
  curl -X POST http://localhost:9083/api/servers \
    -H 'Content-Type: application/json' \
    -d "{
      \"name\": \"LXC-$i\",
      \"host\": \"192.168.1.$i\",
      \"username\": \"root\",
      \"description\": \"Container $i\"
    }"
done
```

### Get all servers status
```bash
curl http://localhost:9083/api/servers | jq '.[] | {name, host, status}'
```

### Monitor all servers
```bash
watch -n 5 'curl -s http://localhost:9083/api/remote/stats/all | jq'
```

## 🎉 Success Indicators

Khi chạy thành công, bạn sẽ thấy:

```
╔══════════════════════════════════════════════════════════╗
║  Central Multi-Server Monitoring API v3                  ║
╚══════════════════════════════════════════════════════════╝

🚀 Server running on http://0.0.0.0:9083

📡 API Endpoints:
   • GET  /api/servers                - List all servers
   • POST /api/servers                - Add new server
   ...
```

## 📈 Next Steps

1. **Test với 1 LXC container** trước
2. **Deploy agent**: `./deploy-agent.sh root@<host>`
3. **Add server**: `curl -X POST http://localhost:9083/api/servers ...`
4. **Get stats**: `curl http://localhost:9083/api/remote/stats/1`
5. **Scale**: Add thêm servers

## 💡 Tips

- SSH key path mặc định: `~/.ssh/id_rsa`
- Agent port mặc định: `8083`
- Central API port: `9083`
- Database location: `/opt/server-monitor-dev/data/servers.db`
- Agent log on remote: `/tmp/agent.log`

---

**Version**: v3.0-dev  
**Date**: 2026-01-06  
**Status**: Backend Complete ✅  

**Created by OpenCode**
