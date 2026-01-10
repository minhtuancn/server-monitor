#!/usr/bin/env python3
"""
Slack Integration for Server Monitoring Alerts
Sends alerts via Slack Incoming Webhooks (no external deps; uses urllib)
"""

import json
import os
import sys
from urllib import request, error
from datetime import datetime

# Slack config file path
SLACK_CONFIG_FILE = "/opt/server-monitor-dev/data/slack_config.json"


def get_slack_config():
    """Load Slack configuration"""
    if not os.path.exists(SLACK_CONFIG_FILE):
        return None
    try:
        with open(SLACK_CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def save_slack_config(webhook_url, enabled=True):
    """Save Slack configuration"""
    config = {"webhook_url": webhook_url, "enabled": enabled, "updated_at": datetime.now().isoformat()}
    os.makedirs(os.path.dirname(SLACK_CONFIG_FILE), exist_ok=True)
    with open(SLACK_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    return {"success": True, "message": "Slack configuration saved"}


def test_slack_config(config=None):
    """Test Slack webhook by sending a test message"""
    if not config:
        config = get_slack_config()

    if not config:
        return {"success": False, "error": "No Slack configuration found"}

    webhook_url = config.get("webhook_url")

    if not webhook_url:
        return {"success": False, "error": "Webhook URL missing"}

    try:
        message = {
            "text": "✅ Server Monitor Test Message",
            "blocks": [
                {"type": "header", "text": {"type": "plain_text", "text": "✅ Server Monitor Test"}},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"This is a test notification from your *Multi-Server Monitor*.\n\n"
                        f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"If you received this, your Slack integration is working correctly!",
                    },
                },
            ],
        }

        return send_slack_message(webhook_url, message)
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_slack_message(webhook_url, payload):
    """Send a message to Slack via webhook"""
    # Security Note: Validate webhook_url is a proper Slack webhook
    # Slack webhooks should use HTTPS and start with hooks.slack.com
    # This includes both standard and Enterprise Grid webhooks
    if not webhook_url or not webhook_url.startswith("https://hooks.slack.com/"):
        return {
            "success": False,
            "error": "Invalid Slack webhook URL. Must be HTTPS and start with https://hooks.slack.com/",
        }

    data = json.dumps(payload).encode("utf-8")
    req = request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})

    try:
        # Security Note: URL validated above to ensure it's a legitimate Slack webhook
        with request.urlopen(req, timeout=10) as response:  # nosec B310
            if response.status == 200:
                return {"success": True, "message": "Slack message sent successfully"}
            else:
                return {"success": False, "error": f"HTTP {response.status}"}
    except error.HTTPError as e:
        return {"success": False, "error": f"HTTP {e.code}: {e.reason}"}
    except error.URLError as e:
        return {"success": False, "error": f"Network error: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_alert_slack(server_name, alert_type, message, severity="warning", server_id=None):
    """Send alert notification via Slack"""
    config = get_slack_config()

    if not config or not config.get("enabled"):
        return {"success": False, "error": "Slack alerts not configured or disabled"}

    # Severity color map
    color_map = {"critical": "#f56565", "warning": "#ed8936", "info": "#4299e1"}
    color = color_map.get(severity, "#ed8936")

    # Emoji map
    emoji_map = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}
    emoji = emoji_map.get(severity, "⚠️")

    # Format Slack message
    slack_message = {
        "text": f"{emoji} Server Alert: {server_name}",
        "attachments": [
            {
                "color": color,
                "fields": [
                    {"title": "Server", "value": server_name, "short": True},
                    {"title": "Severity", "value": severity.upper(), "short": True},
                    {"title": "Alert Type", "value": alert_type, "short": False},
                    {"title": "Message", "value": message, "short": False},
                    {"title": "Time", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "short": True},
                ],
                "footer": "Multi-Server Monitor v4.0",
            }
        ],
    }

    if server_id:
        slack_message["attachments"][0]["fields"].insert(
            1, {"title": "Server ID", "value": str(server_id), "short": True}
        )

    return send_slack_message(config["webhook_url"], slack_message)


if __name__ == "__main__":
    print("Slack Integration - Server Monitor v4.0")
    print("=" * 60)

    config = get_slack_config()
    if config:
        print(f"✓ Configuration found")
        print(f"  Webhook URL: {config['webhook_url'][:40]}...")
        print(f"  Status: {'Enabled' if config.get('enabled') else 'Disabled'}")
    else:
        print("✗ No configuration found")
        print("\nTo configure, use save_slack_config(webhook_url)")
