# System Health Dashboard

**Version:** 2.4.0
**Last Updated:** 2026-01-11
**Status:** ✅ Implemented

---

## Overview

The System Health Dashboard provides real-time monitoring of all server monitor services and system metrics. This admin-only feature allows administrators to quickly identify issues and monitor resource usage.

## Features

### Service Monitoring

- **API Server**: Monitor REST API health (port 9083)
- **WebSocket Server**: Check real-time monitoring service (port 9085)
- **Terminal Server**: Monitor SSH terminal service (port 9084)
- **Database**: Check database integrity and connection

Each service displays:
- Status indicator (Healthy, Unhealthy, Degraded, Error)
- Port number
- Descriptive message
- Additional metrics (database size, server count)

### System Metrics

- **Memory Usage**: Real-time RAM utilization with progress bar
- **Disk Usage**: Storage capacity and utilization
- **CPU Usage**: Processor utilization across all cores
- **System Uptime**: How long the system has been running

### Auto-Refresh

- Automatic refresh every 10 seconds
- Manual refresh button
- Toggle auto-refresh on/off
- Countdown timer showing next refresh

---

## Access

### URL

```
http://localhost:9081/en/settings/health
```

### Requirements

- **Role**: Admin only
- **Authentication**: Required (JWT token)
- **Permissions**: Admin role enforced by middleware

---

## API Endpoint

### GET /api/admin/health

Returns comprehensive health status for all services and system metrics.

**Authentication**: Required (Admin only)

**Response Format**:

```json
{
  "status": "healthy",
  "timestamp": "2026-01-11T05:30:00.000Z",
  "services": {
    "api": {
      "status": "healthy",
      "port": 9083,
      "message": "API server running"
    },
    "websocket": {
      "status": "healthy",
      "port": 9085,
      "message": "WebSocket server running"
    },
    "terminal": {
      "status": "healthy",
      "port": 9084,
      "message": "Terminal server running"
    },
    "database": {
      "status": "healthy",
      "message": "Database operational",
      "size_mb": 25.6,
      "server_count": 10
    }
  },
  "system": {
    "memory": {
      "total_mb": 16384,
      "used_mb": 8192,
      "available_mb": 8192,
      "percent_used": 50.0
    },
    "disk": {
      "total_gb": 500,
      "used_gb": 250,
      "available_gb": 250,
      "percent_used": 50.0
    },
    "cpu": {
      "percent_used": 25.5,
      "cores": 8
    },
    "uptime": {
      "seconds": 86400,
      "human": "1d 0h 0m"
    }
  }
}
```

**Status Values**:
- `healthy`: All services operational
- `degraded`: Some services have issues but system is functional
- `unhealthy`: Critical services down
- `error`: Unable to check service status

---

## Implementation Details

### Backend Components

**File**: `backend/observability.py`

```python
@staticmethod
def check_services_health() -> Dict[str, Any]:
    """
    Comprehensive health check for all services and system metrics

    Checks:
    - API service (always healthy if endpoint responds)
    - WebSocket service (port check on 9085)
    - Terminal service (port check on 9084)
    - Database (integrity check, size, server count)
    - System metrics (memory, disk, CPU, uptime via psutil)

    Returns:
        Dict with service statuses and system metrics
    """
```

**Dependencies**:
- `psutil`: System metrics collection
- `socket`: Port connectivity checks
- `sqlite3`: Database health checks

**File**: `backend/central_api.py`

```python
elif path == "/api/admin/health":
    # Admin-only endpoint
    # Calls HealthCheck.check_services_health()
```

### Frontend Components

**File**: `frontend-next/src/app/[locale]/(dashboard)/settings/health/page.tsx`

- React Query for data fetching with 10s refetch interval
- MUI components for UI
- Auto-refresh toggle and countdown timer
- Color-coded status indicators
- Progress bars for system metrics

**Navigation**: Added to admin settings menu in `AppShell.tsx`

---

## Usage

### For Administrators

1. Navigate to **Settings → System Health** in the sidebar
2. View overall system status banner at the top
3. Check individual service status cards
4. Monitor system metrics (memory, disk, CPU, uptime)
5. Toggle auto-refresh on/off as needed
6. Click refresh button for manual updates

### Status Indicators

| Color | Status | Meaning |
|-------|--------|---------|
| 🟢 Green | Healthy | Service is operational |
| 🟡 Yellow | Degraded | Service has warnings but functional |
| 🔴 Red | Unhealthy/Error | Service is down or failing |

### Alert Thresholds

System metrics show color-coded warnings:
- **Memory/Disk**:
  - Green: < 75%
  - Yellow: 75-90%
  - Red: > 90%
- **CPU**:
  - Green: < 75%
  - Yellow: 75-90%
  - Red: > 90%

---

## Troubleshooting

### Service Shows "Unhealthy"

**WebSocket or Terminal Server**:
1. Check if service is running: `ps aux | grep websocket_server` or `grep terminal`
2. Check logs: `tail -f logs/websocket.log` or `logs/terminal.log`
3. Restart service: `./start-all.sh`

**Database**:
1. Check database file exists: `ls -lh data/servers.db`
2. Run integrity check: `sqlite3 data/servers.db "PRAGMA integrity_check;"`
3. Check permissions: `ls -l data/servers.db`

### System Metrics Not Showing

1. Verify `psutil` is installed: `pip list | grep psutil`
2. Install if missing: `pip install psutil`
3. Check Python version: `python --version` (requires 3.7+)

### Access Denied

1. Verify you're logged in as admin user
2. Check role in browser DevTools: `/api/auth/session`
3. Contact admin to upgrade your role if needed

---

## Performance Considerations

- Health checks use minimal resources (< 100ms response time)
- Port checks have 1-second timeout
- CPU sampling uses 0.1s interval (low overhead)
- Auto-refresh can be disabled to reduce load
- Frontend caching via React Query

---

## Security

- **Authentication**: JWT token required
- **Authorization**: Admin role enforced
- **Rate Limiting**: Subject to global rate limits (100 req/min)
- **CORS**: Protected by CORS policy
- **Data Exposure**: Only aggregated metrics exposed (no sensitive data)

---

## Future Enhancements

Potential improvements for future versions:

1. **Alerting**: Automatic notifications when services go down
2. **History**: Track health metrics over time
3. **Thresholds**: Configurable alert thresholds per metric
4. **Export**: Download health reports as CSV/PDF
5. **Charts**: Historical graphs for metrics trends
6. **Webhooks**: Trigger webhooks on health status changes

---

## Related Documentation

- [Observability](../architecture/OBSERVABILITY.md) - Logging and metrics
- [API Reference](../api/README.md) - Complete API documentation
- [Security](../security/SECURITY.md) - Security best practices
- [Troubleshooting](../operations/TROUBLESHOOTING.md) - Common issues

---

**Questions or Issues?**

- GitHub Issues: [github.com/minhtuancn/server-monitor/issues](https://github.com/minhtuancn/server-monitor/issues)
- Documentation: [docs/README.md](../README.md)
