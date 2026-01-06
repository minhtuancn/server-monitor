# Server Monitor Dashboard v4.1

**Multi-server monitoring system với real-time updates, web terminal, và advanced security**

🚀 **Live Demo**: [http://your-server:9081](http://your-server:9081)  
📖 **Documentation**: [README.md](README.md)

---

## ⚠️ Security Notice

**IMPORTANT**: Kho này không chứa:
- ❌ Database files (`*.db`)
- ❌ SSH keys (private keys)
- ❌ Email configuration (SMTP passwords)
- ❌ Session tokens
- ❌ Log files

Các file này được liệt kê trong [.gitignore](.gitignore) và cần được cấu hình riêng cho mỗi môi trường.

---

## 🚀 Quick Deploy

### 1. Clone Repository

```bash
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor
```

### 2. Install Dependencies

```bash
# Backend dependencies
cd backend
pip3 install -r requirements.txt --break-system-packages

# Test dependencies (optional)
cd ../tests
pip3 install -r requirements.txt --break-system-packages
```

### 3. Initialize Database

```bash
cd backend
python3 -c "import database; database.init_database()"
```

### 4. Configure Email (Optional)

```bash
# Create email config file
cat > data/email_config.json << 'EOF'
{
  "enabled": false,
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your-email@gmail.com",
  "smtp_password": "your-app-password",
  "recipients": ["admin@example.com"]
}
EOF
```

### 5. Start Services

```bash
./start-all.sh
```

### 6. Access Dashboard

- **URL**: http://YOUR_SERVER_IP:9081
- **Default Login**: admin / admin123

**⚠️ CHANGE PASSWORD IMMEDIATELY AFTER FIRST LOGIN**

---

## 📦 What's Included

### Source Code
- ✅ Backend Python services
- ✅ Frontend HTML/CSS/JS
- ✅ Automated tests
- ✅ Documentation

### Not Included (Create Manually)
- ❌ `data/servers.db` - Will be auto-created on first run
- ❌ `data/email_config.json` - Create from template above
- ❌ SSH keys - Generate your own: `ssh-keygen -t rsa -b 4096`

---

## 🔐 Security Setup

### 1. Generate SSH Keys (for monitoring remote servers)

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/monitor_key
```

### 2. Change Default Password

```bash
# Login to dashboard and go to Settings > Change Password
# Or use API:
curl -X POST http://localhost:9083/api/auth/change-password \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"old_password": "admin123", "new_password": "NEW_SECURE_PASSWORD"}'
```

### 3. Configure Firewall

```bash
# Allow only necessary ports
ufw allow 9081/tcp  # Frontend
ufw allow 9083/tcp  # API
ufw enable
```

### 4. Enable HTTPS (Production)

```bash
# Use nginx or apache as reverse proxy with SSL
# See: docs/HTTPS_SETUP.md (future documentation)
```

---

## 📚 Documentation

- [README.md](README.md) - Full documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [IMPLEMENTATION_REPORT_V4.1.md](IMPLEMENTATION_REPORT_V4.1.md) - Latest features
- [API-TESTING-GUIDE.txt](API-TESTING-GUIDE.txt) - API testing guide
- [MULTI-SERVER-GUIDE.md](MULTI-SERVER-GUIDE.md) - Multi-server setup

---

## 🧪 Testing

```bash
cd tests
python3 -m pytest -v
```

---

## 🐛 Troubleshooting

### Issue: Database error on startup

```bash
# Reinitialize database
cd backend
python3 -c "import database; database.init_database()"
```

### Issue: Port already in use

```bash
# Stop all services
./stop-all.sh

# Check what's using the port
lsof -i :9083

# Restart
./start-all.sh
```

### Issue: SSH connection failed

```bash
# Test SSH manually
ssh -i ~/.ssh/monitor_key root@target-server

# Copy public key to target
ssh-copy-id -i ~/.ssh/monitor_key.pub root@target-server
```

---

## 📋 Project Structure

```
server-monitor/
├── backend/           # Python backend services
├── frontend/          # Web UI (HTML/JS/CSS)
├── tests/            # Automated tests
├── docs/             # Documentation
├── data/             # Database & config (not in git)
├── logs/             # Log files (not in git)
├── start-all.sh      # Start script
├── stop-all.sh       # Stop script
└── .gitignore        # Git ignore rules
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Proprietary - Internal use only

---

## 👨‍💻 Author

**minhtuancn**  
GitHub: [@minhtuancn](https://github.com/minhtuancn)

---

## ⭐ Features

- 🌐 Multi-server management
- 📊 Real-time metrics (WebSocket)
- 🖥️ Web terminal (SSH)
- 📧 Email alerts
- 📤 Export data (CSV/JSON)
- 🔒 Advanced security
- 🧪 Automated testing
- 🚀 Easy deployment

---

**Made with ❤️ using Python & JavaScript**
