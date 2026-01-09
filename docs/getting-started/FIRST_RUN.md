# First-Run Setup Guide

**Welcome to Server Monitor!** This guide walks you through the initial setup after a fresh installation.

Last Updated: 2026-01-09

---

## What Happens on First Run?

When you access a fresh Server Monitor installation:

1. **No users exist** in the database
2. **Middleware detects** this via `/api/setup/status`
3. **You're redirected** to `/setup` page
4. **Create admin account** via setup wizard
5. **Auto-login** and redirect to dashboard

---

## Setup Wizard Steps

### Step 1: Access Dashboard

```bash
# Start services
./start-all.sh

# Open browser
open http://localhost:9081
```

### Step 2: Automatic Redirect

- First visit → redirected to `/en/setup` (or your locale)
- No login page shown (no users exist yet)

### Step 3: Fill Setup Form

```
Username:  [admin         ] (3+ characters)
Email:     [admin@example.com] (valid email)
Password:  [●●●●●●●●] (8+ chars, uppercase, lowercase, digit)
Confirm:   [●●●●●●●●] (must match password)

[Create Admin Account]
```

**Password Requirements**:

- ✅ At least 8 characters
- ✅ Contains uppercase letter (A-Z)
- ✅ Contains lowercase letter (a-z)
- ✅ Contains digit (0-9)

### Step 4: Account Created

- ✅ Admin user created in database
- ✅ JWT token generated and set in cookie
- ✅ Redirected to dashboard

### Step 5: You're In!

- Dashboard loads with default state
- No servers yet (empty dashboard)
- Ready to add servers

---

## What If Setup Fails?

### "This server is already configured"

- **Cause**: Users already exist in database
- **Solution**: Login at `/login` instead
- **Default credentials** (if installer created them): `admin` / `admin123`

### "Username already taken"

- **Cause**: Database not empty
- **Solution**: Use different username or reset database

### "Password too weak"

- **Cause**: Password doesn't meet requirements
- **Solution**: Use stronger password (8+ chars, uppercase, lowercase, digit)

### "Setup endpoint not responding"

- **Cause**: Backend not running
- **Solution**: Check backend logs:
  ```bash
  tail -f logs/api.log
  lsof -i:9083  # Should show python process
  ```

---

## Behind the Scenes

### Backend Endpoints

**GET /api/setup/status** (Public)

```json
{
  "needs_setup": true|false
}
```

- Returns `true` if no users exist
- Returns `false` if any users exist

**POST /api/setup/initialize** (Public, one-time)

```json
// Request
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "SecurePass123"
}

// Response
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  },
  "token": "eyJ...",
  "expires_in": 86400
}
```

- Only works when no users exist
- Creates user with admin role
- Returns JWT token for immediate login

### Frontend Flow

**Middleware** (`frontend-next/middleware.ts`):

1. Check if user authenticated (cookie exists)
2. If not authenticated:
   - Fetch `/api/proxy/api/setup/status`
   - If `needs_setup=true` → redirect to `/setup`
   - Else → redirect to `/login`

**Setup Page** (`src/app/[locale]/(auth)/setup/page.tsx`):

- Form with username, email, password, confirm
- Client-side validation
- Submits to `/api/auth/setup` (BFF)
- Sets cookie on success
- Redirects to dashboard

**Setup API** (`src/app/api/auth/setup/route.ts`):

- Proxies to backend `/api/setup/initialize`
- Sets `auth_token` HttpOnly cookie
- Returns user data

---

## Security Notes

### Why Public Endpoints?

Setup endpoints are **public** (no auth required) because:

- No users exist yet (can't authenticate)
- Protected by user count check (only works once)
- Rate-limited (prevent brute force)

### What Prevents Abuse?

1. **User count check**: Only runs when `user_count=0`
2. **Rate limiting**: 5 requests per minute per IP
3. **Input validation**: Username, email, password validated
4. **One-time use**: After first user created, endpoint returns error

### Default Admin

The installer **no longer creates default admin** (as of v2.3.1):

- Old behavior: Auto-create `admin`/`admin123`
- New behavior: User creates admin via setup wizard
- Why: Improved security (no default credentials)
- Override: Set `SKIP_DEFAULT_ADMIN=false` to restore old behavior

---

## Advanced: Skip Setup in Development

### Option 1: Create Default Admin

```bash
# Start with default admin (old behavior)
SKIP_DEFAULT_ADMIN=false ./start-all.sh
```

### Option 2: Create User via API

```bash
# Directly call setup endpoint
curl -X POST http://localhost:9083/api/setup/initialize \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"SecurePass123"}'
```

### Option 3: Database Insert

```bash
# Add user directly to database (NOT RECOMMENDED)
sqlite3 data/servers.db <<EOF
INSERT INTO users (username, password, email, role, is_active)
VALUES ('admin', '<hashed_password>', 'admin@example.com', 'admin', 1);
EOF
```

---

## After Setup

### Change Password

1. Go to **Settings** → **Profile**
2. Click **Change Password**
3. Enter current and new password
4. Save

### Add More Users

1. Go to **Users** (admin only)
2. Click **Add User**
3. Fill form (username, email, role)
4. User receives credentials via email (if configured)

### Configure System

1. **Email**: Settings → Email (SMTP)
2. **Alerts**: Settings → Integrations (Telegram, Slack, Webhooks)
3. **Backups**: Configure automated backups (see [BACKUP_RESTORE.md](../operations/BACKUP_RESTORE.md))

---

## Troubleshooting

### Setup page keeps showing even after creating admin

**Cause**: Cookie not set or backend user count check failing  
**Solution**:

```bash
# Check backend logs
tail -f logs/api.log | grep setup

# Verify user created
sqlite3 data/servers.db "SELECT * FROM users;"

# Clear browser cookies and try again
```

### Can't access /setup page (redirects to /login)

**Cause**: Users already exist  
**Solution**: Login with existing credentials or reset database

### "JWT token invalid" after setup

**Cause**: Cookie not set correctly  
**Solution**:

```bash
# Check JWT_SECRET in .env
grep JWT_SECRET backend/.env

# Regenerate if empty
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))" >> backend/.env

# Restart backend
./stop-all.sh && ./start-all.sh
```

---

## Resources

- [Quick Start](QUICK_START.md) — Installation guide
- [Troubleshooting](TROUBLESHOOTING.md) — Common issues
- [Security](../../SECURITY.md) — Security best practices
- [User Management](../../backend/README.md#user-management) — Managing users

---

**Next**: [Add your first server →](QUICK_START.md#add-servers)
