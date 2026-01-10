# Custom Domain Configuration Guide

When deploying Server Monitor to a custom domain (e.g., `mon.go7s.net`), follow this guide to ensure the frontend, API, WebSocket, and agent connections work seamlessly.

## Quick Setup

### For a Custom Domain (e.g., mon.go7s.net)

#### 1. Backend (.env)

```bash
# Enable frontend domain in CORS
export ALLOWED_FRONTEND_DOMAINS=mon.go7s.net

# Optional: Allow multiple domains
export ALLOWED_FRONTEND_DOMAINS=mon.go7s.net,mon.local,192.168.1.100
```

#### 2. Frontend (.env.local)

```bash
# Backend API URL (for server-side requests)
API_PROXY_TARGET=http://localhost:9083
# OR if backend is on same reverse proxy:
# API_PROXY_TARGET=https://mon.go7s.net/api/backend

# WebSocket URLs (client-side direct connections via reverse proxy)
NEXT_PUBLIC_MONITORING_WS_URL=wss://mon.go7s.net/ws/monitoring
NEXT_PUBLIC_TERMINAL_WS_URL=wss://mon.go7s.net/ws/terminal

# Domain identifier
NEXT_PUBLIC_DOMAIN=mon.go7s.net

# Node environment
NODE_ENV=production
```

#### 3. Reverse Proxy (Nginx Example)

```nginx
upstream backend_api {
    server localhost:9083;
}

upstream monitoring_ws {
    server localhost:9085;
}

upstream terminal_ws {
    server localhost:9084;
}

server {
    server_name mon.go7s.net;
    listen 443 ssl http2;

    # SSL configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Frontend (Next.js on 9081)
    location / {
        proxy_pass http://localhost:9081;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Proxy (Next.js BFF layer)
    location /api/proxy/ {
        proxy_pass http://backend_api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Direct API (backend, if needed)
    location /api/ {
        proxy_pass http://backend_api/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket: Monitoring
    location /ws/monitoring {
        proxy_pass http://monitoring_ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # WebSocket: Terminal
    location /ws/terminal {
        proxy_pass http://terminal_ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}

# HTTP redirect to HTTPS
server {
    server_name mon.go7s.net;
    listen 80;
    return 301 https://$server_name$request_uri;
}
```

#### 4. Caddy Alternative (Simpler)

```caddy
mon.go7s.net {
    # Frontend
    reverse_proxy * localhost:9081

    # API Proxy
    reverse_proxy /api/proxy/* localhost:9083

    # WebSocket endpoints (upgraded automatically)
    reverse_proxy /ws/* localhost:9085
}
```

## Environment Variables

### Backend (central_api.py)

| Variable                   | Value                    | Description                                             |
| -------------------------- | ------------------------ | ------------------------------------------------------- |
| `ALLOWED_FRONTEND_DOMAINS` | `mon.go7s.net,mon.local` | Comma-separated list of allowed frontend domains (CORS) |
| `CORS_ALLOW_ALL`           | `false` (default)        | Set to `true` only in development                       |
| `API_PORT`                 | `9083` (default)         | Backend API port                                        |

### Frontend (frontend-next/.env.local)

| Variable                        | Value                              | Description                            |
| ------------------------------- | ---------------------------------- | -------------------------------------- |
| `API_PROXY_TARGET`              | `http://localhost:9083`            | Backend address (server-side requests) |
| `NEXT_PUBLIC_MONITORING_WS_URL` | `wss://mon.go7s.net/ws/monitoring` | WebSocket for monitoring (client-side) |
| `NEXT_PUBLIC_TERMINAL_WS_URL`   | `wss://mon.go7s.net/ws/terminal`   | WebSocket for terminal (client-side)   |
| `NEXT_PUBLIC_DOMAIN`            | `mon.go7s.net`                     | Current domain (for logging/tracking)  |
| `NODE_ENV`                      | `production`                       | Node environment                       |

## Typical Deployment Scenarios

### Scenario 1: Development (Localhost + LAN Access)

**Goal**: Run on localhost and access from other LAN machines

```bash
# Backend
export ALLOWED_FRONTEND_DOMAINS=localhost,192.168.1.100

# Frontend (.env.local)
NEXT_PUBLIC_MONITORING_WS_URL=ws://192.168.1.100:9085
NEXT_PUBLIC_TERMINAL_WS_URL=ws://192.168.1.100:9084
NODE_ENV=development
```

**Access**: `http://192.168.1.100:9081`

---

### Scenario 2: Production with Custom Domain (mon.go7s.net)

**Goal**: Production deployment on custom domain with reverse proxy

```bash
# Backend
export ALLOWED_FRONTEND_DOMAINS=mon.go7s.net

# Frontend (.env.local)
API_PROXY_TARGET=https://mon.go7s.net/api/backend
NEXT_PUBLIC_MONITORING_WS_URL=wss://mon.go7s.net/ws/monitoring
NEXT_PUBLIC_TERMINAL_WS_URL=wss://mon.go7s.net/ws/terminal
NEXT_PUBLIC_DOMAIN=mon.go7s.net
NODE_ENV=production
```

**Access**: `https://mon.go7s.net`

**Reverse Proxy**: Nginx/Caddy on port 443 (SSL)

---

### Scenario 3: Multiple Domains / Subdomains

**Goal**: Support mon.go7s.net and mon.backup.go7s.net

```bash
# Backend
export ALLOWED_FRONTEND_DOMAINS=mon.go7s.net,mon.backup.go7s.net,mon.local

# Frontend (.env.local) - per environment
API_PROXY_TARGET=https://mon.go7s.net/api/backend
NEXT_PUBLIC_MONITORING_WS_URL=wss://mon.go7s.net/ws/monitoring
NEXT_PUBLIC_TERMINAL_WS_URL=wss://mon.go7s.net/ws/terminal
NODE_ENV=production
```

---

## Agent Server Connections

When agents connect to the central monitoring system:

1. **Agent discovers central server**:

   - Uses `CENTRAL_API_URL` env var or hostname
   - Example: `CENTRAL_API_URL=https://mon.go7s.net/api`

2. **Agent sends stats to API**:

   - All agent → API calls go through `/api/proxy` (BFF layer)
   - Reverse proxy forwards to backend on port 9083
   - CORS headers checked (must match `ALLOWED_FRONTEND_DOMAINS`)

3. **Dashboard receives agent data**:
   - Frontend calls `/api/proxy/api/remote/stats/:id`
   - Next.js BFF forwards to backend
   - Backend calls agent (via SSH or direct HTTP)
   - Response flows back through proxy

### Agent Configuration (.env)

```bash
# Central API address
CENTRAL_API_URL=https://mon.go7s.net/api

# For SSH-based remote servers
SSH_KEY_PATH=/root/.ssh/id_rsa
SSH_USER=root

# Optional: specify local network range (for intra-LAN agent discovery)
LOCAL_NETWORK_RANGE=192.168.0.0/16
```

---

## Troubleshooting

### CORS Errors

**Problem**: Browser console shows "CORS policy blocked"
**Solution**:

1. Verify `ALLOWED_FRONTEND_DOMAINS` includes your domain
2. Restart backend: `systemctl restart server-monitor-api`
3. Check `Access-Control-Allow-Origin` header in browser dev tools

### WebSocket Connection Failed

**Problem**: Terminal or monitoring disconnects immediately
**Solution**:

1. Verify reverse proxy forwards `/ws/*` paths
2. Ensure `proxy_http_version 1.1` and `proxy_set_header Connection "upgrade"`
3. Check firewall: ensure ports 443 (HTTPS) and WebSocket port are open
4. Verify `NEXT_PUBLIC_*_WS_URL` matches reverse proxy domain

### Agent Can't Reach API

**Problem**: Agents report "Connection refused" to central API
**Solution**:

1. Test from agent server: `curl https://mon.go7s.net/api/health`
2. Verify DNS resolves mon.go7s.net to your reverse proxy IP
3. Ensure firewall allows outbound HTTPS from agent to central server
4. Check reverse proxy logs: `tail -f /var/log/nginx/error.log`

---

## Security Checklist

- [ ] Enable HTTPS (SSL/TLS) on reverse proxy
- [ ] Set strong JWT_SECRET in backend .env
- [ ] Set strong ENCRYPTION_KEY in backend .env
- [ ] Change default admin password after first login
- [ ] Restrict `ALLOWED_FRONTEND_DOMAINS` to your domain(s) only
- [ ] Set `NODE_ENV=production` on frontend
- [ ] Disable debug logging in production
- [ ] Use firewall rules to restrict API port 9083 to reverse proxy only
- [ ] Set up log rotation and monitoring

---

## References

- [HTTPS-SETUP.md](docs/security/HTTPS_SETUP.md) — SSL/TLS certificate setup
- [DEPLOYMENT.md](docs/operations/DEPLOYMENT.md) — Production deployment guide
- [backend/security.py](../backend/security.py) — CORS and security settings
- [frontend-next/.env.example](../frontend-next/.env.example) — Frontend env vars
