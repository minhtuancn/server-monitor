#!/usr/bin/env python3

"""
Email Alerts Module for Server Monitoring
Sends email notifications when alerts are triggered
"""

import smtplib
import json
import sys
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db

# Email configuration file
EMAIL_CONFIG_FILE = "/opt/server-monitor-dev/data/email_config.json"


def get_email_config():
    """Load email configuration"""
    if not os.path.exists(EMAIL_CONFIG_FILE):
        return None

    try:
        with open(EMAIL_CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return None


def save_email_config(
    smtp_host, smtp_port, smtp_user, smtp_password, from_email, to_emails, use_tls=True, enabled=True
):
    """Save email configuration"""
    config = {
        "smtp_host": smtp_host,
        "smtp_port": smtp_port,
        "smtp_user": smtp_user,
        "smtp_password": smtp_password,
        "from_email": from_email,
        "to_emails": to_emails if isinstance(to_emails, list) else [to_emails],
        "use_tls": use_tls,
        "enabled": enabled,
        "updated_at": datetime.now().isoformat(),
    }

    os.makedirs(os.path.dirname(EMAIL_CONFIG_FILE), exist_ok=True)

    with open(EMAIL_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

    return {"success": True, "message": "Email configuration saved"}


def test_email_config(config=None):
    """Test email configuration by sending a test email"""
    if not config:
        config = get_email_config()

    if not config:
        return {"success": False, "error": "No email configuration found"}

    try:
        # Create test message
        msg = MIMEMultipart()
        msg["From"] = config["from_email"]
        msg["To"] = ", ".join(config["to_emails"])
        msg["Subject"] = "Server Monitor - Test Email"

        body = """
        <html>
        <body>
            <h2>Server Monitor Alert System</h2>
            <p>This is a test email from your Server Monitor Dashboard.</p>
            <p>If you received this email, your email configuration is working correctly!</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                Sent from Multi-Server Monitor v4.0<br>
                Time: {time}
            </p>
        </body>
        </html>
        """.format(
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        msg.attach(MIMEText(body, "html"))

        # Connect to SMTP server
        if config["use_tls"]:
            server = smtplib.SMTP(config["smtp_host"], config["smtp_port"])
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(config["smtp_host"], config["smtp_port"])

        server.login(config["smtp_user"], config["smtp_password"])
        server.send_message(msg)
        server.quit()

        return {"success": True, "message": "Test email sent successfully"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def send_alert_email(server_name, alert_type, message, severity="warning", server_id=None):
    """Send alert email"""
    config = get_email_config()

    if not config or not config.get("enabled"):
        return {"success": False, "error": "Email alerts not configured or disabled"}

    try:
        # Determine color based on severity
        colors = {"critical": "#f56565", "warning": "#ed8936", "info": "#4299e1"}
        color = colors.get(severity, "#ed8936")

        # Create email message
        msg = MIMEMultipart()
        msg["From"] = config["from_email"]
        msg["To"] = ", ".join(config["to_emails"])
        msg["Subject"] = f"🚨 Server Alert: {server_name} - {alert_type}"

        # HTML body
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert-box {{
                    border-left: 4px solid {color};
                    background: #f7fafc;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .severity {{
                    color: {color};
                    font-weight: bold;
                    text-transform: uppercase;
                }}
                .details {{
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                }}
                .footer {{
                    color: #666;
                    font-size: 12px;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                }}
            </style>
        </head>
        <body>
            <h2>🚨 Server Alert Notification</h2>
            
            <div class="alert-box">
                <p class="severity">Severity: {severity}</p>
                <h3>{alert_type}</h3>
                <p>{message}</p>
            </div>
            
            <div class="details">
                <strong>Server:</strong> {server_name}<br>
                <strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                {f'<strong>Server ID:</strong> {server_id}<br>' if server_id else ''}
            </div>
            
            <p>Please check your server dashboard for more details.</p>
            
            <div class="footer">
                Sent from Multi-Server Monitor v4.0<br>
                This is an automated alert. Do not reply to this email.
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, "html"))

        # Connect and send
        if config["use_tls"]:
            server = smtplib.SMTP(config["smtp_host"], config["smtp_port"])
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(config["smtp_host"], config["smtp_port"])

        server.login(config["smtp_user"], config["smtp_password"])
        server.send_message(msg)
        server.quit()

        return {"success": True, "message": "Alert email sent"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def check_server_thresholds(server_id, metrics):
    """
    Check if server metrics exceed thresholds and create alerts
    Returns list of alerts that should be sent
    """
    alerts_to_send = []

    # Default thresholds
    thresholds = {"cpu": 90, "memory": 85, "disk": 90}  # CPU usage > 90%  # Memory usage > 85%  # Disk usage > 90%

    # Check CPU
    if metrics.get("cpu", 0) > thresholds["cpu"]:
        alerts_to_send.append(
            {
                "type": "High CPU Usage",
                "message": f"CPU usage is at {metrics['cpu']}% (threshold: {thresholds['cpu']}%)",
                "severity": "critical" if metrics["cpu"] > 95 else "warning",
            }
        )

    # Check Memory
    if metrics.get("memory", 0) > thresholds["memory"]:
        alerts_to_send.append(
            {
                "type": "High Memory Usage",
                "message": f"Memory usage is at {metrics['memory']}% (threshold: {thresholds['memory']}%)",
                "severity": "critical" if metrics["memory"] > 95 else "warning",
            }
        )

    # Check Disk
    if metrics.get("disk", 0) > thresholds["disk"]:
        alerts_to_send.append(
            {
                "type": "High Disk Usage",
                "message": f"Disk usage is at {metrics['disk']}% (threshold: {thresholds['disk']}%)",
                "severity": "critical" if metrics["disk"] > 95 else "warning",
            }
        )

    return alerts_to_send


if __name__ == "__main__":
    print("Email Alerts Module - Server Monitor v4.0")
    print("=" * 60)

    # Test configuration
    print("\nTesting email configuration...")

    config = get_email_config()
    if config:
        print(f"✓ Configuration found")
        print(f"  SMTP: {config['smtp_host']}:{config['smtp_port']}")
        print(f"  From: {config['from_email']}")
        print(f"  To: {', '.join(config['to_emails'])}")
        print(f"  Status: {'Enabled' if config.get('enabled') else 'Disabled'}")
    else:
        print("✗ No configuration found")
        print("\nExample configuration:")
        print(
            """
        result = save_email_config(
            smtp_host='smtp.gmail.com',
            smtp_port=587,
            smtp_user='your-email@gmail.com',
            smtp_password='your-app-password',
            from_email='your-email@gmail.com',
            to_emails=['admin@example.com'],
            use_tls=True,
            enabled=True
        )
        """
        )
