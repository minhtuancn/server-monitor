# Quick Start Guide - Updated for Python 3.12+

## Issue Fixed
The startup scripts (`start-all.sh`, `start-dev.sh`, `start-central.sh`) now automatically detect and activate Python virtual environments, fixing the PEP 668 error on Python 3.12+.

## Installation Steps (Updated)

### 1. Clone and Setup
```bash
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows
```

### 3. Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Generate Security Keys
```bash
cp .env.example .env

# Generate secure keys
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))" >> .env
python3 -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(24))" >> .env
python3 -c "import secrets; print('KEY_VAULT_MASTER_KEY=' + secrets.token_urlsafe(32))" >> .env
```

### 5. Install Frontend Dependencies
```bash
cd frontend-next
npm install
cd ..
```

### 6. Configure Frontend
```bash
cat > frontend-next/.env.local << 'EOF'
API_PROXY_TARGET=http://localhost:9083
NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084
EOF
```

## Starting Services (Automatic venv Detection)

### Option 1: All Services (Recommended)
```bash
# The script will automatically activate venv if it exists!
./start-all.sh
```

**What happens:**
- ✅ Script detects venv and activates it automatically
- ✅ Shows "Found virtual environment, activating..."
- ✅ Checks if .env file exists
- ✅ Starts all backend services
- ✅ No manual venv activation needed!

### Option 2: Development Mode
```bash
./start-dev.sh
```

### Option 3: Central Server Only
```bash
./start-central.sh
```

## Frontend (Next.js)

In a separate terminal:
```bash
cd frontend-next
npm run dev
```

Access: http://localhost:9081

## Script Behavior

### With venv present:
```
✅ Found virtual environment, activating...
```
Scripts use venv automatically.

### Without venv:
```
⚠️  No virtual environment found. Using system Python.
   For Python 3.12+, consider creating a venv: python3 -m venv venv
```
Scripts fall back to system Python (backward compatible).

### Missing .env file:
```
⚠️  WARNING: .env file not found!
   Please create .env file with required keys. See .env.example
   Generate keys with:
     python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))" >> .env
     ...
```

## Troubleshooting

### Error: "ENCRYPTION_KEY not set"
**Before fix:** Script failed with Python import errors

**After fix:** 
1. Check if `.env` exists: `ls -la .env`
2. If missing, generate keys (see step 4 above)
3. Restart: `./stop-all.sh && ./start-all.sh`

### Error: "externally-managed-environment"
**Solution:** Use virtual environment (see step 2 above)

### Services won't start
1. Ensure venv is created: `ls -d venv`
2. Check dependencies installed: `source venv/bin/activate && pip list`
3. Check .env exists: `cat .env`
4. View logs: `tail -f logs/*.log`

## Key Changes (Commit f50e224)

1. ✅ `start-all.sh` - Auto-detects and activates venv
2. ✅ `start-dev.sh` - Auto-detects and activates venv  
3. ✅ `start-central.sh` - Auto-detects and activates venv
4. ✅ Added .env file existence check
5. ✅ Added helpful warning messages
6. ✅ Backward compatible with system Python

## What You Don't Need To Do Anymore

❌ Manually activate venv before running start scripts
❌ Use `--break-system-packages` flag
❌ Install packages globally with sudo

## What The Scripts Do Automatically

✅ Detect venv location (`./venv` or `./.venv`)
✅ Activate venv if found
✅ Check .env file exists
✅ Display helpful warnings
✅ Use correct Python command

---

**Updated:** January 8, 2026  
**Commit:** f50e224
