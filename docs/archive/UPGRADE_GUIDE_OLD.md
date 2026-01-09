# Upgrade Guide - Package Manager Updates (v2.4.0)

**Date:** January 8, 2026  
**Version:** 2.4.0

---

## Overview

This guide explains the updates made to support modern package manager requirements and fix security vulnerabilities.

## What Changed?

### 1. Backend Installation (Python)

**Problem:** Python 3.12+ uses PEP 668 which prevents system-wide package installation to avoid breaking system packages.

**Solution:** Use Python virtual environments (venv) for installation.

#### Before (❌ No longer works on Python 3.12+):
```bash
cd backend
pip3 install -r requirements.txt
```

#### After (✅ Recommended):
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Frontend Dependencies (npm)

**Problem:** 3 high severity vulnerabilities in glob package (command injection CVE)

**Solution:** Updated to Next.js 15.5.9 and React 19 with latest security patches.

#### Dependency Updates:

| Package | Old Version | New Version | Change |
|---------|-------------|-------------|--------|
| next | 14.2.35 | 15.5.9 | Major (security fix) |
| react | 18.2.0 | 19.0.0 | Major |
| react-dom | 18.2.0 | 19.0.0 | Major |
| eslint | 8.57.1 | 9.18.0 | Major (removes deprecation) |
| next-intl | 3.13.0 | 4.0.0 | Major |
| next-themes | 0.3.0 | 0.4.6 | Minor |
| paramiko | 2.12.0 | 4.0.0 | Major |
| PyJWT | 2.8.0 | 2.10.1 | Minor |
| python-dotenv | 1.0.0 | 1.2.1 | Minor |
| cryptography | 41.0.0 | 46.0.3 | Major |

### 3. Code Changes for Next.js 15

Next.js 15 introduced breaking changes where `params` are now asynchronous Promises.

#### Files Updated:
- `src/app/[locale]/layout.tsx` - Handle async params
- `src/app/[locale]/page.tsx` - Handle async params
- `src/app/api/proxy/[...path]/route.ts` - Handle async params in API routes
- `src/i18n/request.ts` - Improve null checking for locale
- `next.config.mjs` - Move typedRoutes from experimental to stable

## Installation Instructions

### Fresh Installation

```bash
# 1. Clone repository
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor

# 2. Setup environment
cp .env.example .env

# 3. Generate secure keys
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))" >> .env
python3 -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(24))" >> .env
python3 -c "import secrets; print('KEY_VAULT_MASTER_KEY=' + secrets.token_urlsafe(32))" >> .env

# 4. Setup Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install backend dependencies
pip install -r backend/requirements.txt

# 6. Install frontend dependencies
cd frontend-next
npm install

# 7. Configure frontend
cat > .env.local << 'EOF'
API_PROXY_TARGET=http://localhost:9083
NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084
EOF
```

### Upgrading Existing Installation

```bash
# 1. Pull latest changes
git pull origin main

# 2. Backend: Create and use virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade -r backend/requirements.txt

# 3. Frontend: Update dependencies
cd frontend-next
rm -rf node_modules package-lock.json
npm install

# 4. Rebuild frontend
npm run build

# 5. Restart services
cd ..
./stop-all.sh
./start-all.sh

# In another terminal (with venv activated)
cd frontend-next
npm run start
```

## Troubleshooting

### Error: externally-managed-environment

**Symptom:**
```
error: externally-managed-environment
× This environment is externally managed
```

**Solution:**
Use virtual environment as shown above. This is a security feature in Python 3.12+.

### Error: Module not found (Python)

**Symptom:**
```
ModuleNotFoundError: No module named 'paramiko'
```

**Solution:**
Ensure virtual environment is activated:
```bash
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows
```

### npm audit shows vulnerabilities

**Before this update:**
```
3 high severity vulnerabilities
```

**After this update:**
```
found 0 vulnerabilities
```

If you still see vulnerabilities, ensure you have the latest version:
```bash
cd frontend-next
rm -rf node_modules package-lock.json
npm install
npm audit
```

### Build errors after upgrade

If you get TypeScript or build errors:

```bash
# Clear Next.js cache
cd frontend-next
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

## Breaking Changes

### For Developers

If you've customized the code, be aware of these breaking changes:

1. **Next.js 15 - Async Params**: All dynamic route parameters are now Promises
   ```typescript
   // Before
   export default function Page({ params }: { params: { id: string } }) {
     const id = params.id;
   }
   
   // After  
   export default async function Page({ params }: { params: Promise<{ id: string }> }) {
     const { id } = await params;
   }
   ```

2. **React 19**: Some React APIs changed. Most components should work without changes.

3. **Python Virtual Environment**: All Python commands must be run with venv activated.

## Security Improvements

### Fixed Vulnerabilities

1. **glob Command Injection (CVE-2025-66478)**
   - Severity: High
   - Fixed by upgrading to Next.js 15.5.9

2. **Outdated Cryptography Packages**
   - Updated cryptography from 41.0.0 to 46.0.3
   - Updated paramiko from 2.12.0 to 4.0.0

### No New Vulnerabilities

- ✅ npm audit: 0 vulnerabilities
- ✅ All Python packages updated to latest stable versions
- ✅ No breaking changes to security features

## Testing

After upgrading, verify everything works:

```bash
# 1. Test backend
source venv/bin/activate
python3 -c "import sys; sys.path.insert(0, 'backend'); import database; database.init_database()"

# 2. Test frontend build
cd frontend-next
npm run build
cd ..

# 3. Test services
./start-all.sh

# 4. Access dashboard
# Open http://localhost:9081
# Login: admin / admin123
```

## Rollback

If you encounter issues, you can rollback:

```bash
# 1. Checkout previous version
git checkout v2.3.0

# 2. Reinstall old dependencies
# Backend
rm -rf venv
pip3 install -r backend/requirements.txt --break-system-packages

# Frontend
cd frontend-next
rm -rf node_modules package-lock.json
npm install

# 3. Restart services
cd ..
./stop-all.sh
./start-all.sh
```

## Support

For issues or questions:
- 📧 Email: vietkeynet@gmail.com
- 🐙 GitHub Issues: https://github.com/minhtuancn/server-monitor/issues

---

**Last Updated:** January 8, 2026
