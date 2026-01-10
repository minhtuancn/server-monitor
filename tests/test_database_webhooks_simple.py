"""
Focused tests for database.py webhook functions
Target: Increase coverage from 26% to 80%+
"""

import pytest
import tempfile
import os
import sys

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


class TestWebhookCRUD:
    """Test webhook CRUD operations"""
    
    def test_create_webhook_success(self, temp_db_path):
        """Test creating a new webhook"""
        result = database.create_webhook(
            name="Test Webhook",
            url="https://example.com/hook",
            secret="my-secret",
            enabled=True,
            event_types=["server.down", "server.up"],
            created_by=1  # Required field
        )
        assert result['success'] is True
        assert 'webhook_id' in result
    
    def test_get_webhooks_empty(self, temp_db_path):
        """Test getting webhooks when none exist"""
        webhooks = database.get_webhooks()
        assert webhooks == []
    
    def test_get_webhooks_multiple(self, temp_db_path):
        """Test getting multiple webhooks"""
        database.create_webhook("Hook 1", "https://1.com", event_types=["event.a"], created_by=1)
        database.create_webhook("Hook 2", "https://2.com", event_types=["event.b"], created_by=1)
        database.create_webhook("Hook 3", "https://3.com", event_types=["event.c"], created_by=1)
        
        webhooks = database.get_webhooks()
        assert len(webhooks) == 3
    
    def test_get_webhook_by_id(self, temp_db_path):
        """Test getting webhook by ID"""
        result = database.create_webhook(
            "Test",
            "https://test.com",
            event_types=["test"],
            created_by=1
        )
        webhook_id = result['webhook_id']
        
        webhook = database.get_webhook(webhook_id)
        assert webhook is not None
        assert webhook['id'] == webhook_id
        assert webhook['name'] == "Test"
    
    def test_get_webhook_nonexistent(self, temp_db_path):
        """Test getting non-existent webhook"""
        webhook = database.get_webhook(99999)
        assert webhook is None
    
    def test_update_webhook_success(self, temp_db_path):
        """Test updating webhook"""
        result = database.create_webhook(
            "Old Name",
            "https://old.com",
            event_types=["old"],
            created_by=1
        )
        webhook_id = result['webhook_id']
        
        update_result = database.update_webhook(
            webhook_id,
            name="New Name",
            url="https://new.com",
            event_types=["new"]
        )
        assert update_result.get('success') is True
        
        webhook = database.get_webhook(webhook_id)
        assert webhook['name'] == "New Name"
    
    def test_delete_webhook_success(self, temp_db_path):
        """Test deleting webhook"""
        result = database.create_webhook(
            "To Delete",
            "https://delete.com",
            event_types=[],
            created_by=1
        )
        webhook_id = result['webhook_id']
        
        delete_result = database.delete_webhook(webhook_id)
        assert delete_result.get('success') is True
        
        webhook = database.get_webhook(webhook_id)
        assert webhook is None
    
    def test_get_webhooks_enabled_only(self, temp_db_path):
        """Test filtering enabled webhooks"""
        enabled_result = database.create_webhook("Enabled", "https://e.com", enabled=True, event_types=["test"], created_by=1)
        disabled_result = database.create_webhook("Disabled", "https://d.com", enabled=False, event_types=["test"], created_by=1)
        
        webhooks = database.get_webhooks(enabled_only=True)
        webhook_ids = [w['id'] for w in webhooks]
        assert enabled_result['webhook_id'] in webhook_ids
        assert disabled_result['webhook_id'] not in webhook_ids


class TestWebhookDelivery:
    """Test webhook delivery logging"""
    
    def test_log_webhook_delivery_success(self, temp_db_path):
        """Test logging successful delivery"""
        result = database.create_webhook("Test", "https://test.com", event_types=["test"], created_by=1)
        webhook_id = result['webhook_id']
        
        log_result = database.log_webhook_delivery(
            webhook_id=webhook_id,
            event_id="evt-123",
            event_type="test.event",
            status="success",
            status_code=200,
            response_body="OK"
        )
        assert log_result.get('success') is True
        assert 'log_id' in log_result
    
    def test_log_webhook_delivery_failure(self, temp_db_path):
        """Test logging failed delivery"""
        result = database.create_webhook("Test", "https://test.com", event_types=["test"], created_by=1)
        webhook_id = result['webhook_id']
        
        log_result = database.log_webhook_delivery(
            webhook_id=webhook_id,
            event_id="evt-456",
            event_type="test.event",
            status="failed",
            status_code=500,
            response_body="Error",
            error="Connection timeout"
        )
        assert log_result.get('success') is True
    
    def test_get_webhook_deliveries(self, temp_db_path):
        """Test getting delivery logs"""
        result = database.create_webhook("Test", "https://test.com", event_types=["test"], created_by=1)
        webhook_id = result['webhook_id']
        
        database.log_webhook_delivery(webhook_id, "evt-1", "event.1", "success", 200, "OK")
        database.log_webhook_delivery(webhook_id, "evt-2", "event.2", "failed", 404, "Not Found")
        database.log_webhook_delivery(webhook_id, "evt-3", "event.3", "success", 200, "OK")
        
        deliveries = database.get_webhook_deliveries(webhook_id=webhook_id)
        assert len(deliveries) >= 3
    
    def test_get_webhook_deliveries_with_limit(self, temp_db_path):
        """Test getting limited deliveries"""
        result = database.create_webhook("Test", "https://test.com", event_types=["test"], created_by=1)
        webhook_id = result['webhook_id']
        
        for i in range(10):
            database.log_webhook_delivery(webhook_id, f"evt-{i}", f"event.{i}", "success", 200, "OK")
        
        deliveries = database.get_webhook_deliveries(webhook_id=webhook_id, limit=5)
        assert len(deliveries) == 5
    
    def test_update_webhook_last_triggered(self, temp_db_path):
        """Test updating last triggered timestamp"""
        result = database.create_webhook("Test", "https://test.com", event_types=["test"], created_by=1)
        webhook_id = result['webhook_id']
        
        database.update_webhook_last_triggered(webhook_id)
        
        webhook = database.get_webhook(webhook_id)
        assert webhook['last_triggered_at'] is not None
    
    def test_get_webhook_delivery_stats(self, temp_db_path):
        """Test getting delivery statistics"""
        webhook_id = database.create_webhook("Test", "https://test.com", event_types=["test"])
        
        database.log_webhook_delivery(webhook_id, "event", {}, 200, "OK", True)
        database.log_webhook_delivery(webhook_id, "event", {}, 500, "Error", False)
        
        stats = database.get_webhook_delivery_stats()
        assert isinstance(stats, (list, dict))


class TestWebhookCleanup:
    """Test webhook cleanup operations"""
    
    def test_cleanup_old_webhook_deliveries(self, temp_db_path):
        """Test cleaning up old delivery logs"""
        result = database.create_webhook("Test", "https://test.com", event_types=["test"], created_by=1)
        webhook_id = result['webhook_id']
        
        # Create some deliveries
        for i in range(5):
            database.log_webhook_delivery(webhook_id, f"evt-{i}", f"event.{i}", "success", 200, "OK")
        
        # Cleanup logs older than 90 days (recent logs should remain)
        result = database.cleanup_old_webhook_deliveries(days=90)
        assert isinstance(result, dict)
        assert 'deleted' in result or 'success' in result
