#!/usr/bin/env python3
"""
User Management System
Handles user CRUD operations, authentication, and role management
"""

import sqlite3
import hashlib
import secrets
import re
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Role definitions
ROLES = {
    'admin': {
        'name': 'Administrator',
        'permissions': ['*'],  # All permissions
        'description': 'Full system access'
    },
    'user': {
        'name': 'User',
        'permissions': ['server.view', 'server.edit', 'terminal.use', 'alerts.view'],
        'description': 'Standard user access'
    },
    'operator': {
        'name': 'Operator',
        'permissions': ['server.view', 'server.edit', 'terminal.use', 'alerts.view', 'alerts.edit'],
        'description': 'Operations team access'
    },
    'auditor': {
        'name': 'Auditor',
        'permissions': ['server.view', 'alerts.view', 'audit.view'],
        'description': 'Read-only audit access'
    }
}

class UserManagement:
    def __init__(self, db_path: str = None):
        # Use provided path or calculate relative to backend directory
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'servers.db')
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure user-related tables exist with all required columns"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if users table exists and has all columns
        c.execute("PRAGMA table_info(users)")
        existing_columns = {row[1] for row in c.fetchall()}
        
        required_columns = {
            'id', 'username', 'email', 'password_hash', 'role',
            'avatar_url', 'is_active', 'last_login', 'created_at',
            'password_reset_token', 'reset_token_expires'
        }
        
        if not existing_columns:
            # Create users table if it doesn't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    avatar_url TEXT,
                    is_active INTEGER DEFAULT 1,
                    last_login TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    password_reset_token TEXT,
                    reset_token_expires TEXT
                )
            ''')
            
            # Create default admin user if no users exist
            c.execute("SELECT COUNT(*) FROM users")
            if c.fetchone()[0] == 0:
                # Create default admin user (admin/admin123)
                # Hash password inline to avoid calling self methods during initialization
                salt = secrets.token_hex(16)
                hash_obj = hashlib.sha256((salt + 'admin123').encode())
                default_password_hash = f"{salt}${hash_obj.hexdigest()}"
                c.execute('''
                    INSERT INTO users (username, email, password_hash, role, is_active)
                    VALUES (?, ?, ?, ?, ?)
                ''', ('admin', 'admin@example.com', default_password_hash, 'admin', 1))
        else:
            # Add missing columns
            missing_columns = required_columns - existing_columns
            for col in missing_columns:
                if col == 'avatar_url':
                    c.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
                elif col == 'is_active':
                    c.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
                elif col == 'last_login':
                    c.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
                elif col == 'password_reset_token':
                    c.execute("ALTER TABLE users ADD COLUMN password_reset_token TEXT")
                elif col == 'reset_token_expires':
                    c.execute("ALTER TABLE users ADD COLUMN reset_token_expires TEXT")
        
        conn.commit()
        conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((salt + password).encode())
        return f"{salt}${hash_obj.hexdigest()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_value = password_hash.split('$')
            hash_obj = hashlib.sha256((salt + password).encode())
            return hash_obj.hexdigest() == hash_value
        except:
            return False
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_username(self, username: str) -> bool:
        """Validate username (alphanumeric, underscore, hyphen, 3-20 chars)"""
        pattern = r'^[a-zA-Z0-9_-]{3,20}$'
        return bool(re.match(pattern, username))
    
    def _validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"
        return True, "Password is valid"
    
    def create_user(self, username: str, email: str, password: str, role: str = 'user', 
                   avatar_url: str = None) -> Tuple[bool, str, Optional[int]]:
        """
        Create new user
        Returns: (success, message, user_id)
        """
        # Validate inputs
        if not self._validate_username(username):
            return False, "Invalid username format (3-20 alphanumeric chars, underscore, hyphen)", None
        
        if not self._validate_email(email):
            return False, "Invalid email format", None
        
        is_valid, msg = self._validate_password(password)
        if not is_valid:
            return False, msg, None
        
        if role not in ROLES:
            return False, f"Invalid role. Must be one of: {', '.join(ROLES.keys())}", None
        
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            # Check if username exists
            c.execute("SELECT id FROM users WHERE username = ?", (username,))
            if c.fetchone():
                conn.close()
                return False, "Username already exists", None
            
            # Check if email exists
            c.execute("SELECT id FROM users WHERE email = ?", (email,))
            if c.fetchone():
                conn.close()
                return False, "Email already exists", None
            
            # Create user
            password_hash = self._hash_password(password)
            created_at = datetime.now().isoformat()
            
            c.execute("""
                INSERT INTO users (username, email, password_hash, role, avatar_url, 
                                 is_active, created_at)
                VALUES (?, ?, ?, ?, ?, 1, ?)
            """, (username, email, password_hash, role, avatar_url, created_at))
            
            user_id = c.lastrowid
            conn.commit()
            conn.close()
            
            return True, "User created successfully", user_id
        
        except Exception as e:
            return False, f"Database error: {str(e)}", None
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authenticate user
        Returns: (success, message, user_data)
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            c.execute("""
                SELECT id, username, email, password_hash, role, avatar_url, 
                       is_active, last_login
                FROM users 
                WHERE username = ? OR email = ?
            """, (username, username))
            
            user = c.fetchone()
            
            if not user:
                conn.close()
                return False, "Invalid username or password", None
            
            if not user['is_active']:
                conn.close()
                return False, "Account is disabled", None
            
            if not self._verify_password(password, user['password_hash']):
                conn.close()
                return False, "Invalid username or password", None
            
            # Update last login
            now = datetime.now().isoformat()
            c.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, user['id']))
            conn.commit()
            conn.close()
            
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'avatar_url': user['avatar_url'],
                'last_login': now,
                'permissions': ROLES[user['role']]['permissions']
            }
            
            return True, "Authentication successful", user_data
        
        except Exception as e:
            return False, f"Database error: {str(e)}", None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            c.execute("""
                SELECT id, username, email, role, avatar_url, is_active, 
                       last_login, created_at
                FROM users 
                WHERE id = ?
            """, (user_id,))
            
            user = c.fetchone()
            conn.close()
            
            if not user:
                return None
            
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'role_name': ROLES[user['role']]['name'],
                'avatar_url': user['avatar_url'],
                'is_active': bool(user['is_active']),
                'last_login': user['last_login'],
                'created_at': user['created_at'],
                'permissions': ROLES[user['role']]['permissions']
            }
        
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (without password hashes)"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            c.execute("""
                SELECT id, username, email, role, avatar_url, is_active, 
                       last_login, created_at
                FROM users 
                ORDER BY created_at DESC
            """)
            
            users = []
            for row in c.fetchall():
                users.append({
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'role': row['role'],
                    'role_name': ROLES[row['role']]['name'],
                    'avatar_url': row['avatar_url'],
                    'is_active': bool(row['is_active']),
                    'last_login': row['last_login'],
                    'created_at': row['created_at']
                })
            
            conn.close()
            return users
        
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def update_user(self, user_id: int, **kwargs) -> Tuple[bool, str]:
        """
        Update user fields
        Allowed fields: email, role, avatar_url, is_active
        """
        allowed_fields = {'email', 'role', 'avatar_url', 'is_active'}
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            return False, "No valid fields to update"
        
        # Validate email if provided
        if 'email' in update_fields and not self._validate_email(update_fields['email']):
            return False, "Invalid email format"
        
        # Validate role if provided
        if 'role' in update_fields and update_fields['role'] not in ROLES:
            return False, f"Invalid role. Must be one of: {', '.join(ROLES.keys())}"
        
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            # Check if user exists
            c.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not c.fetchone():
                conn.close()
                return False, "User not found"
            
            # Build UPDATE query
            set_clause = ', '.join([f"{k} = ?" for k in update_fields.keys()])
            values = list(update_fields.values()) + [user_id]
            
            c.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
            conn.commit()
            conn.close()
            
            return True, "User updated successfully"
        
        except Exception as e:
            return False, f"Database error: {str(e)}"
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user password"""
        # Validate new password
        is_valid, msg = self._validate_password(new_password)
        if not is_valid:
            return False, msg
        
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            c.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
            user = c.fetchone()
            
            if not user:
                conn.close()
                return False, "User not found"
            
            # Verify old password
            if not self._verify_password(old_password, user['password_hash']):
                conn.close()
                return False, "Current password is incorrect"
            
            # Update password
            new_hash = self._hash_password(new_password)
            c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
            conn.commit()
            conn.close()
            
            return True, "Password changed successfully"
        
        except Exception as e:
            return False, f"Database error: {str(e)}"
    
    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """Delete user"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            # Check if user exists and is not the last admin
            c.execute("SELECT role FROM users WHERE id = ?", (user_id,))
            user = c.fetchone()
            
            if not user:
                conn.close()
                return False, "User not found"
            
            if user['role'] == 'admin':
                c.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
                admin_count = c.fetchone()['count']
                if admin_count <= 1:
                    conn.close()
                    return False, "Cannot delete the last admin user"
            
            c.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            
            return True, "User deleted successfully"
        
        except Exception as e:
            return False, f"Database error: {str(e)}"
    
    def has_permission(self, user_id: int, permission: str) -> bool:
        """Check if user has specific permission"""
        user = self.get_user(user_id)
        if not user or not user['is_active']:
            return False
        
        permissions = user['permissions']
        
        # Admin has all permissions
        if '*' in permissions:
            return True
        
        # Check exact permission or wildcard
        return permission in permissions or any(
            p.endswith('.*') and permission.startswith(p[:-2])
            for p in permissions
        )
    
    def get_roles(self) -> Dict:
        """Get all available roles"""
        return ROLES


# Singleton instance
_user_manager = None

def get_user_manager(db_path: str = None) -> UserManagement:
    """Get UserManagement singleton instance"""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManagement(db_path)
    return _user_manager
