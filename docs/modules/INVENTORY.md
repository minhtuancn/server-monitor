# Server Inventory Module (Phase 4 Module 3)

## Overview

The Server Inventory module provides agentless system information collection from remote servers via SSH. It collects comprehensive system details including OS information, hardware specs, resource usage, and network configuration.

## Features

- **Agentless Collection**: Uses SSH to run read-only commands without requiring agent installation
- **SSH Key Vault Integration**: Supports encrypted SSH keys from the key vault
- **Comprehensive Data**: Collects OS, kernel, CPU, memory, disk, network, and optionally packages and services
- **Historical Tracking**: Maintains inventory snapshots for trend analysis
- **RBAC Enforcement**: Admin and operator roles can refresh inventory; all roles can view
- **Audit Logging**: All refresh operations are logged for security and compliance

## Architecture

### Data Flow

```
Frontend                Backend API              SSH Collector           Target Server
   |                        |                          |                       |
   |--Refresh Inventory---->|                          |                       |
   |                        |--Collect Inventory------>|                       |
   |                        |                          |--Execute Commands---->|
   |                        |                          |<---Return Output------|
   |                        |<---Inventory Data--------|                       |
   |                        |--Save to Database        |                       |
   |                        |--Add Audit Log           |                       |
   |<--Success Response-----|                          |                       |
   |                        |                          |                       |
   |--Get Latest----------->|                          |                       |
   |<--Inventory Data-------|                          |                       |
```

### Database Schema

#### `server_inventory_latest`
Stores the most recent inventory for each server.

| Column           | Type    | Description                      |
|-----------------|---------|----------------------------------|
| server_id       | INTEGER | Primary key, references servers  |
| collected_at    | TEXT    | Timestamp of collection          |
| inventory_json  | TEXT    | JSON-encoded inventory data      |

#### `server_inventory_snapshots`
Stores historical inventory snapshots.

| Column           | Type    | Description                      |
|-----------------|---------|----------------------------------|
| id              | TEXT    | UUID primary key                 |
| server_id       | INTEGER | References servers               |
| collected_at    | TEXT    | Timestamp of collection          |
| inventory_json  | TEXT    | JSON-encoded inventory data      |

### Inventory Data Structure

```json
{
  "collected_at": "2026-01-07T12:00:00Z",
  "os": {
    "name": "Ubuntu",
    "version": "22.04",
    "pretty_name": "Ubuntu 22.04.3 LTS"
  },
  "kernel": "5.15.0-91-generic",
  "hostname": "web-server-01",
  "uptime": {
    "uptime_seconds": 864000,
    "uptime_human": "10d 0h 0m"
  },
  "cpu": {
    "model": "Intel(R) Xeon(R) CPU E5-2680 v4 @ 2.40GHz",
    "cores": 8
  },
  "memory": {
    "total_mb": 16384,
    "used_mb": 8192,
    "available_mb": 8192,
    "used_percent": 50.0
  },
  "disk": {
    "total_gb": 100,
    "used_gb": 45,
    "available_gb": 55,
    "used_percent": 45
  },
  "network": {
    "primary_ip": "192.168.1.100",
    "interfaces": ["eth0", "eth1"]
  },
  "packages": [
    {"type": "dpkg", "count": 1234}
  ],
  "services": [
    {"type": "systemd", "running_count": 45}
  ]
}
```

## API Endpoints

### Refresh Inventory

**POST** `/api/servers/{id}/inventory/refresh`

Triggers inventory collection for a specific server.

**Authorization**: Admin or Operator role required

**Request Body**:
```json
{
  "ssh_key_id": "optional-key-vault-id",
  "include_packages": false,
  "include_services": false
}
```

**Response**:
```json
{
  "success": true,
  "message": "Inventory refreshed successfully",
  "collected_at": "2026-01-07T12:00:00Z",
  "inventory": { /* inventory data */ }
}
```

**Audit Log**: Creates `inventory.refresh` audit entry

### Get Latest Inventory

**GET** `/api/servers/{id}/inventory/latest`

Retrieves the most recent inventory data for a server.

**Authorization**: All authenticated users

**Response**:
```json
{
  "server_id": 1,
  "collected_at": "2026-01-07T12:00:00Z",
  "inventory": { /* inventory data */ }
}
```

## Collection Process

### Commands Executed

The inventory collector runs the following read-only commands:

1. **OS Information**:
   - `cat /etc/os-release` - OS name and version
   - `uname -s` - Fallback OS name
   - `uname -r` - Kernel version

2. **Hostname**:
   - `hostname`

3. **Uptime**:
   - `cat /proc/uptime` - Uptime in seconds

4. **CPU**:
   - `cat /proc/cpuinfo` - CPU model and cores
   - `nproc` - Fallback for core count

5. **Memory**:
   - `cat /proc/meminfo` - Total, available, and used memory

6. **Disk**:
   - `df -BG /` - Root filesystem usage

7. **Network**:
   - `ip route get 8.8.8.8` - Primary IP address
   - `hostname -I` - Fallback IP addresses
   - `ip -o link show` - Network interfaces

8. **Packages** (optional):
   - `dpkg -l | grep "^ii" | wc -l` - Debian/Ubuntu
   - `rpm -qa | wc -l` - RedHat/CentOS
   - `pacman -Q | wc -l` - Arch Linux

9. **Services** (optional):
   - `systemctl list-units --type=service --state=running --no-pager --no-legend | wc -l`

### Security Considerations

- **Read-Only**: All commands are read-only and do not modify the system
- **Timeout**: Each command has a 30-second timeout to prevent hanging
- **No Credential Logging**: SSH passwords and keys are never logged
- **Fallback Logic**: If a command fails, the collector continues with best-effort data
- **SSH Key Priority**: Vault key > File path > Password

## Frontend UI

### Server Workspace

The Server Detail page includes an "Inventory" tab with:

1. **Refresh Button**: Triggers inventory collection
2. **Loading States**: Shows progress during collection
3. **Card Layout**: Organized information cards:
   - Operating System (OS, kernel, hostname, uptime)
   - CPU (model, cores)
   - Memory (total, used, available, percentage)
   - Disk (total, used, available, percentage)
   - Network (primary IP, interfaces)
   - Packages (optional, count by type)
   - Services (optional, running count)

### Empty State

When no inventory data exists, displays a helpful message prompting the user to click "Refresh Inventory".

### Error Handling

- Connection failures display error messages
- Partial data is shown even if some collection fails
- Last collection timestamp is always displayed

## Usage Examples

### Refresh Inventory via API

```bash
curl -X POST http://localhost:9083/api/servers/1/inventory/refresh \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Get Latest Inventory

```bash
curl http://localhost:9083/api/servers/1/inventory/latest \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Using SSH Key from Vault

```bash
curl -X POST http://localhost:9083/api/servers/1/inventory/refresh \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ssh_key_id": "key-vault-uuid"}'
```

## Troubleshooting

### Common Issues

1. **"No inventory data available"**
   - Solution: Click "Refresh Inventory" button to collect data

2. **Connection timeout**
   - Verify server is accessible via SSH
   - Check firewall rules
   - Verify SSH credentials

3. **Partial data collection**
   - Some commands may fail on non-Linux systems
   - Check server logs for specific command failures
   - System may use different tools (e.g., busybox)

4. **Permission denied**
   - Ensure user has read access to `/proc`, `/etc`, and system commands
   - Most commands don't require root access

### Debug Mode

To enable detailed logging:

1. Check backend logs: `sudo journalctl -u server-monitor-api -f`
2. Look for "inventory" related entries
3. Check audit logs for failed refresh attempts

## Performance Considerations

- **Collection Time**: Typically 2-5 seconds per server
- **CPU Usage**: Minimal, read-only commands are lightweight
- **Network**: Small data transfer (< 1KB per collection)
- **Storage**: JSON inventory data is compressed and efficient

## Best Practices

1. **Refresh Frequency**: Refresh inventory hourly or when making system changes
2. **SSH Key Vault**: Use vault keys for better security
3. **Monitoring**: Set up alerts for collection failures
4. **Historical Data**: Periodically review inventory snapshots for trends
5. **RBAC**: Limit refresh permission to operators and admins only

## Future Enhancements

Potential future improvements:

- Scheduled automatic refreshes
- Diff view between snapshots
- Advanced filtering and search
- Export inventory to CSV/JSON
- Integration with configuration management tools
- Custom collection scripts
- Alert on inventory changes
