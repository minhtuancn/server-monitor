#!/usr/bin/env python3

"""
Database module for multi-server monitoring
Manages server list, credentials, and monitoring history
"""

import sqlite3
import json
from datetime import datetime
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
_default_db_path = str(Path(__file__).parent.parent / 'data' / 'servers.db')
DB_PATH = os.environ.get('DB_PATH', _default_db_path)

# Encryption key - Use environment variable or generate a random default
# WARNING: Random default means encrypted data won't survive server restarts
_env_key = os.environ.get('ENCRYPTION_KEY')
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
        return ''
    result = bytearray()
    key = ENCRYPTION_KEY
    for i, char in enumerate(password.encode()):
        result.append(char ^ key[i % len(key)])
    return base64.b64encode(bytes(result)).decode()

def decrypt_ssh_password(encrypted):
    """Decrypt SSH password"""
    if not encrypted:
        return ''
    try:
        data = base64.b64decode(encrypted)
        result = bytearray()
        key = ENCRYPTION_KEY
        for i, byte in enumerate(data):
            result.append(byte ^ key[i % len(key)])
        return bytes(result).decode()
    except:
        return ''

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
    cursor.execute('''
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Admin users table (for authentication)
    cursor.execute('''
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
    ''')
    
    # Session tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE CASCADE
        )
    ''')
    
    # Monitoring history table (optional - for long-term storage)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitoring_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id INTEGER NOT NULL,
            metric_type TEXT NOT NULL,
            metric_data TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
        )
    ''')
    
    # Alerts table
    cursor.execute('''
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
    ''')
    
    # Command snippets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS command_snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            command TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            is_sudo INTEGER DEFAULT 0,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL
        )
    ''')
    
    # SSH keys management table
    cursor.execute('''
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
    ''')
    
    # Server notes table (Markdown)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS server_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL
        )
    ''')
    
    # Domain settings table
    cursor.execute('''
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
    ''')
    
    # Terminal sessions table (Phase 4 Module 2)
    cursor.execute('''
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
    ''')
    
    # Audit logs table (Phase 4 Module 6 - Foundation)
    cursor.execute('''
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
    ''')
    
    # Create indexes for audit logs
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id 
        ON audit_logs(user_id)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_audit_logs_action 
        ON audit_logs(action)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at 
        ON audit_logs(created_at)
    ''')
    
    # Server inventory tables (Phase 4 Module 3)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS server_inventory_latest (
            server_id INTEGER PRIMARY KEY,
            collected_at TEXT NOT NULL,
            inventory_json TEXT NOT NULL,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS server_inventory_snapshots (
            id TEXT PRIMARY KEY,
            server_id INTEGER NOT NULL,
            collected_at TEXT NOT NULL,
            inventory_json TEXT NOT NULL,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
        )
    ''')
    
    # Create index for inventory snapshots
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_inventory_snapshots_server_id 
        ON server_inventory_snapshots(server_id)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_inventory_snapshots_collected_at 
        ON server_inventory_snapshots(collected_at)
    ''')
    
    # Tasks table (Phase 4 Module 4)
    cursor.execute('''
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
    ''')
    
    # Create indexes for tasks
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_tasks_server_id 
        ON tasks(server_id, created_at DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_tasks_user_id 
        ON tasks(user_id, created_at DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_tasks_status 
        ON tasks(status)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_tasks_created_at 
        ON tasks(created_at DESC)
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    """Get database connection"""
    init_database()  # Ensure DB exists
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# ==================== SERVER MANAGEMENT ====================

def add_server(name, host, port, username, description='', ssh_key_path='', ssh_password='', agent_port=8083, tags=''):
    """Add a new server to monitor"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Encrypt password if provided
        if ssh_password:
            ssh_password = encrypt_ssh_password(ssh_password)
        
        cursor.execute('''
            INSERT INTO servers (name, host, port, username, description, ssh_key_path, ssh_password, agent_port, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, host, port, username, description, ssh_key_path, ssh_password, agent_port, tags))
        
        conn.commit()
        server_id = cursor.lastrowid
        conn.close()
        
        return {'success': True, 'server_id': server_id, 'message': f'Server {name} added successfully'}
    
    except sqlite3.IntegrityError:
        conn.close()
        return {'success': False, 'error': f'Server with host {host} already exists'}
    
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def get_servers(status=None):
    """Get all servers or filter by status"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if status:
        cursor.execute('SELECT * FROM servers WHERE status = ? ORDER BY name', (status,))
    else:
        cursor.execute('SELECT * FROM servers ORDER BY name')
    
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
    
    cursor.execute('SELECT * FROM servers WHERE id = ?', (server_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    columns = [desc[0] for desc in cursor.description]
    server = dict(zip(columns, row))
    
    # Decrypt SSH password if requested and exists
    if decrypt_password and server.get('ssh_password'):
        server['ssh_password'] = decrypt_ssh_password(server['ssh_password'])
    
    conn.close()
    return server

def update_server(server_id, **kwargs):
    """Update server information"""
    conn = get_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['name', 'host', 'port', 'username', 'description', 'ssh_key_path', 'ssh_password', 'agent_port', 'tags', 'status', 'agent_installed']
    
    updates = []
    values = []
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            # Encrypt password if updating password
            if key == 'ssh_password' and value:
                value = encrypt_ssh_password(value)
            updates.append(f'{key} = ?')
            values.append(value)
    
    if not updates:
        conn.close()
        return {'success': False, 'error': 'No valid fields to update'}
    
    updates.append('updated_at = CURRENT_TIMESTAMP')
    values.append(server_id)
    
    query = f"UPDATE servers SET {', '.join(updates)} WHERE id = ?"
    
    try:
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': f'Server {server_id} updated successfully'}
    
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def delete_server(server_id):
    """Delete a server"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM servers WHERE id = ?', (server_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return {'success': False, 'error': 'Server not found'}
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': f'Server {server_id} deleted successfully'}
    
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def update_server_status(server_id, status, last_seen=None):
    """Update server online/offline status"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if last_seen is None:
        last_seen = datetime.now().isoformat()
    
    cursor.execute('''
        UPDATE servers 
        SET status = ?, last_seen = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (status, last_seen, server_id))
    
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
    
    cursor.execute('''
        INSERT INTO monitoring_history (server_id, metric_type, metric_data)
        VALUES (?, ?, ?)
    ''', (server_id, metric_type, metric_data))
    
    conn.commit()
    conn.close()

def get_monitoring_history(server_id, metric_type=None, hours=24):
    """Get monitoring history for a server"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if metric_type:
        cursor.execute('''
            SELECT * FROM monitoring_history 
            WHERE server_id = ? AND metric_type = ?
            AND timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp DESC
        ''', (server_id, metric_type, hours))
    else:
        cursor.execute('''
            SELECT * FROM monitoring_history 
            WHERE server_id = ?
            AND timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp DESC
        ''', (server_id, hours))
    
    columns = [desc[0] for desc in cursor.description]
    history = []
    
    for row in cursor.fetchall():
        item = dict(zip(columns, row))
        # Parse JSON data
        try:
            item['metric_data'] = json.loads(item['metric_data'])
        except:
            pass
        history.append(item)
    
    conn.close()
    return history

def cleanup_old_history(days=7):
    """Delete monitoring history older than N days"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM monitoring_history 
        WHERE timestamp < datetime('now', '-' || ? || ' days')
    ''', (days,))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted

# ==================== ALERTS ====================

def create_alert(server_id, alert_type, message, severity='warning'):
    """Create an alert"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO alerts (server_id, alert_type, message, severity)
        VALUES (?, ?, ?, ?)
    ''', (server_id, alert_type, message, severity))
    
    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()
    
    return alert_id

def get_alerts(server_id=None, is_read=None, limit=50):
    """Get alerts"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM alerts WHERE 1=1'
    params = []
    
    if server_id:
        query += ' AND server_id = ?'
        params.append(server_id)
    
    if is_read is not None:
        query += ' AND is_read = ?'
        params.append(is_read)
    
    query += ' ORDER BY created_at DESC LIMIT ?'
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
    
    cursor.execute('UPDATE alerts SET is_read = 1 WHERE id = ?', (alert_id,))
    
    conn.commit()
    conn.close()

# ==================== STATISTICS ====================

def get_server_stats():
    """Get overview statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM servers')
    total_servers = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM servers WHERE status = 'online'")
    online_servers = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM servers WHERE status = 'offline'")
    offline_servers = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM alerts WHERE is_read = 0')
    unread_alerts = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_servers': total_servers,
        'online_servers': online_servers,
        'offline_servers': offline_servers,
        'unknown_servers': total_servers - online_servers - offline_servers,
        'unread_alerts': unread_alerts
    }

# ==================== AUTHENTICATION ====================

def create_admin_user(username, password, email='', role='admin'):
    """Create a new admin user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        
        cursor.execute('''
            INSERT INTO admin_users (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', (username, password_hash, email, role))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return {'success': True, 'user_id': user_id, 'message': f'Admin user {username} created'}
    
    except sqlite3.IntegrityError:
        conn.close()
        return {'success': False, 'error': f'Username {username} already exists'}
    
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def authenticate_user(username, password):
    """Authenticate user and create session"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, password_hash, is_active FROM admin_users WHERE username = ?', (username,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return {'success': False, 'error': 'Invalid username or password'}
    
    user_id, password_hash, is_active = row
    
    if not is_active:
        conn.close()
        return {'success': False, 'error': 'Account is disabled'}
    
    if not verify_password(password, password_hash):
        conn.close()
        return {'success': False, 'error': 'Invalid username or password'}
    
    # Create session token (expires in 7 days)
    token = generate_token()
    from datetime import timedelta
    expires_at = (datetime.now() + timedelta(days=7)).isoformat()
    
    cursor.execute('''
        INSERT INTO sessions (user_id, token, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, token, expires_at))
    
    # Update last login
    cursor.execute('''
        UPDATE admin_users 
        SET last_login = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (user_id,))
    
    conn.commit()
    conn.close()
    
    return {
        'success': True,
        'token': token,
        'username': username,
        'expires_at': expires_at
    }

def verify_session(token):
    """Verify session token"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.user_id, u.username, u.role, s.expires_at
        FROM sessions s
        JOIN admin_users u ON s.user_id = u.id
        WHERE s.token = ? AND u.is_active = 1
    ''', (token,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {'valid': False, 'error': 'Invalid session'}
    
    user_id, username, role, expires_at = row
    
    # Check if expired
    if datetime.fromisoformat(expires_at) < datetime.now():
        return {'valid': False, 'error': 'Session expired'}
    
    return {
        'valid': True,
        'user_id': user_id,
        'username': username,
        'role': role
    }

def logout_user(token):
    """Delete session token"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
    deleted = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return {'success': deleted > 0}

def get_all_users():
    """Get all admin users"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, role, is_active, created_at, last_login 
        FROM admin_users 
        ORDER BY created_at DESC
    ''')
    
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
    
    cursor.execute('SELECT id, password_hash FROM admin_users WHERE username = ?', (username,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return {'success': False, 'error': 'User not found'}
    
    user_id, current_hash = row
    
    if not verify_password(old_password, current_hash):
        conn.close()
        return {'success': False, 'error': 'Invalid current password'}
    
    new_hash = hash_password(new_password)
    
    cursor.execute('''
        UPDATE admin_users 
        SET password_hash = ? 
        WHERE id = ?
    ''', (new_hash, user_id))
    
    conn.commit()
    conn.close()
    
    return {'success': True, 'message': 'Password changed successfully'}

def cleanup_expired_sessions(days=7):
    """Delete sessions older than N days (default 7 days = 1 week)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM sessions 
        WHERE datetime(created_at, '+' || ? || ' days') < datetime('now')
    """, (days,))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return {'deleted': deleted, 'message': f'Deleted {deleted} expired sessions'}

# ==================== COMMAND SNIPPETS ====================

def add_snippet(name, command, description='', category='general', is_sudo=0, created_by=None):
    """Add a command snippet"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO command_snippets (name, command, description, category, is_sudo, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, command, description, category, is_sudo, created_by))
        
        conn.commit()
        snippet_id = cursor.lastrowid
        conn.close()
        
        return {'success': True, 'snippet_id': snippet_id, 'message': f'Snippet {name} created'}
    
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def get_snippets(category=None):
    """Get all command snippets or filter by category"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if category:
        cursor.execute('SELECT * FROM command_snippets WHERE category = ? ORDER BY name', (category,))
    else:
        cursor.execute('SELECT * FROM command_snippets ORDER BY category, name')
    
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
    
    cursor.execute('SELECT * FROM command_snippets WHERE id = ?', (snippet_id,))
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
    
    allowed_fields = ['name', 'command', 'description', 'category', 'is_sudo']
    
    updates = []
    values = []
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f'{key} = ?')
            values.append(value)
    
    if not updates:
        conn.close()
        return {'success': False, 'error': 'No valid fields to update'}
    
    updates.append('updated_at = CURRENT_TIMESTAMP')
    values.append(snippet_id)
    
    query = f"UPDATE command_snippets SET {', '.join(updates)} WHERE id = ?"
    
    try:
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': f'Snippet {snippet_id} updated'}
    
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def delete_snippet(snippet_id):
    """Delete a snippet"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM command_snippets WHERE id = ?', (snippet_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return {'success': False, 'error': 'Snippet not found'}
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': f'Snippet {snippet_id} deleted'}
    
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

# ==================== SSH KEYS MANAGEMENT ====================

def add_ssh_key(name, private_key_path, description='', key_type='rsa', public_key='', passphrase='', created_by=None):
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
        
        cursor.execute('''
            INSERT INTO ssh_keys (name, private_key_path, description, key_type, public_key, fingerprint, passphrase, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, private_key_path, description, key_type, public_key, fingerprint, passphrase, created_by))
        
        conn.commit()
        key_id = cursor.lastrowid
        conn.close()
        
        return {'success': True, 'key_id': key_id, 'message': f'SSH key {name} added successfully'}
    
    except sqlite3.IntegrityError:
        conn.close()
        return {'success': False, 'error': f'SSH key with name {name} already exists'}
    
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def get_ssh_keys():
    """Get all SSH keys"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, description, key_type, private_key_path, public_key, fingerprint, 
               created_at, updated_at, last_used
        FROM ssh_keys 
        ORDER BY name
    ''')
    
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
    
    cursor.execute('SELECT * FROM ssh_keys WHERE id = ?', (key_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    columns = [desc[0] for desc in cursor.description]
    key = dict(zip(columns, row))
    
    # Decrypt passphrase if requested and exists
    if decrypt_passphrase and key.get('passphrase'):
        key['passphrase'] = decrypt_ssh_password(key['passphrase'])
    
    conn.close()
    return key

def update_ssh_key(key_id, **kwargs):
    """Update SSH key information"""
    conn = get_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['name', 'description', 'key_type', 'private_key_path', 'public_key', 'passphrase']
    
    updates = []
    values = []
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            # Encrypt passphrase if updating
            if key == 'passphrase' and value:
                value = encrypt_ssh_password(value)
            updates.append(f'{key} = ?')
            values.append(value)
    
    if not updates:
        conn.close()
        return {'success': False, 'error': 'No valid fields to update'}
    
    updates.append('updated_at = CURRENT_TIMESTAMP')
    values.append(key_id)
    
    query = f"UPDATE ssh_keys SET {', '.join(updates)} WHERE id = ?"
    
    try:
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': f'SSH key {key_id} updated successfully'}
    
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def delete_ssh_key(key_id):
    """Delete an SSH key"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM ssh_keys WHERE id = ?', (key_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return {'success': False, 'error': 'SSH key not found'}
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': f'SSH key {key_id} deleted successfully'}
    
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def update_ssh_key_last_used(key_id):
    """Update last used timestamp for SSH key"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE ssh_keys 
        SET last_used = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (key_id,))
    
    conn.commit()
    conn.close()

def get_ssh_key_by_name(name):
    """Get SSH key by name"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM ssh_keys WHERE name = ?', (name,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    columns = [desc[0] for desc in cursor.description]
    key = dict(zip(columns, row))
    
    conn.close()
    return key

# ==================== EXPORT FUNCTIONS ====================

def export_servers_csv():
    """Export servers list to CSV format"""
    import csv
    from io import StringIO
    
    servers = get_servers()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['ID', 'Name', 'Host', 'Port', 'Username', 'Description', 'Status', 'Tags', 'Agent Port', 'Last Seen', 'Created At'])
    
    # Data
    for server in servers:
        writer.writerow([
            server.get('id'),
            server.get('name'),
            server.get('host'),
            server.get('port'),
            server.get('username'),
            server.get('description', ''),
            server.get('status'),
            server.get('tags', ''),
            server.get('agent_port'),
            server.get('last_seen', ''),
            server.get('created_at', '')
        ])
    
    return output.getvalue()

def export_monitoring_history_csv(server_id=None, start_date=None, end_date=None):
    """Export monitoring history to CSV"""
    import csv
    from io import StringIO
    
    history = get_monitoring_history(server_id, start_date, end_date)
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Timestamp', 'Server ID', 'Metric Type', 'CPU %', 'Memory %', 'Disk %', 'Network RX', 'Network TX'])
    
    # Data
    for item in history:
        metric_data = item.get('metric_data', {})
        if isinstance(metric_data, str):
            try:
                metric_data = json.loads(metric_data)
            except:
                metric_data = {}
        
        writer.writerow([
            item.get('timestamp'),
            item.get('server_id'),
            item.get('metric_type'),
            metric_data.get('cpu', ''),
            metric_data.get('memory', ''),
            metric_data.get('disk', ''),
            metric_data.get('network_rx', ''),
            metric_data.get('network_tx', '')
        ])
    
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
    writer.writerow(['ID', 'Server ID', 'Alert Type', 'Message', 'Severity', 'Is Read', 'Created At'])
    
    # Data
    for alert in alerts:
        writer.writerow([
            alert.get('id'),
            alert.get('server_id'),
            alert.get('alert_type'),
            alert.get('message'),
            alert.get('severity'),
            'Yes' if alert.get('is_read') else 'No',
            alert.get('created_at')
        ])
    
    return output.getvalue()

# ==================== SERVER NOTES ====================

def add_server_note(server_id, title, content='', created_by=None):
    """Add a note to a server"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO server_notes (server_id, title, content, created_by)
            VALUES (?, ?, ?, ?)
        ''', (server_id, title, content, created_by))
        
        conn.commit()
        note_id = cursor.lastrowid
        conn.close()
        return {'success': True, 'note_id': note_id, 'message': 'Note added successfully'}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def get_server_notes(server_id):
    """Get all notes for a server"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM server_notes 
        WHERE server_id = ?
        ORDER BY updated_at DESC
    ''', (server_id,))
    
    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return notes

def get_server_note(note_id):
    """Get a single note by ID"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM server_notes WHERE id = ?', (note_id,))
    note = cursor.fetchone()
    conn.close()
    return dict(note) if note else None

def update_server_note(note_id, title=None, content=None):
    """Update a server note"""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    values = []
    
    if title is not None:
        updates.append('title = ?')
        values.append(title)
    
    if content is not None:
        updates.append('content = ?')
        values.append(content)
    
    if not updates:
        conn.close()
        return {'success': False, 'error': 'No fields to update'}
    
    updates.append('updated_at = CURRENT_TIMESTAMP')
    values.append(note_id)
    
    try:
        cursor.execute(f'''
            UPDATE server_notes 
            SET {', '.join(updates)}
            WHERE id = ?
        ''', values)
        
        conn.commit()
        conn.close()
        return {'success': True, 'message': 'Note updated successfully'}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def delete_server_note(note_id):
    """Delete a server note"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM server_notes WHERE id = ?', (note_id,))
        conn.commit()
        conn.close()
        return {'success': True, 'message': 'Note deleted successfully'}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

# ==================== DOMAIN SETTINGS ====================

def get_domain_settings():
    """Get domain configuration settings"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM domain_settings LIMIT 1')
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
            'domain_name': '',
            'ssl_enabled': 0,
            'ssl_type': 'none',
            'cert_path': '',
            'key_path': '',
            'auto_renew': 0
        }

def save_domain_settings(domain_name='', ssl_enabled=0, ssl_type='none', cert_path='', key_path='', auto_renew=0):
    """Save domain configuration settings"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if settings exist
        cursor.execute('SELECT id FROM domain_settings LIMIT 1')
        existing = cursor.fetchone()
        
        if existing:
            # Update existing settings
            cursor.execute('''
                UPDATE domain_settings 
                SET domain_name = ?, ssl_enabled = ?, ssl_type = ?, 
                    cert_path = ?, key_path = ?, auto_renew = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (domain_name, ssl_enabled, ssl_type, cert_path, key_path, auto_renew, existing[0]))
        else:
            # Insert new settings
            cursor.execute('''
                INSERT INTO domain_settings 
                (domain_name, ssl_enabled, ssl_type, cert_path, key_path, auto_renew)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (domain_name, ssl_enabled, ssl_type, cert_path, key_path, auto_renew))
        
        conn.commit()
        conn.close()
        return {'success': True, 'message': 'Domain settings saved successfully'}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

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
        now = datetime.utcnow().isoformat() + 'Z'
        meta_json = json.dumps(meta) if meta else None
        
        cursor.execute('''
            INSERT INTO audit_logs (id, user_id, action, target_type, target_id, meta_json, ip, user_agent, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (log_id, user_id, action, target_type, target_id, meta_json, ip, user_agent, now))
        
        conn.commit()
        conn.close()
        return {'success': True, 'log_id': log_id}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

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
    query = 'SELECT * FROM audit_logs WHERE 1=1'
    params = []
    
    if user_id:
        query += ' AND user_id = ?'
        params.append(user_id)
    
    if action:
        query += ' AND action = ?'
        params.append(action)
    
    if target_type:
        query += ' AND target_type = ?'
        params.append(target_type)
    
    if start_date:
        query += ' AND created_at >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND created_at <= ?'
        params.append(end_date)
    
    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    
    logs = []
    for row in cursor.fetchall():
        log = {
            'id': row[0],
            'user_id': row[1],
            'action': row[2],
            'target_type': row[3],
            'target_id': row[4],
            'meta': json.loads(row[5]) if row[5] else None,
            'ip': row[6],
            'user_agent': row[7],
            'created_at': row[8]
        }
        logs.append(log)
    
    conn.close()
    return logs

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
        now = datetime.utcnow().isoformat() + 'Z'
        
        cursor.execute('''
            INSERT INTO terminal_sessions (id, server_id, user_id, ssh_key_id, started_at, last_activity, status)
            VALUES (?, ?, ?, ?, ?, ?, 'active')
        ''', (session_id, server_id, user_id, ssh_key_id, now, now))
        
        conn.commit()
        conn.close()
        return {'success': True, 'session_id': session_id}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def end_terminal_session(session_id, status='closed'):
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
        now = datetime.utcnow().isoformat() + 'Z'
        
        cursor.execute('''
            UPDATE terminal_sessions 
            SET ended_at = ?, status = ?, last_activity = ?
            WHERE id = ?
        ''', (now, status, now, session_id))
        
        conn.commit()
        conn.close()
        return {'success': True}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

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
        now = datetime.utcnow().isoformat() + 'Z'
        
        cursor.execute('''
            UPDATE terminal_sessions 
            SET last_activity = ?
            WHERE id = ?
        ''', (now, session_id))
        
        conn.commit()
        conn.close()
        return {'success': True}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def get_terminal_sessions(user_id=None, server_id=None, status='active'):
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
    
    query = 'SELECT * FROM terminal_sessions WHERE 1=1'
    params = []
    
    if user_id:
        query += ' AND user_id = ?'
        params.append(user_id)
    
    if server_id:
        query += ' AND server_id = ?'
        params.append(server_id)
    
    if status:
        query += ' AND status = ?'
        params.append(status)
    
    query += ' ORDER BY started_at DESC'
    
    cursor.execute(query, params)
    
    sessions = []
    for row in cursor.fetchall():
        session = {
            'id': row[0],
            'server_id': row[1],
            'user_id': row[2],
            'ssh_key_id': row[3],
            'started_at': row[4],
            'ended_at': row[5],
            'status': row[6],
            'last_activity': row[7]
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
        collected_at = datetime.utcnow().isoformat() + 'Z'
        
        # Save/update latest inventory
        cursor.execute('''
            INSERT OR REPLACE INTO server_inventory_latest (server_id, collected_at, inventory_json)
            VALUES (?, ?, ?)
        ''', (server_id, collected_at, inventory_json))
        
        # Optionally save snapshot for history
        if save_snapshot:
            snapshot_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO server_inventory_snapshots (id, server_id, collected_at, inventory_json)
                VALUES (?, ?, ?, ?)
            ''', (snapshot_id, server_id, collected_at, inventory_json))
        
        conn.commit()
        conn.close()
        return {'success': True, 'collected_at': collected_at}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

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
    
    cursor.execute('''
        SELECT collected_at, inventory_json
        FROM server_inventory_latest
        WHERE server_id = ?
    ''', (server_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'server_id': server_id,
            'collected_at': row[0],
            'inventory': json.loads(row[1])
        }
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
    
    cursor.execute('''
        SELECT id, collected_at, inventory_json
        FROM server_inventory_snapshots
        WHERE server_id = ?
        ORDER BY collected_at DESC
        LIMIT ?
    ''', (server_id, limit))
    
    snapshots = []
    for row in cursor.fetchall():
        snapshots.append({
            'id': row[0],
            'server_id': server_id,
            'collected_at': row[1],
            'inventory': json.loads(row[2])
        })
    
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
        now = datetime.utcnow().isoformat() + 'Z'
        
        cursor.execute('''
            INSERT INTO tasks (id, server_id, user_id, command, status, timeout_seconds, store_output, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (task_id, server_id, user_id, command, 'queued', timeout_seconds, store_output, now))
        
        conn.commit()
        conn.close()
        return {'success': True, 'task_id': task_id}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

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
    
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
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
    query = 'SELECT * FROM tasks WHERE 1=1'
    params = []
    
    if server_id:
        query += ' AND server_id = ?'
        params.append(server_id)
    
    if user_id:
        query += ' AND user_id = ?'
        params.append(user_id)
    
    if status:
        query += ' AND status = ?'
        params.append(status)
    
    if from_date:
        query += ' AND created_at >= ?'
        params.append(from_date)
    
    if to_date:
        query += ' AND created_at <= ?'
        params.append(to_date)
    
    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
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
        updates = ['status = ?']
        values = [status]
        
        if exit_code is not None:
            updates.append('exit_code = ?')
            values.append(exit_code)
        
        if stdout is not None:
            updates.append('stdout = ?')
            values.append(stdout)
        
        if stderr is not None:
            updates.append('stderr = ?')
            values.append(stderr)
        
        if started_at is not None:
            updates.append('started_at = ?')
            values.append(started_at)
        
        if finished_at is not None:
            updates.append('finished_at = ?')
            values.append(finished_at)
        
        values.append(task_id)
        
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        return {'success': True}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

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
    
    cursor.execute("""
        DELETE FROM tasks 
        WHERE datetime(created_at, '+' || ? || ' days') < datetime('now')
    """, (days,))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return {'deleted': deleted, 'message': f'Deleted {deleted} old tasks'}

if __name__ == '__main__':
    # Initialize database
    init_database()
    print("Database initialized successfully!")
    
    # Create default admin user
    admin_result = create_admin_user('admin', 'admin123', 'admin@example.com')
    print("\nAdmin user:", admin_result)
    
    # Test: Add a sample server
    result = add_server(
        name='Test LXC Container',
        host='192.168.1.100',
        port=22,
        username='root',
        description='Test container for monitoring',
        ssh_key_path='~/.ssh/id_rsa',
        agent_port=8083,
        tags='lxc,test,production'
    )
    
    print("\nTest server:", result)
    
    # Get all servers
    servers = get_servers()
    print("\nServers:", len(servers))
    
    # Get stats
    stats = get_server_stats()
    print("\nStats:", stats)
