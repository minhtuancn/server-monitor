#!/usr/bin/env python3

"""
Database module for multi-server monitoring
Manages server list, credentials, and monitoring history
"""

import sqlite3
import json
from datetime import datetime, timezone
import os
import hashlib
import secrets
import base64
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Determine database path - support both development and production paths
# Use pathlib for cleaner path manipulation
from pathlib import Path

_default_db_path = str(Path(__file__).parent.parent / "data" / "servers.db")
DB_PATH = os.environ.get("DB_PATH", _default_db_path)

# Encryption key - Use environment variable or generate a random default
# WARNING: Random default means encrypted data won't survive server restarts
_env_key = os.environ.get("ENCRYPTION_KEY")
if _env_key:
    # Pad key to 32 bytes using SHA256 hash for consistent, secure padding
    _key_hash = hashlib.sha256(_env_key.encode()).digest()
    ENCRYPTION_KEY = _key_hash
else:
    # Generate a random key for development
    ENCRYPTION_KEY = secrets.token_bytes(32)
    print("WARNING: ENCRYPTION_KEY not set in environment. Using randomly generated key.")
    print("         Encrypted data will not survive server restarts. Set ENCRYPTION_KEY in .env for production.")


def hash_password(password):
    """Hash password using SHA256 (for admin users)"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed


def encrypt_ssh_password(password):
    """Simple XOR encryption for SSH passwords (for storage)"""
    if not password:
        return ""
    result = bytearray()
    key = ENCRYPTION_KEY
    for i, char in enumerate(password.encode()):
        result.append(char ^ key[i % len(key)])
    return base64.b64encode(bytes(result)).decode()


def decrypt_ssh_password(encrypted):
    """Decrypt SSH password"""
    if not encrypted:
        return ""
    try:
        data = base64.b64decode(encrypted)
        result = bytearray()
        key = ENCRYPTION_KEY
        for i, byte in enumerate(data):
            result.append(byte ^ key[i % len(key)])
        return bytes(result).decode()
    except:
        return ""


def generate_token():
    """Generate random session token"""
    return secrets.token_urlsafe(32)


def init_database():
    """Initialize database and create tables"""
    # Create data directory if not exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Servers table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            host TEXT NOT NULL UNIQUE,
            port INTEGER DEFAULT 22,
            username TEXT NOT NULL,
            description TEXT,
            ssh_key_path TEXT,
            ssh_password TEXT,
            agent_port INTEGER DEFAULT 8083,
            agent_installed INTEGER DEFAULT 0,
            status TEXT DEFAULT 'unknown',
            last_seen TIMESTAMP,
            tags TEXT,
            timezone TEXT DEFAULT 'UTC',
            connection_timeout INTEGER DEFAULT 10,
            group_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE SET NULL
        )
    """
    )

    # Admin users table (for authentication)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'admin',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """
    )

    # Session tokens table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE CASCADE
        )
    """
    )

    # Monitoring history table (optional - for long-term storage)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS monitoring_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id INTEGER NOT NULL,
            metric_type TEXT NOT NULL,
            metric_data TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
        )
    """
    )

    # Alerts table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id INTEGER NOT NULL,
            alert_type TEXT NOT NULL,
            message TEXT NOT NULL,
            severity TEXT DEFAULT 'warning',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
        )
    """
    )

    # Command snippets table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS command_snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            command TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            group_id INTEGER,
            is_sudo INTEGER DEFAULT 0,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE SET NULL,
            FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL
        )
    """
    )

    # Groups table for organizing servers, notes, snippets, inventory
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            color TEXT DEFAULT '#1976d2',
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL,
            UNIQUE(name, type)
        )
    """
    )

    # Group memberships (many-to-many relationships)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS group_memberships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            item_type TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
            UNIQUE(group_id, item_id, item_type)
        )
    """
    )

    # SSH keys management table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ssh_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            key_type TEXT DEFAULT 'rsa',
            private_key_path TEXT NOT NULL,
            public_key TEXT,
            fingerprint TEXT,
            passphrase TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL
        )
    """
    )

    # Server notes table (Markdown) - Phase 4 Module 5 Enhanced
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS server_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            group_id INTEGER,
            created_by INTEGER,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE,
            FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE SET NULL,
            FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL,
            FOREIGN KEY (updated_by) REFERENCES admin_users(id) ON DELETE SET NULL
        )
    """
    )

    # Tags table (Phase 4 Module 5)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color TEXT DEFAULT '#3f51b5',
            description TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL
        )
    """
    )

    # Server-Tag mapping table (Phase 4 Module 5)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS server_tag_map (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL,
            UNIQUE(server_id, tag_id)
        )
    """
    )

    # Create indexes for tags
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_server_tag_map_server_id 
        ON server_tag_map(server_id)
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_server_tag_map_tag_id 
        ON server_tag_map(tag_id)
    """
    )

    # Domain settings table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain_name TEXT,
            ssl_enabled INTEGER DEFAULT 0,
            ssl_type TEXT DEFAULT 'none',
            cert_path TEXT,
            key_path TEXT,
            auto_renew INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Terminal sessions table (Phase 4 Module 2)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS terminal_sessions (
            id TEXT PRIMARY KEY,
            server_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            ssh_key_id TEXT,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            status TEXT DEFAULT 'active',
            last_activity TEXT,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE CASCADE,
            FOREIGN KEY (ssh_key_id) REFERENCES ssh_keys(id) ON DELETE SET NULL
        )
    """
    )

    # Audit logs table (Phase 4 Module 6 - Foundation)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_id TEXT NOT NULL,
            meta_json TEXT,
            ip TEXT,
            user_agent TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE CASCADE
        )
    """
    )

    # Create indexes for audit logs
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id 
        ON audit_logs(user_id)
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_audit_logs_action 
        ON audit_logs(action)
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at 
        ON audit_logs(created_at)
    """
    )

    # Server inventory tables (Phase 4 Module 3)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS server_inventory_latest (
            server_id INTEGER PRIMARY KEY,
            collected_at TEXT NOT NULL,
            inventory_json TEXT NOT NULL,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS server_inventory_snapshots (
            id TEXT PRIMARY KEY,
            server_id INTEGER NOT NULL,
            collected_at TEXT NOT NULL,
            inventory_json TEXT NOT NULL,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
        )
    """
    )

    # Create index for inventory snapshots
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_inventory_snapshots_server_id 
        ON server_inventory_snapshots(server_id)
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_inventory_snapshots_collected_at 
        ON server_inventory_snapshots(collected_at)
    """
    )

    # Tasks table (Phase 4 Module 4)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            server_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            command TEXT NOT NULL,
            status TEXT NOT NULL,
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
        )
    """
    )

    # Create indexes for tasks
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tasks_server_id 
        ON tasks(server_id, created_at DESC)
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tasks_user_id 
        ON tasks(user_id, created_at DESC)
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tasks_status 
        ON tasks(status)
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tasks_created_at 
        ON tasks(created_at DESC)
    """
    )

    # Webhooks table (Phase 8)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS webhooks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            secret TEXT,
            enabled INTEGER DEFAULT 1,
            event_types TEXT,
            retry_max INTEGER DEFAULT 3,
            timeout INTEGER DEFAULT 10,
            created_by INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_triggered_at TEXT,
            FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE CASCADE
        )
    """
    )

    # Create indexes for webhooks
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_webhooks_enabled 
        ON webhooks(enabled)
    """
    )

    # Webhook delivery log (for tracking and debugging)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS webhook_deliveries (
            id TEXT PRIMARY KEY,
            webhook_id TEXT NOT NULL,
            event_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            status TEXT NOT NULL,
            status_code INTEGER,
            response_body TEXT,
            error TEXT,
            attempt INTEGER DEFAULT 1,
            delivered_at TEXT NOT NULL,
            FOREIGN KEY (webhook_id) REFERENCES webhooks(id) ON DELETE CASCADE
        )
    """
    )

    # Create indexes for webhook deliveries
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_webhook_id 
        ON webhook_deliveries(webhook_id)
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_delivered_at 
        ON webhook_deliveries(delivered_at DESC)
    """
    )

    # ==================== MIGRATIONS ====================
    # Add group_id columns to existing tables if they don't exist

    # Check if servers table has group_id column
    cursor.execute("PRAGMA table_info(servers)")
    servers_columns = [col[1] for col in cursor.fetchall()]
    if "group_id" not in servers_columns:
        cursor.execute("ALTER TABLE servers ADD COLUMN group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL")
        print("✓ Added group_id column to servers table")

    # Check if server_notes table has group_id column
    cursor.execute("PRAGMA table_info(server_notes)")
    notes_columns = [col[1] for col in cursor.fetchall()]
    if "group_id" not in notes_columns:
        cursor.execute("ALTER TABLE server_notes ADD COLUMN group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL")
        print("✓ Added group_id column to server_notes table")

    # Check if command_snippets table has group_id column
    cursor.execute("PRAGMA table_info(command_snippets)")
    snippets_columns = [col[1] for col in cursor.fetchall()]
    if "group_id" not in snippets_columns:
        cursor.execute(
            "ALTER TABLE command_snippets ADD COLUMN group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL"
        )
        print("✓ Added group_id column to command_snippets table")

    # ==================== PERFORMANCE INDEXES ====================
    # Add indexes for frequently queried columns to improve performance

    # Servers table indexes
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_servers_status
        ON servers(status)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_servers_group_id
        ON servers(group_id)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_servers_created_at
        ON servers(created_at DESC)
        """
    )

    # Alerts table indexes
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_alerts_server_id
        ON alerts(server_id)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_alerts_is_read
        ON alerts(is_read)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_alerts_created_at
        ON alerts(created_at DESC)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_alerts_severity
        ON alerts(severity)
        """
    )

    # Sessions table index (critical for auth performance)
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_sessions_token
        ON sessions(token)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_sessions_user_id
        ON sessions(user_id)
        """
    )

    # Monitoring history indexes
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_monitoring_history_server_id
        ON monitoring_history(server_id)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_monitoring_history_timestamp
        ON monitoring_history(timestamp DESC)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_monitoring_history_metric_type
        ON monitoring_history(metric_type)
        """
    )

    # Composite index for common query pattern
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_monitoring_history_server_metric
        ON monitoring_history(server_id, metric_type, timestamp DESC)
        """
    )

    # Terminal sessions indexes
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_terminal_sessions_user_id
        ON terminal_sessions(user_id)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_terminal_sessions_status
        ON terminal_sessions(status)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_terminal_sessions_server_id
        ON terminal_sessions(server_id)
        """
    )

    # Server notes indexes
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_server_notes_server_id
        ON server_notes(server_id)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_server_notes_created_at
        ON server_notes(created_at DESC)
        """
    )

    # Admin users index
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_admin_users_username
        ON admin_users(username)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_admin_users_is_active
        ON admin_users(is_active)
        """
    )

    # Groups indexes
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_groups_created_at
        ON groups(created_at DESC)
        """
    )

    # Group memberships index
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_group_memberships_group_id
        ON group_memberships(group_id)
        """
    )

    # Command snippets indexes
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_command_snippets_category
        ON command_snippets(category)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_command_snippets_group_id
        ON command_snippets(group_id)
        """
    )

    # SSH keys indexes
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ssh_keys_created_by
        ON ssh_keys(created_by)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ssh_keys_deleted_at
        ON ssh_keys(deleted_at)
        """
    )

    print("✓ Added performance indexes for all tables")

    conn.commit()
    conn.close()


def get_connection():
    """Get database connection"""
    init_database()  # Ensure DB exists
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# ==================== SERVER MANAGEMENT ====================


def add_server(
    name,
    host,
    port,
    username,
    description="",
    ssh_key_path="",
    ssh_password="",
    agent_port=8083,
    tags="",
    group_id=None,
):
    """Add a new server to monitor"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Encrypt password if provided
        if ssh_password:
            ssh_password = encrypt_ssh_password(ssh_password)

        cursor.execute(
            """
            INSERT INTO servers (name, host, port, username, description, ssh_key_path, ssh_password, agent_port, tags, group_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (name, host, port, username, description, ssh_key_path, ssh_password, agent_port, tags, group_id),
        )

        conn.commit()
        server_id = cursor.lastrowid
        conn.close()

        return {"success": True, "server_id": server_id, "message": f"Server {name} added successfully"}

    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "error": f"Server with host {host} already exists"}

    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def get_servers(status=None):
    """Get all servers or filter by status"""
    conn = get_connection()
    cursor = conn.cursor()

    if status:
        cursor.execute(
            """
            SELECT s.*, g.name as group_name, g.color as group_color
            FROM servers s
            LEFT JOIN groups g ON s.group_id = g.id
            WHERE s.status = ?
            ORDER BY s.name
        """,
            (status,),
        )
    else:
        cursor.execute(
            """
            SELECT s.*, g.name as group_name, g.color as group_color
            FROM servers s
            LEFT JOIN groups g ON s.group_id = g.id
            ORDER BY s.name
        """
        )

    columns = [desc[0] for desc in cursor.description]
    servers = []

    for row in cursor.fetchall():
        server = dict(zip(columns, row))
        servers.append(server)

    conn.close()
    return servers


def get_server(server_id, decrypt_password=False):
    """Get a single server by ID"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT s.*, g.name as group_name, g.color as group_color
        FROM servers s
        LEFT JOIN groups g ON s.group_id = g.id
        WHERE s.id = ?
    """,
        (server_id,),
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    columns = [desc[0] for desc in cursor.description]
    server = dict(zip(columns, row))

    # Decrypt SSH password if requested and exists
    if decrypt_password and server.get("ssh_password"):
        server["ssh_password"] = decrypt_ssh_password(server["ssh_password"])

    conn.close()
    return server


def update_server(server_id, **kwargs):
    """Update server information"""
    conn = get_connection()
    cursor = conn.cursor()

    allowed_fields = [
        "name",
        "host",
        "port",
        "username",
        "description",
        "ssh_key_path",
        "ssh_password",
        "agent_port",
        "tags",
        "status",
        "agent_installed",
        "group_id",
    ]

    updates = []
    values = []

    for key, value in kwargs.items():
        if key in allowed_fields:
            # Encrypt password if updating password
            if key == "ssh_password" and value:
                value = encrypt_ssh_password(value)
            updates.append(f"{key} = ?")
            values.append(value)

    if not updates:
        conn.close()
        return {"success": False, "error": "No valid fields to update"}

    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(server_id)

    # Security Note: Column names in query are from allowed_fields allowlist above (line 529)
    # This is NOT a SQL injection vulnerability - column names are controlled, not from user input
    query = f"UPDATE servers SET {', '.join(updates)} WHERE id = ?"  # nosec B608

    try:
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return {"success": True, "message": f"Server {server_id} updated successfully"}

    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def delete_server(server_id):
    """Delete a server"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM servers WHERE id = ?", (server_id,))

        if cursor.rowcount == 0:
            conn.close()
            return {"success": False, "error": "Server not found"}

        conn.commit()
        conn.close()

        return {"success": True, "message": f"Server {server_id} deleted successfully"}

    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def update_server_status(server_id, status, last_seen=None):
    """Update server online/offline status"""
    conn = get_connection()
    cursor = conn.cursor()

    if last_seen is None:
        last_seen = datetime.now().isoformat()

    cursor.execute(
        """
        UPDATE servers 
        SET status = ?, last_seen = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    """,
        (status, last_seen, server_id),
    )

    conn.commit()
    conn.close()


# ==================== MONITORING HISTORY ====================


def save_monitoring_data(server_id, metric_type, metric_data):
    """Save monitoring data to history"""
    conn = get_connection()
    cursor = conn.cursor()

    # Convert dict to JSON string
    if isinstance(metric_data, dict):
        metric_data = json.dumps(metric_data)

    cursor.execute(
        """
        INSERT INTO monitoring_history (server_id, metric_type, metric_data)
        VALUES (?, ?, ?)
    """,
        (server_id, metric_type, metric_data),
    )

    conn.commit()
    conn.close()


def get_monitoring_history(server_id, metric_type=None, hours=24):
    """Get monitoring history for a server"""
    conn = get_connection()
    cursor = conn.cursor()

    if metric_type:
        cursor.execute(
            """
            SELECT * FROM monitoring_history 
            WHERE server_id = ? AND metric_type = ?
            AND timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp DESC
        """,
            (server_id, metric_type, hours),
        )
    else:
        cursor.execute(
            """
            SELECT * FROM monitoring_history 
            WHERE server_id = ?
            AND timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp DESC
        """,
            (server_id, hours),
        )

    columns = [desc[0] for desc in cursor.description]
    history = []

    for row in cursor.fetchall():
        item = dict(zip(columns, row))
        # Parse JSON data
        try:
            item["metric_data"] = json.loads(item["metric_data"])
        except:
            pass
        history.append(item)

    conn.close()
    return history


def cleanup_old_history(days=7):
    """Delete monitoring history older than N days"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM monitoring_history 
        WHERE timestamp < datetime('now', '-' || ? || ' days')
    """,
        (days,),
    )

    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    return deleted


# ==================== ALERTS ====================


def create_alert(server_id, alert_type, message, severity="warning"):
    """Create an alert"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO alerts (server_id, alert_type, message, severity)
        VALUES (?, ?, ?, ?)
    """,
        (server_id, alert_type, message, severity),
    )

    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()

    return alert_id


def get_alerts(server_id=None, is_read=None, limit=50):
    """Get alerts"""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM alerts WHERE 1=1"
    params = []

    if server_id:
        query += " AND server_id = ?"
        params.append(server_id)

    if is_read is not None:
        query += " AND is_read = ?"
        params.append(is_read)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)

    columns = [desc[0] for desc in cursor.description]
    alerts = []

    for row in cursor.fetchall():
        alert = dict(zip(columns, row))
        alerts.append(alert)

    conn.close()
    return alerts


def mark_alert_read(alert_id):
    """Mark an alert as read"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE alerts SET is_read = 1 WHERE id = ?", (alert_id,))

    conn.commit()
    conn.close()


# ==================== STATISTICS ====================


def get_server_stats():
    """Get overview statistics"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM servers")
    total_servers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM servers WHERE status = 'online'")
    online_servers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM servers WHERE status = 'offline'")
    offline_servers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alerts WHERE is_read = 0")
    unread_alerts = cursor.fetchone()[0]

    conn.close()

    return {
        "total_servers": total_servers,
        "online_servers": online_servers,
        "offline_servers": offline_servers,
        "unknown_servers": total_servers - online_servers - offline_servers,
        "unread_alerts": unread_alerts,
    }


# ==================== AUTHENTICATION ====================


def create_admin_user(username, password, email="", role="admin"):
    """Create a new admin user"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        password_hash = hash_password(password)

        cursor.execute(
            """
            INSERT INTO admin_users (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        """,
            (username, password_hash, email, role),
        )

        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        return {"success": True, "user_id": user_id, "message": f"Admin user {username} created"}

    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "error": f"Username {username} already exists"}

    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def authenticate_user(username, password):
    """Authenticate user and create session"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, password_hash, is_active FROM admin_users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"success": False, "error": "Invalid username or password"}

    user_id, password_hash, is_active = row

    if not is_active:
        conn.close()
        return {"success": False, "error": "Account is disabled"}

    if not verify_password(password, password_hash):
        conn.close()
        return {"success": False, "error": "Invalid username or password"}

    # Create session token (expires in 7 days)
    token = generate_token()
    from datetime import timedelta

    expires_at = (datetime.now() + timedelta(days=7)).isoformat()

    cursor.execute(
        """
        INSERT INTO sessions (user_id, token, expires_at)
        VALUES (?, ?, ?)
    """,
        (user_id, token, expires_at),
    )

    # Update last login
    cursor.execute(
        """
        UPDATE admin_users 
        SET last_login = CURRENT_TIMESTAMP 
        WHERE id = ?
    """,
        (user_id,),
    )

    conn.commit()
    conn.close()

    return {"success": True, "token": token, "username": username, "expires_at": expires_at}


def verify_session(token):
    """Verify session token"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT s.user_id, u.username, u.role, s.expires_at
        FROM sessions s
        JOIN admin_users u ON s.user_id = u.id
        WHERE s.token = ? AND u.is_active = 1
    """,
        (token,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"valid": False, "error": "Invalid session"}

    user_id, username, role, expires_at = row

    # Check if expired
    if datetime.fromisoformat(expires_at) < datetime.now():
        return {"valid": False, "error": "Session expired"}

    return {"valid": True, "user_id": user_id, "username": username, "role": role}


def logout_user(token):
    """Delete session token"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    return {"success": deleted > 0}


def get_admin_user(user_id):
    """Get admin user by ID"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username, email, role, is_active, created_at, last_login 
        FROM admin_users 
        WHERE id = ?
    """,
        (user_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    columns = ["id", "username", "email", "role", "is_active", "created_at", "last_login"]
    user = dict(zip(columns, row))
    return user


def get_all_users():
    """Get all admin users"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username, email, role, is_active, created_at, last_login 
        FROM admin_users 
        ORDER BY created_at DESC
    """
    )

    columns = [desc[0] for desc in cursor.description]
    users = []

    for row in cursor.fetchall():
        user = dict(zip(columns, row))
        users.append(user)

    conn.close()
    return users


def change_password(username, old_password, new_password):
    """Change user password"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, password_hash FROM admin_users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"success": False, "error": "User not found"}

    user_id, current_hash = row

    if not verify_password(old_password, current_hash):
        conn.close()
        return {"success": False, "error": "Invalid current password"}

    new_hash = hash_password(new_password)

    cursor.execute(
        """
        UPDATE admin_users 
        SET password_hash = ? 
        WHERE id = ?
    """,
        (new_hash, user_id),
    )

    conn.commit()
    conn.close()

    return {"success": True, "message": "Password changed successfully"}


def cleanup_expired_sessions(days=7):
    """Delete sessions older than N days (default 7 days = 1 week)"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM sessions 
        WHERE datetime(created_at, '+' || ? || ' days') < datetime('now')
    """,
        (days,),
    )

    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    return {"deleted": deleted, "message": f"Deleted {deleted} expired sessions"}


# ==================== COMMAND SNIPPETS ====================


def add_snippet(name, command, description="", category="general", is_sudo=0, created_by=None, group_id=None):
    """Add a command snippet"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO command_snippets (name, command, description, category, is_sudo, created_by, group_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (name, command, description, category, is_sudo, created_by, group_id),
        )

        conn.commit()
        snippet_id = cursor.lastrowid
        conn.close()

        return {"success": True, "snippet_id": snippet_id, "message": f"Snippet {name} created"}

    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def get_snippets(category=None):
    """Get all command snippets or filter by category"""
    conn = get_connection()
    cursor = conn.cursor()

    if category:
        cursor.execute(
            """
            SELECT cs.*, g.name as group_name, g.color as group_color
            FROM command_snippets cs
            LEFT JOIN groups g ON cs.group_id = g.id
            WHERE cs.category = ?
            ORDER BY cs.name
        """,
            (category,),
        )
    else:
        cursor.execute(
            """
            SELECT cs.*, g.name as group_name, g.color as group_color
            FROM command_snippets cs
            LEFT JOIN groups g ON cs.group_id = g.id
            ORDER BY cs.category, cs.name
        """
        )

    columns = [desc[0] for desc in cursor.description]
    snippets = []

    for row in cursor.fetchall():
        snippet = dict(zip(columns, row))
        snippets.append(snippet)

    conn.close()
    return snippets


def get_snippet(snippet_id):
    """Get a single snippet by ID"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM command_snippets WHERE id = ?", (snippet_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    columns = [desc[0] for desc in cursor.description]
    snippet = dict(zip(columns, row))

    conn.close()
    return snippet


def update_snippet(snippet_id, **kwargs):
    """Update snippet information"""
    conn = get_connection()
    cursor = conn.cursor()

    allowed_fields = ["name", "command", "description", "category", "is_sudo", "group_id"]

    updates = []
    values = []

    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            values.append(value)

    if not updates:
        conn.close()
        return {"success": False, "error": "No valid fields to update"}

    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(snippet_id)

    # Security Note: Column names from allowed_fields allowlist (line 1037)
    query = f"UPDATE command_snippets SET {', '.join(updates)} WHERE id = ?"  # nosec B608

    try:
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return {"success": True, "message": f"Snippet {snippet_id} updated"}

    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def delete_snippet(snippet_id):
    """Delete a snippet"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM command_snippets WHERE id = ?", (snippet_id,))

        if cursor.rowcount == 0:
            conn.close()
            return {"success": False, "error": "Snippet not found"}

        conn.commit()
        conn.close()

        return {"success": True, "message": f"Snippet {snippet_id} deleted"}

    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


# ==================== SSH KEYS MANAGEMENT ====================


def add_ssh_key(name, private_key_path, description="", key_type="rsa", public_key="", passphrase="", created_by=None):
    """Add a new SSH key"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Encrypt passphrase if provided
        if passphrase:
            passphrase = encrypt_ssh_password(passphrase)

        # Generate fingerprint from private key
        fingerprint = None
        if os.path.exists(private_key_path):
            try:
                import paramiko

                key = paramiko.RSAKey.from_private_key_file(private_key_path)
                fingerprint = key.get_fingerprint().hex()
            except:
                pass

        cursor.execute(
            """
            INSERT INTO ssh_keys (name, private_key_path, description, key_type, public_key, fingerprint, passphrase, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (name, private_key_path, description, key_type, public_key, fingerprint, passphrase, created_by),
        )

        conn.commit()
        key_id = cursor.lastrowid
        conn.close()

        return {"success": True, "key_id": key_id, "message": f"SSH key {name} added successfully"}

    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "error": f"SSH key with name {name} already exists"}

    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def get_ssh_keys():
    """Get all SSH keys"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, description, key_type, private_key_path, public_key, fingerprint, 
               created_at, updated_at, last_used
        FROM ssh_keys 
        ORDER BY name
    """
    )

    columns = [desc[0] for desc in cursor.description]
    keys = []

    for row in cursor.fetchall():
        key = dict(zip(columns, row))
        keys.append(key)

    conn.close()
    return keys


def get_ssh_key(key_id, decrypt_passphrase=False):
    """Get a single SSH key by ID"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ssh_keys WHERE id = ?", (key_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    columns = [desc[0] for desc in cursor.description]
    key = dict(zip(columns, row))

    # Decrypt passphrase if requested and exists
    if decrypt_passphrase and key.get("passphrase"):
        key["passphrase"] = decrypt_ssh_password(key["passphrase"])

    conn.close()
    return key


def update_ssh_key(key_id, **kwargs):
    """Update SSH key information"""
    conn = get_connection()
    cursor = conn.cursor()

    allowed_fields = ["name", "description", "key_type", "private_key_path", "public_key", "passphrase"]

    updates = []
    values = []

    for key, value in kwargs.items():
        if key in allowed_fields:
            # Encrypt passphrase if updating
            if key == "passphrase" and value:
                value = encrypt_ssh_password(value)
            updates.append(f"{key} = ?")
            values.append(value)

    if not updates:
        conn.close()
        return {"success": False, "error": "No valid fields to update"}

    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(key_id)

    # Security Note: Column names from allowed_fields allowlist (line 1179)
    query = f"UPDATE ssh_keys SET {', '.join(updates)} WHERE id = ?"  # nosec B608

    try:
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return {"success": True, "message": f"SSH key {key_id} updated successfully"}

    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def delete_ssh_key(key_id):
    """Delete an SSH key"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM ssh_keys WHERE id = ?", (key_id,))

        if cursor.rowcount == 0:
            conn.close()
            return {"success": False, "error": "SSH key not found"}

        conn.commit()
        conn.close()

        return {"success": True, "message": f"SSH key {key_id} deleted successfully"}

    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def update_ssh_key_last_used(key_id):
    """Update last used timestamp for SSH key"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE ssh_keys 
        SET last_used = CURRENT_TIMESTAMP 
        WHERE id = ?
    """,
        (key_id,),
    )

    conn.commit()
    conn.close()


def get_ssh_key_by_name(name):
    """Get SSH key by name"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ssh_keys WHERE name = ?", (name,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    columns = [desc[0] for desc in cursor.description]
    key = dict(zip(columns, row))

    conn.close()
    return key


# ==================== EXPORT FUNCTIONS ====================


def _sanitize_csv_field(value):
    """
    Sanitize CSV field to prevent CSV injection
    Prefix with single quote if starts with =, +, -, @, tab, or carriage return

    Args:
        value: Field value to sanitize

    Returns:
        Sanitized field value
    """
    if value is None:
        return ""

    value_str = str(value)

    # Check if field starts with potentially dangerous characters
    # The if check is needed to prevent IndexError on empty strings
    if value_str:
        first_char = value_str[0]
        if first_char in ["=", "+", "-", "@", "\t", "\r"]:
            # Prefix with single quote to prevent formula injection
            return "'" + value_str

    return value_str


def export_servers_csv():
    """Export servers list to CSV format"""
    import csv
    from io import StringIO

    servers = get_servers()

    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "ID",
            "Name",
            "Host",
            "Port",
            "Username",
            "Description",
            "Status",
            "Tags",
            "Agent Port",
            "Last Seen",
            "Created At",
        ]
    )

    # Data - sanitize each field to prevent CSV injection
    for server in servers:
        writer.writerow(
            [
                _sanitize_csv_field(server.get("id")),
                _sanitize_csv_field(server.get("name")),
                _sanitize_csv_field(server.get("host")),
                _sanitize_csv_field(server.get("port")),
                _sanitize_csv_field(server.get("username")),
                _sanitize_csv_field(server.get("description", "")),
                _sanitize_csv_field(server.get("status")),
                _sanitize_csv_field(server.get("tags", "")),
                _sanitize_csv_field(server.get("agent_port")),
                _sanitize_csv_field(server.get("last_seen", "")),
                _sanitize_csv_field(server.get("created_at", "")),
            ]
        )

    return output.getvalue()


def export_monitoring_history_csv(server_id=None, start_date=None, end_date=None):
    """Export monitoring history to CSV"""
    import csv
    from io import StringIO

    history = get_monitoring_history(server_id, start_date, end_date)

    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        ["Timestamp", "Server ID", "Metric Type", "CPU %", "Memory %", "Disk %", "Network RX", "Network TX"]
    )

    # Data
    for item in history:
        metric_data = item.get("metric_data", {})
        if isinstance(metric_data, str):
            try:
                metric_data = json.loads(metric_data)
            except:
                metric_data = {}

        # Sanitize each field to prevent CSV injection
        writer.writerow(
            [
                _sanitize_csv_field(item.get("timestamp")),
                _sanitize_csv_field(item.get("server_id")),
                _sanitize_csv_field(item.get("metric_type")),
                _sanitize_csv_field(metric_data.get("cpu", "")),
                _sanitize_csv_field(metric_data.get("memory", "")),
                _sanitize_csv_field(metric_data.get("disk", "")),
                _sanitize_csv_field(metric_data.get("network_rx", "")),
                _sanitize_csv_field(metric_data.get("network_tx", "")),
            ]
        )

    return output.getvalue()


def export_servers_json():
    """Export servers to JSON format"""
    servers = get_servers()
    return json.dumps(servers, indent=2, ensure_ascii=False)


def export_monitoring_history_json(server_id=None, start_date=None, end_date=None):
    """Export monitoring history to JSON"""
    history = get_monitoring_history(server_id, start_date, end_date)
    return json.dumps(history, indent=2, ensure_ascii=False)


def export_alerts_csv(server_id=None, is_read=None):
    """Export alerts to CSV"""
    import csv
    from io import StringIO

    alerts = get_alerts(server_id, is_read, limit=1000)

    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["ID", "Server ID", "Alert Type", "Message", "Severity", "Is Read", "Created At"])

    # Data - sanitize each field to prevent CSV injection
    for alert in alerts:
        is_read_str = "Yes" if alert.get("is_read") else "No"
        writer.writerow(
            [
                _sanitize_csv_field(alert.get("id")),
                _sanitize_csv_field(alert.get("server_id")),
                _sanitize_csv_field(alert.get("alert_type")),
                _sanitize_csv_field(alert.get("message")),
                _sanitize_csv_field(alert.get("severity")),
                _sanitize_csv_field(is_read_str),
                _sanitize_csv_field(alert.get("created_at")),
            ]
        )

    return output.getvalue()


def export_audit_logs_csv(user_id=None, action=None, target_type=None, start_date=None, end_date=None, limit=10000):
    """
    Export audit logs to CSV format with proper sanitization

    Args:
        user_id: Filter by user ID
        action: Filter by action
        target_type: Filter by target type
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        limit: Maximum number of records to export (default 10000)

    Returns:
        CSV string
    """
    import csv
    from io import StringIO

    # Get audit logs with filters
    logs = get_audit_logs(
        user_id=user_id,
        action=action,
        target_type=target_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=0,
    )

    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Header
    writer.writerow(["ID", "User ID", "Action", "Target Type", "Target ID", "IP", "Created At"])

    # Data - sanitize each field to prevent CSV injection
    # Note: We deliberately exclude meta_json and user_agent to avoid exporting
    # potentially large or sensitive data
    for log in logs:
        writer.writerow(
            [
                _sanitize_csv_field(log.get("id")),
                _sanitize_csv_field(log.get("user_id")),
                _sanitize_csv_field(log.get("action")),
                _sanitize_csv_field(log.get("target_type")),
                _sanitize_csv_field(log.get("target_id")),
                _sanitize_csv_field(log.get("ip")),
                _sanitize_csv_field(log.get("created_at")),
            ]
        )

    return output.getvalue()


def export_audit_logs_json(user_id=None, action=None, target_type=None, start_date=None, end_date=None, limit=10000):
    """
    Export audit logs to JSON format

    Args:
        user_id: Filter by user ID
        action: Filter by action
        target_type: Filter by target type
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        limit: Maximum number of records to export (default 10000)

    Returns:
        JSON string
    """
    # Get audit logs with filters
    logs = get_audit_logs(
        user_id=user_id,
        action=action,
        target_type=target_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=0,
    )

    # Sanitize logs: limit meta_json size and remove user_agent if too large
    sanitized_logs = []
    for log in logs:
        sanitized_log = {
            "id": log.get("id"),
            "user_id": log.get("user_id"),
            "action": log.get("action"),
            "target_type": log.get("target_type"),
            "target_id": log.get("target_id"),
            "ip": log.get("ip"),
            "created_at": log.get("created_at"),
        }

        # Include limited meta_json (max 1000 chars to avoid huge exports)
        meta = log.get("meta")
        if meta:
            meta_str = json.dumps(meta)
            if len(meta_str) > 1000:
                sanitized_log["meta"] = {"_truncated": True, "_size": len(meta_str)}
            else:
                sanitized_log["meta"] = meta

        sanitized_logs.append(sanitized_log)

    return json.dumps(sanitized_logs, indent=2, ensure_ascii=False)


# ==================== SERVER NOTES ====================


def add_server_note(server_id, title, content="", created_by=None, group_id=None):
    """Add a note to a server (Phase 4 Module 5 Enhanced)"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Note: updated_by intentionally left NULL on creation, will be set on first update
        cursor.execute(
            """
            INSERT INTO server_notes (server_id, title, content, created_by, group_id)
            VALUES (?, ?, ?, ?, ?)
        """,
            (server_id, title, content, created_by, group_id),
        )

        conn.commit()
        note_id = cursor.lastrowid
        conn.close()
        return {"success": True, "note_id": note_id, "message": "Note added successfully"}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def get_server_notes(server_id, include_deleted=False):
    """Get all notes for a server (Phase 4 Module 5 Enhanced)"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if include_deleted:
        cursor.execute(
            """
            SELECT sn.*, g.name as group_name, g.color as group_color
            FROM server_notes sn
            LEFT JOIN groups g ON sn.group_id = g.id
            WHERE sn.server_id = ?
            ORDER BY sn.updated_at DESC
        """,
            (server_id,),
        )
    else:
        cursor.execute(
            """
            SELECT sn.*, g.name as group_name, g.color as group_color
            FROM server_notes sn
            LEFT JOIN groups g ON sn.group_id = g.id
            WHERE sn.server_id = ? AND sn.deleted_at IS NULL
            ORDER BY sn.updated_at DESC
        """,
            (server_id,),
        )

    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return notes


def get_server_note(note_id):
    """Get a single note by ID"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM server_notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()
    conn.close()
    return dict(note) if note else None


def update_server_note(note_id, title=None, content=None, updated_by=None, group_id=None):
    """Update a server note (Phase 4 Module 5 Enhanced)"""
    conn = get_connection()
    cursor = conn.cursor()

    updates = []
    values = []

    if title is not None:
        updates.append("title = ?")
        values.append(title)

    if content is not None:
        updates.append("content = ?")
        values.append(content)

    if updated_by is not None:
        updates.append("updated_by = ?")
        values.append(updated_by)

    if group_id is not None:
        updates.append("group_id = ?")
        values.append(group_id)

    if not updates:
        conn.close()
        return {"success": False, "error": "No fields to update"}

    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(note_id)

    try:
        # Security Note: Column names are hardcoded above (lines 1569, 1573, 1577, 1584)
        # Not from user input
        query = f"UPDATE server_notes SET {', '.join(updates)} WHERE id = ?"  # nosec B608
        cursor.execute(query, values)

        conn.commit()
        conn.close()
        return {"success": True, "message": "Note updated successfully"}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def delete_server_note(note_id, soft_delete=True):
    """Delete a server note (soft delete by default, Phase 4 Module 5 Enhanced)"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if soft_delete:
            cursor.execute(
                """
                UPDATE server_notes 
                SET deleted_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """,
                (note_id,),
            )
        else:
            cursor.execute("DELETE FROM server_notes WHERE id = ?", (note_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Note deleted successfully"}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


# ==================== DOMAIN SETTINGS ====================


def get_domain_settings():
    """Get domain configuration settings"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM domain_settings LIMIT 1")
    row = cursor.fetchone()

    if row:
        columns = [desc[0] for desc in cursor.description]
        settings = dict(zip(columns, row))
        conn.close()
        return settings
    else:
        # Return default settings if none exist
        conn.close()
        return {
            "domain_name": "",
            "ssl_enabled": 0,
            "ssl_type": "none",
            "cert_path": "",
            "key_path": "",
            "auto_renew": 0,
        }


def save_domain_settings(domain_name="", ssl_enabled=0, ssl_type="none", cert_path="", key_path="", auto_renew=0):
    """Save domain configuration settings"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if settings exist
        cursor.execute("SELECT id FROM domain_settings LIMIT 1")
        existing = cursor.fetchone()

        if existing:
            # Update existing settings
            cursor.execute(
                """
                UPDATE domain_settings 
                SET domain_name = ?, ssl_enabled = ?, ssl_type = ?, 
                    cert_path = ?, key_path = ?, auto_renew = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (domain_name, ssl_enabled, ssl_type, cert_path, key_path, auto_renew, existing[0]),
            )
        else:
            # Insert new settings
            cursor.execute(
                """
                INSERT INTO domain_settings 
                (domain_name, ssl_enabled, ssl_type, cert_path, key_path, auto_renew)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (domain_name, ssl_enabled, ssl_type, cert_path, key_path, auto_renew),
            )

        conn.commit()
        conn.close()
        return {"success": True, "message": "Domain settings saved successfully"}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


# ==================== AUDIT LOGS (Phase 4 Module 6) ====================


def add_audit_log(user_id, action, target_type, target_id, meta=None, ip=None, user_agent=None):
    """
    Add an audit log entry (append-only)

    Args:
        user_id: ID of user performing action
        action: Action performed (e.g., 'terminal.open', 'ssh_key.create', 'command.execute')
        target_type: Type of target (e.g., 'server', 'ssh_key', 'user')
        target_id: ID of target resource
        meta: Optional dict with additional metadata
        ip: Client IP address
        user_agent: Client user agent

    Returns:
        Dict with success status and log_id
    """
    import uuid

    conn = get_connection()
    cursor = conn.cursor()

    try:
        log_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        meta_json = json.dumps(meta) if meta else None

        cursor.execute(
            """
            INSERT INTO audit_logs (id, user_id, action, target_type, target_id, meta_json, ip, user_agent, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (log_id, user_id, action, target_type, target_id, meta_json, ip, user_agent, now),
        )

        conn.commit()
        conn.close()
        return {"success": True, "log_id": log_id}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def get_audit_logs(user_id=None, action=None, target_type=None, start_date=None, end_date=None, limit=100, offset=0):
    """
    Get audit logs with optional filtering

    Args:
        user_id: Filter by user ID
        action: Filter by action
        target_type: Filter by target type
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        limit: Maximum number of records to return
        offset: Offset for pagination

    Returns:
        List of audit log entries
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Build query with filters
    query = "SELECT * FROM audit_logs WHERE 1=1"
    params = []

    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)

    if action:
        query += " AND action = ?"
        params.append(action)

    if target_type:
        query += " AND target_type = ?"
        params.append(target_type)

    if start_date:
        query += " AND created_at >= ?"
        params.append(start_date)

    if end_date:
        query += " AND created_at <= ?"
        params.append(end_date)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)

    logs = []
    for row in cursor.fetchall():
        log = {
            "id": row[0],
            "user_id": row[1],
            "action": row[2],
            "target_type": row[3],
            "target_id": row[4],
            "meta": json.loads(row[5]) if row[5] else None,
            "ip": row[6],
            "user_agent": row[7],
            "created_at": row[8],
        }
        logs.append(log)

    conn.close()
    return logs


def cleanup_old_audit_logs(days=90):
    """
    Delete audit logs older than specified days

    Args:
        days: Number of days to retain (default 90)

    Returns:
        Dict with number of deleted logs
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Calculate cutoff date
    from datetime import datetime, timedelta

    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    # Delete old logs
    cursor.execute(
        """
        DELETE FROM audit_logs 
        WHERE created_at < ?
    """,
        (cutoff_date,),
    )

    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    return {
        "deleted": deleted,
        "message": f"Deleted {deleted} audit logs older than {days} days",
        "cutoff_date": cutoff_date,
    }


# ==================== TERMINAL SESSIONS (Phase 4 Module 2) ====================


def create_terminal_session(server_id, user_id, ssh_key_id=None):
    """
    Create a new terminal session

    Args:
        server_id: Server ID
        user_id: User ID
        ssh_key_id: Optional SSH key ID from vault

    Returns:
        Dict with success status and session_id
    """
    import uuid

    conn = get_connection()
    cursor = conn.cursor()

    try:
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            """
            INSERT INTO terminal_sessions (id, server_id, user_id, ssh_key_id, started_at, last_activity, status)
            VALUES (?, ?, ?, ?, ?, ?, 'active')
        """,
            (session_id, server_id, user_id, ssh_key_id, now, now),
        )

        conn.commit()
        conn.close()
        return {"success": True, "session_id": session_id}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def end_terminal_session(session_id, status="closed"):
    """
    End a terminal session

    Args:
        session_id: Session ID
        status: Final status (closed, timeout, error)

    Returns:
        Dict with success status
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        now = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            """
            UPDATE terminal_sessions 
            SET ended_at = ?, status = ?, last_activity = ?
            WHERE id = ?
        """,
            (now, status, now, session_id),
        )

        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def update_terminal_session_activity(session_id):
    """
    Update last activity timestamp for a session

    Args:
        session_id: Session ID

    Returns:
        Dict with success status
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        now = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            """
            UPDATE terminal_sessions 
            SET last_activity = ?
            WHERE id = ?
        """,
            (now, session_id),
        )

        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def get_terminal_sessions(user_id=None, server_id=None, status="active"):
    """
    Get terminal sessions with optional filtering

    Args:
        user_id: Filter by user ID
        server_id: Filter by server ID
        status: Filter by status (active, closed, timeout, error)

    Returns:
        List of terminal sessions
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM terminal_sessions WHERE 1=1"
    params = []

    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)

    if server_id:
        query += " AND server_id = ?"
        params.append(server_id)

    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY started_at DESC"

    cursor.execute(query, params)

    sessions = []
    for row in cursor.fetchall():
        session = {
            "id": row[0],
            "server_id": row[1],
            "user_id": row[2],
            "ssh_key_id": row[3],
            "started_at": row[4],
            "ended_at": row[5],
            "status": row[6],
            "last_activity": row[7],
        }
        sessions.append(session)

    conn.close()
    return sessions


# ==================== INVENTORY MANAGEMENT (Phase 4 Module 3) ====================


def save_server_inventory(server_id, inventory_json, save_snapshot=True):
    """
    Save server inventory data

    Args:
        server_id: Server ID
        inventory_json: Inventory data as JSON string
        save_snapshot: Whether to save a snapshot for history

    Returns:
        Dict with success status
    """
    import uuid

    conn = get_connection()
    cursor = conn.cursor()

    try:
        collected_at = datetime.now(timezone.utc).isoformat()

        # Save/update latest inventory
        cursor.execute(
            """
            INSERT OR REPLACE INTO server_inventory_latest (server_id, collected_at, inventory_json)
            VALUES (?, ?, ?)
        """,
            (server_id, collected_at, inventory_json),
        )

        # Optionally save snapshot for history
        if save_snapshot:
            snapshot_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO server_inventory_snapshots (id, server_id, collected_at, inventory_json)
                VALUES (?, ?, ?, ?)
            """,
                (snapshot_id, server_id, collected_at, inventory_json),
            )

        conn.commit()
        conn.close()
        return {"success": True, "collected_at": collected_at}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def get_server_inventory_latest(server_id):
    """
    Get latest inventory for a server

    Args:
        server_id: Server ID

    Returns:
        Inventory data dict or None
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT collected_at, inventory_json
        FROM server_inventory_latest
        WHERE server_id = ?
    """,
        (server_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return {"server_id": server_id, "collected_at": row[0], "inventory": json.loads(row[1])}
    return None


def get_server_inventory_snapshots(server_id, limit=10):
    """
    Get inventory snapshots for a server

    Args:
        server_id: Server ID
        limit: Maximum number of snapshots to return

    Returns:
        List of inventory snapshots
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, collected_at, inventory_json
        FROM server_inventory_snapshots
        WHERE server_id = ?
        ORDER BY collected_at DESC
        LIMIT ?
    """,
        (server_id, limit),
    )

    snapshots = []
    for row in cursor.fetchall():
        snapshots.append(
            {"id": row[0], "server_id": server_id, "collected_at": row[1], "inventory": json.loads(row[2])}
        )

    conn.close()
    return snapshots


# ==================== TASKS MANAGEMENT (PHASE 4 MODULE 4) ====================


def create_task(server_id, user_id, command, timeout_seconds=60, store_output=0):
    """
    Create a new task for remote command execution

    Args:
        server_id: ID of target server
        user_id: ID of user creating the task
        command: Command to execute
        timeout_seconds: Command timeout in seconds
        store_output: Whether to store stdout/stderr (0 or 1)

    Returns:
        Dict with success status and task_id
    """
    import uuid

    conn = get_connection()
    cursor = conn.cursor()

    try:
        task_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            """
            INSERT INTO tasks (id, server_id, user_id, command, status, timeout_seconds, store_output, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (task_id, server_id, user_id, command, "queued", timeout_seconds, store_output, now),
        )

        conn.commit()
        conn.close()
        return {"success": True, "task_id": task_id}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def get_task(task_id):
    """
    Get task by ID

    Args:
        task_id: Task ID

    Returns:
        Task dict or None
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    columns = [desc[0] for desc in cursor.description]
    task = dict(zip(columns, row))

    conn.close()
    return task


def get_tasks(server_id=None, user_id=None, status=None, limit=100, offset=0, from_date=None, to_date=None):
    """
    Get tasks with optional filtering

    Args:
        server_id: Filter by server ID
        user_id: Filter by user ID
        status: Filter by status
        limit: Maximum number of records to return
        offset: Offset for pagination
        from_date: Filter by start date (ISO format)
        to_date: Filter by end date (ISO format)

    Returns:
        List of task dicts
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Build query with filters
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if server_id:
        query += " AND server_id = ?"
        params.append(server_id)

    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)

    if status:
        query += " AND status = ?"
        params.append(status)

    if from_date:
        query += " AND created_at >= ?"
        params.append(from_date)

    if to_date:
        query += " AND created_at <= ?"
        params.append(to_date)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)

    columns = [desc[0] for desc in cursor.description]
    tasks = []

    for row in cursor.fetchall():
        task = dict(zip(columns, row))
        tasks.append(task)

    conn.close()
    return tasks


def update_task_status(task_id, status, exit_code=None, stdout=None, stderr=None, started_at=None, finished_at=None):
    """
    Update task status and results

    Args:
        task_id: Task ID
        status: New status (queued, running, success, failed, timeout, cancelled)
        exit_code: Exit code
        stdout: Standard output
        stderr: Standard error
        started_at: When task started (ISO format)
        finished_at: When task finished (ISO format)

    Returns:
        Dict with success status
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        updates = ["status = ?"]
        values = [status]

        if exit_code is not None:
            updates.append("exit_code = ?")
            values.append(exit_code)

        if stdout is not None:
            updates.append("stdout = ?")
            values.append(stdout)

        if stderr is not None:
            updates.append("stderr = ?")
            values.append(stderr)

        if started_at is not None:
            updates.append("started_at = ?")
            values.append(started_at)

        if finished_at is not None:
            updates.append("finished_at = ?")
            values.append(finished_at)

        values.append(task_id)

        # Security Note: Column names hardcoded above (lines 2215-2231), not from user input
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"  # nosec B608
        cursor.execute(query, values)

        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def delete_old_tasks(days=30):
    """
    Delete tasks older than specified days

    Args:
        days: Number of days to keep

    Returns:
        Dict with number of deleted tasks
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM tasks 
        WHERE datetime(created_at, '+' || ? || ' days') < datetime('now')
    """,
        (days,),
    )

    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    return {"deleted": deleted, "message": f"Deleted {deleted} old tasks"}


# ==================== TAGS MANAGEMENT (PHASE 4 MODULE 5) ====================


def create_tag(name, color="#3f51b5", description="", created_by=None):
    """
    Create a new tag

    Args:
        name: Tag name
        color: Tag color (hex)
        description: Tag description
        created_by: User ID

    Returns:
        Dict with success status and tag_id
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO tags (name, color, description, created_by)
            VALUES (?, ?, ?, ?)
        """,
            (name, color, description, created_by),
        )

        conn.commit()
        tag_id = cursor.lastrowid
        conn.close()
        return {"success": True, "tag_id": tag_id}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "error": f'Tag "{name}" already exists'}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def get_tags():
    """
    Get all tags

    Returns:
        List of tag dicts
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tags ORDER BY name")

    columns = [desc[0] for desc in cursor.description]
    tags = []

    for row in cursor.fetchall():
        tag = dict(zip(columns, row))
        tags.append(tag)

    conn.close()
    return tags


def get_tag(tag_id):
    """
    Get tag by ID

    Args:
        tag_id: Tag ID

    Returns:
        Tag dict or None
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    columns = [desc[0] for desc in cursor.description]
    tag = dict(zip(columns, row))

    conn.close()
    return tag


def update_tag(tag_id, **kwargs):
    """
    Update tag

    Args:
        tag_id: Tag ID
        **kwargs: Fields to update (name, color, description)

    Returns:
        Dict with success status
    """
    conn = get_connection()
    cursor = conn.cursor()

    allowed_fields = ["name", "color", "description"]

    updates = []
    values = []

    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            values.append(value)

    if not updates:
        conn.close()
        return {"success": False, "error": "No valid fields to update"}

    values.append(tag_id)

    # Security Note: Column names from allowed_fields allowlist above
    query = f"UPDATE tags SET {', '.join(updates)} WHERE id = ?"  # nosec B608

    try:
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return {"success": True, "message": f"Tag {tag_id} updated"}

    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def delete_tag(tag_id):
    """
    Delete a tag (also removes all server-tag mappings)

    Args:
        tag_id: Tag ID

    Returns:
        Dict with success status
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))

        if cursor.rowcount == 0:
            conn.close()
            return {"success": False, "error": "Tag not found"}

        conn.commit()
        conn.close()

        return {"success": True, "message": f"Tag {tag_id} deleted"}

    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def add_server_tag(server_id, tag_id, created_by=None):
    """
    Add a tag to a server

    Args:
        server_id: Server ID
        tag_id: Tag ID
        created_by: User ID

    Returns:
        Dict with success status
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO server_tag_map (server_id, tag_id, created_by)
            VALUES (?, ?, ?)
        """,
            (server_id, tag_id, created_by),
        )

        conn.commit()
        conn.close()
        return {"success": True}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "error": "Tag already added to server"}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def remove_server_tag(server_id, tag_id):
    """
    Remove a tag from a server

    Args:
        server_id: Server ID
        tag_id: Tag ID

    Returns:
        Dict with success status
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM server_tag_map 
            WHERE server_id = ? AND tag_id = ?
        """,
            (server_id, tag_id),
        )

        if cursor.rowcount == 0:
            conn.close()
            return {"success": False, "error": "Tag not found on server"}

        conn.commit()
        conn.close()

        return {"success": True}

    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def get_server_tags(server_id):
    """
    Get all tags for a server

    Args:
        server_id: Server ID

    Returns:
        List of tag dicts
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT t.* FROM tags t
        INNER JOIN server_tag_map stm ON t.id = stm.tag_id
        WHERE stm.server_id = ?
        ORDER BY t.name
    """,
        (server_id,),
    )

    columns = [desc[0] for desc in cursor.description]
    tags = []

    for row in cursor.fetchall():
        tag = dict(zip(columns, row))
        tags.append(tag)

    conn.close()
    return tags


def get_servers_by_tag(tag_id):
    """
    Get all servers with a specific tag

    Args:
        tag_id: Tag ID

    Returns:
        List of server IDs
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT server_id FROM server_tag_map
        WHERE tag_id = ?
    """,
        (tag_id,),
    )

    server_ids = [row[0] for row in cursor.fetchall()]

    conn.close()
    return server_ids


# ==================== WEBHOOKS MANAGEMENT (Phase 8) ====================


def create_webhook(name, url, secret=None, enabled=True, event_types=None, retry_max=3, timeout=10, created_by=None):
    """
    Create a new webhook

    Args:
        name: Webhook name/description
        url: Webhook URL
        secret: Optional secret for HMAC signing
        enabled: Whether webhook is enabled
        event_types: List of event types to trigger on (None = all events)
        retry_max: Maximum retry attempts
        timeout: Request timeout in seconds
        created_by: User ID who created the webhook

    Returns:
        Dict with success status and webhook_id
    """
    import uuid

    conn = get_connection()
    cursor = conn.cursor()

    try:
        webhook_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        # Convert event_types list to JSON string
        event_types_json = json.dumps(event_types) if event_types else None

        cursor.execute(
            """
            INSERT INTO webhooks (
                id, name, url, secret, enabled, event_types, 
                retry_max, timeout, created_by, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (webhook_id, name, url, secret, int(enabled), event_types_json, retry_max, timeout, created_by, now, now),
        )

        conn.commit()
        conn.close()
        return {"success": True, "webhook_id": webhook_id}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def get_webhooks(enabled_only=False):
    """
    Get all webhooks

    Args:
        enabled_only: If True, return only enabled webhooks

    Returns:
        List of webhook dicts
    """
    conn = get_connection()
    cursor = conn.cursor()

    if enabled_only:
        cursor.execute("SELECT * FROM webhooks WHERE enabled = 1 ORDER BY created_at DESC")
    else:
        cursor.execute("SELECT * FROM webhooks ORDER BY created_at DESC")

    columns = [desc[0] for desc in cursor.description]
    webhooks = []

    for row in cursor.fetchall():
        webhook = dict(zip(columns, row))
        # Parse event_types JSON
        if webhook.get("event_types"):
            try:
                webhook["event_types"] = json.loads(webhook["event_types"])
            except:
                webhook["event_types"] = None
        # Convert enabled to boolean
        webhook["enabled"] = bool(webhook.get("enabled", 0))
        webhooks.append(webhook)

    conn.close()
    return webhooks


def get_webhook(webhook_id):
    """
    Get a single webhook by ID

    Args:
        webhook_id: Webhook ID

    Returns:
        Webhook dict or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM webhooks WHERE id = ?", (webhook_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    columns = [desc[0] for desc in cursor.description]
    webhook = dict(zip(columns, row))

    # Parse event_types JSON
    if webhook.get("event_types"):
        try:
            webhook["event_types"] = json.loads(webhook["event_types"])
        except:
            webhook["event_types"] = None

    # Convert enabled to boolean
    webhook["enabled"] = bool(webhook.get("enabled", 0))

    conn.close()
    return webhook


def update_webhook(
    webhook_id, name=None, url=None, secret=None, enabled=None, event_types=None, retry_max=None, timeout=None
):
    """
    Update a webhook

    Args:
        webhook_id: Webhook ID
        name: New name (optional)
        url: New URL (optional)
        secret: New secret (optional, empty string to clear)
        enabled: New enabled status (optional)
        event_types: New event types list (optional)
        retry_max: New retry max (optional)
        timeout: New timeout (optional)

    Returns:
        Dict with success status
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        now = datetime.now(timezone.utc).isoformat()

        # Build update query dynamically
        updates = ["updated_at = ?"]
        params = [now]

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if url is not None:
            updates.append("url = ?")
            params.append(url)
        if secret is not None:
            updates.append("secret = ?")
            params.append(secret if secret else None)
        if enabled is not None:
            updates.append("enabled = ?")
            params.append(int(enabled))
        if event_types is not None:
            updates.append("event_types = ?")
            params.append(json.dumps(event_types) if event_types else None)
        if retry_max is not None:
            updates.append("retry_max = ?")
            params.append(retry_max)
        if timeout is not None:
            updates.append("timeout = ?")
            params.append(timeout)

        params.append(webhook_id)

        # Security Note: Column names hardcoded above (lines 2683-2712), not from user input
        query = f'UPDATE webhooks SET {", ".join(updates)} WHERE id = ?'  # nosec B608
        cursor.execute(query, params)

        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def delete_webhook(webhook_id):
    """
    Delete a webhook

    Args:
        webhook_id: Webhook ID

    Returns:
        Dict with success status
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM webhooks WHERE id = ?", (webhook_id,))

        if cursor.rowcount == 0:
            conn.close()
            return {"success": False, "error": "Webhook not found"}

        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def update_webhook_last_triggered(webhook_id):
    """
    Update last triggered timestamp for webhook

    Args:
        webhook_id: Webhook ID

    Returns:
        Dict with success status
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            """
            UPDATE webhooks 
            SET last_triggered_at = ?
            WHERE id = ?
        """,
            (now, webhook_id),
        )

        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def log_webhook_delivery(
    webhook_id, event_id, event_type, status, status_code=None, response_body=None, error=None, attempt=1
):
    """
    Log a webhook delivery attempt

    Args:
        webhook_id: Webhook ID
        event_id: Event ID that triggered webhook
        event_type: Event type
        status: 'success', 'failed', or 'retrying'
        status_code: HTTP status code (if available)
        response_body: Response body (truncated)
        error: Error message (if failed)
        attempt: Attempt number

    Returns:
        Dict with success status and log_id
    """
    import uuid

    conn = get_connection()
    cursor = conn.cursor()

    try:
        log_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        # Truncate response body if too large
        if response_body and len(response_body) > 10000:
            response_body = response_body[:10000] + "... (truncated)"

        cursor.execute(
            """
            INSERT INTO webhook_deliveries (
                id, webhook_id, event_id, event_type, status, 
                status_code, response_body, error, attempt, delivered_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (log_id, webhook_id, event_id, event_type, status, status_code, response_body, error, attempt, now),
        )

        conn.commit()
        conn.close()
        return {"success": True, "log_id": log_id}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def get_webhook_deliveries(webhook_id=None, limit=100, offset=0):
    """
    Get webhook delivery logs

    Args:
        webhook_id: Filter by webhook ID (optional)
        limit: Maximum number of records
        offset: Offset for pagination

    Returns:
        List of delivery log dicts
    """
    conn = get_connection()
    cursor = conn.cursor()

    if webhook_id:
        cursor.execute(
            """
            SELECT * FROM webhook_deliveries 
            WHERE webhook_id = ?
            ORDER BY delivered_at DESC 
            LIMIT ? OFFSET ?
        """,
            (webhook_id, limit, offset),
        )
    else:
        cursor.execute(
            """
            SELECT * FROM webhook_deliveries 
            ORDER BY delivered_at DESC 
            LIMIT ? OFFSET ?
        """,
            (limit, offset),
        )

    columns = [desc[0] for desc in cursor.description]
    deliveries = []

    for row in cursor.fetchall():
        delivery = dict(zip(columns, row))
        deliveries.append(delivery)

    conn.close()
    return deliveries


# ==================== METRICS HELPER FUNCTIONS ====================


def get_active_terminal_sessions_count():
    """
    Get count of active terminal sessions

    Returns:
        int: Number of active sessions
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) FROM terminal_sessions 
        WHERE status = 'active'
    """
    )

    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_task_stats():
    """
    Get task statistics (queued and running)

    Returns:
        dict: Task stats with 'queued' and 'running' keys
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            SUM(CASE WHEN status = 'queued' THEN 1 ELSE 0 END) as queued,
            SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running
        FROM tasks
    """
    )

    row = cursor.fetchone()
    conn.close()

    return {"queued": row[0] or 0, "running": row[1] or 0}


def get_webhook_delivery_stats():
    """
    Get webhook delivery statistics

    Returns:
        dict: Delivery stats with 'success' and 'failed' keys
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
        FROM webhook_deliveries
    """
    )

    row = cursor.fetchone()
    conn.close()

    return {"success": row[0] or 0, "failed": row[1] or 0}


def cleanup_old_webhook_deliveries(days=90):
    """
    Delete webhook delivery logs older than specified days

    Args:
        days: Number of days to retain (default 90)

    Returns:
        Dict with number of deleted delivery logs
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Calculate cutoff date
    from datetime import datetime, timedelta

    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    # Delete old webhook delivery logs
    cursor.execute(
        """
        DELETE FROM webhook_deliveries 
        WHERE delivered_at < ?
    """,
        (cutoff_date,),
    )

    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    return {
        "deleted": deleted,
        "message": f"Deleted {deleted} webhook delivery logs older than {days} days",
        "cutoff_date": cutoff_date,
    }


# ==================== TEST CODE ====================

if __name__ == "__main__":
    # Initialize database
    init_database()
    print("Database initialized successfully!")

    # Create default admin user
    admin_result = create_admin_user("admin", "admin123", "admin@example.com")
    print("\nAdmin user:", admin_result)

    # Test: Add a sample server
    result = add_server(
        name="Test LXC Container",
        host="192.168.1.100",
        port=22,
        username="root",
        description="Test container for monitoring",
        ssh_key_path="~/.ssh/id_rsa",
        agent_port=8083,
        tags="lxc,test,production",
    )

    print("\nTest server:", result)

    # Get all servers
    servers = get_servers()
    print("\nServers:", len(servers))

    # Get stats
    stats = get_server_stats()
    print("\nStats:", stats)
