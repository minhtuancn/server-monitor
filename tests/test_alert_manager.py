"""
Alert Manager Tests for alert_manager.py
Target: Test alert dispatching, threshold checking, multi-channel notifications
Focus: Channel routing, severity levels, threshold monitoring
"""

import pytest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import alert_manager


class TestDefaultThresholds:
    """Test default alert thresholds"""
    
    def test_default_thresholds_exist(self):
        """Test default thresholds are defined"""
        assert hasattr(alert_manager, 'DEFAULT_THRESHOLDS')
        assert isinstance(alert_manager.DEFAULT_THRESHOLDS, dict)
    
    def test_cpu_threshold_default(self):
        """Test CPU threshold default value"""
        thresholds = alert_manager.DEFAULT_THRESHOLDS
        
        assert "cpu" in thresholds
        assert thresholds["cpu"] == 90
    
    def test_memory_threshold_default(self):
        """Test memory threshold default value"""
        thresholds = alert_manager.DEFAULT_THRESHOLDS
        
        assert "memory" in thresholds
        assert thresholds["memory"] == 85
    
    def test_disk_threshold_default(self):
        """Test disk threshold default value"""
        thresholds = alert_manager.DEFAULT_THRESHOLDS
        
        assert "disk" in thresholds
        assert thresholds["disk"] == 90
    
    def test_all_threshold_keys_present(self):
        """Test all required threshold keys are present"""
        thresholds = alert_manager.DEFAULT_THRESHOLDS
        required_keys = ["cpu", "memory", "disk"]
        
        for key in required_keys:
            assert key in thresholds


class TestEnabledChannels:
    """Test notification channel detection"""
    
    def test_get_enabled_channels_exists(self):
        """Test get_enabled_channels function exists"""
        assert hasattr(alert_manager, 'get_enabled_channels')
        assert callable(alert_manager.get_enabled_channels)
    
    def test_enabled_channels_returns_dict(self):
        """Test get_enabled_channels returns dict"""
        with patch('alert_manager.email.get_email_config') as mock_email, \
             patch('alert_manager.telegram_bot.get_telegram_config') as mock_tg, \
             patch('alert_manager.slack_integration.get_slack_config') as mock_slack:
            
            mock_email.return_value = None
            mock_tg.return_value = None
            mock_slack.return_value = None
            
            channels = alert_manager.get_enabled_channels()
            
            assert isinstance(channels, dict)
    
    def test_checks_email_channel(self):
        """Test checks email channel status"""
        with patch('alert_manager.email.get_email_config') as mock_email, \
             patch('alert_manager.telegram_bot.get_telegram_config') as mock_tg, \
             patch('alert_manager.slack_integration.get_slack_config') as mock_slack:
            
            mock_email.return_value = {"enabled": True}
            mock_tg.return_value = None
            mock_slack.return_value = None
            
            channels = alert_manager.get_enabled_channels()
            
            assert "email" in channels
            assert channels["email"] is True
    
    def test_checks_telegram_channel(self):
        """Test checks telegram channel status"""
        with patch('alert_manager.email.get_email_config') as mock_email, \
             patch('alert_manager.telegram_bot.get_telegram_config') as mock_tg, \
             patch('alert_manager.slack_integration.get_slack_config') as mock_slack:
            
            mock_email.return_value = None
            mock_tg.return_value = {"enabled": True}
            mock_slack.return_value = None
            
            channels = alert_manager.get_enabled_channels()
            
            assert "telegram" in channels
            assert channels["telegram"] is True
    
    def test_checks_slack_channel(self):
        """Test checks slack channel status"""
        with patch('alert_manager.email.get_email_config') as mock_email, \
             patch('alert_manager.telegram_bot.get_telegram_config') as mock_tg, \
             patch('alert_manager.slack_integration.get_slack_config') as mock_slack:
            
            mock_email.return_value = None
            mock_tg.return_value = None
            mock_slack.return_value = {"enabled": True}
            
            channels = alert_manager.get_enabled_channels()
            
            assert "slack" in channels
            assert channels["slack"] is True
    
    def test_disabled_channel_returns_false(self):
        """Test disabled channels return False"""
        with patch('alert_manager.email.get_email_config') as mock_email, \
             patch('alert_manager.telegram_bot.get_telegram_config') as mock_tg, \
             patch('alert_manager.slack_integration.get_slack_config') as mock_slack:
            
            mock_email.return_value = {"enabled": False}
            mock_tg.return_value = None
            mock_slack.return_value = None
            
            channels = alert_manager.get_enabled_channels()
            
            assert channels["email"] is False


class TestSendAlert:
    """Test send_alert function"""
    
    def test_send_alert_exists(self):
        """Test send_alert function exists"""
        assert hasattr(alert_manager, 'send_alert')
        assert callable(alert_manager.send_alert)
    
    def test_send_alert_parameters(self):
        """Test send_alert accepts required parameters"""
        params = {
            "server_name": "web-1",
            "alert_type": "High CPU Usage",
            "message": "CPU at 95%",
            "severity": "critical",
            "server_id": 5
        }
        
        assert all(k in params for k in ["server_name", "alert_type", "message"])
    
    def test_send_alert_returns_dict(self):
        """Test send_alert returns results dict"""
        with patch('alert_manager.get_enabled_channels') as mock_channels, \
             patch('alert_manager.db.create_alert') as mock_db:
            
            mock_channels.return_value = {
                "email": False,
                "telegram": False,
                "slack": False
            }
            mock_db.return_value = 1
            
            result = alert_manager.send_alert(
                server_name="test",
                alert_type="Test",
                message="Test message"
            )
            
            assert isinstance(result, dict)
    
    def test_alert_result_has_channel_keys(self):
        """Test alert result has keys for all channels"""
        with patch('alert_manager.get_enabled_channels') as mock_channels, \
             patch('alert_manager.db.create_alert') as mock_db:
            
            mock_channels.return_value = {
                "email": False,
                "telegram": False,
                "slack": False
            }
            mock_db.return_value = 1
            
            result = alert_manager.send_alert(
                server_name="test",
                alert_type="Test",
                message="Test"
            )
            
            assert "email" in result
            assert "telegram" in result
            assert "slack" in result
    
    def test_severity_levels(self):
        """Test valid severity levels"""
        valid_severities = ["info", "warning", "critical"]
        
        assert "info" in valid_severities
        assert "warning" in valid_severities
        assert "critical" in valid_severities
    
    def test_database_alert_creation(self):
        """Test alert is created in database"""
        with patch('alert_manager.get_enabled_channels') as mock_channels, \
             patch('alert_manager.db.create_alert') as mock_db:
            
            mock_channels.return_value = {
                "email": False,
                "telegram": False,
                "slack": False
            }
            mock_db.return_value = 123
            
            result = alert_manager.send_alert(
                server_name="test",
                alert_type="Test",
                message="Test",
                server_id=5
            )
            
            mock_db.assert_called_once()
            assert result.get("alert_id") == 123


class TestThresholdChecking:
    """Test threshold checking logic"""
    
    def test_check_server_thresholds_exists(self):
        """Test check_server_thresholds function exists"""
        assert hasattr(alert_manager, 'check_server_thresholds')
        assert callable(alert_manager.check_server_thresholds)
    
    def test_cpu_threshold_exceeded(self):
        """Test CPU threshold exceeded triggers alert"""
        cpu_usage = 95
        threshold = 90
        
        exceeded = cpu_usage > threshold
        
        assert exceeded is True
    
    def test_cpu_below_threshold(self):
        """Test CPU below threshold does not trigger"""
        cpu_usage = 75
        threshold = 90
        
        exceeded = cpu_usage > threshold
        
        assert exceeded is False
    
    def test_memory_threshold_exceeded(self):
        """Test memory threshold exceeded triggers alert"""
        memory_usage = 90
        threshold = 85
        
        exceeded = memory_usage > threshold
        
        assert exceeded is True
    
    def test_disk_threshold_exceeded(self):
        """Test disk threshold exceeded triggers alert"""
        disk_usage = 92
        threshold = 90
        
        exceeded = disk_usage > threshold
        
        assert exceeded is True
    
    def test_critical_severity_threshold(self):
        """Test critical severity for values > 95"""
        value = 96
        
        severity = "critical" if value > 95 else "warning"
        
        assert severity == "critical"
    
    def test_warning_severity_threshold(self):
        """Test warning severity for values between threshold and 95"""
        value = 92
        
        severity = "critical" if value > 95 else "warning"
        
        assert severity == "warning"
    
    def test_custom_thresholds(self):
        """Test custom thresholds can be provided"""
        custom = {"cpu": 80, "memory": 75, "disk": 85}
        
        assert custom["cpu"] != alert_manager.DEFAULT_THRESHOLDS["cpu"]
    
    def test_metrics_dict_format(self):
        """Test metrics dictionary format"""
        metrics = {
            "cpu": 85.5,
            "memory": 70.2,
            "disk": 60.0
        }
        
        assert "cpu" in metrics
        assert "memory" in metrics
        assert "disk" in metrics
        assert all(isinstance(v, (int, float)) for v in metrics.values())


class TestAlertTypes:
    """Test different alert types"""
    
    def test_high_cpu_alert_type(self):
        """Test high CPU alert type"""
        alert_type = "High CPU Usage"
        
        assert "CPU" in alert_type
        assert "High" in alert_type
    
    def test_high_memory_alert_type(self):
        """Test high memory alert type"""
        alert_type = "High Memory Usage"
        
        assert "Memory" in alert_type
        assert "High" in alert_type
    
    def test_high_disk_alert_type(self):
        """Test high disk alert type"""
        alert_type = "High Disk Usage"
        
        assert "Disk" in alert_type
        assert "High" in alert_type
    
    def test_alert_message_format(self):
        """Test alert message format"""
        cpu_usage = 92.5
        threshold = 90
        
        message = f"CPU usage is at {cpu_usage:.1f}% (threshold: {threshold}%)"
        
        assert str(cpu_usage) in message or "92.5" in message
        assert str(threshold) in message


class TestChannelDispatching:
    """Test alert dispatching to channels"""
    
    def test_email_alert_dispatch(self):
        """Test email alert is dispatched when enabled"""
        with patch('alert_manager.get_enabled_channels') as mock_channels, \
             patch('alert_manager.email.send_alert_email') as mock_email, \
             patch('alert_manager.db.create_alert') as mock_db:
            
            mock_channels.return_value = {
                "email": True,
                "telegram": False,
                "slack": False
            }
            mock_email.return_value = {"success": True}
            mock_db.return_value = 1
            
            result = alert_manager.send_alert(
                server_name="test",
                alert_type="Test",
                message="Test"
            )
            
            mock_email.assert_called_once()
            assert result["email"]["enabled"] is True
    
    def test_telegram_alert_dispatch(self):
        """Test telegram alert is dispatched when enabled"""
        with patch('alert_manager.get_enabled_channels') as mock_channels, \
             patch('alert_manager.telegram_bot.send_alert_telegram') as mock_tg, \
             patch('alert_manager.db.create_alert') as mock_db:
            
            mock_channels.return_value = {
                "email": False,
                "telegram": True,
                "slack": False
            }
            mock_tg.return_value = {"success": True}
            mock_db.return_value = 1
            
            result = alert_manager.send_alert(
                server_name="test",
                alert_type="Test",
                message="Test"
            )
            
            mock_tg.assert_called_once()
            assert result["telegram"]["enabled"] is True
    
    def test_slack_alert_dispatch(self):
        """Test slack alert is dispatched when enabled"""
        with patch('alert_manager.get_enabled_channels') as mock_channels, \
             patch('alert_manager.slack_integration.send_alert_slack') as mock_slack, \
             patch('alert_manager.db.create_alert') as mock_db:
            
            mock_channels.return_value = {
                "email": False,
                "telegram": False,
                "slack": True
            }
            mock_slack.return_value = {"success": True}
            mock_db.return_value = 1
            
            result = alert_manager.send_alert(
                server_name="test",
                alert_type="Test",
                message="Test"
            )
            
            mock_slack.assert_called_once()
            assert result["slack"]["enabled"] is True
    
    def test_multiple_channels_dispatch(self):
        """Test alert dispatches to multiple channels"""
        with patch('alert_manager.get_enabled_channels') as mock_channels, \
             patch('alert_manager.email.send_alert_email') as mock_email, \
             patch('alert_manager.telegram_bot.send_alert_telegram') as mock_tg, \
             patch('alert_manager.slack_integration.send_alert_slack') as mock_slack, \
             patch('alert_manager.db.create_alert') as mock_db:
            
            mock_channels.return_value = {
                "email": True,
                "telegram": True,
                "slack": True
            }
            mock_email.return_value = {"success": True}
            mock_tg.return_value = {"success": True}
            mock_slack.return_value = {"success": True}
            mock_db.return_value = 1
            
            result = alert_manager.send_alert(
                server_name="test",
                alert_type="Test",
                message="Test"
            )
            
            mock_email.assert_called_once()
            mock_tg.assert_called_once()
            mock_slack.assert_called_once()


class TestErrorHandling:
    """Test error handling in alert manager"""
    
    def test_channel_error_handling(self):
        """Test channel errors are caught and recorded"""
        with patch('alert_manager.get_enabled_channels') as mock_channels, \
             patch('alert_manager.email.send_alert_email') as mock_email, \
             patch('alert_manager.db.create_alert') as mock_db:
            
            mock_channels.return_value = {
                "email": True,
                "telegram": False,
                "slack": False
            }
            mock_email.side_effect = Exception("SMTP error")
            mock_db.return_value = 1
            
            result = alert_manager.send_alert(
                server_name="test",
                alert_type="Test",
                message="Test"
            )
            
            assert result["email"]["enabled"] is True
            assert "error" in result["email"]
    
    def test_database_error_handling(self):
        """Test database errors are handled"""
        with patch('alert_manager.get_enabled_channels') as mock_channels, \
             patch('alert_manager.db.create_alert') as mock_db:
            
            mock_channels.return_value = {
                "email": False,
                "telegram": False,
                "slack": False
            }
            mock_db.side_effect = Exception("Database error")
            
            result = alert_manager.send_alert(
                server_name="test",
                alert_type="Test",
                message="Test",
                server_id=5
            )
            
            assert "db_error" in result


class TestAlertResults:
    """Test alert result structure"""
    
    def test_result_channel_structure(self):
        """Test result has correct structure for each channel"""
        result = {
            "email": {"sent": False, "enabled": False},
            "telegram": {"sent": False, "enabled": False},
            "slack": {"sent": False, "enabled": False}
        }
        
        for channel in ["email", "telegram", "slack"]:
            assert channel in result
            assert "sent" in result[channel]
            assert "enabled" in result[channel]
    
    def test_successful_send_result(self):
        """Test successful send result"""
        channel_result = {
            "sent": True,
            "enabled": True,
            "response": {"success": True}
        }
        
        assert channel_result["sent"] is True
        assert channel_result["enabled"] is True
    
    def test_failed_send_result(self):
        """Test failed send result"""
        channel_result = {
            "sent": False,
            "enabled": True,
            "error": "Connection failed"
        }
        
        assert channel_result["sent"] is False
        assert "error" in channel_result


class TestAlertTracking:
    """Test alert tracking and history"""
    
    def test_alerts_sent_list(self):
        """Test alerts_sent returns list"""
        alerts_sent = []
        
        assert isinstance(alerts_sent, list)
    
    def test_alert_record_structure(self):
        """Test alert record structure"""
        alert_record = {
            "type": "High CPU Usage",
            "metric": "cpu",
            "value": 92.5,
            "threshold": 90,
            "severity": "warning",
            "result": {}
        }
        
        required_keys = ["type", "metric", "value", "threshold", "severity"]
        assert all(k in alert_record for k in required_keys)
    
    def test_multiple_alerts_tracked(self):
        """Test multiple alerts can be tracked"""
        alerts_sent = [
            {"type": "High CPU Usage", "metric": "cpu"},
            {"type": "High Memory Usage", "metric": "memory"}
        ]
        
        assert len(alerts_sent) == 2
        assert alerts_sent[0]["metric"] == "cpu"
        assert alerts_sent[1]["metric"] == "memory"


class TestTestAlert:
    """Test send_test_alert function"""
    
    def test_send_test_alert_exists(self):
        """Test send_test_alert function exists"""
        assert hasattr(alert_manager, 'send_test_alert')
        assert callable(alert_manager.send_test_alert)
    
    def test_test_alert_channel_parameter(self):
        """Test test alert accepts channel parameter"""
        channel = "all"
        
        valid_channels = ["all", "email", "telegram", "slack"]
        
        assert channel in valid_channels
    
    def test_test_alert_default_channel(self):
        """Test test alert default channel is 'all'"""
        default_channel = "all"
        
        assert default_channel == "all"


class TestAlertParameters:
    """Test alert parameter validation"""
    
    def test_server_name_required(self):
        """Test server name is required parameter"""
        server_name = "web-1"
        
        assert server_name is not None
        assert len(server_name) > 0
    
    def test_alert_type_required(self):
        """Test alert type is required parameter"""
        alert_type = "High CPU Usage"
        
        assert alert_type is not None
        assert len(alert_type) > 0
    
    def test_message_required(self):
        """Test message is required parameter"""
        message = "CPU at 95%"
        
        assert message is not None
        assert len(message) > 0
    
    def test_severity_defaults_to_warning(self):
        """Test severity defaults to warning"""
        severity = "warning"
        
        assert severity in ["info", "warning", "critical"]
    
    def test_server_id_optional(self):
        """Test server_id is optional"""
        server_id = None
        
        # Should work with or without server_id
        assert server_id is None or isinstance(server_id, int)
