# Nginx Reverse Proxy Configuration Guide

This guide shows how to configure nginx as a reverse proxy for Server Monitor, allowing you to access it via a custom domain (e.g., https://mon.go7s.net) while the application runs on localhost.

## Prerequisites

- Server Monitor installed and running
- Nginx installed
- SSL certificate for your domain (Let's Encrypt recommended)
- Domain pointing to your server

## Architecture

```
Internet → Nginx (443/HTTPS) → Server Monitor Services (localhost)
                ├─ Frontend (port 9081)
                ├─ API (port 9083)
                ├─ Terminal WS (port 9084)
                └─ WebSocket (port 9085)
```

## Step 1: Configure CORS for Your Domain

Edit your `.env` file:

```bash
# For testing with any domain (development only)
CORS_ALLOW_ALL=true

# Or for production, leave it as is - the system automatically allows
# any origin on port 9081 and common localhost variations
```

The application automatically allows:
- Any origin ending with `:9081`
- Both HTTP and HTTPS protocols
- Common localhost variations (localhost, 127.0.0.1)

## Step 2: Nginx Configuration

Create a new nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/server-monitor
```

Add this configuration:

```nginx
# Server Monitor - Nginx Reverse Proxy Configuration
# Domain: mon.go7s.net (replace with your domain)

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name mon.go7s.net;
    
    # Redirect all HTTP traffic to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name mon.go7s.net;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/mon.go7s.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mon.go7s.net/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Increase timeouts for long-running operations
    proxy_connect_timeout 600;
    proxy_send_timeout 600;
    proxy_read_timeout 600;
    send_timeout 600;

    # Frontend (Static Files)
    location / {
        proxy_pass http://127.0.0.1:9081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }

    # API Endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:9083;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers (if needed, though the app handles this)
        add_header 'Access-Control-Allow-Origin' $http_origin always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization, X-Requested-With' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' $http_origin always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization, X-Requested-With' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Max-Age' 86400;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }

    # WebSocket for Real-time Updates (port 9085)
    location /ws/ {
        proxy_pass http://127.0.0.1:9085;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket timeout
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }

    # Terminal WebSocket (port 9084)
    location /terminal/ {
        proxy_pass http://127.0.0.1:9084;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Terminal timeout
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }

    # Logs
    access_log /var/log/nginx/server-monitor-access.log;
    error_log /var/log/nginx/server-monitor-error.log;
}
```

## Step 3: Enable the Site

```bash
# Create symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/server-monitor /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

## Step 4: Start Server Monitor

```bash
cd /path/to/server-monitor
./start-all.sh
```

## Step 5: Test the Setup

1. **Frontend**: Open https://mon.go7s.net in your browser
2. **Check Console**: Open Developer Tools (F12) → Console
   - Should see no CORS errors
   - All assets should load from local paths
3. **Test Login**: Try logging in with valid credentials
4. **Network Tab**: Verify all requests go to https://mon.go7s.net

## Alternative: Using Port-based Proxying

If you prefer to keep the API on a separate port (8083) accessible externally:

```nginx
# API on separate port
server {
    listen 8083 ssl http2;
    listen [::]:8083 ssl http2;
    server_name mon.go7s.net;

    ssl_certificate /etc/letsencrypt/live/mon.go7s.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mon.go7s.net/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:9083;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

In this case, the frontend would access the API at `https://mon.go7s.net:8083/api/...`

## Troubleshooting

### 1. CORS Errors

If you see CORS errors in the browser console:

```bash
# Enable permissive CORS temporarily
echo "CORS_ALLOW_ALL=true" >> .env
./stop-all.sh
./start-all.sh

# Check nginx error logs
sudo tail -f /var/log/nginx/server-monitor-error.log
```

### 2. 502 Bad Gateway

This means nginx can't reach the backend services:

```bash
# Check if services are running
curl http://localhost:9081
curl http://localhost:9083/api/health

# Check logs
tail -f logs/api.log
tail -f logs/web.log

# Restart services
./stop-all.sh
./start-all.sh
```

### 3. WebSocket Connection Failed

Check nginx configuration and ensure WebSocket upgrade headers are set:

```bash
# Test WebSocket endpoint
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Host: mon.go7s.net" \
  -H "Origin: https://mon.go7s.net" \
  https://mon.go7s.net/ws/

# Check nginx logs
sudo tail -f /var/log/nginx/server-monitor-error.log
```

### 4. Assets Not Loading (404)

Verify the frontend server is serving files correctly:

```bash
# Check if Python HTTP server is running on 9081
netstat -tulpn | grep 9081

# Test directly
curl http://localhost:9081/assets/vendor/fontawesome/css/all.min.css

# Check permissions
chmod -R 755 frontend/assets/vendor/
```

### 5. SSL Certificate Issues

If using Let's Encrypt:

```bash
# Obtain certificate
sudo certbot certonly --nginx -d mon.go7s.net

# Auto-renewal test
sudo certbot renew --dry-run
```

## Security Recommendations

1. **Use CORS_ALLOW_ALL=false in production**
2. **Keep SSL certificates up to date**
3. **Use strong JWT secrets** (see .env.example)
4. **Enable firewall** to block direct access to backend ports:
   ```bash
   # Allow only localhost to access backend ports
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw deny 9081/tcp
   sudo ufw deny 9083/tcp
   sudo ufw deny 9084/tcp
   sudo ufw deny 9085/tcp
   ```

## Performance Tuning

For high-traffic deployments:

```nginx
# Add to nginx.conf
worker_processes auto;
worker_connections 1024;

# Add to server block
client_max_body_size 10M;
keepalive_timeout 65;

# Enable gzip compression
gzip on;
gzip_vary on;
gzip_min_length 256;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
```

## Monitoring

Monitor nginx and Server Monitor:

```bash
# Nginx access logs
sudo tail -f /var/log/nginx/server-monitor-access.log

# Application logs
tail -f logs/api.log
tail -f logs/web.log

# Check service status
./stop-dev.sh && ./start-dev.sh
```
