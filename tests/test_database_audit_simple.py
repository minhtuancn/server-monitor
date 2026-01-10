"""
Focused tests for database.py audit log functions
Target: Increase coverage from 26% to 80%+
"""

import pytest
import tempfile
import os
import sys
from datetime import datetime, timezone, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import database


@pytest.fixture
def temp_db_path():
    """Create temporary database"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    original_db_path = database.DB_PATH
    database.DB_PATH = path
    database.init_database()
    
    yield path
    
    database.DB_PATH = original_db_path
    try:
        os.unlink(path)
    except:
        pass


class TestAuditLogCRUD:
    """Test audit log operations"""
    
    def test_add_audit_log_success(self, temp_db_path):
        """Test adding an audit log entry"""
        result = database.add_audit_log(
            user_id=1,
            action="user.login",
            target_type="user",
            target_id=1,
            meta={"ip": "192.168.1.1"},
            ip="192.168.1.1"
        )
        assert result['success'] is True
        assert 'log_id' in result
        assert isinstance(result['log_id'], str)
    
    def test_add_audit_log_minimal(self, temp_db_path):
        """Test audit log with minimal fields (all required fields)"""
        result = database.add_audit_log(
            user_id=1,  # Required by schema
            action="system.startup",
            target_type="system",  # Required by schema
            target_id="sys-001"  # Required by schema
        )
        assert result['success'] is True
    
    def test_add_audit_log_with_metadata(self, temp_db_path):
        """Test audit log with complex metadata"""
        metadata = {
            "request_id": "req-123",
            "changes": {
                "before": {"status": "active"},
                "after": {"status": "inactive"}
            }
        }
        
        result = database.add_audit_log(
            user_id=1,
            action="server.update",
            target_type="server",
            target_id=10,
            meta=metadata
        )
        assert result['success'] is True
    
    def test_get_audit_logs_all(self, temp_db_path):
        """Test getting all audit logs"""
        database.add_audit_log(1, "action.1", "type.a", 1)
        database.add_audit_log(2, "action.2", "type.b", 2)
        database.add_audit_log(3, "action.3", "type.c", 3)
        
        logs = database.get_audit_logs()
        assert len(logs) >= 3
    
    def test_get_audit_logs_with_limit(self, temp_db_path):
        """Test getting limited audit logs"""
        for i in range(10):
            database.add_audit_log(1, f"action.{i}", "type", i)
        
        logs = database.get_audit_logs(limit=5)
        assert len(logs) == 5
    
    def test_get_audit_logs_with_offset(self, temp_db_path):
        """Test pagination of audit logs"""
        for i in range(10):
            database.add_audit_log(1, f"action.{i}", "type", i)
        
        page1 = database.get_audit_logs(limit=5, offset=0)
        page2 = database.get_audit_logs(limit=5, offset=5)
        
        assert len(page1) == 5
        assert len(page2) == 5
        
        # Verify different pages
        page1_ids = [log['id'] for log in page1]
        page2_ids = [log['id'] for log in page2]
        assert set(page1_ids).isdisjoint(set(page2_ids))


class TestAuditLogFiltering:
    """Test audit log filtering"""
    
    def test_get_audit_logs_by_user(self, temp_db_path):
        """Test filtering by user"""
        database.add_audit_log(1, "action.a", "type", 1)
        database.add_audit_log(2, "action.b", "type", 2)
        database.add_audit_log(1, "action.c", "type", 3)
        
        user1_logs = database.get_audit_logs(user_id=1)
        assert len(user1_logs) == 2
        assert all(log['user_id'] == 1 for log in user1_logs)
    
    def test_get_audit_logs_by_action(self, temp_db_path):
        """Test filtering by action"""
        database.add_audit_log(1, "user.login", "user", 1)
        database.add_audit_log(1, "user.logout", "user", 1)
        database.add_audit_log(1, "user.login", "user", 2)
        
        login_logs = database.get_audit_logs(action="user.login")
        assert len(login_logs) == 2
        assert all(log['action'] == "user.login" for log in login_logs)
    
    def test_get_audit_logs_by_target_type(self, temp_db_path):
        """Test filtering by target type"""
        database.add_audit_log(1, "update", "server", 10)
        database.add_audit_log(1, "delete", "server", 20)
        database.add_audit_log(1, "update", "user", 1)
        
        server_logs = database.get_audit_logs(target_type="server")
        assert len(server_logs) == 2
        assert all(log['target_type'] == "server" for log in server_logs)
    
    def test_get_audit_logs_multiple_filters(self, temp_db_path):
        """Test filtering with multiple criteria"""
        database.add_audit_log(1, "server.update", "server", 10)
        database.add_audit_log(1, "server.update", "server", 20)
        database.add_audit_log(2, "server.update", "server", 10)
        
        logs = database.get_audit_logs(
            user_id=1,
            action="server.update",
            target_type="server"
        )
        assert len(logs) == 2
        assert all(log['user_id'] == 1 for log in logs)


class TestAuditLogExport:
    """Test audit log export functions"""
    
    def test_export_audit_logs_csv(self, temp_db_path):
        """Test exporting audit logs as CSV"""
        database.add_audit_log(1, "action.1", "type", 1)
        database.add_audit_log(2, "action.2", "type", 2)
        
        csv_data = database.export_audit_logs_csv()
        assert isinstance(csv_data, str)
        assert len(csv_data) > 0
        assert "action.1" in csv_data or "action" in csv_data
    
    def test_export_audit_logs_csv_with_filters(self, temp_db_path):
        """Test exporting filtered audit logs as CSV"""
        database.add_audit_log(1, "action.a", "type", 1)
        database.add_audit_log(2, "action.b", "type", 2)
        
        csv_data = database.export_audit_logs_csv(user_id=1)
        assert isinstance(csv_data, str)
    
    def test_export_audit_logs_json(self, temp_db_path):
        """Test exporting audit logs as JSON"""
        database.add_audit_log(1, "action.1", "type", 1)
        database.add_audit_log(2, "action.2", "type", 2)
        
        json_data = database.export_audit_logs_json()
        assert isinstance(json_data, str)
        assert len(json_data) > 0
    
    def test_export_audit_logs_json_with_limit(self, temp_db_path):
        """Test exporting limited audit logs as JSON"""
        for i in range(10):
            database.add_audit_log(1, f"action.{i}", "type", i)
        
        json_data = database.export_audit_logs_json(limit=5)
        assert isinstance(json_data, str)


class TestAuditLogCleanup:
    """Test audit log retention"""
    
    def test_cleanup_old_audit_logs(self, temp_db_path):
        """Test cleaning up old audit logs"""
        # Add some logs
        for i in range(5):
            database.add_audit_log(1, f"action.{i}", "type", i)
        
        # Cleanup logs older than 90 days (recent logs should remain)
        result = database.cleanup_old_audit_logs(days=90)
        assert isinstance(result, dict)
        assert 'deleted' in result or 'success' in result
        
        # Recent logs should still exist
        logs = database.get_audit_logs()
        assert len(logs) >= 5


class TestAuditLogEdgeCases:
    """Test edge cases"""
    
    def test_add_audit_log_system_user(self, temp_db_path):
        """Test system events with system user (user_id required by schema)"""
        # Schema requires user_id NOT NULL, so use system user ID
        result = database.add_audit_log(
            user_id=0,  # System user ID
            action="system.cron",
            target_type="system",
            target_id="cron-job-1"
        )
        assert result['success'] is True
    
    def test_add_audit_log_with_user_agent(self, temp_db_path):
        """Test audit log with user agent"""
        result = database.add_audit_log(
            user_id=1,
            action="user.login",
            target_type="user",
            target_id=1,
            user_agent="Mozilla/5.0"
        )
        assert result['success'] is True
    
    def test_get_audit_logs_empty_database(self, temp_db_path):
        """Test getting logs from empty database"""
        logs = database.get_audit_logs()
        assert logs == []
    
    def test_audit_log_unicode_support(self, temp_db_path):
        """Test audit logs with unicode"""
        result = database.add_audit_log(
            1,
            "user.update",
            "user",
            1,
            meta={"name": "日本語", "emoji": "🚀"}
        )
        assert result['success'] is True
        
        logs = database.get_audit_logs(limit=1)
        assert len(logs) == 1
