# Offline Mode Setup

## Overview

This guide explains how to run the Server Monitor application in offline mode without requiring internet access for CDN resources.

## Changes Made

### 1. Local Asset Dependencies

All external CDN dependencies have been downloaded and are now hosted locally:

- **Font Awesome 6.4.0**: Located in `/frontend/assets/vendor/fontawesome/`
  - CSS files: `/frontend/assets/vendor/fontawesome/css/`
  - Web fonts: `/frontend/assets/vendor/fontawesome/webfonts/`

- **xterm.js 5.3.0**: Located in `/frontend/assets/vendor/xterm/`
  - CSS: `/frontend/assets/vendor/xterm/css/`
  - JavaScript: `/frontend/assets/vendor/xterm/lib/`
  - Fit Addon: `/frontend/assets/vendor/xterm/addon-fit/`
  - Web Links Addon: `/frontend/assets/vendor/xterm/addon-web-links/`

### 2. Updated HTML Files

All HTML files have been updated to reference local assets instead of CDN URLs:

- `dashboard.html`
- `email-settings.html`
- `notifications.html`
- `server-detail.html`
- `settings.html`
- `ssh-keys.html`
- `system-check.html`
- `terminal.html`
- `users.html`

### 3. CORS Configuration

The CORS configuration has been enhanced to support flexible origin handling:

**Automatic Support:**
- Any origin on port 9081 (the frontend port) is automatically allowed
- Both HTTP and HTTPS origins are supported
- Common localhost variations (localhost, 127.0.0.1) are pre-configured

**Development Mode:**
To allow all origins (useful for testing with proxy servers), set in your `.env` file:
```bash
CORS_ALLOW_ALL=true
```

**Note:** This should only be used in development environments.

## Testing Instructions

### 1. Local Testing

Run the application locally:

```bash
# Start all services
./start-all.sh

# Access the frontend at:
# http://localhost:9081
```

### 2. Testing with External Domain

If you're running behind a reverse proxy (like nginx) or accessing via an external domain:

1. Configure your reverse proxy to forward to:
   - Frontend: `localhost:9081`
   - API: `localhost:9083`
   - WebSocket: `localhost:9085`
   - Terminal: `localhost:9084`

2. The application will automatically detect your domain and configure CORS appropriately.

3. For testing purposes, you can enable permissive CORS:
   ```bash
   echo "CORS_ALLOW_ALL=true" >> .env
   ./stop-all.sh
   ./start-all.sh
   ```

### 3. Nginx Proxy Example

Example nginx configuration for proxying the frontend on port 9081:

```nginx
server {
    listen 443 ssl http2;
    server_name mon.go7s.net;
    
    # SSL configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Frontend
    location / {
        proxy_pass http://localhost:9081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API (adjust port if different)
    location /api/ {
        proxy_pass http://localhost:9083;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:9085;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    # Terminal WebSocket
    location /terminal/ {
        proxy_pass http://localhost:9084;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Verification

To verify offline mode is working:

1. **Check Network Tab**: Open browser developer tools (F12) and check the Network tab
   - All Font Awesome resources should load from `/assets/vendor/fontawesome/`
   - All xterm resources should load from `/assets/vendor/xterm/`
   - No requests should go to `cdnjs.cloudflare.com`

2. **Test Without Internet**: Disconnect your internet and reload the page
   - The interface should load completely
   - Icons and terminal should work normally

3. **Login Test**: Try logging in with valid credentials
   - If you see "CORS Failed" errors, enable CORS_ALLOW_ALL in `.env`
   - Check that the API URL is correctly detected

## Troubleshooting

### CORS Errors

If you see "CORS Failed" in the browser console:

1. Check your `.env` file and add:
   ```
   CORS_ALLOW_ALL=true
   ```

2. Restart the services:
   ```bash
   ./stop-all.sh
   ./start-all.sh
   ```

3. Check the browser console for the exact origin being used

4. Verify the API server is running on port 9083:
   ```bash
   curl http://localhost:9083/api/health
   ```

### Assets Not Loading

If Font Awesome or xterm assets don't load:

1. Verify files exist:
   ```bash
   ls -la frontend/assets/vendor/fontawesome/css/
   ls -la frontend/assets/vendor/xterm/lib/
   ```

2. Check file permissions:
   ```bash
   chmod -R 755 frontend/assets/vendor/
   ```

3. Clear browser cache and reload

### Login Issues

If login doesn't work:

1. Check API server logs:
   ```bash
   tail -f logs/central_api.log
   ```

2. Verify JWT_SECRET is set in `.env`:
   ```bash
   grep JWT_SECRET .env
   ```

3. Test the API directly:
   ```bash
   curl -X POST http://localhost:9083/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"your-password"}'
   ```

## Security Notes

- **Production**: Set `CORS_ALLOW_ALL=false` or remove it entirely
- The application automatically allows origins on port 9081 and common localhost variations
- Use HTTPS in production environments
- Review and restrict ALLOWED_ORIGINS in `backend/security.py` for production deployments
