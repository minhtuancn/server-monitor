#!/usr/bin/env python3

"""
Alert Manager - Centralized Alert Dispatcher
Routes alerts to all enabled notification channels (Email, Telegram, Slack)
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import email_alerts as email
import telegram_bot
import slack_integration
import database as db
from datetime import datetime


# Default alert thresholds
DEFAULT_THRESHOLDS = {
    'cpu': 90,      # CPU usage > 90%
    'memory': 85,   # Memory usage > 85%
    'disk': 90      # Disk usage > 90%
}


def get_enabled_channels():
    """Get list of enabled notification channels"""
    channels = {}
    
    # Check Email
    email_config = email.get_email_config()
    channels['email'] = email_config and email_config.get('enabled', False)
    
    # Check Telegram
    telegram_config = telegram_bot.get_telegram_config()
    channels['telegram'] = telegram_config and telegram_config.get('enabled', False)
    
    # Check Slack
    slack_config = slack_integration.get_slack_config()
    channels['slack'] = slack_config and slack_config.get('enabled', False)
    
    return channels


def send_alert(server_name, alert_type, message, severity='warning', server_id=None):
    """
    Send alert to all enabled notification channels
    
    Args:
        server_name: Name of the server triggering the alert
        alert_type: Type of alert (e.g., 'High CPU Usage', 'High Memory Usage')
        message: Alert message details
        severity: 'info', 'warning', or 'critical'
        server_id: Server ID for database tracking
    
    Returns:
        dict: Results from each channel
    """
    results = {
        'email': {'sent': False, 'enabled': False},
        'telegram': {'sent': False, 'enabled': False},
        'slack': {'sent': False, 'enabled': False}
    }
    
    # Get enabled channels
    enabled_channels = get_enabled_channels()
    
    # Send to Email
    if enabled_channels.get('email'):
        results['email']['enabled'] = True
        try:
            email_result = email.send_alert_email(
                server_name=server_name,
                alert_type=alert_type,
                message=message,
                severity=severity,
                server_id=server_id
            )
            results['email']['sent'] = email_result.get('success', False)
            results['email']['response'] = email_result
        except Exception as e:
            results['email']['error'] = str(e)
    
    # Send to Telegram
    if enabled_channels.get('telegram'):
        results['telegram']['enabled'] = True
        try:
            telegram_result = telegram_bot.send_alert_telegram(
                server_name=server_name,
                alert_type=alert_type,
                message=message,
                severity=severity,
                server_id=server_id
            )
            results['telegram']['sent'] = telegram_result.get('success', False)
            results['telegram']['response'] = telegram_result
        except Exception as e:
            results['telegram']['error'] = str(e)
    
    # Send to Slack
    if enabled_channels.get('slack'):
        results['slack']['enabled'] = True
        try:
            slack_result = slack_integration.send_alert_slack(
                server_name=server_name,
                alert_type=alert_type,
                message=message,
                severity=severity,
                server_id=server_id
            )
            results['slack']['sent'] = slack_result.get('success', False)
            results['slack']['response'] = slack_result
        except Exception as e:
            results['slack']['error'] = str(e)
    
    # Create alert record in database
    if server_id:
        try:
            alert_id = db.create_alert(
                server_id=server_id,
                alert_type=alert_type,
                message=message,
                severity=severity
            )
            results['alert_id'] = alert_id
        except Exception as e:
            results['db_error'] = str(e)
    
    return results


def check_server_thresholds(server_id, server_name, metrics, thresholds=None):
    """
    Check if server metrics exceed thresholds and send alerts
    
    Args:
        server_id: Server ID
        server_name: Server name for alert messages
        metrics: Dict with 'cpu', 'memory', 'disk' percentage values
        thresholds: Optional custom thresholds (uses defaults if None)
    
    Returns:
        list: List of alerts that were triggered and sent
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS
    
    alerts_sent = []
    
    # Check CPU
    cpu_usage = metrics.get('cpu', 0)
    if cpu_usage > thresholds['cpu']:
        severity = 'critical' if cpu_usage > 95 else 'warning'
        alert_type = 'High CPU Usage'
        message = f"CPU usage is at {cpu_usage:.1f}% (threshold: {thresholds['cpu']}%)"
        
        result = send_alert(
            server_name=server_name,
            alert_type=alert_type,
            message=message,
            severity=severity,
            server_id=server_id
        )
        alerts_sent.append({
            'type': alert_type,
            'metric': 'cpu',
            'value': cpu_usage,
            'threshold': thresholds['cpu'],
            'severity': severity,
            'result': result
        })
    
    # Check Memory
    memory_usage = metrics.get('memory', 0)
    if memory_usage > thresholds['memory']:
        severity = 'critical' if memory_usage > 95 else 'warning'
        alert_type = 'High Memory Usage'
        message = f"Memory usage is at {memory_usage:.1f}% (threshold: {thresholds['memory']}%)"
        
        result = send_alert(
            server_name=server_name,
            alert_type=alert_type,
            message=message,
            severity=severity,
            server_id=server_id
        )
        alerts_sent.append({
            'type': alert_type,
            'metric': 'memory',
            'value': memory_usage,
            'threshold': thresholds['memory'],
            'severity': severity,
            'result': result
        })
    
    # Check Disk
    disk_usage = metrics.get('disk', 0)
    if disk_usage > thresholds['disk']:
        severity = 'critical' if disk_usage > 95 else 'warning'
        alert_type = 'High Disk Usage'
        message = f"Disk usage is at {disk_usage:.1f}% (threshold: {thresholds['disk']}%)"
        
        result = send_alert(
            server_name=server_name,
            alert_type=alert_type,
            message=message,
            severity=severity,
            server_id=server_id
        )
        alerts_sent.append({
            'type': alert_type,
            'metric': 'disk',
            'value': disk_usage,
            'threshold': thresholds['disk'],
            'severity': severity,
            'result': result
        })
    
    return alerts_sent


def send_test_alert(channel='all'):
    """
    Send a test alert to verify notification configuration
    
    Args:
        channel: 'email', 'telegram', 'slack', or 'all'
    
    Returns:
        dict: Results from each channel
    """
    server_name = 'Test Server'
    alert_type = 'Test Alert'
    message = 'This is a test notification from Server Monitor Dashboard'
    severity = 'info'
    
    results = {}
    
    if channel in ['email', 'all']:
        try:
            results['email'] = email.send_alert_email(
                server_name=server_name,
                alert_type=alert_type,
                message=message,
                severity=severity
            )
        except Exception as e:
            results['email'] = {'success': False, 'error': str(e)}
    
    if channel in ['telegram', 'all']:
        try:
            results['telegram'] = telegram_bot.send_alert_telegram(
                server_name=server_name,
                alert_type=alert_type,
                message=message,
                severity=severity
            )
        except Exception as e:
            results['telegram'] = {'success': False, 'error': str(e)}
    
    if channel in ['slack', 'all']:
        try:
            results['slack'] = slack_integration.send_alert_slack(
                server_name=server_name,
                alert_type=alert_type,
                message=message,
                severity=severity
            )
        except Exception as e:
            results['slack'] = {'success': False, 'error': str(e)}
    
    return results


if __name__ == '__main__':
    print("Alert Manager - Server Monitor v4.0")
    print("=" * 60)
    
    # Show enabled channels
    print("\n📡 Enabled Notification Channels:")
    channels = get_enabled_channels()
    for channel, enabled in channels.items():
        status = "✅ Enabled" if enabled else "❌ Disabled"
        print(f"  {channel.capitalize()}: {status}")
    
    # Test alert
    print("\n🔔 Sending test alert...")
    results = send_test_alert()
    
    print("\n📊 Test Results:")
    for channel, result in results.items():
        success = result.get('success', False)
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {channel.capitalize()}: {status}")
        if not success and 'error' in result:
            print(f"    Error: {result['error']}")
