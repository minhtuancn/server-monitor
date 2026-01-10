# Legacy Service Files (DEPRECATED)

⚠️ **WARNING: These service files are deprecated and should not be used in new installations.**

## Files in this directory

- `server-dashboard-api-v2.service` - Old API service (replaced by `server-monitor-api.service`)
- `opencode-dashboard.service` - OpenCode status dashboard (from different project, not part of server-monitor)

## Migration Path

If you are using these legacy services, please migrate to the current service architecture:

### Old (Legacy)
```bash
server-dashboard-api-v2.service   # Old single-file API on port 9083
opencode-dashboard.service        # Not related to this project
```

### Current (Recommended)
```bash
server-monitor-api.service        # Central API on port 9083
server-monitor-ws.service         # WebSocket server on port 9085
server-monitor-terminal.service   # Terminal service on port 9084
server-monitor-frontend.service   # Next.js frontend on port 9081
```

## How to Migrate

1. **Stop old services:**
   ```bash
   sudo systemctl stop server-dashboard-api-v2.service
   sudo systemctl disable server-dashboard-api-v2.service
   ```

2. **Install current services:**
   
   Option A - Automated (Recommended):
   ```bash
   curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash
   ```
   
   Option B - Manual:
   ```bash
   sudo cp services/systemd/*.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now server-monitor-api.service
   sudo systemctl enable --now server-monitor-ws.service
   sudo systemctl enable --now server-monitor-terminal.service
   sudo systemctl enable --now server-monitor-frontend.service
   ```

3. **Verify migration:**
   ```bash
   sudo systemctl status server-monitor-*
   ```

## Why These Were Deprecated

1. **server-dashboard-api-v2.service**: 
   - Monolithic design with all features in one file
   - Hard-coded paths (`/root/server_dashboard_api_v2.py`)
   - Running as root (security issue)
   - Replaced by modular architecture with separate services

2. **opencode-dashboard.service**:
   - From a different project (OpenCode)
   - Not related to server-monitor functionality
   - Should not have been in this repository

## Support

These files are provided for reference only. No support or updates will be provided.
For current installations, see: [DEPLOYMENT.md](docs/operations/DEPLOYMENT.md)
