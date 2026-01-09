# Troubleshooting Guide

This guide covers common issues you might encounter when setting up or running Server Monitor Dashboard in local development mode.

## Table of Contents

1. [Clone/Repository Issues](#clonerepository-issues)
2. [Wrong Directory Issues](#wrong-directory-issues)
3. [Virtual Environment Issues](#virtual-environment-issues)
4. [Missing Dependencies](#missing-dependencies)
5. [npm Warnings](#npm-warnings)
6. [Environment File Creation Issues](#environment-file-creation-issues)
7. [Port Already in Use](#port-already-in-use)
8. [Database Issues](#database-issues)
9. [Log File Issues](#log-file-issues)
10. [WebSocket Connection Issues](#websocket-connection-issues)
11. [Frontend Build Issues](#frontend-build-issues)
12. [Permission Issues](#permission-issues)

---

## Clone/Repository Issues

### Symptom: `fatal: destination path 'server-monitor' already exists`

**Cause**: You're trying to clone into a directory that already exists.

**Solution**:

```bash
# Option 1: Update the existing repository (RECOMMENDED)
cd server-monitor
git pull

# Option 2: Clone to a different directory
git clone https://github.com/minhtuancn/server-monitor.git server-monitor-new
cd server-monitor-new

# Option 3: Delete and re-clone (WARNING: loses local changes!)
rm -rf server-monitor
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor
```

**Best Practice**: If you already have the repo, use `git pull` to update instead of cloning again.

---

## Wrong Directory Issues

### Symptom: `source venv/bin/activate: No such file or directory`

**Cause**: You're not in the project root directory, or you haven't created the virtual environment yet.

**Solution**:

```bash
# Check your current directory
pwd

# You should see: /path/to/server-monitor
# If not, navigate to project root:
cd /path/to/server-monitor

# Verify you're in the right place
ls -la
# Should show: backend/ frontend-next/ start-all.sh .env.example

# If venv doesn't exist, create it:
python3 -m venv venv

# Then activate it:
source venv/bin/activate
```

### Symptom: `cd backend: No such file or directory`

**Cause**: You're already inside the `backend/` directory trying to `cd` into it again, or you're in the wrong location.

**Solution**:

```bash
# Check where you are
pwd

# If you see /path/to/server-monitor/backend, you're already in backend
# Don't run 'cd backend' again

# Navigate back to project root:
cd ..  # or cd /path/to/server-monitor

# Verify:
ls -la  # Should show backend/ directory
```

**Best Practice**: Always run commands from the project root unless explicitly instructed otherwise.

---

## Virtual Environment Issues

### Symptom: `externally-managed-environment` error (Python 3.12+)

**Cause**: PEP 668 prevents installing packages globally on Python 3.12+ to protect system Python.

**Solution**: Always use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Symptom: Virtual environment not activated

**Cause**: Forgot to activate the virtual environment before running Python commands.

**Solution**:

```bash
# Check if venv is activated
# Your prompt should show: (venv)

# If not, activate it:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Verify activation
which python3
# Should show: /path/to/server-monitor/venv/bin/python3
```

---

## Missing Dependencies

### Symptom: `ModuleNotFoundError: No module named 'paramiko'`

**Cause**: Backend dependencies not installed, or virtual environment not activated.

**Solution**:

```bash
# Activate virtual environment first!
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Verify installation
python3 -c "import paramiko; print('paramiko installed')"
```

### Symptom: `ModuleNotFoundError: No module named 'websockets'`

**Cause**: Missing `websockets` dependency required by `websocket_server.py` and `terminal.py`.

**Solution**:

```bash
# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
pip install -r backend/requirements.txt

# Verify websockets is installed
python3 -c "import websockets; print(f'websockets {websockets.__version__} installed')"
```

### Symptom: Frontend errors about missing npm packages

**Cause**: Node modules not installed.

**Solution**:

```bash
cd frontend-next

# Remove existing node_modules and package-lock if corrupted
rm -rf node_modules package-lock.json

# Clean install
npm ci

# Or regular install
npm install

cd ..
```

---

## npm Warnings

### Symptom: `npm warn deprecated package@version` during npm install

**Cause**: Some packages in the dependency tree are marked as deprecated by their maintainers.

**Is this a problem?**: **NO!** These are warnings, not errors.

**Explanation**:
- Deprecated packages still function correctly
- They won't prevent your application from running
- npm only shows these as informational warnings
- You only have a real problem if you see `npm ERR!` (not `npm warn`)

**Example of normal warnings (safe to ignore)**:
```
npm warn deprecated inflight@1.0.6: This module is not supported
npm warn deprecated glob@7.2.3: Glob versions prior to v9 are no longer supported
npm warn deprecated @humanwhocodes/config-array@0.11.14: Use @eslint/config-array instead
```

**When to worry**:
```
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
```

**Action**: Only investigate if:
- `npm install` exits with non-zero status code
- You see `npm ERR!` messages
- Your application fails to start due to missing packages

**Solution**: For local development, you can safely ignore npm warnings. For production, consider updating dependencies periodically.

---

## Environment File Creation Issues

### Symptom: Terminal "hangs" after running heredoc command, or `.env.local` has wrong content

**Cause**: Incorrect heredoc syntax when creating `frontend-next/.env.local`.

**Common mistakes**:
1. Not closing the heredoc with `EOF`
2. Having spaces/tabs before the closing `EOF`
3. Using `EOF` without quotes (causes variable expansion)
4. Typo in closing delimiter (e.g., `EOFT` instead of `EOF`)

**Correct syntax**:

```bash
cat > frontend-next/.env.local << 'EOF'
API_PROXY_TARGET=http://localhost:9083
NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084
EOF
```

**Key points**:
- Use `'EOF'` with single quotes to prevent bash variable expansion
- The closing `EOF` must be on its own line
- No spaces or tabs before `EOF`
- No text after `EOF` on that line

**If terminal is hanging**:

```bash
# Press Ctrl+C to cancel the command
# Then re-run with correct syntax

# Verify the file was created correctly:
cat frontend-next/.env.local

# Should show exactly:
# API_PROXY_TARGET=http://localhost:9083
# NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
# NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084
```

**Alternative method (if heredoc is problematic)**:

```bash
# Create file manually with echo
echo "API_PROXY_TARGET=http://localhost:9083" > frontend-next/.env.local
echo "NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085" >> frontend-next/.env.local
echo "NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084" >> frontend-next/.env.local

# Or use a text editor
nano frontend-next/.env.local
# Then paste the content and save with Ctrl+O, Exit with Ctrl+X
```

---

## Port Already in Use

### Symptom: `Address already in use` or `Port 9083 already in use`

**Cause**: A service is already running on the port.

**Solution**:

```bash
# Find process using the port
lsof -i :9083
lsof -i :9085
lsof -i :9084
lsof -i :9081

# Kill the process (try graceful shutdown first)
# Replace <PID> with the actual process ID from lsof
kill <PID>

# If it doesn't stop, force kill:
kill -9 <PID>

# Or kill by port:
lsof -ti:9083 | xargs kill
lsof -ti:9085 | xargs kill
lsof -ti:9084 | xargs kill
lsof -ti:9081 | xargs kill

# Then restart services
./start-all.sh
```

---

## Database Issues

### Symptom: Database corruption or locked database

**Cause**: Multiple processes accessing database simultaneously, or improper shutdown.

**Solution**:

```bash
# Stop all services first
./stop-all.sh

# Backup current database (optional)
cp data/servers.db data/servers.db.backup

# Reinitialize database
source venv/bin/activate
python3 -c "import sys; sys.path.insert(0, 'backend'); import database; database.init_database()"

# Restart services
./start-all.sh
```

### Symptom: `no such table` errors

**Cause**: Database not initialized.

**Solution**:

```bash
source venv/bin/activate
python3 -c "import sys; sys.path.insert(0, 'backend'); import database; database.init_database()"
```

---

## Log File Issues

### Symptom: `tail -f logs/*.log: No such file or directory`

**Cause**: The `logs/` directory doesn't exist yet, or logs are stored elsewhere.

**Solution**:

**For development mode (start-all.sh)**:

```bash
# Check if logs directory exists
ls -la logs/

# If it doesn't exist, start-all.sh will create it
./start-all.sh

# Then view logs
tail -f logs/*.log
```

**For manual start**:

When running services manually (e.g., `python3 backend/central_api.py`), logs appear in the terminal where the service was started. There are no log files created.

**For production (systemd)**:

```bash
# View systemd logs
sudo journalctl -u server-monitor-api -f
sudo journalctl -u server-monitor-ws -f
sudo journalctl -u server-monitor-terminal -f
```

### Symptom: Cannot find logs anywhere

**Check where logs are actually stored**:

```bash
# Check start-all.sh to see log locations
grep "LOGS_DIR" start-all.sh

# Check if logs are in project root
ls -la logs/

# Check if logs are in /tmp
ls -la /tmp/*.log | grep server-monitor

# Check systemd logs (if running as service)
sudo journalctl -u server-monitor-* --since "10 minutes ago"
```

---

## WebSocket Connection Issues

### Symptom: Dashboard shows "WebSocket disconnected" or real-time updates not working

**Cause**: WebSocket server not running, firewall blocking port, or incorrect URL.

**Solution**:

```bash
# 1. Verify WebSocket server is running
lsof -i :9085

# 2. Check WebSocket server logs
tail -f logs/websocket.log

# 3. Test WebSocket connection
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" http://localhost:9085

# 4. Restart WebSocket server
source venv/bin/activate
python3 backend/websocket_server.py

# 5. Check frontend WebSocket URL configuration
cat frontend-next/.env.local
# Should have: NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
```

### Symptom: Terminal WebSocket not connecting

**Solution**:

```bash
# 1. Verify Terminal server is running
lsof -i :9084

# 2. Check Terminal server logs
tail -f logs/terminal.log

# 3. Restart Terminal server
source venv/bin/activate
python3 backend/terminal.py

# 4. Check frontend terminal URL
cat frontend-next/.env.local
# Should have: NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084
```

---

## Frontend Build Issues

### Symptom: Next.js build fails

**Cause**: TypeScript errors, missing dependencies, or configuration issues.

**Solution**:

```bash
cd frontend-next

# 1. Clean install dependencies
rm -rf node_modules package-lock.json .next
npm ci

# 2. Check TypeScript errors
npx tsc --noEmit

# 3. Run linter
npm run lint

# 4. Try dev mode first
npm run dev

# 5. Then build
npm run build

cd ..
```

### Symptom: `NEXT_PUBLIC_*` environment variables not working

**Cause**: Environment variables not properly set or frontend not restarted after changes.

**Solution**:

```bash
# 1. Verify .env.local exists
cat frontend-next/.env.local

# 2. Restart Next.js (stop with Ctrl+C)
cd frontend-next
npm run dev

# Note: NEXT_PUBLIC_* variables are embedded at build time
# For production builds, rebuild after changing them:
npm run build
npm run start
```

---

## Permission Issues

### Symptom: `Permission denied` when running scripts

**Cause**: Script files don't have execute permission.

**Solution**:

```bash
# Add execute permission
chmod +x start-all.sh
chmod +x stop-all.sh
chmod +x start-dev.sh
chmod +x stop-dev.sh

# Then run
./start-all.sh
```

### Symptom: Cannot write to database or logs

**Cause**: Insufficient file permissions.

**Solution**:

```bash
# Fix permissions for data directory
chmod -R u+w data/

# Fix permissions for logs directory
mkdir -p logs
chmod -R u+w logs/

# Fix database file permissions
chmod 644 data/servers.db
```

---

## Additional Tips

### Check System Requirements

```bash
# Python version (must be 3.8+)
python3 --version

# Node.js version (must be 18+)
node --version

# npm version
npm --version

# Available disk space
df -h .

# Available memory
free -h
```

### Clean Restart

When all else fails, do a complete clean restart:

```bash
# 1. Stop all services
./stop-all.sh
pkill -f "python3.*central_api"
pkill -f "python3.*websocket_server"
pkill -f "python3.*terminal.py"

# 2. Deactivate venv
deactivate

# 3. Clean temporary files
rm -rf logs/*.log
rm -f *.pid

# 4. Reactivate and restart
source venv/bin/activate
./start-all.sh

# 5. In new terminal, start frontend
cd frontend-next
npm run dev
```

### Enable Debug Mode

For more detailed error messages:

```bash
# Python - enable debug logging
# Edit backend/central_api.py and set DEBUG = True

# Or set environment variable
export DEBUG=1

# Run services
./start-all.sh
```

---

## Still Having Issues?

If your issue isn't covered here:

1. **Check logs carefully**: `tail -f logs/*.log`
2. **Review the error message**: Copy the full error and search online
3. **Check GitHub Issues**: https://github.com/minhtuancn/server-monitor/issues
4. **Open a new issue**: Include:
   - Your OS and Python/Node.js versions
   - Full error message
   - Steps to reproduce
   - What you've already tried

## Quick Reference Commands

```bash
# Verify you're in project root
pwd && ls -la | grep -E "backend|frontend-next|start-all.sh"

# Check virtual environment
which python3

# Check running services
lsof -i :9081 :9083 :9084 :9085

# View all logs
tail -f logs/*.log

# Clean restart
./stop-all.sh && ./start-all.sh

# Check health
curl http://localhost:9083/api/health
```
