"""
Database Management Module

Provides database backup, restore, and health monitoring functionality.
"""

import os
import json
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DB_FILE = PROJECT_ROOT / "data" / "servers.db"
BACKUP_DIR = PROJECT_ROOT / "data" / "backups"
BACKUP_SCRIPT = PROJECT_ROOT / "scripts" / "backup-database.sh"
RESTORE_SCRIPT = PROJECT_ROOT / "scripts" / "restore-database.sh"


class DatabaseManager:
    """Manage database backup, restore, and health operations"""
    
    def __init__(self):
        self.db_file = DB_FILE
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self) -> Dict:
        """
        Create a new database backup
        
        Returns:
            Dict with backup status and details
        """
        try:
            result = subprocess.run(
                [str(BACKUP_SCRIPT), "backup"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Parse output to get backup details
                backups = self.list_backups()
                latest = backups[0] if backups else None
                
                return {
                    "success": True,
                    "message": "Backup created successfully",
                    "backup": latest
                }
            else:
                return {
                    "success": False,
                    "message": f"Backup failed: {result.stderr}",
                    "error": result.stderr
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Backup timed out",
                "error": "Operation took longer than 60 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Backup error: {str(e)}",
                "error": str(e)
            }
    
    def list_backups(self) -> List[Dict]:
        """
        List all available backups with metadata
        
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        if not self.backup_dir.exists():
            return backups
        
        for backup_file in sorted(self.backup_dir.glob("servers_db_*.db.gpg"), reverse=True):
            metadata_file = backup_file.with_suffix('.meta')
            
            # Get file stats
            stat = backup_file.stat()
            
            backup_info = {
                "filename": backup_file.name,
                "path": str(backup_file),
                "size": stat.st_size,
                "size_human": self._format_size(stat.st_size),
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "encrypted": backup_file.suffix == ".gpg"
            }
            
            # Load metadata if available
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        backup_info.update({
                            "checksum": metadata.get("checksum_sha256"),
                            "timestamp": metadata.get("timestamp")
                        })
                except Exception:
                    pass
            
            backups.append(backup_info)
        
        return backups
    
    def get_backup_details(self, filename: str) -> Optional[Dict]:
        """
        Get detailed information about a specific backup
        
        Args:
            filename: Backup filename
            
        Returns:
            Backup details or None if not found
        """
        backups = self.list_backups()
        for backup in backups:
            if backup["filename"] == filename:
                return backup
        return None
    
    def delete_backup(self, filename: str) -> Dict:
        """
        Delete a backup file and its metadata
        
        Args:
            filename: Backup filename to delete
            
        Returns:
            Dict with deletion status
        """
        try:
            backup_file = self.backup_dir / filename
            metadata_file = backup_file.with_suffix('.meta')
            
            if not backup_file.exists():
                return {
                    "success": False,
                    "message": f"Backup not found: {filename}"
                }
            
            # Delete files
            backup_file.unlink()
            if metadata_file.exists():
                metadata_file.unlink()
            
            return {
                "success": True,
                "message": f"Backup deleted: {filename}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to delete backup: {str(e)}",
                "error": str(e)
            }
    
    def restore_backup(self, filename: str) -> Dict:
        """
        Restore database from backup
        
        Args:
            filename: Backup filename to restore
            
        Returns:
            Dict with restore status
        """
        try:
            result = subprocess.run(
                [str(RESTORE_SCRIPT), "restore", filename],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Database restored successfully",
                    "warning": "Please restart services for changes to take effect"
                }
            else:
                return {
                    "success": False,
                    "message": f"Restore failed: {result.stderr}",
                    "error": result.stderr
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Restore timed out",
                "error": "Operation took longer than 120 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Restore error: {str(e)}",
                "error": str(e)
            }
    
    def check_health(self) -> Dict:
        """
        Check database health and integrity
        
        Returns:
            Dict with health status and metrics
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # PRAGMA integrity_check
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            integrity_ok = integrity_result == "ok"
            
            # Get database size
            db_size = self.db_file.stat().st_size
            
            # Count tables
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # Get table statistics
            tables = []
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            for (table_name,) in cursor.fetchall():
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                tables.append({
                    "name": table_name,
                    "rows": row_count
                })
            
            # Check foreign keys
            cursor.execute("PRAGMA foreign_key_check")
            foreign_key_errors = cursor.fetchall()
            
            # Get database page count and page size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "healthy": integrity_ok and len(foreign_key_errors) == 0,
                "integrity_check": "passed" if integrity_ok else "failed",
                "size": db_size,
                "size_human": self._format_size(db_size),
                "tables": table_count,
                "table_details": tables,
                "page_count": page_count,
                "page_size": page_size,
                "foreign_key_errors": len(foreign_key_errors),
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "last_checked": datetime.now().isoformat()
            }
    
    def get_storage_stats(self) -> Dict:
        """
        Get storage statistics for database and backups
        
        Returns:
            Dict with storage metrics
        """
        try:
            # Database size
            db_size = self.db_file.stat().st_size if self.db_file.exists() else 0
            
            # Backup sizes
            backup_count = 0
            backup_total_size = 0
            
            if self.backup_dir.exists():
                for backup_file in self.backup_dir.glob("servers_db_*.db.gpg"):
                    backup_count += 1
                    backup_total_size += backup_file.stat().st_size
            
            # Data directory total
            data_dir = PROJECT_ROOT / "data"
            data_total_size = sum(f.stat().st_size for f in data_dir.rglob('*') if f.is_file())
            
            return {
                "database": {
                    "size": db_size,
                    "size_human": self._format_size(db_size)
                },
                "backups": {
                    "count": backup_count,
                    "total_size": backup_total_size,
                    "size_human": self._format_size(backup_total_size),
                    "average_size": backup_total_size // backup_count if backup_count > 0 else 0
                },
                "data_directory": {
                    "total_size": data_total_size,
                    "size_human": self._format_size(data_total_size)
                }
            }
        except Exception as e:
            return {
                "error": str(e)
            }
    
    @staticmethod
    def _format_size(bytes_size: int) -> str:
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"


# Singleton instance
db_manager = DatabaseManager()
