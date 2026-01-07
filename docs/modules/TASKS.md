# Module 4: Tasks / Remote Command Execution

## Overview

The Tasks module provides secure remote command execution capabilities across monitored servers. It enables administrators and operators to run commands on remote servers through the web interface with proper authentication, authorization, audit logging, and output management.

## Features

- **Remote Command Execution**: Run shell commands on remote servers via SSH
- **Asynchronous Task Queue**: Non-blocking command execution with status tracking
- **RBAC Integration**: Role-based access control (admin + operator can execute, viewer can read)
- **Security-First Design**: 
  - Output truncation to prevent data leaks
  - Configurable output storage
  - No logging of sensitive data
  - SSH key vault integration
- **Comprehensive Audit Trail**: All task operations logged with user, command, and metadata
- **Real-time Status Updates**: Track task execution status (queued, running, success, failed, timeout, cancelled)
- **Timeout Management**: Configurable per-task timeouts (1-600 seconds)
- **Task Cancellation**: Cancel running or queued tasks

## Architecture

### Components

1. **Task Database Schema** (`backend/database.py`)
   - `tasks` table with UUID primary keys
   - Indexes on server_id, user_id, status, created_at
   - Stores command, status, exit code, stdout/stderr (if enabled)

2. **Task Runner** (`backend/task_runner.py`)
   - In-process worker threads (default: 4)
   - Task queue with concurrency limits per server
   - SSH authentication via vault → key file → password
   - Output truncation and security policies

3. **API Endpoints** (`backend/central_api.py`)
   - `POST /api/servers/:id/tasks` - Create task
   - `GET /api/tasks` - List tasks (filtered by role)
   - `GET /api/tasks/:id` - Get task details
   - `POST /api/tasks/:id/cancel` - Cancel task

4. **Frontend UI** (`frontend-next/`)
   - Server Workspace "Tasks" tab
   - Task execution form with security warnings
   - Task list with status badges
   - Task detail viewer with stdout/stderr display

### Execution Flow

```
1. User submits command via UI
2. Backend validates auth & RBAC
3. Task created in database (status: queued)
4. Task ID returned to user
5. Task enqueued in task_runner
6. Worker thread picks up task
7. SSH connection established (vault → key → password)
8. Command executed with timeout
9. Output captured (if enabled) and truncated
10. Task status updated (success/failed/timeout)
11. Audit log created
12. UI polls for status updates
```

### Security Model

#### Output Storage Policy

By default, task output is **NOT** stored to prevent accidental data leaks. Users must explicitly enable output storage with the `store_output` flag.

When output storage is enabled:
- Output is truncated to `TASKS_OUTPUT_MAX_BYTES` (default: 64KB)
- Both stdout and stderr are captured separately
- Output is stored in the `tasks` table
- Users are warned about security implications in the UI

#### RBAC Enforcement

| Role | Create Tasks | View All Tasks | View Own Tasks | Cancel Any Task | Cancel Own Task |
|------|--------------|----------------|----------------|-----------------|-----------------|
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| Operator | ✅ | ❌ | ✅ | ❌ | ✅ |
| Viewer | ❌ | ❌ | ❌ | ❌ | ❌ |

#### SSH Authentication Priority

1. **SSH Key Vault**: Use encrypted key from vault (if server has `ssh_key_vault_id`)
2. **SSH Key File**: Use key file from `ssh_key_path`
3. **Password**: Use encrypted password from `ssh_password`

#### Audit Logging

All task operations are logged:
- `task.create` - Task created
- `task.start` - Task execution started
- `task.finish` - Task completed
- `task.fail` - Task failed
- `task.timeout` - Task timeout
- `task.cancel` - Task cancelled

Each audit log includes:
- User ID and username
- Task ID
- Server ID
- Command preview (first 100 chars)
- Client IP and user agent
- Metadata (timeout, store_output flag)

## Configuration

### Environment Variables

Add to `.env` file:

```bash
# Default behavior for storing task output (0 = don't store, 1 = store)
TASKS_STORE_OUTPUT_DEFAULT=0

# Maximum output size to store (in bytes, default: 65536 = 64KB)
TASKS_OUTPUT_MAX_BYTES=65536

# Maximum concurrent tasks per server (default: 1)
TASKS_CONCURRENT_PER_SERVER=1

# Default task timeout in seconds (default: 60)
TASKS_DEFAULT_TIMEOUT=60

# Number of task worker threads (default: 4)
TASKS_NUM_WORKERS=4
```

### Database Schema

The `tasks` table is created automatically via `init_database()` or migration `007`:

```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,                    -- UUID
    server_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    command TEXT NOT NULL,
    status TEXT NOT NULL,                   -- queued/running/success/failed/timeout/cancelled
    exit_code INTEGER,
    stdout TEXT,
    stderr TEXT,
    timeout_seconds INTEGER DEFAULT 60,
    store_output INTEGER DEFAULT 0,
    started_at TEXT,
    finished_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE CASCADE
);
```

Indexes for performance:
- `idx_tasks_server_id` - (server_id, created_at DESC)
- `idx_tasks_user_id` - (user_id, created_at DESC)
- `idx_tasks_status` - (status)
- `idx_tasks_created_at` - (created_at DESC)

## API Reference

### Create Task

```http
POST /api/servers/:id/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "command": "df -h",
  "timeout_seconds": 60,
  "store_output": false
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Task created and queued for execution"
}
```

**Authorization:**
- Requires `admin` or `operator` role

### List Tasks

```http
GET /api/tasks?server_id=1&status=success&limit=100&offset=0
Authorization: Bearer <token>
```

**Query Parameters:**
- `server_id` (optional) - Filter by server
- `user_id` (optional) - Filter by user (admin only)
- `status` (optional) - Filter by status (queued/running/success/failed/timeout/cancelled)
- `from` (optional) - Filter from date (ISO 8601)
- `to` (optional) - Filter to date (ISO 8601)
- `limit` (optional) - Max results (default: 100, max: 100)
- `offset` (optional) - Pagination offset (default: 0)

**Response:**
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "server_id": 1,
      "user_id": 1,
      "command": "df -h",
      "status": "success",
      "exit_code": 0,
      "stdout": null,
      "stderr": null,
      "timeout_seconds": 60,
      "store_output": 0,
      "started_at": "2026-01-07T15:30:00Z",
      "finished_at": "2026-01-07T15:30:02Z",
      "created_at": "2026-01-07T15:29:59Z"
    }
  ],
  "count": 1,
  "limit": 100,
  "offset": 0
}
```

**Authorization:**
- `admin` - See all tasks
- `operator` - See only own tasks
- `viewer` - See only own tasks

### Get Task Details

```http
GET /api/tasks/:id
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "server_id": 1,
  "user_id": 1,
  "command": "df -h",
  "status": "success",
  "exit_code": 0,
  "stdout": "Filesystem      Size  Used Avail Use% Mounted on\n...",
  "stderr": "",
  "timeout_seconds": 60,
  "store_output": 1,
  "started_at": "2026-01-07T15:30:00Z",
  "finished_at": "2026-01-07T15:30:02Z",
  "created_at": "2026-01-07T15:29:59Z"
}
```

**Authorization:**
- `admin` - See any task
- `operator` - See only own tasks
- `viewer` - See only own tasks

### Cancel Task

```http
POST /api/tasks/:id/cancel
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Task cancelled successfully"
}
```

**Authorization:**
- `admin` - Cancel any task
- `operator` - Cancel only own tasks
- `viewer` - Cannot cancel tasks

**Note:** Only tasks with status `queued` or `running` can be cancelled.

## UI Usage

### Server Workspace - Tasks Tab

1. Navigate to a server's workspace page
2. Click the "Tasks" tab
3. Click "Run Command" button
4. Enter command, timeout, and output storage preference
5. Review security warning
6. Click "Run Command"
7. Task appears in the list with status badge
8. Status updates automatically (polling every 3s for active tasks)
9. Click "View" to see task details and output

### Task Status Badges

- **Queued** (gray) - Task waiting in queue
- **Running** (blue) - Task currently executing
- **Success** (green) - Task completed with exit code 0
- **Failed** (red) - Task completed with non-zero exit code
- **Timeout** (red) - Task exceeded timeout limit
- **Cancelled** (orange) - Task was cancelled by user

## Best Practices

### Security

1. **Minimize Output Storage**: Only enable `store_output` when necessary for debugging
2. **Use Short Timeouts**: Set appropriate timeouts to prevent hung processes
3. **Audit Regular Review**: Review audit logs for unusual command patterns
4. **SSH Key Vault**: Prefer vault-stored keys over passwords
5. **Command Validation**: Be cautious with user-provided input in commands

### Operations

1. **Test Commands**: Test commands in terminal tab before automating
2. **Monitor Queue**: Check task queue status under high load
3. **Cleanup Old Tasks**: Run `db.delete_old_tasks(days=30)` periodically
4. **Error Handling**: Always check task status and exit codes
5. **Concurrency Limits**: Adjust `TASKS_CONCURRENT_PER_SERVER` based on server capacity

### Development

1. **Worker Threads**: Adjust `TASKS_NUM_WORKERS` based on workload
2. **Output Limits**: Tune `TASKS_OUTPUT_MAX_BYTES` based on use case
3. **Timeout Defaults**: Set `TASKS_DEFAULT_TIMEOUT` appropriate for typical commands
4. **Testing**: Mock SSH runner in tests to avoid external dependencies

## Troubleshooting

### Task Stuck in "Queued" Status

**Causes:**
- Server concurrency limit reached
- Worker threads busy
- SSH connection issues

**Solutions:**
- Check running tasks on same server
- Increase `TASKS_NUM_WORKERS` or `TASKS_CONCURRENT_PER_SERVER`
- Verify SSH credentials and connectivity

### Task Fails with "Authentication Failed"

**Causes:**
- Invalid SSH credentials
- Key vault key not found
- Network connectivity issues

**Solutions:**
- Test SSH connection in Terminal tab
- Verify SSH key vault configuration
- Check server firewall rules

### Output Truncated

**Causes:**
- Output exceeds `TASKS_OUTPUT_MAX_BYTES`

**Solutions:**
- Increase `TASKS_OUTPUT_MAX_BYTES` in .env
- Redirect output to file on remote server
- Use multiple smaller commands

### Task Timeout

**Causes:**
- Command takes longer than `timeout_seconds`
- Hung process on remote server

**Solutions:**
- Increase timeout for specific task
- Use background jobs (`nohup`, `screen`, `tmux`)
- Investigate remote server performance

## Migration

To add tasks support to existing database:

```bash
cd backend/migrations
python3 migrate.py
```

This runs migration `007` which creates the `tasks` table and indexes.

## Future Enhancements

- **Task Templates**: Save common commands as templates
- **Scheduled Tasks**: Cron-like task scheduling
- **Task Chains**: Execute multiple tasks in sequence
- **Output Streaming**: Real-time output streaming via WebSocket
- **Task History**: Enhanced search and filtering
- **Bulk Operations**: Run same command on multiple servers
- **Approval Workflow**: Require approval for sensitive commands

## Related Documentation

- [RBAC Guide](../SECURITY.md)
- [SSH Key Vault](./SSH_KEY_VAULT.md)
- [Audit Logging](../ARCHITECTURE.md)
- [API Documentation](../README.md)
