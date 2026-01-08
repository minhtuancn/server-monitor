#!/usr/bin/env python3

"""
Tests for Webhooks Management
Tests database CRUD operations and webhook dispatcher functionality
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import json
import tempfile

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import database as db
from event_model import Event, EventTypes, create_event
import webhook_dispatcher


class TestWebhookDatabase(unittest.TestCase):
    """Test webhook database operations"""
    
    def setUp(self):
        """Set up test database"""
        # Use temporary file for test database
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_file.close()
        db.DB_PATH = self.db_file.name
        db.init_database()
    
    def tearDown(self):
        """Clean up test database"""
        try:
            os.unlink(self.db_file.name)
        except:
            pass
    
    def test_create_webhook(self):
        """Test creating a webhook"""
        result = db.create_webhook(
            name='Test Webhook',
            url='https://example.com/hook',
            secret='test-secret',
            enabled=True,
            event_types=['task.finished', 'server.created'],
            created_by=1
        )
        
        self.assertTrue(result['success'])
        self.assertIn('webhook_id', result)
        self.assertIsNotNone(result['webhook_id'])
    
    def test_get_webhooks(self):
        """Test getting all webhooks"""
        # Create test webhooks
        db.create_webhook('Webhook 1', 'https://example.com/1', created_by=1)
        db.create_webhook('Webhook 2', 'https://example.com/2', created_by=1, enabled=False)
        db.create_webhook('Webhook 3', 'https://example.com/3', created_by=1)
        
        # Get all webhooks
        all_webhooks = db.get_webhooks()
        self.assertEqual(len(all_webhooks), 3)
        
        # Get only enabled webhooks
        enabled_webhooks = db.get_webhooks(enabled_only=True)
        self.assertEqual(len(enabled_webhooks), 2)
    
    def test_get_webhook(self):
        """Test getting a single webhook"""
        result = db.create_webhook('Test', 'https://example.com', created_by=1)
        webhook_id = result['webhook_id']
        
        webhook = db.get_webhook(webhook_id)
        self.assertIsNotNone(webhook)
        self.assertEqual(webhook['name'], 'Test')
        self.assertEqual(webhook['url'], 'https://example.com')
    
    def test_get_webhook_not_found(self):
        """Test getting non-existent webhook"""
        webhook = db.get_webhook('non-existent-id')
        self.assertIsNone(webhook)
    
    def test_update_webhook(self):
        """Test updating a webhook"""
        result = db.create_webhook('Original', 'https://example.com', created_by=1)
        webhook_id = result['webhook_id']
        
        # Update name and enabled status
        update_result = db.update_webhook(
            webhook_id,
            name='Updated',
            enabled=False
        )
        self.assertTrue(update_result['success'])
        
        # Verify updates
        webhook = db.get_webhook(webhook_id)
        self.assertEqual(webhook['name'], 'Updated')
        self.assertEqual(webhook['enabled'], 0)  # SQLite stores as integer
    
    def test_update_webhook_clear_secret(self):
        """Test clearing webhook secret"""
        result = db.create_webhook(
            'Test',
            'https://example.com',
            secret='original-secret',
            created_by=1
        )
        webhook_id = result['webhook_id']
        
        # Clear secret
        update_result = db.update_webhook(webhook_id, secret='')
        self.assertTrue(update_result['success'])
        
        webhook = db.get_webhook(webhook_id)
        # SQLite may return None or empty string for cleared fields
        self.assertTrue(webhook['secret'] in ('', None))
    
    def test_delete_webhook(self):
        """Test deleting a webhook"""
        result = db.create_webhook('Test', 'https://example.com', created_by=1)
        webhook_id = result['webhook_id']
        
        # Delete webhook
        delete_result = db.delete_webhook(webhook_id)
        self.assertTrue(delete_result['success'])
        
        # Verify deletion
        webhook = db.get_webhook(webhook_id)
        self.assertIsNone(webhook)
    
    def test_log_webhook_delivery(self):
        """Test logging a webhook delivery"""
        result = db.create_webhook('Test', 'https://example.com', created_by=1)
        webhook_id = result['webhook_id']
        
        # Log successful delivery
        log_result = db.log_webhook_delivery(
            webhook_id=webhook_id,
            event_id='event-123',
            event_type='task.finished',
            status='success',
            status_code=200,
            response_body='OK',
            attempt=1
        )
        self.assertTrue(log_result['success'])
    
    def test_get_webhook_deliveries(self):
        """Test getting webhook deliveries"""
        result = db.create_webhook('Test', 'https://example.com', created_by=1)
        webhook_id = result['webhook_id']
        
        # Log multiple deliveries
        for i in range(5):
            db.log_webhook_delivery(
                webhook_id=webhook_id,
                event_id=f'event-{i}',
                event_type='test.event',
                status='success',
                status_code=200,
                attempt=1
            )
        
        # Get deliveries
        deliveries = db.get_webhook_deliveries(webhook_id)
        self.assertEqual(len(deliveries), 5)
        
        # Test pagination
        deliveries_page1 = db.get_webhook_deliveries(webhook_id, limit=2, offset=0)
        self.assertEqual(len(deliveries_page1), 2)
        
        deliveries_page2 = db.get_webhook_deliveries(webhook_id, limit=2, offset=2)
        self.assertEqual(len(deliveries_page2), 2)
    
    def test_update_webhook_last_triggered(self):
        """Test updating webhook last triggered timestamp"""
        result = db.create_webhook('Test', 'https://example.com', created_by=1)
        webhook_id = result['webhook_id']
        
        # Update last triggered
        update_result = db.update_webhook_last_triggered(webhook_id)
        self.assertTrue(update_result['success'])
        
        # Verify timestamp was set
        webhook = db.get_webhook(webhook_id)
        self.assertIsNotNone(webhook['last_triggered_at'])
    
    def test_webhook_event_types_json(self):
        """Test that event_types are stored and retrieved as list"""
        event_types = ['task.finished', 'server.created', 'alert.triggered']
        result = db.create_webhook(
            'Test',
            'https://example.com',
            event_types=event_types,
            created_by=1
        )
        webhook_id = result['webhook_id']
        
        webhook = db.get_webhook(webhook_id)
        self.assertEqual(webhook['event_types'], event_types)


class TestSSRFProtection(unittest.TestCase):
    """Test SSRF protection in webhook dispatcher"""
    
    def test_safe_https_url(self):
        """Test that HTTPS URLs to public domains are allowed"""
        is_safe, error = webhook_dispatcher.is_safe_url('https://example.com/webhook')
        self.assertTrue(is_safe)
        self.assertIsNone(error)
    
    def test_safe_http_url(self):
        """Test that HTTP URLs to public domains are allowed"""
        is_safe, error = webhook_dispatcher.is_safe_url('http://example.com/webhook')
        self.assertTrue(is_safe)
        self.assertIsNone(error)
    
    def test_block_localhost(self):
        """Test that localhost is blocked"""
        is_safe, error = webhook_dispatcher.is_safe_url('http://localhost/webhook')
        self.assertFalse(is_safe)
        self.assertIn('localhost', error.lower())
    
    def test_block_127_0_0_1(self):
        """Test that 127.0.0.1 is blocked"""
        is_safe, error = webhook_dispatcher.is_safe_url('http://127.0.0.1/webhook')
        self.assertFalse(is_safe)
        self.assertIn('localhost', error.lower())
    
    def test_block_0_0_0_0(self):
        """Test that 0.0.0.0 is blocked"""
        is_safe, error = webhook_dispatcher.is_safe_url('http://0.0.0.0/webhook')
        self.assertFalse(is_safe)
        self.assertIn('localhost', error.lower())
    
    def test_block_ipv6_localhost(self):
        """Test that IPv6 localhost is blocked"""
        is_safe, error = webhook_dispatcher.is_safe_url('http://[::1]/webhook')
        self.assertFalse(is_safe)
        # Can be either loopback or localhost depending on how IP is detected
        self.assertTrue('loopback' in error.lower() or 'localhost' in error.lower())
    
    def test_block_private_ip_10(self):
        """Test that 10.x.x.x is blocked"""
        is_safe, error = webhook_dispatcher.is_safe_url('http://10.0.0.1/webhook')
        self.assertFalse(is_safe)
        self.assertIn('private', error.lower())
    
    def test_block_private_ip_192(self):
        """Test that 192.168.x.x is blocked"""
        is_safe, error = webhook_dispatcher.is_safe_url('http://192.168.1.1/webhook')
        self.assertFalse(is_safe)
        self.assertIn('private', error.lower())
    
    def test_block_private_ip_172(self):
        """Test that 172.16-31.x.x is blocked"""
        is_safe, error = webhook_dispatcher.is_safe_url('http://172.16.0.1/webhook')
        self.assertFalse(is_safe)
        self.assertIn('private', error.lower())
    
    def test_block_invalid_scheme(self):
        """Test that non-HTTP schemes are blocked"""
        is_safe, error = webhook_dispatcher.is_safe_url('file:///etc/passwd')
        self.assertFalse(is_safe)
        self.assertIn('scheme', error.lower())
        
        is_safe, error = webhook_dispatcher.is_safe_url('gopher://example.com')
        self.assertFalse(is_safe)
        self.assertIn('scheme', error.lower())
    
    def test_block_internal_domains(self):
        """Test that internal domain patterns are blocked"""
        is_safe, error = webhook_dispatcher.is_safe_url('http://internal.local/webhook')
        self.assertFalse(is_safe)
        self.assertIn('internal', error.lower())


class TestWebhookDispatcher(unittest.TestCase):
    """Test webhook dispatcher functionality"""
    
    def setUp(self):
        """Set up test database"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_file.close()
        db.DB_PATH = self.db_file.name
        db.init_database()
    
    def tearDown(self):
        """Clean up test database"""
        try:
            os.unlink(self.db_file.name)
        except:
            pass
    
    @patch('webhook_dispatcher.urllib.request.urlopen')
    def test_dispatch_to_webhooks_success(self, mock_urlopen):
        """Test successful webhook dispatch"""
        # Mock successful HTTP response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'{"status":"ok"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Create webhook
        result = db.create_webhook(
            'Test Webhook',
            'https://example.com/hook',
            secret='test-secret',
            created_by=1
        )
        webhook_id = result['webhook_id']
        
        # Create event
        event = create_event(
            event_type='task.finished',
            user_id=1,
            target_type='task',
            target_id='123'
        )
        
        # Dispatch
        webhook_dispatcher.dispatch_to_webhooks(event)
        
        # Verify HTTP request was made
        self.assertTrue(mock_urlopen.called)
        
        # Verify delivery was logged
        deliveries = db.get_webhook_deliveries(webhook_id)
        self.assertEqual(len(deliveries), 1)
        self.assertEqual(deliveries[0]['status'], 'success')
        self.assertEqual(deliveries[0]['status_code'], 200)
    
    @patch('webhook_dispatcher.urllib.request.urlopen')
    def test_dispatch_with_event_type_filter(self, mock_urlopen):
        """Test that webhooks filter by event type"""
        # Create webhook that only listens to server events
        result = db.create_webhook(
            'Server Webhook',
            'https://example.com/hook',
            event_types=['server.created', 'server.deleted'],
            created_by=1
        )
        
        # Create task event (should be ignored)
        task_event = create_event(
            event_type='task.finished',
            user_id=1
        )
        
        # Dispatch task event
        webhook_dispatcher.dispatch_to_webhooks(task_event)
        
        # Verify no HTTP request was made
        self.assertFalse(mock_urlopen.called)
        
        # Create server event (should be delivered)
        server_event = create_event(
            event_type='server.created',
            user_id=1
        )
        
        # Mock response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'OK'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Dispatch server event
        webhook_dispatcher.dispatch_to_webhooks(server_event)
        
        # Verify HTTP request was made this time
        self.assertTrue(mock_urlopen.called)
    
    @patch('webhook_dispatcher.urllib.request.urlopen')
    def test_dispatch_hmac_signature(self, mock_urlopen):
        """Test that HMAC signature is included in headers"""
        # Mock response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'OK'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Create webhook with secret
        db.create_webhook(
            'Test',
            'https://example.com/hook',
            secret='test-secret',
            created_by=1
        )
        
        # Create and dispatch event
        event = create_event(event_type='test.event', user_id=1)
        webhook_dispatcher.dispatch_to_webhooks(event)
        
        # Get the request object passed to urlopen
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        
        # Verify signature header is present
        self.assertIn('X-sm-signature', request.headers)
        signature = request.headers['X-sm-signature']
        self.assertTrue(signature.startswith('sha256='))
    
    def test_ssrf_protection_blocks_delivery(self):
        """Test that SSRF protection prevents delivery to internal URLs"""
        # Create webhook with internal URL
        result = db.create_webhook(
            'Internal Webhook',
            'http://localhost:8080/hook',
            created_by=1
        )
        webhook_id = result['webhook_id']
        
        # Create event
        event = create_event(event_type='test.event', user_id=1)
        
        # Dispatch (should be blocked)
        webhook_dispatcher.dispatch_to_webhooks(event)
        
        # Verify delivery was logged as failed
        deliveries = db.get_webhook_deliveries(webhook_id)
        self.assertEqual(len(deliveries), 1)
        self.assertEqual(deliveries[0]['status'], 'failed')
        self.assertIn('SSRF', deliveries[0]['error'])
    
    @patch('webhook_dispatcher.urllib.request.urlopen')
    @patch('webhook_dispatcher.time.sleep')  # Mock sleep to speed up test
    def test_retry_on_failure(self, mock_sleep, mock_urlopen):
        """Test that webhook delivery retries on failure"""
        # Mock HTTP error
        mock_urlopen.side_effect = Exception('Connection timeout')
        
        # Create webhook with retry_max=2
        result = db.create_webhook(
            'Test',
            'https://example.com/hook',
            retry_max=2,
            created_by=1
        )
        webhook_id = result['webhook_id']
        
        # Create and dispatch event
        event = create_event(event_type='test.event', user_id=1)
        webhook_dispatcher.dispatch_to_webhooks(event)
        
        # Verify retry was attempted (called 2 times)
        self.assertEqual(mock_urlopen.call_count, 2)
        
        # Verify deliveries were logged (2 attempts)
        deliveries = db.get_webhook_deliveries(webhook_id)
        self.assertEqual(len(deliveries), 2)
        self.assertEqual(deliveries[0]['attempt'], 2)  # Most recent first
        self.assertEqual(deliveries[1]['attempt'], 1)


class TestCSVInjectionPrevention(unittest.TestCase):
    """Test CSV injection prevention in export functions"""
    
    def setUp(self):
        """Set up test database"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_file.close()
        db.DB_PATH = self.db_file.name
        db.init_database()
    
    def tearDown(self):
        """Clean up test database"""
        try:
            os.unlink(self.db_file.name)
        except:
            pass
    
    def test_sanitize_csv_field_formula_injection(self):
        """Test that formula injection characters are escaped"""
        # Test = (formula prefix)
        self.assertEqual(db._sanitize_csv_field('=HYPERLINK("http://evil.com")'), 
                        "'=HYPERLINK(\"http://evil.com\")")
        
        # Test + (formula prefix)
        self.assertEqual(db._sanitize_csv_field('+1+cmd|" /C calc"!A0'), 
                        "'+1+cmd|\" /C calc\"!A0")
        
        # Test - (formula prefix, also negative numbers)
        self.assertEqual(db._sanitize_csv_field('-1+cmd|" /C calc"!A0'), 
                        "'-1+cmd|\" /C calc\"!A0")
        
        # Test @ (formula prefix in some apps)
        self.assertEqual(db._sanitize_csv_field('@SUM(1+1)*cmd|" /C calc"!A0'), 
                        "'@SUM(1+1)*cmd|\" /C calc\"!A0")
        
        # Test tab character
        self.assertEqual(db._sanitize_csv_field('\t=evil'), "'\t=evil")
        
        # Test carriage return
        self.assertEqual(db._sanitize_csv_field('\r=evil'), "'\r=evil")
    
    def test_sanitize_csv_field_safe_values(self):
        """Test that safe values are not modified"""
        self.assertEqual(db._sanitize_csv_field('normal text'), 'normal text')
        self.assertEqual(db._sanitize_csv_field('server-name'), 'server-name')
        self.assertEqual(db._sanitize_csv_field('192.168.1.1'), '192.168.1.1')
        self.assertEqual(db._sanitize_csv_field(123), '123')
        self.assertEqual(db._sanitize_csv_field(None), '')
        self.assertEqual(db._sanitize_csv_field(''), '')
    
    def test_export_servers_csv_sanitizes_fields(self):
        """Test that export_servers_csv sanitizes fields"""
        # Create a server with a malicious name
        db.add_server(
            name='=HYPERLINK("http://evil.com","Click me")',
            host='192.168.1.1',
            port=22,
            username='root',
            description='+cmd|" /C calc"!A0'
        )
        
        csv_data = db.export_servers_csv()
        
        # Verify the malicious content is sanitized
        self.assertIn("'=HYPERLINK", csv_data)
        self.assertIn("'+cmd", csv_data)
        # Verify the original malicious content is not present unescaped
        self.assertNotIn(',=HYPERLINK', csv_data)
        self.assertNotIn(',+cmd', csv_data)
    
    def test_export_alerts_csv_sanitizes_fields(self):
        """Test that export_alerts_csv sanitizes fields"""
        # First, we need a server to attach an alert to
        server_result = db.add_server(
            name='TestServer',
            host='192.168.1.2',
            port=22,
            username='root'
        )
        server_id = server_result.get('server_id')
        
        # Create an alert with malicious content
        db.create_alert(
            server_id=server_id,
            alert_type='=FORMULA',
            message='-dangerous payload',
            severity='high'
        )
        
        csv_data = db.export_alerts_csv()
        
        # Verify the malicious content is sanitized
        self.assertIn("'=FORMULA", csv_data)
        self.assertIn("'-dangerous", csv_data)


if __name__ == '__main__':
    unittest.main()
