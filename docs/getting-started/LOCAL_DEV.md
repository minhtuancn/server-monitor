# Local Development Setup Guide

This guide provides detailed instructions for setting up Server Monitor Dashboard on your local machine for development and testing purposes.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.8+** (check: `python3 --version`)
- **Node.js 18+** and npm (check: `node --version`)
- **Git** (check: `git --version`)
- **Operating System**: Linux/macOS (Windows requires WSL)
- **RAM**: Minimum 2GB
- **Disk Space**: ~500MB for code and dependencies

## Important: Working Directory

**⚠️ CRITICAL: All commands in this guide must be run from the project root directory.**

The project root is the directory that contains:
- `backend/` directory
- `frontend-next/` directory
- `start-all.sh` script
- `.env.example` file

### Verify You're in the Right Directory

Before proceeding, verify you're in the project root:

```bash
pwd
ls -la
```

You should see output like:
```
backend/
frontend-next/
start-all.sh
.env.example
README.md
...
```

If you don't see these files/directories, navigate to the project root first:

```bash
cd ~/server-monitor
# or wherever you cloned the repository
```

## Step-by-Step Setup

### 1. Clone the Repository

**If you haven't cloned the repository yet:**

```bash
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor
```

**If you already have the repository (update to latest):**

```bash
cd ~/server-monitor  # or wherever you cloned it
git pull
```

**If you want a fresh install (clean slate):**

```bash
# WARNING: This deletes your local repository and all local changes!
cd ~
rm -rf server-monitor
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor
```

**Troubleshooting: "destination path 'server-monitor' already exists"**

This error means you've already cloned the repository. You have two options:
1. Use `cd server-monitor && git pull` to update the existing repo
2. Use `rm -rf server-monitor` to delete it, then clone again

### 2. Create Python Virtual Environment

**For Python 3.12+**, virtual environments are required due to PEP 668:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows (WSL):
source venv/bin/activate

# On Windows (PowerShell):
# venv\Scripts\Activate.ps1
```

After activation, your prompt should show `(venv)` prefix.

### 3. Install Backend Dependencies

**Make sure your virtual environment is activated first!**

```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Optional: Install test dependencies
pip install -r tests/requirements.txt
```

This installs:
- `paramiko` - SSH connection management
- `PyJWT` - JWT authentication
- `python-dotenv` - Environment variables
- `cryptography` - Encryption for SSH keys
- `websockets` - WebSocket server (for real-time updates and terminal)

### 4. Install Frontend Dependencies

```bash
# Install Next.js dependencies
cd frontend-next
npm ci  # or npm install
cd ..
```

**Note**: Always return to project root after cd commands!

**About npm warnings**: You might see messages like `npm warn deprecated package@version`. These are warnings, not errors:
- Deprecated packages still work normally
- They won't block your development or build process
- Only worry if you see `npm ERR!` (which indicates actual errors)
- Warnings are safe to ignore for local development

### 5. Configure Environment Variables

Create the `.env` file in the project root:

```bash
# Copy example file
cp .env.example .env

# Generate secure keys
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))" >> .env
python3 -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(24))" >> .env
python3 -c "import secrets; print('KEY_VAULT_MASTER_KEY=' + secrets.token_urlsafe(32))" >> .env
```

**⚠️ Important**: If you run the key generation commands multiple times, delete the old keys from `.env` first to avoid duplicates.

### 6. Configure Frontend Environment

Create `.env.local` in the `frontend-next/` directory:

```bash
cat > frontend-next/.env.local << 'EOF'
API_PROXY_TARGET=http://localhost:9083
NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084
EOF
```

**Important notes about heredoc syntax:**
- The closing `EOF` must be on its own line with no spaces before or after it
- Use `'EOF'` (with single quotes) to prevent bash variable substitution
- If you see your terminal "hanging" after running this command, you likely didn't close the heredoc properly
- Press `Ctrl+C` to cancel and try again, ensuring EOF is on its own line

## Starting the Development Environment

You have two options for starting the services:

### Option 1: Automated Start (Recommended)

**Terminal 1 - Backend Services:**

```bash
# Ensure you're in project root
pwd  # Should show /path/to/server-monitor

# Activate virtual environment
source venv/bin/activate

# Start all backend services
./start-all.sh
```

This starts:
- Central API (port 9083)
- WebSocket Server (port 9085)
- Terminal Server (port 9084)

**Terminal 2 - Frontend:**

```bash
# Ensure you're in project root
cd frontend-next

# Start Next.js development server
npm run dev
```

### Reducing First-Load Lag (Optional but Recommended)

**Why is the first page load slow in dev mode?**

Next.js development mode compiles pages on-demand (cold start). The first time you visit a page or API route, Next.js needs to:
- Compile the TypeScript/React code
- Bundle dependencies
- Generate the page

This can take 4-5 seconds for the initial load. **This is normal development behavior** and does not happen in production builds.

**Solution 1: Use the warm-up script**

After starting your dev servers, run the warm-up script to pre-compile common routes:

```bash
# From project root (run in a 3rd terminal or after services are up)
./scripts/warmup-dev.sh
```

This will trigger compilation for:
- Dashboard pages (English and Vietnamese)
- Settings, Servers, Terminal, Users pages
- Common API proxy routes

**Solution 2: Test with production build**

To measure real performance (without dev compilation lag):

```bash
cd frontend-next

# Build production bundle (takes 1-2 minutes)
npm run build

# Start production server
npm run start
```

Production builds are fully pre-compiled and respond instantly.

**Accessing from LAN IP (e.g., 172.x.x.x)**

If you need to access the dev server from other devices on your network:

1. Set the `ALLOW_LAN` environment variable:
   ```bash
   # In frontend-next/.env.local, add:
   ALLOW_LAN=true
   ```

2. Restart the frontend dev server

3. Access using your machine's LAN IP:
   ```
   http://192.168.1.100:9081
   http://172.16.0.50:9081
   ```

This prevents Next.js "allowedDevOrigins" warnings when accessing from non-localhost IPs.

### Option 2: Manual Start (For Debugging)

**Terminal 1 - Central API:**

```bash
# From project root
source venv/bin/activate
python3 backend/central_api.py
```

**Terminal 2 - WebSocket Server:**

```bash
# From project root
source venv/bin/activate
python3 backend/websocket_server.py
```

**Terminal 3 - Terminal Server:**

```bash
# From project root
source venv/bin/activate
python3 backend/terminal.py
```

**Terminal 4 - Frontend:**

```bash
# From project root
cd frontend-next
npm run dev
```

## Accessing the Application

Once all services are running:

- **Dashboard**: http://localhost:9081
- **API Backend**: http://localhost:9083
- **API Documentation (Swagger)**: http://localhost:9083/docs
- **Health Check**: http://localhost:9083/api/health

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Change this password immediately after first login!**

## Verifying Services

Check if all services are running:

```bash
# Check ports
lsof -i :9081  # Frontend
lsof -i :9083  # API
lsof -i :9084  # Terminal WebSocket
lsof -i :9085  # Monitoring WebSocket

# Check API health
curl http://localhost:9083/api/health
```

## Viewing Logs

Logs are stored in different locations depending on how you started the services:

### Development Mode (start-all.sh)

Logs are in the `logs/` directory:

```bash
# View all logs
tail -f logs/*.log

# View specific service
tail -f logs/central_api.log
tail -f logs/websocket.log
tail -f logs/terminal.log
```

### Manual Start

When running services manually, logs appear in the terminal where the service was started.

### Production (systemd)

If installed as systemd services:

```bash
sudo journalctl -u server-monitor-api -f
sudo journalctl -u server-monitor-ws -f
sudo journalctl -u server-monitor-terminal -f
```

## Stopping Services

### Stop Backend Services

```bash
# From project root
./stop-all.sh
```

### Stop Frontend

Press `Ctrl+C` in the terminal running `npm run dev`

## Hot Reload / Development Workflow

- **Frontend (Next.js)**: Automatically reloads when you save files (Fast Refresh)
- **Backend (Python)**: Requires manual restart after code changes

### Auto-restart Backend (Optional)

Install watchdog for automatic backend restarts:

```bash
pip install watchdog

# Start API with auto-restart
cd backend
watchmedo auto-restart --patterns="*.py" --recursive -- python3 central_api.py
```

## Testing Your Setup

Try these quick tests:

1. **Add a test server**: Dashboard → Add Server
2. **View metrics**: Dashboard should show real-time updates
3. **Test terminal**: Terminal → Connect via SSH
4. **Test exports**: Servers → Export to CSV/JSON

## Common Development Tasks

### Reinitialize Database

```bash
# From project root
source venv/bin/activate
python3 -c "import sys; sys.path.insert(0, 'backend'); import database; database.init_database()"
```

### Run Backend Tests

```bash
# From project root
source venv/bin/activate
cd tests
python3 -m pytest test_api.py -v
python3 -m pytest test_security.py -v
```

### Run Frontend Linting

```bash
cd frontend-next
npm run lint
npx tsc --noEmit  # Type checking
```

### Build Frontend for Production

```bash
cd frontend-next
npm run build
npm run start  # Start production server
```

## Next Steps

- Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- See [ARCHITECTURE.md](../../ARCHITECTURE.md) to understand the system design
- Check [SECURITY.md](../../SECURITY.md) for security best practices
- Read [CONTRIBUTING.md](../../CONTRIBUTING.md) to contribute code

## Need Help?

If you encounter issues not covered in this guide:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review logs in the `logs/` directory
3. Search for similar issues in the GitHub repository
4. Open a new issue with detailed error messages
