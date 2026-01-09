# Quick Start Guide

Get Server Monitor running in 5 minutes!

**Last Updated**: 2026-01-09

---

## Prerequisites

- **Python 3.8+** (`python3 --version`)
- **Node.js 18+** (`node --version`)
- **Linux/macOS** (Windows requires WSL)
- **2GB RAM** minimum
- **~500MB disk** for code and dependencies

---

## Local Development (5 Minutes)

### 1. Clone Repository

```bash
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor
```

### 2. Start Services

```bash
# Automatically installs dependencies and starts all services
./start-dev.sh
```

### 3. Access Dashboard

```bash
open http://localhost:9081
```

**First-run setup**: You'll be redirected to `/setup` to create your admin account.

---

## Production Deployment (One Command)

### Option 1: Quick Install (Ubuntu/Debian)

```bash
# Downloads and runs installer
curl -sSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/installer.sh | bash
```

### Option 2: Manual Install

```bash
# Clone and run installer
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor
./installer.sh
```

The installer:

- ✅ Installs dependencies
- ✅ Creates systemd services
- ✅ Sets up auto-start on boot
- ✅ Configures firewall
- ✅ Generates secure keys

---

## Custom Domain Deployment

Deploy to `mon.go7s.net` or any domain:

### Quick Setup

```bash
# Run interactive setup script
./setup-custom-domain.sh mon.go7s.net

# Start with custom domain
CUSTOM_DOMAIN=mon.go7s.net ./start-all.sh
```

### Manual Configuration

1. Set environment variables:

   ```bash
   echo "ALLOWED_FRONTEND_DOMAINS=mon.go7s.net" >> backend/.env
   ```

2. Update frontend `.env.local`:

   ```bash
   NEXT_PUBLIC_MONITORING_WS_URL=wss://mon.go7s.net/ws/monitoring
   NEXT_PUBLIC_TERMINAL_WS_URL=wss://mon.go7s.net/ws/terminal
   NEXT_PUBLIC_DOMAIN=mon.go7s.net
   NODE_ENV=production
   ```

3. Configure reverse proxy (Nginx/Caddy)

See [CUSTOM-DOMAIN-GUIDE.md](/CUSTOM-DOMAIN-GUIDE.md) for details.

---

## Default Ports

| Service     | Port | Purpose                |
| ----------- | ---- | ---------------------- |
| Frontend    | 9081 | Next.js dashboard      |
| Backend API | 9083 | REST API               |
| Terminal    | 9084 | SSH terminal WebSocket |
| Monitoring  | 9085 | Metrics WebSocket      |

**Firewall**: Open ports if accessing from other machines.

---

## First-Run Setup

1. **Visit dashboard**: http://localhost:9081
2. **Create admin**: Redirected to `/setup` page
3. **Fill form**:
   - Username (3+ chars)
   - Email (valid format)
   - Password (8+ chars, uppercase, lowercase, digit)
4. **Login**: Auto-logged in after setup

---

## Verify Installation

### Check Services

```bash
# Check all services running
./scripts/check-services.sh

# Or manually:
lsof -i:9081  # Frontend
lsof -i:9083  # API
lsof -i:9084  # Terminal
lsof -9085    # WebSocket
```

### Run Smoke Tests

```bash
# Run full smoke test suite
./scripts/smoke-test.sh

# Or check checklist:
cat SMOKE_TEST_CHECKLIST.md
```

---

## Common Issues

### "Port already in use"

```bash
# Kill process on port
lsof -ti:9081 | xargs -r kill -9

# Or stop all services
./stop-all.sh
```

### "Module not found" (Python)

```bash
# Reinstall backend dependencies
cd backend
pip install -r requirements.txt
```

### "Module not found" (Node.js)

```bash
# Reinstall frontend dependencies
cd frontend-next
rm -rf node_modules .next
npm install
```

### Database errors

```bash
# Fresh start (WARNING: deletes data!)
rm data/servers.db
./start-dev.sh
```

### Can't access from other machines

```bash
# Check firewall
sudo ufw allow 9081/tcp
sudo ufw allow 9083/tcp

# Or disable firewall (dev only!)
sudo ufw disable
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more.

---

## Next Steps

### Add Servers

1. Go to **Servers** → **Add Server**
2. Enter server details (hostname, SSH credentials)
3. Test connection
4. View metrics on dashboard

### Configure Alerts

1. Go to **Settings** → **Integrations**
2. Configure Email, Telegram, or Slack
3. Set alert thresholds per server

### Explore Features

- **Dashboard**: Real-time metrics
- **Terminal**: SSH into servers via browser
- **Inventory**: View system info
- **Tasks**: Run remote commands
- **Notes**: Document server details
- **Webhooks**: Integrate with external services

---

## Resources

- **Full Documentation**: [docs/README.md](/docs/README.md)
- **Custom Domain**: [CUSTOM-DOMAIN-GUIDE.md](/CUSTOM-DOMAIN-GUIDE.md)
- **HTTPS Setup**: [HTTPS-SETUP.md](/HTTPS-SETUP.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Architecture**: [ARCHITECTURE.md](/ARCHITECTURE.md)
- **API Docs**: http://localhost:9083/docs (Swagger UI)

---

## Development Workflow

### Start Development

```bash
./start-dev.sh
```

### Run Tests

```bash
# Backend
cd backend && pytest tests/ -v

# Frontend
cd frontend-next && npm run lint && npm run build
```

### Watch Logs

```bash
tail -f logs/api.log
tail -f logs/websocket.log
tail -f logs/web.log
```

### Stop Services

```bash
./stop-all.sh
```

---

**Need help?** See [docs/getting-started/TROUBLESHOOTING.md](TROUBLESHOOTING.md) or [open an issue](https://github.com/minhtuancn/server-monitor/issues)!
