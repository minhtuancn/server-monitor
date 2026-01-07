#!/usr/bin/env python3

"""
Audit Log Cleanup Scheduler
Periodically removes old audit logs based on retention policy
"""

import os
import sys
import threading
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
from observability import StructuredLogger

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration from environment
AUDIT_RETENTION_DAYS = int(os.environ.get('AUDIT_RETENTION_DAYS', '90'))
AUDIT_CLEANUP_ENABLED = os.environ.get('AUDIT_CLEANUP_ENABLED', 'true').lower() in ['true', '1', 'yes']
AUDIT_CLEANUP_INTERVAL_HOURS = int(os.environ.get('AUDIT_CLEANUP_INTERVAL_HOURS', '24'))

# Initialize logger
logger = StructuredLogger('audit_cleanup')


class AuditCleanupScheduler:
    """
    Background scheduler for audit log cleanup
    Runs cleanup on startup and periodically thereafter
    """
    
    def __init__(self, retention_days=None, interval_hours=None, enabled=None):
        """
        Initialize cleanup scheduler
        
        Args:
            retention_days: Days to retain logs (defaults to AUDIT_RETENTION_DAYS env)
            interval_hours: Hours between cleanup runs (defaults to AUDIT_CLEANUP_INTERVAL_HOURS env)
            enabled: Whether cleanup is enabled (defaults to AUDIT_CLEANUP_ENABLED env)
        """
        self.retention_days = retention_days if retention_days is not None else AUDIT_RETENTION_DAYS
        self.interval_hours = interval_hours if interval_hours is not None else AUDIT_CLEANUP_INTERVAL_HOURS
        self.enabled = enabled if enabled is not None else AUDIT_CLEANUP_ENABLED
        self.thread = None
        self.stop_event = threading.Event()
        
        logger.info(
            'Audit cleanup scheduler initialized',
            enabled=self.enabled,
            retention_days=self.retention_days,
            interval_hours=self.interval_hours
        )
    
    def _cleanup_once(self):
        """Perform a single cleanup operation"""
        if not self.enabled:
            logger.info('Audit cleanup skipped - disabled by configuration')
            return
        
        try:
            logger.info(
                'Starting audit log cleanup',
                retention_days=self.retention_days
            )
            
            result = db.cleanup_old_audit_logs(days=self.retention_days)
            
            logger.info(
                'Audit log cleanup completed',
                deleted=result['deleted'],
                retention_days=self.retention_days,
                cutoff_date=result.get('cutoff_date')
            )
            
            # Add audit log for cleanup action (system user = 0 or special marker)
            # Only log if we actually deleted something to avoid spam
            if result['deleted'] > 0:
                try:
                    # Get first admin user as fallback for system actions
                    admin_users = db.get_all_users()
                    system_user_id = admin_users[0]['id'] if admin_users else 1
                    
                    db.add_audit_log(
                        user_id=system_user_id,
                        action='audit.cleanup',
                        target_type='audit_logs',
                        target_id='system',
                        meta={
                            'deleted_count': result['deleted'],
                            'retention_days': self.retention_days,
                            'cutoff_date': result.get('cutoff_date')
                        }
                    )
                except Exception as e:
                    logger.warning(
                        'Failed to create audit log for cleanup',
                        error=str(e)
                    )
            
        except Exception as e:
            logger.error(
                'Audit log cleanup failed',
                error=str(e),
                retention_days=self.retention_days
            )
    
    def _cleanup_loop(self):
        """Background cleanup loop"""
        # Run cleanup immediately on startup
        self._cleanup_once()
        
        # Then run periodically
        while not self.stop_event.is_set():
            # Sleep for the interval (check every minute for stop signal)
            for _ in range(self.interval_hours * 60):
                if self.stop_event.is_set():
                    break
                time.sleep(60)  # Sleep 1 minute
            
            # Run cleanup if not stopped
            if not self.stop_event.is_set():
                self._cleanup_once()
    
    def start(self):
        """Start the background cleanup scheduler"""
        if not self.enabled:
            logger.info('Audit cleanup scheduler not started - disabled by configuration')
            return
        
        if self.thread and self.thread.is_alive():
            logger.warning('Audit cleanup scheduler already running')
            return
        
        logger.info('Starting audit cleanup scheduler thread')
        self.thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the background cleanup scheduler"""
        if not self.thread or not self.thread.is_alive():
            return
        
        logger.info('Stopping audit cleanup scheduler')
        self.stop_event.set()
        
        # Wait for thread to finish (max 10 seconds)
        self.thread.join(timeout=10)
        
        if self.thread.is_alive():
            logger.warning('Audit cleanup thread did not stop gracefully')
        else:
            logger.info('Audit cleanup scheduler stopped')
    
    def is_running(self):
        """Check if scheduler is running"""
        return self.thread and self.thread.is_alive()


# Global scheduler instance
_scheduler = None


def get_audit_cleanup_scheduler():
    """Get or create global audit cleanup scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = AuditCleanupScheduler()
    return _scheduler


def start_audit_cleanup():
    """Start the audit cleanup scheduler"""
    scheduler = get_audit_cleanup_scheduler()
    scheduler.start()


def stop_audit_cleanup():
    """Stop the audit cleanup scheduler"""
    scheduler = get_audit_cleanup_scheduler()
    scheduler.stop()


if __name__ == '__main__':
    # Test the scheduler
    print("Testing audit cleanup scheduler...")
    scheduler = AuditCleanupScheduler(retention_days=90, interval_hours=24)
    
    print("Running cleanup once...")
    scheduler._cleanup_once()
    
    print("Done!")
