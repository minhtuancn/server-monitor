#!/usr/bin/env python3

"""
SSH Key Manager
Manages SSH private keys with AES-256-GCM encryption
"""

import sqlite3
import uuid
import os
import re
import hashlib
import base64
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Import crypto vault
from crypto_vault import get_vault

# Determine database path
_default_db_path = str(Path(__file__).parent.parent / 'data' / 'servers.db')
DB_PATH = os.environ.get('DB_PATH', _default_db_path)


class SSHKeyManager:
    """
    Manages SSH private keys with encryption
    
    Features:
    - AES-256-GCM encryption for private keys
    - Soft delete (keys are never permanently deleted)
    - Fingerprint calculation
    - Key type detection
    - RBAC support
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize SSH key manager
        
        Args:
            db_path: Path to SQLite database (optional)
        """
        self.db_path = db_path or DB_PATH
        self._ensure_table()
    
    def _ensure_table(self):
        """Ensure ssh_keys table exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ssh_keys (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    public_key TEXT,
                    private_key_enc BLOB NOT NULL,
                    iv BLOB NOT NULL,
                    auth_tag BLOB NOT NULL,
                    key_type TEXT DEFAULT 'rsa',
                    fingerprint TEXT,
                    created_by_user_id INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    deleted_at TEXT,
                    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE SET NULL
                )
            ''')
            
            # Create indexes
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_ssh_keys_created_by 
                ON ssh_keys(created_by_user_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_ssh_keys_deleted_at 
                ON ssh_keys(deleted_at)
            ''')
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Failed to initialize ssh_keys table: {e}")
        finally:
            conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _parse_ssh_key(self, private_key: str) -> Tuple[str, Optional[str]]:
        """
        Parse SSH private key to extract key type and public key
        
        Args:
            private_key: SSH private key string
            
        Returns:
            Tuple of (key_type, public_key or None)
            
        Raises:
            ValueError: If key format is invalid
        """
        # Validate key format
        if not private_key or not isinstance(private_key, str):
            raise ValueError("Invalid private key: empty or not a string")
        
        private_key = private_key.strip()
        
        # Check for valid SSH key markers
        valid_markers = [
            '-----BEGIN OPENSSH PRIVATE KEY-----',
            '-----BEGIN RSA PRIVATE KEY-----',
            '-----BEGIN EC PRIVATE KEY-----',
            '-----BEGIN DSA PRIVATE KEY-----',
            '-----BEGIN PRIVATE KEY-----',
        ]
        
        if not any(marker in private_key for marker in valid_markers):
            raise ValueError("Invalid SSH private key format: missing BEGIN marker")
        
        # Determine key type from content
        key_type = 'rsa'  # default
        if 'BEGIN OPENSSH PRIVATE KEY' in private_key:
            # OpenSSH format - try to detect type from key data
            if 'ssh-ed25519' in private_key or 'ED25519' in private_key:
                key_type = 'ed25519'
            elif 'ecdsa' in private_key.lower():
                key_type = 'ecdsa'
        elif 'BEGIN RSA PRIVATE KEY' in private_key:
            key_type = 'rsa'
        elif 'BEGIN EC PRIVATE KEY' in private_key:
            key_type = 'ecdsa'
        elif 'BEGIN DSA PRIVATE KEY' in private_key:
            key_type = 'dsa'
        
        # Extract public key if present (some formats include it)
        public_key = None
        # For now, we'll generate it from private key later if needed
        # This would require paramiko to load the key, which we'll do when connecting
        
        return key_type, public_key
    
    def _calculate_fingerprint(self, private_key: str) -> str:
        """
        Calculate SSH key fingerprint (SHA256)
        
        Args:
            private_key: SSH private key string
            
        Returns:
            Fingerprint string (SHA256:base64)
        """
        # For a real implementation, we'd use paramiko to load the key
        # and calculate the fingerprint. For now, use a hash of the key content.
        # This is not a real SSH fingerprint but serves as a unique identifier.
        
        # Remove whitespace and markers for consistent hashing
        key_content = re.sub(r'\s', '', private_key)
        key_content = re.sub(r'-----[^-]+-----', '', key_content)
        
        # Calculate SHA256 hash
        hash_obj = hashlib.sha256(key_content.encode('utf-8'))
        fingerprint_bytes = hash_obj.digest()
        
        # Encode as base64 (without padding)
        fingerprint_b64 = base64.b64encode(fingerprint_bytes).decode('ascii').rstrip('=')
        
        return f"SHA256:{fingerprint_b64}"
    
    def create_key(
        self, 
        name: str, 
        private_key: str,
        description: str = None,
        user_id: int = None
    ) -> Dict:
        """
        Create and store an encrypted SSH key
        
        Args:
            name: Unique name for the key
            private_key: SSH private key content
            description: Optional description
            user_id: ID of user creating the key
            
        Returns:
            Dict with key metadata (no private key)
            
        Raises:
            ValueError: If key format is invalid or name already exists
        """
        # Parse and validate key
        key_type, public_key = self._parse_ssh_key(private_key)
        fingerprint = self._calculate_fingerprint(private_key)
        
        # Encrypt private key
        vault = get_vault()
        ciphertext, iv, auth_tag = vault.encrypt(private_key)
        
        # Generate UUID
        key_id = str(uuid.uuid4())
        
        # Store in database
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            
            cursor.execute('''
                INSERT INTO ssh_keys (
                    id, name, description, public_key,
                    private_key_enc, iv, auth_tag,
                    key_type, fingerprint, created_by_user_id,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                key_id, name, description, public_key,
                ciphertext, iv, auth_tag,
                key_type, fingerprint, user_id,
                now, now
            ))
            
            conn.commit()
            
            return {
                'id': key_id,
                'name': name,
                'description': description,
                'key_type': key_type,
                'fingerprint': fingerprint,
                'created_at': now,
                'created_by_user_id': user_id
            }
        
        except sqlite3.IntegrityError as e:
            conn.rollback()
            if 'UNIQUE constraint failed' in str(e):
                raise ValueError(f"SSH key with name '{name}' already exists")
            raise ValueError(f"Database error: {e}")
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Failed to create SSH key: {e}")
        finally:
            conn.close()
    
    def list_keys(self, include_deleted: bool = False) -> List[Dict]:
        """
        List all SSH keys (metadata only, no private keys)
        
        Args:
            include_deleted: Include soft-deleted keys
            
        Returns:
            List of key metadata dicts
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if include_deleted:
                query = 'SELECT * FROM ssh_keys ORDER BY created_at DESC'
            else:
                query = '''
                    SELECT * FROM ssh_keys 
                    WHERE deleted_at IS NULL 
                    ORDER BY created_at DESC
                '''
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            keys = []
            for row in rows:
                # Get username if available
                username = None
                if row['created_by_user_id']:
                    cursor.execute(
                        'SELECT username FROM users WHERE id = ?',
                        (row['created_by_user_id'],)
                    )
                    user_row = cursor.fetchone()
                    if user_row:
                        username = user_row['username']
                
                keys.append({
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'key_type': row['key_type'],
                    'fingerprint': row['fingerprint'],
                    'public_key': row['public_key'],
                    'created_by': username,
                    'created_at': row['created_at'],
                    'deleted_at': row['deleted_at']
                })
            
            return keys
        
        finally:
            conn.close()
    
    def get_key(self, key_id: str, include_deleted: bool = False) -> Optional[Dict]:
        """
        Get SSH key metadata (no private key)
        
        Args:
            key_id: Key UUID
            include_deleted: Include soft-deleted keys
            
        Returns:
            Key metadata dict or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if include_deleted:
                query = 'SELECT * FROM ssh_keys WHERE id = ?'
            else:
                query = 'SELECT * FROM ssh_keys WHERE id = ? AND deleted_at IS NULL'
            
            cursor.execute(query, (key_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Get username if available
            username = None
            if row['created_by_user_id']:
                cursor.execute(
                    'SELECT username FROM users WHERE id = ?',
                    (row['created_by_user_id'],)
                )
                user_row = cursor.fetchone()
                if user_row:
                    username = user_row['username']
            
            return {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'key_type': row['key_type'],
                'fingerprint': row['fingerprint'],
                'public_key': row['public_key'],
                'created_by': username,
                'created_at': row['created_at'],
                'deleted_at': row['deleted_at']
            }
        
        finally:
            conn.close()
    
    def get_decrypted_key(self, key_id: str) -> Optional[str]:
        """
        Get decrypted private key (internal use only)
        
        SECURITY: This function should only be called server-side
        for SSH connections. Never expose via HTTP API.
        
        Args:
            key_id: Key UUID
            
        Returns:
            Decrypted private key string or None if not found
            
        Raises:
            ValueError: If decryption fails
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT private_key_enc, iv, auth_tag 
                FROM ssh_keys 
                WHERE id = ? AND deleted_at IS NULL
            ''', (key_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Decrypt private key
            vault = get_vault()
            private_key = vault.decrypt(
                row['private_key_enc'],
                row['iv'],
                row['auth_tag']
            )
            
            return private_key
        
        finally:
            conn.close()
    
    def delete_key(self, key_id: str) -> bool:
        """
        Soft delete SSH key
        
        Args:
            key_id: Key UUID
            
        Returns:
            True if deleted, False if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            
            cursor.execute('''
                UPDATE ssh_keys 
                SET deleted_at = ?
                WHERE id = ? AND deleted_at IS NULL
            ''', (now, key_id))
            
            conn.commit()
            
            return cursor.rowcount > 0
        
        finally:
            conn.close()


# Module-level functions for convenience
_manager = None


def get_manager() -> SSHKeyManager:
    """Get singleton SSH key manager instance"""
    global _manager
    if _manager is None:
        _manager = SSHKeyManager()
    return _manager


# Export convenience functions
def create_key(name: str, private_key: str, description: str = None, user_id: int = None) -> Dict:
    """Create SSH key"""
    return get_manager().create_key(name, private_key, description, user_id)


def list_keys(include_deleted: bool = False) -> List[Dict]:
    """List SSH keys"""
    return get_manager().list_keys(include_deleted)


def get_key(key_id: str, include_deleted: bool = False) -> Optional[Dict]:
    """Get SSH key metadata"""
    return get_manager().get_key(key_id, include_deleted)


def get_decrypted_key(key_id: str) -> Optional[str]:
    """Get decrypted private key (internal use only)"""
    return get_manager().get_decrypted_key(key_id)


def delete_key(key_id: str) -> bool:
    """Delete SSH key"""
    return get_manager().delete_key(key_id)
