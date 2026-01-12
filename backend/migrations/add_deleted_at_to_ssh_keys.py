#!/usr/bin/env python3
"""
Database Migration: Add deleted_at column to ssh_keys table
For existing databases that don't have this column
"""

import sqlite3
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import database as db

def migrate():
    """Add deleted_at column to ssh_keys if it doesn't exist"""
    print("🔄 Starting database migration...")
    
    conn = sqlite3.connect(db.DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if ssh_keys table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ssh_keys'")
        if not cursor.fetchone():
            print("⚠️  ssh_keys table does not exist yet - skipping migration")
            conn.close()
            return
        
        # Check if deleted_at column already exists
        cursor.execute("PRAGMA table_info(ssh_keys)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'deleted_at' in columns:
            print("✓ Column ssh_keys.deleted_at already exists - no migration needed")
            conn.close()
            return
        
        # Add deleted_at column
        print("Adding deleted_at column to ssh_keys table...")
        cursor.execute("""
            ALTER TABLE ssh_keys 
            ADD COLUMN deleted_at TIMESTAMP
        """)
        
        # Create index
        print("Creating index on deleted_at...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ssh_keys_deleted_at
            ON ssh_keys(deleted_at)
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print(f"Database path: {db.DB_PATH}")
    migrate()
