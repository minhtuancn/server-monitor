#!/usr/bin/env python3
"""
Telegram Bot Integration for Server Monitoring Alerts
Sends alerts via Telegram Bot API (no external deps; uses urllib)
"""

import json
import os
import sys
from urllib import request, error
from datetime import datetime
from pathlib import Path

# Telegram config file path - use relative path from project root
_project_root = Path(__file__).parent.parent
_default_config_path = str(_project_root / 'data' / 'telegram_config.json')
TELEGRAM_CONFIG_FILE = os.environ.get('TELEGRAM_CONFIG_FILE', _default_config_path)


def get_telegram_config():
    """Load Telegram configuration"""
    if not os.path.exists(TELEGRAM_CONFIG_FILE):
        return None
    try:
        with open(TELEGRAM_CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def save_telegram_config(bot_token, chat_id, enabled=True):
    """Save Telegram configuration"""
    config = {
        'bot_token': bot_token,
        'chat_id': chat_id,
        'enabled': enabled,
        'updated_at': datetime.now().isoformat()
    }
    os.makedirs(os.path.dirname(TELEGRAM_CONFIG_FILE), exist_ok=True)
    with open(TELEGRAM_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    return {'success': True, 'message': 'Telegram configuration saved'}


def test_telegram_config(config=None):
    """Test Telegram bot configuration by sending a test message"""
    if not config:
        config = get_telegram_config()
    
    if not config:
        return {'success': False, 'error': 'No Telegram configuration found'}
    
    bot_token = config.get('bot_token')
    chat_id = config.get('chat_id')
    
    if not bot_token or not chat_id:
        return {'success': False, 'error': 'Bot token or chat ID missing'}
    
    try:
        message = f"✅ Server Monitor Test Message\n\n" \
                  f"This is a test notification from your Multi-Server Monitor.\n" \
                  f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n" \
                  f"If you received this, your Telegram integration is working correctly!"
        
        return send_telegram_message(bot_token, chat_id, message)
    except Exception as e:
        return {'success': False, 'error': str(e)}


def send_telegram_message(bot_token, chat_id, message, parse_mode='HTML'):
    """Send a message via Telegram Bot API"""
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': parse_mode
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('ok'):
                return {'success': True, 'message': 'Telegram message sent successfully'}
            else:
                return {'success': False, 'error': result.get('description', 'Unknown error')}
    except error.HTTPError as e:
        return {'success': False, 'error': f'HTTP {e.code}: {e.reason}'}
    except error.URLError as e:
        return {'success': False, 'error': f'Network error: {e.reason}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def send_alert_telegram(server_name, alert_type, message, severity='warning', server_id=None):
    """Send alert notification via Telegram"""
    config = get_telegram_config()
    
    if not config or not config.get('enabled'):
        return {'success': False, 'error': 'Telegram alerts not configured or disabled'}
    
    # Severity emoji map
    emoji_map = {
        'critical': '🚨',
        'warning': '⚠️',
        'info': 'ℹ️'
    }
    emoji = emoji_map.get(severity, '⚠️')
    
    # Format message
    telegram_message = f"{emoji} <b>Server Alert</b>\n\n" \
                       f"<b>Server:</b> {server_name}\n" \
                       f"<b>Alert:</b> {alert_type}\n" \
                       f"<b>Severity:</b> {severity.upper()}\n" \
                       f"<b>Message:</b> {message}\n" \
                       f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    if server_id:
        telegram_message += f"<b>Server ID:</b> {server_id}\n"
    
    telegram_message += "\n<i>Sent from Multi-Server Monitor v4.0</i>"
    
    return send_telegram_message(config['bot_token'], config['chat_id'], telegram_message)


if __name__ == '__main__':
    print("Telegram Bot Integration - Server Monitor v4.0")
    print("=" * 60)
    
    config = get_telegram_config()
    if config:
        print(f"✓ Configuration found")
        print(f"  Bot Token: {config['bot_token'][:15]}...{config['bot_token'][-5:]}")
        print(f"  Chat ID: {config['chat_id']}")
        print(f"  Status: {'Enabled' if config.get('enabled') else 'Disabled'}")
    else:
        print("✗ No configuration found")
        print("\nTo configure, use save_telegram_config(bot_token, chat_id)")

