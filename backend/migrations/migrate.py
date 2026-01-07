#!/usr/bin/env python3

"""
Database Migration System for Server Monitor v4.0
Run migrations to add new features
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

# Database path - use relative path from project root
_project_root = Path(__file__).parent.parent.parent
_default_db_path = str(_project_root / 'data' / 'servers.db')
DB_PATH = os.environ.get('DB_PATH', _default_db_path)
MIGRATIONS_TABLE = 'schema_migrations'

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_migrations_table():
    """Create migrations tracking table"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {MIGRATIONS_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def is_migration_applied(version):
    """Check if migration was already applied"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(f'SELECT COUNT(*) FROM {MIGRATIONS_TABLE} WHERE version = ?', (version,))
    count = cursor.fetchone()[0]
    
    conn.close()
    return count > 0

def mark_migration_applied(version, name):
    """Mark migration as applied"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(f'''
        INSERT INTO {MIGRATIONS_TABLE} (version, name)
        VALUES (?, ?)
    ''', (version, name))
    
    conn.commit()
    conn.close()

# ========================================
# Migration 001: Add user settings columns
# ========================================
def migration_001_user_settings():
    """Add theme and language columns to admin_users"""
    version = '001'
    name = 'Add user settings (theme, language)'
    
    if is_migration_applied(version):
        print(f'[SKIP] Migration {version}: {name} already applied')
        return
    
    print(f'[RUN] Migration {version}: {name}')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(admin_users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'theme' not in columns:
            cursor.execute('''
                ALTER TABLE admin_users 
                ADD COLUMN theme VARCHAR(20) DEFAULT 'dark'
            ''')
            print('  ✓ Added column: admin_users.theme')
        
        if 'language' not in columns:
            cursor.execute('''
                ALTER TABLE admin_users 
                ADD COLUMN language VARCHAR(10) DEFAULT 'en'
            ''')
            print('  ✓ Added column: admin_users.language')
        
        conn.commit()
        mark_migration_applied(version, name)
        print(f'[DONE] Migration {version} completed')
        
    except Exception as e:
        conn.rollback()
        print(f'[ERROR] Migration {version} failed: {e}')
        raise
    finally:
        conn.close()

# ========================================
# Migration 002: Server groups
# ========================================
def migration_002_server_groups():
    """Create server groups and membership tables"""
    version = '002'
    name = 'Create server groups tables'
    
    if is_migration_applied(version):
        print(f'[SKIP] Migration {version}: {name} already applied')
        return
    
    print(f'[RUN] Migration {version}: {name}')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Server groups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS server_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                color VARCHAR(7) DEFAULT '#667eea',
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL
            )
        ''')
        print('  ✓ Created table: server_groups')
        
        # Server group members table (many-to-many relationship)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS server_group_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                server_id INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES server_groups(id) ON DELETE CASCADE,
                FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE,
                UNIQUE(group_id, server_id)
            )
        ''')
        print('  ✓ Created table: server_group_members')
        
        conn.commit()
        mark_migration_applied(version, name)
        print(f'[DONE] Migration {version} completed')
        
    except Exception as e:
        conn.rollback()
        print(f'[ERROR] Migration {version} failed: {e}')
        raise
    finally:
        conn.close()

# ========================================
# Migration 003: SSH key enhancements
# ========================================
def migration_003_ssh_key_enhancements():
    """Add SSH key deployment tracking"""
    version = '003'
    name = 'SSH key deployment tracking'
    
    if is_migration_applied(version):
        print(f'[SKIP] Migration {version}: {name} already applied')
        return
    
    print(f'[RUN] Migration {version}: {name}')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # SSH key deployments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ssh_key_deployments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id INTEGER NOT NULL,
                server_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                deployed_at TIMESTAMP,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (key_id) REFERENCES ssh_keys(id) ON DELETE CASCADE,
                FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
            )
        ''')
        print('  ✓ Created table: ssh_key_deployments')
        
        conn.commit()
        mark_migration_applied(version, name)
        print(f'[DONE] Migration {version} completed')
        
    except Exception as e:
        conn.rollback()
        print(f'[ERROR] Migration {version} failed: {e}')
        raise
    finally:
        conn.close()

# ========================================
# Migration 004: Network scan history
# ========================================
def migration_004_network_scan_history():
    """Create network scan history table"""
    version = '004'
    name = 'Network scan history'
    
    if is_migration_applied(version):
        print(f'[SKIP] Migration {version}: {name} already applied')
        return
    
    print(f'[RUN] Migration {version}: {name}')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                scan_type TEXT NOT NULL,
                target TEXT NOT NULL,
                result TEXT NOT NULL,
                status TEXT DEFAULT 'completed',
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE,
                FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL
            )
        ''')
        print('  ✓ Created table: network_scan_history')
        
        conn.commit()
        mark_migration_applied(version, name)
        print(f'[DONE] Migration {version} completed')
        
    except Exception as e:
        conn.rollback()
        print(f'[ERROR] Migration {version} failed: {e}')
        raise
    finally:
        conn.close()

# ========================================
# Migration 005: Agent installation logs
# ========================================
def migration_005_agent_installation_logs():
    """Create agent installation logs table"""
    version = '005'
    name = 'Agent installation logs'
    
    if is_migration_applied(version):
        print(f'[SKIP] Migration {version}: {name} already applied')
        return
    
    print(f'[RUN] Migration {version}: {name}')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_installation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                log_output TEXT,
                error_message TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                installed_by INTEGER,
                FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE,
                FOREIGN KEY (installed_by) REFERENCES admin_users(id) ON DELETE SET NULL
            )
        ''')
        print('  ✓ Created table: agent_installation_logs')
        
        conn.commit()
        mark_migration_applied(version, name)
        print(f'[DONE] Migration {version} completed')
        
    except Exception as e:
        conn.rollback()
        print(f'[ERROR] Migration {version} failed: {e}')
        raise
    finally:
        conn.close()

# ========================================
# Migration 006: Email settings table
# ========================================
def migration_006_email_settings():
    """Create email settings table"""
    version = '006'
    name = 'Email settings table'
    
    if is_migration_applied(version):
        print(f'[SKIP] Migration {version}: {name} already applied')
        return
    
    print(f'[RUN] Migration {version}: {name}')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                smtp_host TEXT NOT NULL,
                smtp_port INTEGER DEFAULT 587,
                smtp_username TEXT,
                smtp_password TEXT,
                smtp_use_tls INTEGER DEFAULT 1,
                from_email TEXT NOT NULL,
                from_name TEXT DEFAULT 'Server Monitor',
                recipients TEXT,
                enabled INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by INTEGER,
                FOREIGN KEY (updated_by) REFERENCES admin_users(id) ON DELETE SET NULL
            )
        ''')
        print('  ✓ Created table: email_settings')
        
        # Insert default settings
        cursor.execute('''
            INSERT OR IGNORE INTO email_settings (id, smtp_host, smtp_port, from_email, enabled)
            VALUES (1, 'smtp.gmail.com', 587, 'noreply@example.com', 0)
        ''')
        print('  ✓ Inserted default email settings')
        
        conn.commit()
        mark_migration_applied(version, name)
        print(f'[DONE] Migration {version} completed')
        
    except Exception as e:
        conn.rollback()
        print(f'[ERROR] Migration {version} failed: {e}')
        raise
    finally:
        conn.close()

# ========================================
# Run all migrations
# ========================================
def run_all_migrations():
    """Run all pending migrations"""
    print('=' * 60)
    print('Server Monitor v4.0 - Database Migrations')
    print('=' * 60)
    print()
    
    # Initialize migrations table
    init_migrations_table()
    
    # Run migrations in order
    migrations = [
        migration_001_user_settings,
        migration_002_server_groups,
        migration_003_ssh_key_enhancements,
        migration_004_network_scan_history,
        migration_005_agent_installation_logs,
        migration_006_email_settings,
    ]
    
    for migration in migrations:
        try:
            migration()
        except Exception as e:
            print(f'\n[FATAL] Migration failed: {e}')
            print('Aborting remaining migrations.')
            return False
    
    print()
    print('=' * 60)
    print('All migrations completed successfully!')
    print('=' * 60)
    return True

if __name__ == '__main__':
    run_all_migrations()
