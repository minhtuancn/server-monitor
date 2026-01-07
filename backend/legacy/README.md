# Legacy Backend Files (DEPRECATED)

⚠️ **WARNING: These files are deprecated and are not used in the current system.**

## Files in this directory

- `server_dashboard_api_v2.py` - Old monolithic API server (v2)
- `server_dashboard_api_v3.py` - Old monolithic API server (v3, backup)
- `status_webserver.py` - OpenCode status dashboard web server (not part of this project)

## Why These Were Deprecated

### server_dashboard_api_v2.py and server_dashboard_api_v3.py

These were early versions of the monitoring API that:
- Combined all functionality into a single monolithic file
- Used hard-coded port configurations
- Included service monitoring for unrelated projects ("opencode" services)
- Lacked proper modularization and separation of concerns

**Replaced by:** The current modular architecture:
- `central_api.py` - Central API with database integration
- `websocket_server.py` - Real-time WebSocket updates
- `terminal.py` - Web terminal service
- `database.py` - Data persistence layer
- Proper module separation in `backend/` directory

### status_webserver.py

This file appears to be from a different project (OpenCode) and:
- Serves content from `/var/www/html/opencode-status.html`
- References "OpenCode Status Dashboard" 
- Is not related to server-monitor functionality
- Should not have been in this repository

## Current Architecture

The current system uses a modular approach:

```
backend/
├── central_api.py           # Main API server (port 9083)
├── websocket_server.py      # WebSocket server (port 9085)
├── terminal.py              # Terminal service (port 9084)
├── database.py              # Database layer
├── ssh_manager.py           # SSH management
├── user_management.py       # User authentication
├── alert_manager.py         # Alert system
├── task_runner.py           # Task execution
└── ...                      # Other modules
```

Each component:
- Has a single responsibility
- Can be maintained independently
- Uses proper configuration management
- Follows security best practices

## Migration

If you have any references to these files in your deployment:

1. **Check for usage:**
   ```bash
   grep -r "server_dashboard_api" /etc/systemd/system/
   ```

2. **Remove old service files:**
   ```bash
   sudo systemctl stop server-dashboard-api-v2.service
   sudo systemctl disable server-dashboard-api-v2.service
   sudo rm /etc/systemd/system/server-dashboard-api-v2.service
   ```

3. **Use current services:**
   ```bash
   # Install via automated installer
   curl -fsSL https://raw.githubusercontent.com/minhtuancn/server-monitor/main/scripts/install.sh | sudo bash
   ```

## Historical Context

These files contain references to services from other projects:
- `opencode.service`
- `opencode-dashboard.service`
- `opencode-control-api.service`
- `opencode-watchdog.timer`

These references indicate that code from another project was accidentally included or used as a template. They have been preserved here for historical reference only.

## Support

These files are provided for reference only. No support or updates will be provided.
For current system documentation, see:
- [ARCHITECTURE.md](../../ARCHITECTURE.md)
- [DEPLOYMENT.md](../../DEPLOYMENT.md)
- [README.md](../../README.md)
