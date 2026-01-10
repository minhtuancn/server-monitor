#!/usr/bin/env python3

"""
Central Multi-Server Monitoring API v3
Manages multiple remote servers via SSH
Enterprise Edition - With User Management & Settings
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys
import os
import time
import signal
import sqlite3
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
import ssh_manager as ssh
import email_alerts as email
import alert_manager
import security
from user_management import get_user_manager
from settings_manager import get_settings_manager
import ssh_key_manager
import inventory_collector
from ssh_key_manager import get_decrypted_key
import task_runner
from observability import StructuredLogger, RequestContext, HealthCheck, get_metrics_collector
import startup_validation
from task_policy import get_task_policy
from audit_cleanup import get_audit_cleanup_scheduler
from task_recovery import run_startup_recovery
from plugin_system import get_plugin_manager
from event_model import EventTypes, create_event, EventSeverity
import webhook_dispatcher
from cache_helper import get_cache
from rate_limiter import get_rate_limiter, check_endpoint_rate_limit

PORT = 9083  # Different port for central server

# Initialize structured logger
logger = StructuredLogger("central_api")
metrics = get_metrics_collector()

# Initialize task policy
task_policy = get_task_policy()

# Initialize plugin manager
plugin_manager = get_plugin_manager()

# Initialize cache and rate limiter
cache = get_cache()
rate_limiter = get_rate_limiter()

# Constants for task validation
TASK_COMMAND_MAX_LENGTH = int(os.environ.get("TASK_COMMAND_MAX_LENGTH", "10000"))
TASK_COMMAND_PREVIEW_LENGTH = 100

# Initialize managers
user_mgr = get_user_manager()
settings_mgr = get_settings_manager()

# Global server instance for graceful shutdown
http_server = None

# ==================== HELPER FUNCTIONS ====================


def dispatch_audit_event(
    user_id,
    action,
    target_type,
    target_id,
    meta=None,
    ip=None,
    user_agent=None,
    username=None,
    server_id=None,
    server_name=None,
    severity=EventSeverity.INFO,
):
    """
    Helper to add audit log and dispatch event to plugin system

    This replaces direct calls to db.add_audit_log() to ensure events
    are propagated to plugins.
    """
    # Add to audit logs
    result = db.add_audit_log(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        meta=meta,
        ip=ip,
        user_agent=user_agent,
    )

    # Create and dispatch event to plugins
    event = create_event(
        event_type=action.replace("_", "."),  # Convert action to event_type
        user_id=user_id,
        username=username,
        server_id=server_id,
        server_name=server_name,
        target_type=target_type,
        target_id=str(target_id),
        meta=meta or {},
        ip=ip,
        user_agent=user_agent,
        severity=severity,
    )

    # Dispatch to plugin system
    plugin_manager.dispatch_event(event)

    # Dispatch to managed webhooks (DB-backed)
    # This is fail-safe - errors won't break the main request
    try:
        webhook_dispatcher.dispatch_to_webhooks(event)
    except Exception as e:
        logger.error("Webhook dispatcher error", event_id=event.event_id, error=str(e))

    return result


def get_server_with_auth(server_id):
    """Get server details with decrypted password for SSH"""
    server = db.get_server(server_id, decrypt_password=True)
    if not server:
        return None
    return server


def verify_auth_token(handler):
    """Verify authentication token from Authorization header (JWT or old format)"""
    auth_header = handler.headers.get("Authorization", "")

    # Allow public endpoints without auth (read-only)
    public_endpoints = ["/api/stats/overview", "/api/servers"]
    if handler.path in public_endpoints and handler.command == "GET":
        return {"valid": True, "role": "public"}

    # Check for token
    if not auth_header.startswith("Bearer "):
        return {"valid": False, "error": "No authentication token provided"}

    token = auth_header.replace("Bearer ", "").strip()

    # Try JWT token first
    user_data = security.AuthMiddleware.decode_token(token)
    if user_data:
        return {
            "valid": True,
            "user_id": user_data.get("user_id"),
            "username": user_data.get("username"),
            "role": user_data.get("role", "user"),
            "permissions": user_data.get("permissions", []),
        }

    # Fallback to old session token for backward compatibility
    result = db.verify_session(token)
    return result


class CentralAPIHandler(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        # Initialize request tracking
        self.request_id = None
        self.request_start_time = None
        super().__init__(*args, **kwargs)

    def _set_headers(self, status=200, extra_headers=None):
        self.send_response(status)
        self.send_header("Content-type", "application/json")

        # Always apply security headers (CORS + Security Headers)
        origin = self.headers.get("Origin", "")
        cors_headers = security.CORS.get_cors_headers(origin)
        sec_headers = security.SecurityHeaders.get_security_headers()

        for key, value in {**cors_headers, **sec_headers}.items():
            self.send_header(key, value)

        # Add request correlation headers
        if self.request_id:
            self.send_header("X-Request-Id", self.request_id)

        # Add any extra headers (will override if keys conflict)
        if extra_headers:
            for key, value in extra_headers.items():
                # Skip if already set by security headers to avoid duplicates
                if key not in cors_headers and key not in sec_headers:
                    self.send_header(key, value)

        self.end_headers()

    def _start_request(self):
        """Initialize request tracking"""
        self.request_start_time = time.time()
        self.request_id = RequestContext.get_or_generate_request_id(self.headers)

    def _finish_request(self, status_code: int, user_id: str = None):
        """Log request completion"""
        if self.request_start_time:
            latency_ms = (time.time() - self.request_start_time) * 1000

            # Get client IP
            ip_address = self.client_address[0] if self.client_address else None

            # Get user agent
            user_agent = self.headers.get("User-Agent")

            # Log the request
            logger.request(
                method=self.command,
                path=self.path,
                status_code=status_code,
                latency_ms=latency_ms,
                request_id=self.request_id,
                user_id=user_id,
                user_agent=user_agent,
                ip_address=ip_address,
            )

            # Record metrics
            metrics.record_request(self.path, latency_ms)

    def do_OPTIONS(self):
        self._start_request()

        # Apply security middleware
        sec_result = security.apply_security_middleware(self, "OPTIONS")
        if sec_result["block"]:
            self._set_headers(sec_result["status"], sec_result.get("headers"))
            self.wfile.write(json.dumps(sec_result["body"]).encode())
            self._finish_request(sec_result["status"])
            return

        self._set_headers(200, sec_result.get("headers"))
        self._finish_request(200)

    def _read_body(self):
        """Read and parse POST body"""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}

        body = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(body)
        except:
            return {}

    def do_GET(self):
        self._start_request()

        # Apply security middleware
        sec_result = security.apply_security_middleware(self, "GET")
        if sec_result["block"]:
            self._set_headers(sec_result["status"], sec_result.get("headers"))
            self.wfile.write(json.dumps(sec_result["body"]).encode())
            self._finish_request(sec_result["status"])
            return

        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # ==================== SETUP (PUBLIC) ====================
        if path == "/api/setup/status":
            # Public endpoint: check if initial admin setup is required
            try:
                users = user_mgr.get_all_users()
                needs_setup = len(users) == 0
                self._set_headers()
                self.wfile.write(json.dumps({"needs_setup": needs_setup}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        # ==================== OBSERVABILITY ENDPOINTS ====================

        if path == "/api/health":
            # Liveness check - is the process running?
            health_status = HealthCheck.liveness()
            self._set_headers()
            self.wfile.write(json.dumps(health_status).encode())
            self._finish_request(200)
            return

        elif path == "/api/ready":
            # Readiness check - is the service ready to handle requests?
            readiness_status = HealthCheck.readiness()
            status_code = 200 if readiness_status["status"] == "ready" else 503
            self._set_headers(status_code)
            self.wfile.write(json.dumps(readiness_status).encode())
            self._finish_request(status_code)
            return

        elif path == "/api/metrics":
            # Metrics endpoint (admin only or localhost)
            auth_result = verify_auth_token(self)

            # Allow access from localhost without auth
            client_ip = self.client_address[0] if self.client_address else None
            is_localhost = client_ip in ["127.0.0.1", "::1", "localhost"]

            if not is_localhost:
                if not auth_result.get("valid"):
                    self._set_headers(401)
                    self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                    self._finish_request(401)
                    return

                if auth_result.get("role") not in ["admin"]:
                    self._set_headers(403)
                    self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                    self._finish_request(403)
                    return

            # Update metrics from task_runner if available
            try:
                metrics.tasks_running = len(task_runner.running_tasks)
                metrics.tasks_queued = task_runner.task_queue.qsize()
            except:
                pass

            # Add cache stats
            try:
                cache_stats = cache.get_stats()
                metrics.cache_hits = cache_stats["hits"]
                metrics.cache_misses = cache_stats["misses"]
                metrics.cache_hit_rate = cache_stats["hit_rate_percent"]
                metrics.cache_entries = cache_stats["entries"]
            except:
                pass

            # Add active terminal sessions
            try:
                metrics.active_terminal_sessions = db.get_active_terminal_sessions_count()
            except:
                pass

            # Add webhook delivery stats
            try:
                webhook_stats = db.get_webhook_delivery_stats()
                metrics.webhook_deliveries_success = webhook_stats.get("success", 0)
                metrics.webhook_deliveries_failed = webhook_stats.get("failed", 0)
            except:
                pass

            # Return metrics in requested format
            accept_header = self.headers.get("Accept", "")
            if "text/plain" in accept_header or "prometheus" in accept_header:
                # Prometheus format
                prometheus_metrics = metrics.to_prometheus()
                self.send_response(200)
                self.send_header("Content-type", "text/plain; version=0.0.4")
                if self.request_id:
                    self.send_header("X-Request-Id", self.request_id)
                self.end_headers()
                self.wfile.write(prometheus_metrics.encode())
                self._finish_request(200)
            else:
                # JSON format
                json_metrics = metrics.get_metrics()
                self._set_headers()
                self.wfile.write(json.dumps(json_metrics).encode())
                self._finish_request(200)
            return

        # ==================== AUTHENTICATION ====================

        if path == "/api/auth/verify":
            # Verify current session
            auth_result = verify_auth_token(self)

            if auth_result["valid"]:
                self._set_headers()
                self.wfile.write(
                    json.dumps(
                        {"valid": True, "username": auth_result.get("username"), "role": auth_result.get("role")}
                    ).encode()
                )
                self._finish_request(200, user_id=str(auth_result.get("user_id")))
            else:
                self._set_headers(401)
                self.wfile.write(json.dumps({"valid": False, "error": auth_result.get("error")}).encode())
                self._finish_request(401)
            return

        # ==================== USER MANAGEMENT ====================

        elif path == "/api/users/me":
            # Get current user's info
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            user_id = auth_result.get("user_id")
            user = user_mgr.get_user(user_id)
            if user:
                self._set_headers()
                self.wfile.write(json.dumps(user).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "User not found"}).encode())
            return

        elif path == "/api/users":
            # Get all users (admin only)
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            users = user_mgr.get_all_users()
            self._set_headers()
            self.wfile.write(json.dumps(users).encode())
            return

        elif path.startswith("/api/users/") and path != "/api/users":
            # Get single user
            try:
                user_id = int(path.split("/")[-1])
                auth_result = verify_auth_token(self)

                if not auth_result.get("valid"):
                    self._set_headers(401)
                    self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                    return

                # Users can see their own data, admins can see anyone
                if auth_result.get("role") != "admin" and auth_result.get("user_id") != user_id:
                    self._set_headers(403)
                    self.wfile.write(json.dumps({"error": "Access denied"}).encode())
                    return

                user = user_mgr.get_user(user_id)
                if user:
                    self._set_headers()
                    self.wfile.write(json.dumps(user).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "User not found"}).encode())
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid user ID"}).encode())
            return

        elif path == "/api/roles":
            # Get available roles
            self._set_headers()
            roles = user_mgr.get_roles()
            self.wfile.write(json.dumps(roles).encode())
            return

        # ==================== SYSTEM SETTINGS ====================

        elif path == "/api/settings":
            # Get all system settings
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            settings = settings_mgr.get_all_settings()
            self._set_headers()
            self.wfile.write(json.dumps(settings).encode())
            return

        elif path.startswith("/api/settings/") and path != "/api/settings":
            # Get single setting
            key = path.split("/")[-1]
            value = settings_mgr.get_setting(key)

            if value is not None:
                self._set_headers()
                self.wfile.write(json.dumps({"key": key, "value": value}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Setting not found"}).encode())
            return

        elif path == "/api/settings/options":
            # Get available options for settings
            options = settings_mgr.get_options()
            self._set_headers()
            self.wfile.write(json.dumps(options).encode())
            return

        # ==================== GROUPS MANAGEMENT ====================

        elif path == "/api/groups":
            # Get all groups (optionally filtered by type)
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            query_params = parse_qs(urlparse(self.path).query)
            group_type = query_params.get("type", [None])[0]

            conn = db.get_connection()
            cursor = conn.cursor()

            if group_type:
                cursor.execute(
                    """
                    SELECT g.*, COUNT(gm.id) as item_count
                    FROM groups g
                    LEFT JOIN group_memberships gm ON g.id = gm.group_id
                    WHERE g.type = ?
                    GROUP BY g.id
                    ORDER BY g.name
                """,
                    (group_type,),
                )
            else:
                cursor.execute(
                    """
                    SELECT g.*, COUNT(gm.id) as item_count
                    FROM groups g
                    LEFT JOIN group_memberships gm ON g.id = gm.group_id
                    GROUP BY g.id
                    ORDER BY g.type, g.name
                """
                )

            groups = []
            for row in cursor.fetchall():
                groups.append(
                    {
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "type": row[3],
                        "color": row[4],
                        "created_by": row[5],
                        "created_at": row[6],
                        "updated_at": row[7],
                        "item_count": row[8] if len(row) > 8 else 0,
                    }
                )

            conn.close()
            self._set_headers()
            self.wfile.write(json.dumps(groups).encode())
            return

        elif path.startswith("/api/groups/") and path.count("/") == 3:
            # Get single group
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            try:
                group_id = int(path.split("/")[-1])
                conn = db.get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT g.*, COUNT(gm.id) as item_count
                    FROM groups g
                    LEFT JOIN group_memberships gm ON g.id = gm.group_id
                    WHERE g.id = ?
                    GROUP BY g.id
                """,
                    (group_id,),
                )

                row = cursor.fetchone()
                if row:
                    group = {
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "type": row[3],
                        "color": row[4],
                        "created_by": row[5],
                        "created_at": row[6],
                        "updated_at": row[7],
                        "item_count": row[8] if len(row) > 8 else 0,
                    }
                    conn.close()
                    self._set_headers()
                    self.wfile.write(json.dumps(group).encode())
                else:
                    conn.close()
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Group not found"}).encode())
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid group ID"}).encode())
            return

        # ==================== DOMAIN SETTINGS ====================
        elif path == "/api/domain/settings":
            # Get domain configuration settings (admin only)
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            settings = db.get_domain_settings()
            self._set_headers()
            self.wfile.write(json.dumps(settings).encode())
            return

        # ==================== DATABASE MANAGEMENT ====================
        elif path == "/api/database/health":
            # Get database health status (admin only)
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            from database_manager import db_manager

            health = db_manager.check_health()
            self._set_headers()
            self.wfile.write(json.dumps(health).encode())
            return

        elif path == "/api/database/backups":
            # List all backups (admin only)
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            from database_manager import db_manager

            backups = db_manager.list_backups()
            self._set_headers()
            self.wfile.write(json.dumps({"backups": backups, "count": len(backups)}).encode())
            return

        elif path == "/api/database/storage":
            # Get storage statistics (admin only)
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            from database_manager import db_manager

            storage = db_manager.get_storage_stats()
            self._set_headers()
            self.wfile.write(json.dumps(storage).encode())
            return

        # ==================== NOTIFICATION CHANNELS ====================
        elif path == "/api/notifications/channels":
            # Get notification channels status (admin only)
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            try:
                email_cfg = email.get_email_config() or {}
            except Exception:
                email_cfg = {}

            # Import Telegram and Slack modules
            try:
                from telegram_bot import get_telegram_config

                telegram_cfg = get_telegram_config() or {}
            except Exception:
                telegram_cfg = {}

            try:
                from slack_integration import get_slack_config

                slack_cfg = get_slack_config() or {}
            except Exception:
                slack_cfg = {}

            settings = settings_mgr.get_all_settings()
            resp = {
                "email": {
                    "enabled": bool(settings.get("smtp_enabled", False)),
                    "configured": bool(email_cfg),
                    "to": (email_cfg.get("to_emails") if email_cfg else None),
                },
                "telegram": {
                    "enabled": bool(settings.get("telegram_enabled", False)),
                    "configured": bool(telegram_cfg.get("bot_token") and telegram_cfg.get("chat_id")),
                },
                "slack": {
                    "enabled": bool(settings.get("slack_enabled", False)),
                    "configured": bool(slack_cfg.get("webhook_url")),
                },
            }
            self._set_headers()
            self.wfile.write(json.dumps(resp).encode())
            return

        elif path == "/api/telegram/config":
            # Get Telegram config (admin only)
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            try:
                from telegram_bot import get_telegram_config

                cfg = get_telegram_config() or {}
                self._set_headers()
                self.wfile.write(json.dumps(cfg).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        elif path == "/api/slack/config":
            # Get Slack config (admin only)
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            try:
                from slack_integration import get_slack_config

                cfg = get_slack_config() or {}
                self._set_headers()
                self.wfile.write(json.dumps(cfg).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        # ==================== SERVER MANAGEMENT ====================

        if path == "/api/servers":
            # Get all servers (public read allowed) with caching (TTL: 10s)
            auth_result = verify_auth_token(self)

            # Create cache key based on auth status
            cache_key = f"servers:list:{auth_result.get('valid', False)}"

            # Try to get from cache
            cached_servers = cache.get(cache_key)
            if cached_servers is not None:
                self._set_headers()
                self.wfile.write(json.dumps(cached_servers).encode())
                return

            # Fetch from database
            servers = db.get_servers()

            # Hide sensitive data for non-authenticated users
            if not auth_result.get("valid") or auth_result.get("role") == "public":
                for server in servers:
                    server.pop("ssh_key_path", None)
                    server.pop("ssh_password", None)

            # Cache for 10 seconds
            cache.set(cache_key, servers, ttl=10)

            self._set_headers()
            self.wfile.write(json.dumps(servers).encode())

        elif path.startswith("/api/servers/"):
            # Check for sub-paths (notes, inventory, etc.)
            parts = [p for p in path.split("/") if p]

            if len(parts) >= 5 and parts[3] == "inventory" and parts[4] == "latest":
                # GET /api/servers/:id/inventory/latest
                # Get latest inventory for a server (all authenticated roles)
                auth_result = verify_auth_token(self)
                if not auth_result.get("valid"):
                    self._set_headers(401)
                    self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                    return

                try:
                    server_id = int(parts[2])
                    inventory = db.get_server_inventory_latest(server_id)

                    if inventory:
                        self._set_headers()
                        self.wfile.write(json.dumps(inventory).encode())
                    else:
                        self._set_headers(404)
                        self.wfile.write(
                            json.dumps({"error": "No inventory data found. Try refreshing inventory first."}).encode()
                        )
                except ValueError:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())
                return

            if len(parts) >= 4 and parts[3] == "notes":
                # GET /api/servers/:id/notes
                # Check authentication
                auth_result = verify_auth_token(self)
                if not auth_result.get("valid"):
                    self._set_headers(401)
                    self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                    return

                try:
                    server_id = int(parts[2])
                    notes = db.get_server_notes(server_id)
                    self._set_headers()
                    self.wfile.write(json.dumps(notes).encode())
                except ValueError:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())
                return

            # Get single server
            server_id = path.split("/")[-1]
            try:
                server_id = int(server_id)
                server = db.get_server(server_id)

                if server:
                    self._set_headers()
                    self.wfile.write(json.dumps(server).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Server not found"}).encode())
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())

        elif path == "/api/stats/overview":
            # Get stats overview of all servers with caching (TTL: 30s)
            cache_key = "stats:overview"

            # Try to get from cache
            cached_stats = cache.get(cache_key)
            if cached_stats is not None:
                self._set_headers()
                self.wfile.write(json.dumps(cached_stats).encode())
                return

            # Compute stats
            stats = db.get_server_stats()

            # Cache for 30 seconds
            cache.set(cache_key, stats, ttl=30)

            self._set_headers()
            self.wfile.write(json.dumps(stats).encode())

        # ==================== EXPORT ENDPOINTS ====================

        elif path == "/api/export/servers/csv":
            # Export servers to CSV
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            try:
                csv_data = db.export_servers_csv()
                self.send_response(200)
                self.send_header("Content-type", "text/csv")
                self.send_header(
                    "Content-Disposition",
                    f'attachment; filename="servers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"',
                )
                self.end_headers()
                self.wfile.write(csv_data.encode("utf-8"))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif path == "/api/export/servers/json":
            # Export servers to JSON
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            try:
                json_data = db.export_servers_json()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header(
                    "Content-Disposition",
                    f'attachment; filename="servers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"',
                )
                self.end_headers()
                self.wfile.write(json_data.encode("utf-8"))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif path.startswith("/api/export/history/"):
            # Export monitoring history
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            # Parse format and parameters
            parts = path.split("/")
            export_format = parts[-1]  # csv or json

            # Get query parameters
            params = parse_qs(parsed.query)
            server_id = params.get("server_id", [None])[0]
            start_date = params.get("start_date", [None])[0]
            end_date = params.get("end_date", [None])[0]

            try:
                if export_format == "csv":
                    csv_data = db.export_monitoring_history_csv(server_id, start_date, end_date)
                    self.send_response(200)
                    self.send_header("Content-type", "text/csv")
                    self.send_header(
                        "Content-Disposition",
                        f'attachment; filename="history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"',
                    )
                    self.end_headers()
                    self.wfile.write(csv_data.encode("utf-8"))
                elif export_format == "json":
                    json_data = db.export_monitoring_history_json(server_id, start_date, end_date)
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header(
                        "Content-Disposition",
                        f'attachment; filename="history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"',
                    )
                    self.end_headers()
                    self.wfile.write(json_data.encode("utf-8"))
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Invalid format. Use csv or json"}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif path == "/api/export/alerts/csv":
            # Export alerts to CSV
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            # Get query parameters
            params = parse_qs(parsed.query)
            server_id = params.get("server_id", [None])[0]
            is_read = params.get("is_read", [None])[0]

            try:
                csv_data = db.export_alerts_csv(server_id, is_read)
                self.send_response(200)
                self.send_header("Content-type", "text/csv")
                self.send_header(
                    "Content-Disposition",
                    f'attachment; filename="alerts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"',
                )
                self.end_headers()
                self.wfile.write(csv_data.encode("utf-8"))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        # ==================== REMOTE SERVER DATA ====================

        elif path.startswith("/api/remote/stats/"):
            # Get monitoring data from remote server
            server_id = path.split("/")[-1]

            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)

                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Server not found"}).encode())
                    return

                # Get data from remote agent
                result = ssh.get_remote_agent_data(
                    host=server["host"],
                    port=server["port"],
                    username=server["username"],
                    agent_port=server["agent_port"],
                    endpoint="/api/all",
                    ssh_key_path=server["ssh_key_path"],
                    password=server.get("ssh_password"),
                )

                if result["success"]:
                    # Update server status
                    db.update_server_status(server_id, "online")

                    # Add server info to response
                    data = result["data"]
                    data["server_info"] = {
                        "id": server["id"],
                        "name": server["name"],
                        "host": server["host"],
                        "description": server["description"],
                    }

                    # Check thresholds and send alerts if needed
                    try:
                        system_metrics = data.get("system", {})
                        cpu_usage = system_metrics.get("cpu", {}).get("usage", 0)
                        memory_percent = system_metrics.get("memory", {}).get("percent", 0)
                        disk_percent = system_metrics.get("disk", {}).get("percent", 0)

                        server_metrics = {"cpu": cpu_usage, "memory": memory_percent, "disk": disk_percent}

                        # Check and send alerts if thresholds exceeded
                        alerts = alert_manager.check_server_thresholds(
                            server_id=server_id, server_name=server["name"], metrics=server_metrics
                        )

                        # Add alert info to response (optional)
                        if alerts:
                            data["alerts_triggered"] = len(alerts)
                    except Exception as e:
                        # Don't fail the request if alert checking fails
                        print(f"Alert checking error: {e}")

                    self._set_headers()
                    self.wfile.write(json.dumps(data).encode())
                else:
                    # Update server status to offline
                    db.update_server_status(server_id, "offline")

                    self._set_headers(503)
                    self.wfile.write(
                        json.dumps(
                            {"error": "Failed to get data from remote server", "details": result.get("error", "")}
                        ).encode()
                    )

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())

        elif path == "/api/remote/stats/all":
            # Get stats from all servers
            self._set_headers()

            servers = db.get_servers()
            results = []

            for server in servers:
                # Get server with decrypted password
                server_full = get_server_with_auth(server["id"])

                if not server_full:
                    continue

                result = ssh.get_remote_agent_data(
                    host=server_full["host"],
                    port=server_full["port"],
                    username=server_full["username"],
                    agent_port=server_full["agent_port"],
                    endpoint="/api/all",
                    ssh_key_path=server_full["ssh_key_path"],
                    password=server_full.get("ssh_password"),
                )

                if result["success"]:
                    db.update_server_status(server["id"], "online")
                    data = result["data"]
                    data["server_info"] = {
                        "id": server["id"],
                        "name": server["name"],
                        "host": server["host"],
                        "description": server["description"],
                        "status": "online",
                    }

                    # Check thresholds and send alerts if needed
                    try:
                        system_metrics = data.get("system", {})
                        cpu_usage = system_metrics.get("cpu", {}).get("usage", 0)
                        memory_percent = system_metrics.get("memory", {}).get("percent", 0)
                        disk_percent = system_metrics.get("disk", {}).get("percent", 0)

                        server_metrics = {"cpu": cpu_usage, "memory": memory_percent, "disk": disk_percent}

                        # Check and send alerts if thresholds exceeded
                        alert_manager.check_server_thresholds(
                            server_id=server["id"], server_name=server["name"], metrics=server_metrics
                        )
                    except Exception as e:
                        print(f"Alert checking error for server {server['id']}: {e}")

                    results.append(data)
                else:
                    db.update_server_status(server["id"], "offline")
                    results.append(
                        {
                            "server_info": {
                                "id": server["id"],
                                "name": server["name"],
                                "host": server["host"],
                                "description": server["description"],
                                "status": "offline",
                            },
                            "error": result.get("error", "Connection failed"),
                        }
                    )

            self.wfile.write(json.dumps(results).encode())

        # ==================== SSH UTILITIES ====================

        elif path == "/api/ssh/pubkey":
            # Get SSH public key for display
            self._set_headers()
            result = ssh.get_ssh_public_key()
            self.wfile.write(json.dumps(result).encode())

        # ==================== ALERTS ====================

        elif path == "/api/alerts":
            self._set_headers()
            server_id = query.get("server_id", [None])[0]
            is_read = query.get("is_read", [None])[0]

            if is_read is not None:
                is_read = int(is_read)

            alerts = db.get_alerts(server_id=server_id, is_read=is_read)
            self.wfile.write(json.dumps(alerts).encode())

        # ==================== COMMAND SNIPPETS ====================

        elif path == "/api/snippets":
            # Get all snippets
            self._set_headers()
            category = query.get("category", [None])[0]
            snippets = db.get_snippets(category=category)
            self.wfile.write(json.dumps(snippets).encode())

        elif path.startswith("/api/snippets/"):
            # Get single snippet
            snippet_id = path.split("/")[-1]
            try:
                snippet_id = int(snippet_id)
                snippet = db.get_snippet(snippet_id)

                if snippet:
                    self._set_headers()
                    self.wfile.write(json.dumps(snippet).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Snippet not found"}).encode())
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid snippet ID"}).encode())

        # ==================== SSH KEY VAULT ====================

        elif path == "/api/ssh-keys":
            # List all SSH keys (encrypted key vault)
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            # Only admin and operator can view keys
            role = auth_result.get("role", "user")
            if role not in ["admin", "operator"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Access denied. Admin or operator role required"}).encode())
                return

            try:
                keys = ssh_key_manager.list_keys(include_deleted=False)
                self._set_headers()
                self.wfile.write(json.dumps({"keys": keys}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to list keys: {str(e)}"}).encode())

        elif path.startswith("/api/ssh-keys/"):
            # Get single SSH key metadata
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            # Only admin and operator can view keys
            role = auth_result.get("role", "user")
            if role not in ["admin", "operator"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Access denied. Admin or operator role required"}).encode())
                return

            key_id = path.split("/")[-1]
            try:
                key = ssh_key_manager.get_key(key_id, include_deleted=False)

                if key:
                    self._set_headers()
                    self.wfile.write(json.dumps(key).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "SSH key not found"}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to get key: {str(e)}"}).encode())

        # ==================== TASKS (PHASE 4 MODULE 4) ====================

        elif path == "/api/tasks":
            # Get all tasks with filtering
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            role = auth_result.get("role", "viewer")
            user_id = auth_result.get("user_id")

            try:
                # Parse query parameters
                server_id_str = query.get("server_id", [None])[0]
                user_id_filter = query.get("user_id", [None])[0]
                status = query.get("status", [None])[0]
                from_date = query.get("from", [None])[0]
                to_date = query.get("to", [None])[0]
                limit = int(query.get("limit", ["100"])[0])
                offset = int(query.get("offset", ["0"])[0])

                # RBAC: admin sees all, operator/viewer sees only own tasks
                if role == "admin":
                    # Admin can filter by any user
                    if user_id_filter:
                        user_id_filter = int(user_id_filter)
                else:
                    # Operator and viewer can only see own tasks
                    user_id_filter = user_id

                # Get tasks
                tasks = db.get_tasks(
                    server_id=int(server_id_str) if server_id_str else None,
                    user_id=user_id_filter,
                    status=status,
                    from_date=from_date,
                    to_date=to_date,
                    limit=min(limit, 100),
                    offset=offset,
                )

                self._set_headers()
                self.wfile.write(
                    json.dumps({"tasks": tasks, "count": len(tasks), "limit": limit, "offset": offset}).encode()
                )
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to get tasks: {str(e)}"}).encode())

        elif path.startswith("/api/tasks/") and not path.endswith("/cancel"):
            # Get single task by ID
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            role = auth_result.get("role", "viewer")
            user_id = auth_result.get("user_id")

            task_id = path.split("/")[-1]

            try:
                task = db.get_task(task_id)

                if not task:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Task not found"}).encode())
                    return

                # RBAC: admin sees all, operator/viewer sees only own tasks
                if role != "admin" and task["user_id"] != user_id:
                    self._set_headers(403)
                    self.wfile.write(json.dumps({"error": "Access denied. You can only view your own tasks"}).encode())
                    return

                self._set_headers()
                self.wfile.write(json.dumps(task).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to get task: {str(e)}"}).encode())

        # ==================== EMAIL ALERTS ====================

        elif path == "/api/email/config":
            # Get email configuration
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            config = email.get_email_config()
            if config:
                # Hide password
                config["smtp_password"] = "********" if config.get("smtp_password") else ""
                self._set_headers()
                self.wfile.write(json.dumps(config).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "No email configuration found"}).encode())

        # ==================== TERMINAL SESSIONS (Phase 4 Module 2) ====================

        elif path == "/api/terminal/sessions":
            # Get terminal sessions
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            # Only admin and operator can view terminal sessions
            role = auth_result.get("role", "user")
            if role not in ["admin", "operator"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Access denied. Admin or operator role required"}).encode())
                return

            try:
                # Parse query parameters
                user_id = query.get("user_id", [None])[0]
                server_id = query.get("server_id", [None])[0]
                status = query.get("status", ["active"])[0]

                # Admins can see all sessions, operators only their own
                if role == "operator":
                    user_id = auth_result.get("user_id")

                sessions = db.get_terminal_sessions(
                    user_id=int(user_id) if user_id else None,
                    server_id=int(server_id) if server_id else None,
                    status=status,
                )

                self._set_headers()
                self.wfile.write(json.dumps({"sessions": sessions}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to get sessions: {str(e)}"}).encode())

        # ==================== AUDIT LOGS (Phase 4 Module 6) ====================

        elif path == "/api/audit-logs":
            # Get audit logs (admin only)
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            # Only admin can view audit logs
            role = auth_result.get("role", "user")
            if role != "admin":
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Access denied. Admin role required"}).encode())
                return

            try:
                # Parse query parameters
                user_id = query.get("user_id", [None])[0]
                action = query.get("action", [None])[0]
                target_type = query.get("target_type", [None])[0]
                start_date = query.get("start_date", [None])[0]
                end_date = query.get("end_date", [None])[0]
                limit = int(query.get("limit", ["100"])[0])
                offset = int(query.get("offset", ["0"])[0])

                logs = db.get_audit_logs(
                    user_id=int(user_id) if user_id else None,
                    action=action,
                    target_type=target_type,
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit,
                    offset=offset,
                )

                self._set_headers()
                self.wfile.write(
                    json.dumps({"logs": logs, "count": len(logs), "limit": limit, "offset": offset}).encode()
                )
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to get audit logs: {str(e)}"}).encode())

        # ==================== WEBHOOKS MANAGEMENT ====================

        elif path == "/api/webhooks":
            # List all webhooks (admin only)
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                self._finish_request(401)
                return

            if auth_result.get("role") != "admin":
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                self._finish_request(403)
                return

            try:
                webhooks = db.get_webhooks()

                # Sanitize secrets in response (don't expose them)
                for webhook in webhooks:
                    if webhook.get("secret"):
                        webhook["secret"] = "***REDACTED***"

                self._set_headers()
                self.wfile.write(json.dumps({"webhooks": webhooks}).encode())
                self._finish_request(200, user_id=str(auth_result.get("user_id")))
            except Exception as e:
                logger.error("Failed to get webhooks", error=str(e))
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to get webhooks: {str(e)}"}).encode())
                self._finish_request(500)

        elif path.startswith("/api/webhooks/") and "/deliveries" in path:
            # GET /api/webhooks/{id}/deliveries - Get delivery logs for webhook
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                self._finish_request(401)
                return

            if auth_result.get("role") != "admin":
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                self._finish_request(403)
                return

            try:
                # Extract webhook_id from path: /api/webhooks/{id}/deliveries
                parts = path.split("/")
                webhook_id = parts[3]  # /api/webhooks/{id}/deliveries

                # Parse query parameters
                limit = int(query.get("limit", ["50"])[0])
                offset = int(query.get("offset", ["0"])[0])

                # Validate webhook exists
                webhook = db.get_webhook(webhook_id)
                if not webhook:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Webhook not found"}).encode())
                    self._finish_request(404)
                    return

                # Get deliveries
                deliveries = db.get_webhook_deliveries(webhook_id=webhook_id, limit=min(limit, 100), offset=offset)

                self._set_headers()
                self.wfile.write(
                    json.dumps(
                        {"deliveries": deliveries, "count": len(deliveries), "limit": limit, "offset": offset}
                    ).encode()
                )
                self._finish_request(200, user_id=str(auth_result.get("user_id")))
            except Exception as e:
                logger.error("Failed to get webhook deliveries", error=str(e))
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to get deliveries: {str(e)}"}).encode())
                self._finish_request(500)

        elif path.startswith("/api/webhooks/") and path != "/api/webhooks":
            # GET /api/webhooks/{id} - Get single webhook
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                self._finish_request(401)
                return

            if auth_result.get("role") != "admin":
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                self._finish_request(403)
                return

            try:
                webhook_id = path.split("/")[-1]
                webhook = db.get_webhook(webhook_id)

                if not webhook:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Webhook not found"}).encode())
                    self._finish_request(404)
                    return

                # Sanitize secret
                if webhook.get("secret"):
                    webhook["secret"] = "***REDACTED***"

                self._set_headers()
                self.wfile.write(json.dumps(webhook).encode())
                self._finish_request(200, user_id=str(auth_result.get("user_id")))
            except Exception as e:
                logger.error("Failed to get webhook", error=str(e))
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to get webhook: {str(e)}"}).encode())
                self._finish_request(500)

        elif path == "/api/export/audit/csv":
            # Export audit logs as CSV (admin only)
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            # Only admin can export audit logs
            role = auth_result.get("role", "user")
            if role != "admin":
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Access denied. Admin role required"}).encode())
                return

            try:
                # Parse query parameters (same as /api/audit-logs)
                user_id = query.get("user_id", [None])[0]
                action = query.get("action", [None])[0]
                target_type = query.get("target_type", [None])[0]
                from_date = query.get("from", [None])[0]
                to_date = query.get("to", [None])[0]
                limit = int(query.get("limit", ["10000"])[0])

                # Export to CSV with sanitization
                csv_data = db.export_audit_logs_csv(
                    user_id=int(user_id) if user_id else None,
                    action=action,
                    target_type=target_type,
                    start_date=from_date,
                    end_date=to_date,
                    limit=min(limit, 50000),  # Cap at 50k records for safety
                )

                # Add audit log for the export action
                user_id_val = auth_result.get("user_id")
                if user_id_val:
                    dispatch_audit_event(
                        user_id=user_id_val,
                        action="audit.export",
                        target_type="audit_logs",
                        target_id="csv",
                        meta={
                            "format": "csv",
                            "filters": {
                                "user_id": user_id,
                                "action": action,
                                "target_type": target_type,
                                "from": from_date,
                                "to": to_date,
                                "limit": limit,
                            },
                        },
                        ip=self.client_address[0] if self.client_address else None,
                        username=auth_result.get("username"),
                        severity=EventSeverity.INFO,
                    )

                # Set CSV headers
                self._set_headers(
                    200,
                    extra_headers={
                        "Content-Type": "text/csv",
                        "Content-Disposition": 'attachment; filename="audit_logs.csv"',
                    },
                )
                self.wfile.write(csv_data.encode("utf-8"))

                logger.info("Audit logs exported", format="csv", user_id=user_id_val, request_id=self.request_id)
            except Exception as e:
                logger.error("Failed to export audit logs", error=str(e), request_id=self.request_id)
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to export audit logs: {str(e)}"}).encode())

        elif path == "/api/export/audit/json":
            # Export audit logs as JSON (admin only)
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            # Only admin can export audit logs
            role = auth_result.get("role", "user")
            if role != "admin":
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Access denied. Admin role required"}).encode())
                return

            try:
                # Parse query parameters (same as /api/audit-logs)
                user_id = query.get("user_id", [None])[0]
                action = query.get("action", [None])[0]
                target_type = query.get("target_type", [None])[0]
                from_date = query.get("from", [None])[0]
                to_date = query.get("to", [None])[0]
                limit = int(query.get("limit", ["10000"])[0])

                # Export to JSON with sanitization
                json_data = db.export_audit_logs_json(
                    user_id=int(user_id) if user_id else None,
                    action=action,
                    target_type=target_type,
                    start_date=from_date,
                    end_date=to_date,
                    limit=min(limit, 50000),  # Cap at 50k records for safety
                )

                # Add audit log for the export action
                user_id_val = auth_result.get("user_id")
                if user_id_val:
                    db.add_audit_log(
                        user_id=user_id_val,
                        action="audit.export",
                        target_type="audit_logs",
                        target_id="json",
                        meta={
                            "format": "json",
                            "filters": {
                                "user_id": user_id,
                                "action": action,
                                "target_type": target_type,
                                "from": from_date,
                                "to": to_date,
                                "limit": limit,
                            },
                        },
                        ip=self.client_address[0] if self.client_address else None,
                    )

                # Set JSON headers
                self._set_headers(
                    200,
                    extra_headers={
                        "Content-Type": "application/json",
                        "Content-Disposition": 'attachment; filename="audit_logs.json"',
                    },
                )
                self.wfile.write(json_data.encode("utf-8"))

                logger.info("Audit logs exported", format="json", user_id=user_id_val, request_id=self.request_id)
            except Exception as e:
                logger.error("Failed to export audit logs", error=str(e), request_id=self.request_id)
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to export audit logs: {str(e)}"}).encode())

        elif path == "/api/activity/recent":
            # Get recent activity for dashboard (all authenticated users) with caching (TTL: 15s)
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            # Get limit from query params
            limit = int(query.get("limit", ["20"])[0])
            limit_capped = min(limit, 50)  # Cap at 50

            cache_key = f"activity:recent:{limit_capped}"

            # Try to get from cache
            cached_activity = cache.get(cache_key)
            if cached_activity is not None:
                self._set_headers()
                self.wfile.write(json.dumps(cached_activity).encode())
                return

            try:
                # Get recent audit logs
                logs = db.get_audit_logs(limit=limit_capped)

                # Enrich with user and server details
                enriched_logs = []
                for log in logs:
                    enriched = dict(log)

                    # Get username
                    user = db.get_admin_user(log["user_id"])
                    if user:
                        enriched["username"] = user.get("username", "Unknown")

                    # Get server name if target is a server
                    if log["target_type"] == "server":
                        try:
                            server = db.get_server(int(log["target_id"]))
                            if server:
                                enriched["server_name"] = server.get("name", "Unknown")
                        except:
                            pass

                    enriched_logs.append(enriched)

                result = {"activities": enriched_logs, "count": len(enriched_logs)}

                # Cache for 15 seconds
                cache.set(cache_key, result, ttl=15)

                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to get recent activity: {str(e)}"}).encode())

        # ==================== OPENAPI / SWAGGER UI ====================

        elif path == "/api/openapi.yaml" or path == "/openapi.yaml":
            # Serve OpenAPI specification (public read access)
            try:
                import os

                openapi_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "openapi.yaml"
                )
                if os.path.exists(openapi_path):
                    with open(openapi_path, "r") as f:
                        openapi_content = f.read()
                    self._set_headers(200, {"Content-Type": "text/yaml"})
                    self.wfile.write(openapi_content.encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "OpenAPI specification not found"}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to load OpenAPI spec: {str(e)}"}).encode())

        elif path == "/docs" or path == "/api/docs":
            # Serve Swagger UI (public read access)
            # Note: In production, consider serving Swagger UI assets locally
            # or adding SRI (Subresource Integrity) hashes for CDN resources
            swagger_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Server Monitor API Documentation</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.0/swagger-ui.css">
    <style>
        body {
            margin: 0;
            padding: 0;
        }
        .topbar {
            display: none;
        }
        .swagger-ui .info .title {
            font-size: 36px;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.0/swagger-ui-bundle.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: '/api/openapi.yaml',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                displayRequestDuration: true,
                filter: true,
                tryItOutEnabled: true
            });
            window.ui = ui;
        }
    </script>
</body>
</html>"""
            self._set_headers(200, {"Content-Type": "text/html; charset=utf-8"})
            self.wfile.write(swagger_html.encode())

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
            self._finish_request(404)

    def do_POST(self):
        self._start_request()

        path = self.path

        # ==================== TESTING ENDPOINTS (CI/DEV ONLY) ====================
        # Must be before security middleware to bypass rate limiting

        if path == "/api/test/clear-rate-limit" and os.environ.get("CI", "").lower() in ("true", "1", "yes"):
            # Clear rate limiter for testing
            # Only available in CI mode to prevent abuse
            try:
                security.clear_rate_limit_state()
                rate_limiter.clear_all()
                self._set_headers(200)
                self.wfile.write(json.dumps({"success": True, "message": "Rate limit state cleared"}).encode())
                self._finish_request(200)
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
                self._finish_request(500)
            return

        # Apply security middleware
        sec_result = security.apply_security_middleware(self, "POST")
        if sec_result["block"]:
            self._set_headers(sec_result["status"], sec_result.get("headers"))
            self.wfile.write(json.dumps(sec_result["body"]).encode())
            self._finish_request(sec_result["status"])
            return

        path = self.path
        data = self._read_body()

        # Sanitize input data
        if data:
            for key, value in data.items():
                if isinstance(value, str):
                    if key in ["name", "description", "username"]:
                        data[key] = security.InputSanitizer.sanitize_string(value)
                    elif key == "host":
                        # Validate hostname or IP
                        if not (
                            security.InputSanitizer.validate_hostname(value)
                            or security.InputSanitizer.validate_ip(value)
                        ):
                            self._set_headers(400)
                            self.wfile.write(json.dumps({"error": "Invalid hostname or IP address"}).encode())
                            return
                    elif key == "port":
                        if not security.InputSanitizer.validate_port(value):
                            self._set_headers(400)
                            self.wfile.write(json.dumps({"error": "Invalid port number"}).encode())
                            return

        # ==================== SETUP (PUBLIC) ====================

        if path == "/api/setup/initialize":
            # Create first admin user without authentication (only allowed when no users exist)
            try:
                users = user_mgr.get_all_users()
                if len(users) > 0:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Setup already completed"}).encode())
                    self._finish_request(400)
                    return
                required = ["username", "email", "password"]
                if not data or not all(k in data for k in required):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Missing required fields"}).encode())
                    self._finish_request(400)
                    return
                success, message, user_id = user_mgr.create_user(
                    username=data["username"],
                    email=data["email"],
                    password=data["password"],
                    role="admin",
                    avatar_url=data.get("avatar_url"),
                )
                if success:
                    user = user_mgr.get_user(user_id)
                    token = security.AuthMiddleware.generate_token(
                        {
                            "user_id": user["id"],
                            "username": user["username"],
                            "role": user["role"],
                            "permissions": user.get("permissions", []),
                        }
                    )
                    self._set_headers(201)
                    self.wfile.write(json.dumps({"success": True, "user": user, "token": token}).encode())
                    self._finish_request(201, user_id=str(user["id"]))
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"success": False, "error": message}).encode())
                    self._finish_request(400)
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
                self._finish_request(500)
            return

        # ==================== AUTHENTICATION ====================

        if path == "/api/auth/login":
            # User login with new auth system
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Username and password required"}).encode())
                return

            # Try new user management system first
            success, message, user_data = user_mgr.authenticate(username, password)

            if success:
                # Generate JWT token
                token = security.AuthMiddleware.generate_token(user_data)
                self._set_headers()
                self.wfile.write(
                    json.dumps(
                        {
                            "success": True,
                            "token": token,
                            "username": user_data.get("username"),  # For backward compatibility
                            "role": user_data.get("role"),  # For backward compatibility
                            "user": user_data,
                            "message": message,
                        }
                    ).encode()
                )
            else:
                # Fallback to old auth system for backward compatibility
                result = db.authenticate_user(username, password)
                if result["success"]:
                    self._set_headers()
                    self.wfile.write(json.dumps(result).encode())
                else:
                    self._set_headers(401)
                    self.wfile.write(json.dumps({"success": False, "error": message}).encode())
            return

        elif path == "/api/auth/logout":
            # Admin logout
            auth_result = verify_auth_token(self)

            if not auth_result["valid"]:
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Not authenticated"}).encode())
                return

            # Extract token from header
            auth_header = self.headers.get("Authorization", "")
            token = auth_header.replace("Bearer ", "").strip()

            result = db.logout_user(token)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
            return

        # ==================== CHECK AUTHENTICATION FOR PROTECTED ROUTES ====================

        # All routes below require authentication
        auth_result = verify_auth_token(self)
        if not auth_result["valid"] or auth_result.get("role") == "public":
            self._set_headers(401)
            self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
            return

        # ==================== GROUPS MANAGEMENT ====================

        if path == "/api/groups":
            # Create new group
            required = ["name", "type"]
            if not all(k in data for k in required):
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing required fields: name, type"}).encode())
                return

            valid_types = ["servers", "notes", "snippets", "inventory"]
            if data["type"] not in valid_types:
                self._set_headers(400)
                self.wfile.write(
                    json.dumps({"error": f'Invalid type. Must be one of: {", ".join(valid_types)}'}).encode()
                )
                return

            try:
                conn = db.get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO groups (name, description, type, color, created_by)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        data["name"],
                        data.get("description", ""),
                        data["type"],
                        data.get("color", "#1976d2"),
                        auth_result.get("user_id"),
                    ),
                )

                group_id = cursor.lastrowid
                conn.commit()
                conn.close()

                self._set_headers(201)
                self.wfile.write(
                    json.dumps({"success": True, "message": "Group created successfully", "id": group_id}).encode()
                )
            except sqlite3.IntegrityError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Group name already exists for this type"}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Database error: {str(e)}"}).encode())
            return

        # ==================== USER MANAGEMENT ====================

        if path == "/api/users":
            # Create new user (admin only)
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            required = ["username", "email", "password", "role"]
            if not all(k in data for k in required):
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing required fields"}).encode())
                return

            success, message, user_id = user_mgr.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                role=data["role"],
                avatar_url=data.get("avatar_url"),
            )

            if success:
                self._set_headers(201)
                self.wfile.write(json.dumps({"success": True, "message": message, "user_id": user_id}).encode())
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "error": message}).encode())
            return

        elif path.startswith("/api/users/") and path.endswith("/change-password"):
            # Change user password
            user_id = int(path.split("/")[-2])

            # Users can change their own password, admins can change anyone's
            if auth_result.get("role") != "admin" and auth_result.get("user_id") != user_id:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Access denied"}).encode())
                return

            required = ["old_password", "new_password"]
            if not all(k in data for k in required):
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing required fields"}).encode())
                return

            success, message = user_mgr.change_password(user_id, data["old_password"], data["new_password"])

            self._set_headers(200 if success else 400)
            self.wfile.write(json.dumps({"success": success, "message": message}).encode())
            return

        # ==================== SYSTEM SETTINGS ====================

        elif path == "/api/settings":
            # Update system settings (admin only)
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            success, message, failed = settings_mgr.update_multiple_settings(data, user_id=auth_result.get("user_id"))

            if success:
                self._set_headers()
                self.wfile.write(json.dumps({"success": True, "message": message}).encode())
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "error": message, "failed": failed}).encode())
            return

        elif path.startswith("/api/settings/") and path != "/api/settings":
            # Update single setting
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            key = path.split("/")[-1]
            value = data.get("value")

            if value is None:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Value is required"}).encode())
                return

            success, message = settings_mgr.update_setting(key, value, user_id=auth_result.get("user_id"))

            self._set_headers(200 if success else 400)
            self.wfile.write(json.dumps({"success": success, "message": message}).encode())
            return

        # ==================== DATABASE MANAGEMENT ====================

        elif path == "/api/database/backup":
            # Create manual backup (admin only)
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            from database_manager import db_manager

            result = db_manager.create_backup()

            status_code = 200 if result["success"] else 500
            self._set_headers(status_code)
            self.wfile.write(json.dumps(result).encode())
            return

        elif path == "/api/database/restore":
            # Restore from backup (admin only)
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            filename = data.get("filename")
            if not filename:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Backup filename is required"}).encode())
                return

            from database_manager import db_manager

            result = db_manager.restore_backup(filename)

            status_code = 200 if result["success"] else 500
            self._set_headers(status_code)
            self.wfile.write(json.dumps(result).encode())
            return

        # ==================== SERVER MANAGEMENT ====================

        if path == "/api/servers":
            # Add new server
            required = ["name", "host", "username"]

            if not all(k in data for k in required):
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing required fields"}).encode())
                return

            # Validate host (IP or hostname)
            host = data["host"]
            if not (security.InputSanitizer.validate_ip(host) or security.InputSanitizer.validate_hostname(host)):
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid IP address or hostname format"}).encode())
                return

            # Validate port if provided
            port = data.get("port", 22)
            if not security.InputSanitizer.validate_port(port):
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid port number. Must be between 1 and 65535"}).encode())
                return

            # Validate agent_port if provided
            agent_port = data.get("agent_port", 8083)
            if not security.InputSanitizer.validate_port(agent_port):
                self._set_headers(400)
                self.wfile.write(
                    json.dumps({"error": "Invalid agent port number. Must be between 1 and 65535"}).encode()
                )
                return

            result = db.add_server(
                name=data["name"],
                host=host,
                port=port,
                username=data["username"],
                description=data.get("description", ""),
                ssh_key_path=data.get("ssh_key_path", "~/.ssh/id_rsa"),
                ssh_password=data.get("ssh_password", ""),
                agent_port=agent_port,
                tags=data.get("tags", ""),
                group_id=data.get("group_id"),
            )

            # Invalidate server cache
            cache.delete("servers:list:True")
            cache.delete("servers:list:False")
            cache.delete("stats:overview")

            if result["success"]:
                self._set_headers(201)
            else:
                self._set_headers(400)

            self.wfile.write(json.dumps(result).encode())

        elif path == "/api/servers/test":
            # Test SSH connection to a server
            required = ["host", "username"]

            if not all(k in data for k in required):
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing required fields"}).encode())
                return

            result = ssh.test_connection(
                host=data["host"],
                port=data.get("port", 22),
                username=data["username"],
                ssh_key_path=data.get("ssh_key_path", "~/.ssh/id_rsa"),
                password=data.get("password", ""),
            )

            self._set_headers()
            self.wfile.write(json.dumps(result).encode())

        # ==================== SERVER NOTES ====================
        elif path.startswith("/api/servers/") and "/notes" in path:
            # POST /api/servers/:id/notes
            # Check authentication
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            parts = [p for p in path.split("/") if p]
            if len(parts) >= 4 and parts[3] == "notes":
                try:
                    server_id = int(parts[2])
                    required = ["title"]
                    if not all(k in data for k in required):
                        self._set_headers(400)
                        self.wfile.write(json.dumps({"error": "Missing title"}).encode())
                        return

                    result = db.add_server_note(
                        server_id=server_id,
                        title=data["title"],
                        content=data.get("content", ""),
                        created_by=auth_result.get("user_id"),
                        group_id=data.get("group_id"),
                    )
                    self._set_headers(201 if result["success"] else 400)
                    self.wfile.write(json.dumps(result).encode())
                except ValueError:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())
                except Exception as e:
                    self._set_headers(500)
                    self.wfile.write(json.dumps({"error": f"Failed to add note: {str(e)}"}).encode())
                return

        elif path.startswith("/api/servers/") and "/tasks" in path and not "/inventory" in path:
            # POST /api/servers/:id/tasks
            # Create a new task for command execution
            parts = path.split("/")
            if len(parts) >= 5 and parts[4] == "tasks":
                server_id = int(parts[3])

                # Only admin and operator can create tasks
                role = auth_result.get("role", "viewer")
                if role not in ["admin", "operator"]:
                    self._set_headers(403)
                    self.wfile.write(json.dumps({"error": "Access denied. Admin or operator role required"}).encode())
                    return

                # Rate limit: 20 requests per minute per user
                user_id = auth_result.get("user_id")
                allowed, rate_info = check_endpoint_rate_limit("task_create", str(user_id))
                if not allowed:
                    self._set_headers(
                        429,
                        extra_headers={
                            "X-RateLimit-Limit": str(rate_info["limit"]),
                            "X-RateLimit-Remaining": str(rate_info["remaining"]),
                            "X-RateLimit-Reset": str(rate_info["reset_at"]),
                            "Retry-After": str(rate_info["retry_after"]),
                        },
                    )
                    self.wfile.write(
                        json.dumps({"error": "Rate limit exceeded", "retry_after": rate_info["retry_after"]}).encode()
                    )
                    self._finish_request(429, user_id=str(user_id))
                    return

                # Validate input
                command = data.get("command", "").strip()
                if not command:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Command is required"}).encode())
                    self._finish_request(400, user_id=str(auth_result.get("user_id")))
                    return

                # Security: Basic command validation
                if len(command) > TASK_COMMAND_MAX_LENGTH:
                    self._set_headers(400)
                    self.wfile.write(
                        json.dumps({"error": f"Command too long (max {TASK_COMMAND_MAX_LENGTH} characters)"}).encode()
                    )
                    self._finish_request(400, user_id=str(auth_result.get("user_id")))
                    return

                # Security: Validate command against safety policy
                is_valid, policy_reason = task_policy.validate_command(command)
                if not is_valid:
                    logger.warning(
                        "Task command blocked by policy",
                        user_id=auth_result.get("user_id"),
                        server_id=server_id,
                        command_preview=command[:100],
                        policy_reason=policy_reason,
                    )

                    self._set_headers(403)
                    self.wfile.write(
                        json.dumps(
                            {
                                "error": "Command violates safety policy",
                                "reason": policy_reason,
                                "policy_mode": task_policy.mode,
                            }
                        ).encode()
                    )
                    self._finish_request(403, user_id=str(auth_result.get("user_id")))
                    return

                logger.info(
                    "Task command passed policy check",
                    user_id=auth_result.get("user_id"),
                    server_id=server_id,
                    command_preview=command[:100],
                )

                # Get optional parameters
                timeout_seconds = data.get("timeout_seconds", 60)
                store_output = 1 if data.get("store_output", False) else 0

                try:
                    # Validate timeout
                    timeout_seconds = int(timeout_seconds)
                    if timeout_seconds < 1 or timeout_seconds > 600:
                        self._set_headers(400)
                        self.wfile.write(json.dumps({"error": "Timeout must be between 1 and 600 seconds"}).encode())
                        return

                    # Check if server exists
                    server = db.get_server(server_id)
                    if not server:
                        self._set_headers(404)
                        self.wfile.write(json.dumps({"error": "Server not found"}).encode())
                        return

                    # Create task
                    user_id = auth_result.get("user_id")
                    result = db.create_task(
                        server_id=server_id,
                        user_id=user_id,
                        command=command,
                        timeout_seconds=timeout_seconds,
                        store_output=store_output,
                    )

                    if result.get("success"):
                        task_id = result.get("task_id")

                        # Enqueue task for execution
                        task_runner.enqueue_task(task_id)

                        # Audit log
                        db.add_audit_log(
                            user_id=user_id,
                            action="task.create",
                            target_type="server",
                            target_id=str(server_id),
                            meta={
                                "task_id": task_id,
                                "command_preview": command[:TASK_COMMAND_PREVIEW_LENGTH],
                                "timeout_seconds": timeout_seconds,
                                "store_output": store_output,
                            },
                            ip=self.client_address[0],
                            user_agent=self.headers.get("User-Agent", ""),
                        )

                        self._set_headers(201)
                        self.wfile.write(
                            json.dumps(
                                {
                                    "success": True,
                                    "task_id": task_id,
                                    "message": "Task created and queued for execution",
                                }
                            ).encode()
                        )
                    else:
                        self._set_headers(500)
                        self.wfile.write(json.dumps({"error": result.get("error", "Failed to create task")}).encode())

                except ValueError as e:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": f"Invalid input: {str(e)}"}).encode())
                except Exception as e:
                    self._set_headers(500)
                    self.wfile.write(json.dumps({"error": f"Failed to create task: {str(e)}"}).encode())
                return

        # ==================== SERVER INVENTORY (Phase 4 Module 3) ====================

        elif path.startswith("/api/servers/") and "/inventory/refresh" in path:
            # POST /api/servers/:id/inventory/refresh
            # Refresh inventory for a server (admin/operator only)
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            # Check role (admin or operator)
            role = auth_result.get("role", "user")
            if role not in ["admin", "operator"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Access denied. Admin or operator role required"}).encode())
                return

            parts = [p for p in path.split("/") if p]
            try:
                server_id = int(parts[2])

                # Rate limit: 10 requests per minute per server
                allowed, rate_info = check_endpoint_rate_limit("inventory_refresh", str(server_id))
                if not allowed:
                    self._set_headers(
                        429,
                        extra_headers={
                            "X-RateLimit-Limit": str(rate_info["limit"]),
                            "X-RateLimit-Remaining": str(rate_info["remaining"]),
                            "X-RateLimit-Reset": str(rate_info["reset_at"]),
                            "Retry-After": str(rate_info["retry_after"]),
                        },
                    )
                    self.wfile.write(
                        json.dumps({"error": "Rate limit exceeded", "retry_after": rate_info["retry_after"]}).encode()
                    )
                    return

                server = get_server_with_auth(server_id)

                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Server not found"}).encode())
                    return

                # Get SSH key from vault if provided
                ssh_key_pem = None
                ssh_key_id = data.get("ssh_key_id")
                if ssh_key_id:
                    ssh_key_pem = get_decrypted_key(ssh_key_id)

                # Collect inventory
                inventory = inventory_collector.collect_server_inventory(
                    server_id=server_id,
                    server=server,
                    ssh_key_pem=ssh_key_pem,
                    include_packages=data.get("include_packages", False),
                    include_services=data.get("include_services", False),
                )

                # Save to database
                result = db.save_server_inventory(
                    server_id=server_id, inventory_json=json.dumps(inventory), save_snapshot=True
                )

                if result["success"]:
                    # Add audit log
                    db.add_audit_log(
                        user_id=auth_result.get("user_id"),
                        action="inventory.refresh",
                        target_type="server",
                        target_id=str(server_id),
                        meta={"server_name": server.get("name"), "collected_at": result["collected_at"]},
                        ip=self.client_address[0],
                        user_agent=self.headers.get("User-Agent", ""),
                    )

                    self._set_headers()
                    self.wfile.write(
                        json.dumps(
                            {
                                "success": True,
                                "message": "Inventory refreshed successfully",
                                "collected_at": result["collected_at"],
                                "inventory": inventory,
                            }
                        ).encode()
                    )
                else:
                    self._set_headers(500)
                    self.wfile.write(
                        json.dumps(
                            {"success": False, "error": result.get("error", "Failed to save inventory")}
                        ).encode()
                    )

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to refresh inventory: {str(e)}"}).encode())
            return

        # ==================== REMOTE AGENT MANAGEMENT ====================

        elif path.startswith("/api/remote/agent/deploy/"):
            # Deploy agent to remote server
            server_id = path.split("/")[-1]

            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)

                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Server not found"}).encode())
                    return

                # Deploy agent
                local_agent_path = os.path.join(os.path.dirname(__file__), "agent.py")
                # Security Note: /tmp is used as a reasonable default for remote agent deployment
                # Users can override via remote_path parameter. The path is on the remote server,
                # not the local system, so local /tmp race conditions don't apply
                remote_agent_path = data.get("remote_path", "/tmp/monitoring_agent.py")  # nosec B108

                result = ssh.deploy_agent(
                    host=server["host"],
                    port=server["port"],
                    username=server["username"],
                    local_agent_path=local_agent_path,
                    remote_agent_path=remote_agent_path,
                    ssh_key_path=server["ssh_key_path"],
                    password=server.get("ssh_password"),
                )

                self._set_headers()
                self.wfile.write(json.dumps(result).encode())

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())

        elif path.startswith("/api/remote/agent/start/"):
            # Start agent on remote server
            server_id = path.split("/")[-1]

            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)

                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Server not found"}).encode())
                    return

                # Security Note: /tmp is used as default for remote agent path
                # Users can override via agent_path parameter. Path is on remote server.
                agent_path = data.get("agent_path", "/tmp/monitoring_agent.py")  # nosec B108

                result = ssh.start_remote_agent(
                    host=server["host"],
                    port=server["port"],
                    username=server["username"],
                    agent_script_path=agent_path,
                    ssh_key_path=server["ssh_key_path"],
                    password=server.get("ssh_password"),
                )

                self._set_headers()
                self.wfile.write(json.dumps(result).encode())

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())

        elif path.startswith("/api/remote/agent/install/"):
            # Install agent on remote server (NEW)
            server_id = path.split("/")[-1]

            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)

                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Server not found"}).encode())
                    return

                agent_port = data.get("agent_port", 8083)

                result = ssh.install_agent_remote(
                    host=server["host"],
                    port=server["port"],
                    username=server["username"],
                    agent_port=agent_port,
                    ssh_key_path=server["ssh_key_path"],
                    password=server.get("ssh_password"),
                )

                # Update server agent_installed status
                if result.get("success"):
                    db.update_server(server_id, agent_installed=1)

                self._set_headers()
                self.wfile.write(json.dumps(result).encode())

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())

        elif path.startswith("/api/remote/agent/uninstall/"):
            # Uninstall agent from remote server (NEW)
            server_id = path.split("/")[-1]

            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)

                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Server not found"}).encode())
                    return

                result = ssh.uninstall_agent_remote(
                    host=server["host"],
                    port=server["port"],
                    username=server["username"],
                    ssh_key_path=server["ssh_key_path"],
                    password=server.get("ssh_password"),
                )

                # Update server agent_installed status
                if result.get("success"):
                    db.update_server(server_id, agent_installed=0)

                self._set_headers()
                self.wfile.write(json.dumps(result).encode())

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())

        elif path.startswith("/api/remote/agent/info/"):
            # Get agent info and status (NEW)
            server_id = path.split("/")[-1]

            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)

                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Server not found"}).encode())
                    return

                result = ssh.get_agent_info(
                    host=server["host"],
                    port=server["port"],
                    username=server["username"],
                    ssh_key_path=server["ssh_key_path"],
                    password=server.get("ssh_password"),
                )

                self._set_headers()
                self.wfile.write(json.dumps(result).encode())

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())

        elif path.startswith("/api/remote/check-port/"):
            # Check if port is available on remote server (NEW)
            server_id = path.split("/")[-1]

            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)

                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Server not found"}).encode())
                    return

                check_port = data.get("port", 8083)

                result = ssh.check_port_available(
                    host=server["host"],
                    port=server["port"],
                    username=server["username"],
                    check_port=check_port,
                    ssh_key_path=server["ssh_key_path"],
                    password=server.get("ssh_password"),
                )

                self._set_headers()
                self.wfile.write(json.dumps(result).encode())

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())

        elif path.startswith("/api/remote/suggest-port/"):
            # Suggest available port on remote server (NEW)
            server_id = path.split("/")[-1]

            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)

                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Server not found"}).encode())
                    return

                start_port = data.get("start_port", 8083)

                result = ssh.suggest_available_port(
                    host=server["host"],
                    port=server["port"],
                    username=server["username"],
                    start_port=start_port,
                    ssh_key_path=server["ssh_key_path"],
                    password=server.get("ssh_password"),
                )

                self._set_headers()
                self.wfile.write(json.dumps(result).encode())

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())

        # ==================== REMOTE ACTIONS ====================

        elif path.startswith("/api/remote/action/"):
            # Execute action on remote server
            server_id = path.split("/")[-1]

            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)

                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Server not found"}).encode())
                    return

                action_type = data.get("action_type")
                action_data = data.get("action_data", {})

                result = ssh.execute_remote_action(
                    host=server["host"],
                    port=server["port"],
                    username=server["username"],
                    action_type=action_type,
                    action_data=action_data,
                    ssh_key_path=server["ssh_key_path"],
                    password=server.get("ssh_password"),
                )

                self._set_headers()
                self.wfile.write(json.dumps(result).encode())

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())

        # ==================== COMMAND SNIPPETS ====================

        elif path == "/api/snippets":
            # Create new snippet
            required = ["name", "command"]

            if not all(k in data for k in required):
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing required fields: name, command"}).encode())
                return

            result = db.add_snippet(
                name=data["name"],
                command=data["command"],
                description=data.get("description", ""),
                category=data.get("category", "general"),
                is_sudo=data.get("is_sudo", 0),
                created_by=auth_result.get("user_id"),
                group_id=data.get("group_id"),
            )

            if result["success"]:
                self._set_headers(201)
            else:
                self._set_headers(400)

            self.wfile.write(json.dumps(result).encode())

        # ==================== SSH KEY MANAGEMENT ====================

        elif path == "/api/ssh-keys":
            # Create new SSH key
            required = ["name", "private_key_path"]

            if not all(k in data for k in required):
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing required fields: name, private_key_path"}).encode())
                return

            result = db.add_ssh_key(
                name=data["name"],
                private_key_path=data["private_key_path"],
                description=data.get("description", ""),
                key_type=data.get("key_type", "rsa"),
                public_key=data.get("public_key", ""),
                passphrase=data.get("passphrase", ""),
                created_by=auth_result.get("user_id"),
            )

            if result["success"]:
                self._set_headers(201)
            else:
                self._set_headers(400)

            self.wfile.write(json.dumps(result).encode())

        elif path.startswith("/api/ssh-keys/") and path.endswith("/test"):
            # Test SSH key connection
            key_id = path.split("/")[-2]

            try:
                key_id = int(key_id)
                key = db.get_ssh_key(key_id, decrypt_passphrase=True)

                if not key:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "SSH key not found"}).encode())
                    return

                # Get test host from request data
                test_host = data.get("host")
                test_port = data.get("port", 22)
                test_user = data.get("username", "root")

                if not test_host:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Missing host parameter"}).encode())
                    return

                # Test connection
                result = ssh.test_ssh_connection(
                    host=test_host,
                    port=test_port,
                    username=test_user,
                    ssh_key_path=key["private_key_path"],
                    password=key.get("passphrase", ""),
                )

                if result["success"]:
                    # Update last used timestamp
                    db.update_ssh_key_last_used(key_id)

                self._set_headers()
                self.wfile.write(json.dumps(result).encode())

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid SSH key ID"}).encode())

        # ==================== SSH KEY VAULT ====================

        elif path == "/api/ssh-keys":
            # Create new SSH key (encrypted key vault)
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            # Only admin and operator can create keys
            role = auth_result.get("role", "user")
            if role not in ["admin", "operator"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Access denied. Admin or operator role required"}).encode())
                return

            try:
                name = data.get("name", "").strip()
                description = data.get("description", "").strip()
                private_key = data.get("private_key", "").strip()

                if not name:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Name is required"}).encode())
                    return

                if not private_key:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Private key is required"}).encode())
                    return

                # Get user ID from auth
                user_id = auth_result.get("user_id")

                # Create encrypted key
                result = ssh_key_manager.create_key(
                    name=name, private_key=private_key, description=description, user_id=user_id
                )

                # Add audit log
                db.add_audit_log(
                    user_id=user_id,
                    action="ssh_key.create",
                    target_type="ssh_key",
                    target_id=result["id"],
                    meta={"key_name": name, "key_type": result.get("key_type")},
                )

                self._set_headers(201)
                self.wfile.write(
                    json.dumps({"success": True, "message": "SSH key created successfully", "key": result}).encode()
                )

            except ValueError as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to create key: {str(e)}"}).encode())

        # ==================== TASKS (PHASE 4 MODULE 4) ====================

        elif path.startswith("/api/tasks/") and path.endswith("/cancel"):
            # POST /api/tasks/:id/cancel
            # Cancel a running task
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            role = auth_result.get("role", "viewer")
            user_id = auth_result.get("user_id")

            # Extract task_id from path
            task_id = path.split("/")[-2]

            try:
                # Get task to check ownership
                task = db.get_task(task_id)

                if not task:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Task not found"}).encode())
                    return

                # RBAC: admin can cancel any task, operator/viewer can only cancel own tasks
                if role != "admin" and task["user_id"] != user_id:
                    self._set_headers(403)
                    self.wfile.write(
                        json.dumps({"error": "Access denied. You can only cancel your own tasks"}).encode()
                    )
                    return

                # Can only cancel queued or running tasks
                if task["status"] not in ["queued", "running"]:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": f'Cannot cancel task in status: {task["status"]}'}).encode())
                    return

                # Cancel the task
                cancelled = task_runner.cancel_task(task_id)

                if cancelled or task["status"] == "queued":
                    # Update status to cancelled
                    db.update_task_status(task_id, "cancelled")

                    # Audit log
                    db.add_audit_log(
                        user_id=user_id,
                        action="task.cancel",
                        target_type="task",
                        target_id=task_id,
                        meta={
                            "server_id": task["server_id"],
                            "command_preview": task["command"][:TASK_COMMAND_PREVIEW_LENGTH],
                        },
                        ip=self.client_address[0],
                        user_agent=self.headers.get("User-Agent", ""),
                    )

                    self._set_headers()
                    self.wfile.write(json.dumps({"success": True, "message": "Task cancelled successfully"}).encode())
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Task is not currently running"}).encode())

            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to cancel task: {str(e)}"}).encode())

        # ==================== TERMINAL SESSIONS (Phase 4 Module 2) ====================

        elif path.startswith("/api/terminal/sessions/") and path.endswith("/stop"):
            # Stop a terminal session
            auth_result = verify_auth_token(self)
            if not auth_result["valid"] or auth_result.get("role") == "public":
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                return

            # Only admin and operator can stop terminal sessions
            role = auth_result.get("role", "user")
            if role not in ["admin", "operator"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Access denied. Admin or operator role required"}).encode())
                return

            try:
                session_id = path.split("/")[-2]

                # Verify user owns this session or is admin
                sessions = db.get_terminal_sessions(status="active")
                session = next((s for s in sessions if s["id"] == session_id), None)

                if not session:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Session not found or already closed"}).encode())
                    return

                # Check ownership (operators can only stop their own sessions)
                user_id = auth_result.get("user_id")
                if role == "operator" and session.get("user_id") != user_id:
                    self._set_headers(403)
                    self.wfile.write(json.dumps({"error": "Access denied. Can only stop your own sessions"}).encode())
                    return

                # Stop the session
                result = db.end_terminal_session(session_id, status="stopped")

                if result.get("success"):
                    # Add audit log
                    db.add_audit_log(
                        user_id=user_id,
                        action="terminal.stop",
                        target_type="session",
                        target_id=session_id,
                        meta={"stopped_by": "api", "server_id": session.get("server_id")},
                    )

                    self._set_headers()
                    self.wfile.write(json.dumps({"success": True, "message": "Session stopped successfully"}).encode())
                else:
                    self._set_headers(500)
                    self.wfile.write(json.dumps({"error": f'Failed to stop session: {result.get("error")}'}).encode())

            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to stop session: {str(e)}"}).encode())

        # ==================== EMAIL ALERTS ====================

        elif path == "/api/email/config":
            # Save email configuration
            result = email.save_email_config(
                smtp_host=data.get("smtp_host"),
                smtp_port=int(data.get("smtp_port", 587)),
                smtp_user=data.get("smtp_user"),
                smtp_password=data.get("smtp_password"),
                from_email=data.get("from_email"),
                to_emails=data.get("to_emails"),
                use_tls=data.get("use_tls", True),
                enabled=data.get("enabled", True),
            )

            self._set_headers()
            self.wfile.write(json.dumps(result).encode())

        elif path == "/api/email/test":
            # Test email configuration
            result = email.test_email_config()

            self._set_headers()
            self.wfile.write(json.dumps(result).encode())

        elif path == "/api/email/send-alert":
            # Manually send an alert email
            result = email.send_alert_email(
                server_name=data.get("server_name", "Unknown Server"),
                alert_type=data.get("alert_type", "Manual Alert"),
                message=data.get("message", "Test alert"),
                severity=data.get("severity", "warning"),
                server_id=data.get("server_id"),
            )

            self._set_headers()
            self.wfile.write(json.dumps(result).encode())

        # ==================== TELEGRAM/SLACK CONFIG ====================
        elif path == "/api/telegram/config":
            # Save Telegram config (admin only)
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            try:
                from telegram_bot import save_telegram_config

                result = save_telegram_config(
                    bot_token=data.get("bot_token", ""),
                    chat_id=data.get("chat_id", ""),
                    enabled=data.get("enabled", True),
                )
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            return

        elif path == "/api/slack/config":
            # Save Slack config (admin only)
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            try:
                from slack_integration import save_slack_config

                result = save_slack_config(webhook_url=data.get("webhook_url", ""), enabled=data.get("enabled", True))
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            return

        # ==================== NOTIFICATION TEST ====================
        elif path == "/api/notifications/test":
            # Send a test notification via selected channel (admin only)
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            channel = (data.get("channel") or "email").lower()
            result = {"success": False, "error": "Unsupported channel"}
            try:
                if channel == "email":
                    result = email.test_email_config()
                elif channel == "telegram":
                    from telegram_bot import test_telegram_config

                    result = test_telegram_config()
                elif channel == "slack":
                    from slack_integration import test_slack_config

                    result = test_slack_config()
            except Exception as e:
                result = {"success": False, "error": str(e)}

            self._set_headers(200 if result.get("success") else 400)
            self.wfile.write(json.dumps(result).encode())

        # ==================== DOMAIN SETTINGS ====================
        elif path == "/api/domain/settings":
            # Save domain configuration settings (admin only)
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            try:
                result = db.save_domain_settings(
                    domain_name=data.get("domain_name", ""),
                    ssl_enabled=data.get("ssl_enabled", 0),
                    ssl_type=data.get("ssl_type", "none"),
                    cert_path=data.get("cert_path", ""),
                    key_path=data.get("key_path", ""),
                    auto_renew=data.get("auto_renew", 0),
                )
                self._set_headers(200 if result.get("success") else 400)
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            return

        # ==================== WEBHOOKS MANAGEMENT ====================

        elif path == "/api/webhooks":
            # POST /api/webhooks - Create webhook (admin only)
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                self._finish_request(401)
                return

            if auth_result.get("role") != "admin":
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                self._finish_request(403)
                return

            try:
                # Validate required fields
                name = data.get("name")
                url = data.get("url")

                if not name or not url:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "name and url are required"}).encode())
                    self._finish_request(400)
                    return

                # Validate URL for SSRF protection
                is_safe, error_msg = webhook_dispatcher.is_safe_url(url)
                if not is_safe:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": error_msg}).encode())
                    self._finish_request(400)
                    return

                # Create webhook
                result = db.create_webhook(
                    name=security.InputSanitizer.sanitize_string(name),
                    url=url,
                    secret=data.get("secret"),
                    enabled=data.get("enabled", True),
                    event_types=data.get("event_types"),
                    retry_max=data.get("retry_max", 3),
                    timeout=data.get("timeout", 10),
                    created_by=auth_result.get("user_id"),
                )

                if result.get("success"):
                    # Audit log
                    dispatch_audit_event(
                        user_id=auth_result.get("user_id"),
                        action=EventTypes.WEBHOOK_CREATED,
                        target_type="webhook",
                        target_id=result["webhook_id"],
                        meta={"name": name, "url": url},
                        ip=self.client_address[0] if self.client_address else None,
                        username=auth_result.get("username"),
                        severity=EventSeverity.INFO,
                    )

                    self._set_headers(201)
                    self.wfile.write(json.dumps(result).encode())
                    self._finish_request(201, user_id=str(auth_result.get("user_id")))
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps(result).encode())
                    self._finish_request(400)
            except Exception as e:
                logger.error("Failed to create webhook", error=str(e))
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to create webhook: {str(e)}"}).encode())
                self._finish_request(500)
            return

        elif path.startswith("/api/webhooks/") and path.endswith("/test"):
            # POST /api/webhooks/{id}/test - Test webhook (admin only)
            auth_result = verify_auth_token(self)
            if not auth_result.get("valid"):
                self._set_headers(401)
                self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                self._finish_request(401)
                return

            if auth_result.get("role") != "admin":
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                self._finish_request(403)
                return

            # Rate limit: 10 requests per minute per user
            user_id = auth_result.get("user_id")
            allowed, rate_info = check_endpoint_rate_limit("webhook_test", str(user_id))
            if not allowed:
                self._set_headers(
                    429,
                    extra_headers={
                        "X-RateLimit-Limit": str(rate_info["limit"]),
                        "X-RateLimit-Remaining": str(rate_info["remaining"]),
                        "X-RateLimit-Reset": str(rate_info["reset_at"]),
                        "Retry-After": str(rate_info["retry_after"]),
                    },
                )
                self.wfile.write(
                    json.dumps({"error": "Rate limit exceeded", "retry_after": rate_info["retry_after"]}).encode()
                )
                self._finish_request(429, user_id=str(user_id))
                return

            try:
                # Extract webhook_id from path
                webhook_id = path.split("/")[-2]  # /api/webhooks/{id}/test

                # Validate webhook exists
                webhook = db.get_webhook(webhook_id)
                if not webhook:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Webhook not found"}).encode())
                    self._finish_request(404)
                    return

                # Create test event
                test_event = create_event(
                    event_type="webhook.test",
                    user_id=auth_result.get("user_id"),
                    username=auth_result.get("username"),
                    target_type="webhook",
                    target_id=webhook_id,
                    meta={
                        "webhook_name": webhook["name"],
                        "webhook_url": webhook["url"],
                        "test_message": "This is a test webhook delivery from Server Monitor",
                    },
                    ip=self.client_address[0] if self.client_address else None,
                    severity=EventSeverity.INFO,
                )

                # Deliver webhook (this will log delivery)
                webhook_dispatcher._deliver_webhook(webhook, test_event)

                # Get most recent delivery for this webhook
                deliveries = db.get_webhook_deliveries(webhook_id=webhook_id, limit=1)

                # Audit log
                dispatch_audit_event(
                    user_id=auth_result.get("user_id"),
                    action="webhook.test",
                    target_type="webhook",
                    target_id=webhook_id,
                    meta={"webhook_name": webhook["name"]},
                    ip=self.client_address[0] if self.client_address else None,
                    username=auth_result.get("username"),
                    severity=EventSeverity.INFO,
                )

                self._set_headers()
                self.wfile.write(
                    json.dumps(
                        {
                            "success": True,
                            "message": "Test webhook sent",
                            "delivery": deliveries[0] if deliveries else None,
                        }
                    ).encode()
                )
                self._finish_request(200, user_id=str(auth_result.get("user_id")))
            except Exception as e:
                logger.error("Failed to test webhook", error=str(e))
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to test webhook: {str(e)}"}).encode())
                self._finish_request(500)
            return

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())

    def do_PUT(self):
        self._start_request()

        path = self.path
        data = self._read_body()

        # Check authentication
        auth_result = verify_auth_token(self)
        if not auth_result["valid"] or auth_result.get("role") == "public":
            self._set_headers(401)
            self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
            self._finish_request(401)
            return

        # ==================== GROUPS MANAGEMENT ====================

        if path.startswith("/api/groups/") and path.count("/") == 3:
            # Update group
            try:
                group_id = int(path.split("/")[-1])
                conn = db.get_connection()
                cursor = conn.cursor()

                # Check if group exists
                cursor.execute("SELECT id FROM groups WHERE id = ?", (group_id,))
                if not cursor.fetchone():
                    conn.close()
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Group not found"}).encode())
                    return

                # Build update query
                update_fields = []
                update_values = []

                if "name" in data:
                    update_fields.append("name = ?")
                    update_values.append(data["name"])
                if "description" in data:
                    update_fields.append("description = ?")
                    update_values.append(data["description"])
                if "color" in data:
                    update_fields.append("color = ?")
                    update_values.append(data["color"])

                if not update_fields:
                    conn.close()
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "No fields to update"}).encode())
                    return

                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                update_values.append(group_id)

                cursor.execute(
                    f"""
                    UPDATE groups 
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                """,
                    update_values,
                )

                conn.commit()
                conn.close()

                self._set_headers()
                self.wfile.write(json.dumps({"success": True, "message": "Group updated successfully"}).encode())
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid group ID"}).encode())
            except sqlite3.IntegrityError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Group name already exists"}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Database error: {str(e)}"}).encode())
            return

        # ==================== USER MANAGEMENT ====================

        if path == "/api/users/me":
            # Update current user's info (users can update their own theme, email, etc.)
            user_id = auth_result.get("user_id")

            # Users can't change their own role
            if "role" in data:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Cannot change your own role"}).encode())
                return

            success, message = user_mgr.update_user(user_id, **data)

            self._set_headers(200 if success else 400)
            self.wfile.write(json.dumps({"success": success, "message": message}).encode())
            return

        elif path.startswith("/api/users/") and not path.endswith("/change-password"):
            # Update user (admin only for changing roles, users can update their own profile)
            try:
                user_id = int(path.split("/")[-1])

                # Check permissions
                if "role" in data and auth_result.get("role") != "admin":
                    self._set_headers(403)
                    self.wfile.write(json.dumps({"error": "Only admins can change roles"}).encode())
                    return

                if auth_result.get("role") != "admin" and auth_result.get("user_id") != user_id:
                    self._set_headers(403)
                    self.wfile.write(json.dumps({"error": "Access denied"}).encode())
                    return

                success, message = user_mgr.update_user(user_id, **data)

                self._set_headers(200 if success else 400)
                self.wfile.write(json.dumps({"success": success, "message": message}).encode())
                return

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid user ID"}).encode())
                return

        # ==================== SERVER MANAGEMENT ====================

        if path.startswith("/api/servers/"):
            # Check for notes sub-path
            parts = [p for p in path.split("/") if p]
            if len(parts) >= 5 and parts[3] == "notes":
                # PUT /api/servers/:id/notes/:note_id
                # Check authentication
                auth_result = verify_auth_token(self)
                if not auth_result.get("valid"):
                    self._set_headers(401)
                    self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                    return

                try:
                    note_id = int(parts[4])
                    result = db.update_server_note(
                        note_id=note_id,
                        title=data.get("title"),
                        content=data.get("content"),
                        group_id=data.get("group_id"),
                    )
                    self._set_headers()
                    self.wfile.write(json.dumps(result).encode())
                except ValueError:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Invalid note ID"}).encode())
                return

            # Update server
            server_id = path.split("/")[-1]

            try:
                server_id = int(server_id)

                # Validate host if provided
                if "host" in data:
                    host = data["host"]
                    if not (
                        security.InputSanitizer.validate_ip(host) or security.InputSanitizer.validate_hostname(host)
                    ):
                        self._set_headers(400)
                        self.wfile.write(json.dumps({"error": "Invalid IP address or hostname format"}).encode())
                        return

                # Validate port if provided
                if "port" in data:
                    if not security.InputSanitizer.validate_port(data["port"]):
                        self._set_headers(400)
                        self.wfile.write(
                            json.dumps({"error": "Invalid port number. Must be between 1 and 65535"}).encode()
                        )
                        return

                # Validate agent_port if provided
                if "agent_port" in data:
                    if not security.InputSanitizer.validate_port(data["agent_port"]):
                        self._set_headers(400)
                        self.wfile.write(
                            json.dumps({"error": "Invalid agent port number. Must be between 1 and 65535"}).encode()
                        )
                        return

                result = db.update_server(server_id, **data)

                self._set_headers()
                self.wfile.write(json.dumps(result).encode())

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())

        elif path.startswith("/api/snippets/"):
            # Update snippet
            snippet_id = path.split("/")[-1]

            try:
                snippet_id = int(snippet_id)
                result = db.update_snippet(snippet_id, **data)

                self._set_headers()
                self.wfile.write(json.dumps(result).encode())

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid snippet ID"}).encode())

        # Note: SSH keys from key vault cannot be updated (create new key instead)
        # elif path.startswith('/api/ssh-keys/'):
        #     # SSH keys are immutable - delete and create new one if needed

        # ==================== NOTIFICATION CHANNEL TOGGLES ====================
        elif path == "/api/notifications/channels":
            # Update channel enable flags (admin only)
            if auth_result.get("role") not in ["admin"]:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            updates = {}
            try:
                if "email" in data and isinstance(data["email"], dict) and "enabled" in data["email"]:
                    updates["smtp_enabled"] = bool(data["email"]["enabled"])
                if "telegram" in data and isinstance(data["telegram"], dict) and "enabled" in data["telegram"]:
                    updates["telegram_enabled"] = bool(data["telegram"]["enabled"])
                if "slack" in data and isinstance(data["slack"], dict) and "enabled" in data["slack"]:
                    updates["slack_enabled"] = bool(data["slack"]["enabled"])
            except Exception:
                pass

            if not updates:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "error": "No valid updates provided"}).encode())
                return

            success, message, failed = settings_mgr.update_multiple_settings(
                updates, user_id=auth_result.get("user_id")
            )
            self._set_headers(200 if success else 400)
            self.wfile.write(json.dumps({"success": success, "message": message, "failed": failed}).encode())
            self._finish_request(200 if success else 400)

        # ==================== WEBHOOKS MANAGEMENT ====================

        elif path.startswith("/api/webhooks/"):
            # PUT /api/webhooks/{id} - Update webhook (admin only)
            if auth_result.get("role") != "admin":
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                self._finish_request(403)
                return

            try:
                webhook_id = path.split("/")[-1]

                # Validate webhook exists
                webhook = db.get_webhook(webhook_id)
                if not webhook:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Webhook not found"}).encode())
                    self._finish_request(404)
                    return

                # Validate URL if provided
                if "url" in data:
                    is_safe, error_msg = webhook_dispatcher.is_safe_url(data["url"])
                    if not is_safe:
                        self._set_headers(400)
                        self.wfile.write(json.dumps({"error": error_msg}).encode())
                        self._finish_request(400)
                        return

                # Sanitize name if provided
                if "name" in data:
                    data["name"] = security.InputSanitizer.sanitize_string(data["name"])

                # Update webhook
                result = db.update_webhook(webhook_id, **data)

                if result.get("success"):
                    # Audit log
                    dispatch_audit_event(
                        user_id=auth_result.get("user_id"),
                        action=EventTypes.WEBHOOK_UPDATED,
                        target_type="webhook",
                        target_id=webhook_id,
                        meta={"updates": list(data.keys())},
                        ip=self.client_address[0] if self.client_address else None,
                        username=auth_result.get("username"),
                        severity=EventSeverity.INFO,
                    )

                    self._set_headers()
                    self.wfile.write(json.dumps(result).encode())
                    self._finish_request(200, user_id=str(auth_result.get("user_id")))
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps(result).encode())
                    self._finish_request(400)
            except Exception as e:
                logger.error("Failed to update webhook", error=str(e))
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to update webhook: {str(e)}"}).encode())
                self._finish_request(500)
            return

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
            self._finish_request(404)

    def do_DELETE(self):
        self._start_request()

        path = self.path

        # Check authentication
        auth_result = verify_auth_token(self)
        if not auth_result["valid"] or auth_result.get("role") == "public":
            self._set_headers(401)
            self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
            self._finish_request(401)
            return

        # ==================== USER MANAGEMENT ====================

        if path.startswith("/api/users/"):
            # Delete user (admin only)
            if auth_result.get("role") != "admin":
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            try:
                user_id = int(path.split("/")[-1])
                success, message = user_mgr.delete_user(user_id)

                self._set_headers(200 if success else 400)
                self.wfile.write(json.dumps({"success": success, "message": message}).encode())
                return

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid user ID"}).encode())
                return

        # ==================== SERVER MANAGEMENT ====================

        if path.startswith("/api/servers/"):
            # Check for notes sub-path first (more specific)
            parts = [p for p in path.split("/") if p]
            if len(parts) >= 5 and parts[3] == "notes":
                # DELETE /api/servers/:id/notes/:note_id
                # Check authentication
                auth_result = verify_auth_token(self)
                if not auth_result.get("valid"):
                    self._set_headers(401)
                    self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                    return

                try:
                    note_id = int(parts[4])
                    result = db.delete_server_note(note_id)
                    self._set_headers()
                    self.wfile.write(json.dumps(result).encode())
                except ValueError:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Invalid note ID"}).encode())
                return

            # Otherwise delete server
            server_id = path.split("/")[-1]

            try:
                server_id = int(server_id)
                result = db.delete_server(server_id)

                self._set_headers()
                self.wfile.write(json.dumps(result).encode())

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid server ID"}).encode())

        # ==================== DATABASE MANAGEMENT ====================

        elif path.startswith("/api/database/backups/"):
            # Delete backup (admin only)
            if auth_result.get("role") != "admin":
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                return

            filename = path.split("/")[-1]

            from database_manager import db_manager

            result = db_manager.delete_backup(filename)

            status_code = 200 if result["success"] else 404
            self._set_headers(status_code)
            self.wfile.write(json.dumps(result).encode())
            return

        # ==================== OTHER ENDPOINTS ====================

        elif path.startswith("/api/groups/") and path.count("/") == 3:
            # Delete group
            try:
                group_id = int(path.split("/")[-1])
                conn = db.get_connection()
                cursor = conn.cursor()

                # Check if group exists
                cursor.execute("SELECT id, name FROM groups WHERE id = ?", (group_id,))
                group = cursor.fetchone()
                if not group:
                    conn.close()
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Group not found"}).encode())
                    return

                # Delete group (memberships will cascade delete)
                cursor.execute("DELETE FROM groups WHERE id = ?", (group_id,))
                conn.commit()
                conn.close()

                self._set_headers()
                self.wfile.write(json.dumps({"success": True, "message": "Group deleted successfully"}).encode())
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid group ID"}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Database error: {str(e)}"}).encode())
            return

        elif path.startswith("/api/snippets/"):
            # Delete snippet
            snippet_id = path.split("/")[-1]

            try:
                snippet_id = int(snippet_id)
                result = db.delete_snippet(snippet_id)

                self._set_headers()
                self.wfile.write(json.dumps(result).encode())

            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid snippet ID"}).encode())

        elif path.startswith("/api/ssh-keys/"):
            # Delete SSH key (soft delete, admin only)
            # Only admin can delete keys
            if auth_result.get("role") != "admin":
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required to delete keys"}).encode())
                return

            key_id = path.split("/")[-1]

            try:
                success = ssh_key_manager.delete_key(key_id)

                if success:
                    # Add audit log
                    db.add_audit_log(
                        user_id=auth_result.get("user_id"),
                        action="ssh_key.delete",
                        target_type="ssh_key",
                        target_id=key_id,
                        meta={"soft_delete": True},
                    )

                    self._set_headers()
                    self.wfile.write(json.dumps({"success": True, "message": "SSH key deleted successfully"}).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "SSH key not found"}).encode())

            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to delete key: {str(e)}"}).encode())

        # ==================== WEBHOOKS MANAGEMENT ====================

        elif path.startswith("/api/webhooks/"):
            # DELETE /api/webhooks/{id} - Delete webhook (admin only)
            if auth_result.get("role") != "admin":
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
                self._finish_request(403)
                return

            try:
                webhook_id = path.split("/")[-1]

                # Get webhook info before deletion (for audit log)
                webhook = db.get_webhook(webhook_id)
                if not webhook:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Webhook not found"}).encode())
                    self._finish_request(404)
                    return

                # Delete webhook
                result = db.delete_webhook(webhook_id)

                if result.get("success"):
                    # Audit log
                    dispatch_audit_event(
                        user_id=auth_result.get("user_id"),
                        action=EventTypes.WEBHOOK_DELETED,
                        target_type="webhook",
                        target_id=webhook_id,
                        meta={"webhook_name": webhook["name"], "webhook_url": webhook["url"]},
                        ip=self.client_address[0] if self.client_address else None,
                        username=auth_result.get("username"),
                        severity=EventSeverity.INFO,
                    )

                    self._set_headers()
                    self.wfile.write(json.dumps(result).encode())
                    self._finish_request(200, user_id=str(auth_result.get("user_id")))
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps(result).encode())
                    self._finish_request(400)
            except Exception as e:
                logger.error("Failed to delete webhook", error=str(e))
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Failed to delete webhook: {str(e)}"}).encode())
                self._finish_request(500)
            return

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
            self._finish_request(404)

    def log_message(self, format, *args):
        # Suppress default HTTP logging (we use structured logging)
        pass


def graceful_shutdown(signum, frame):
    """
    Handle graceful shutdown on SIGTERM/SIGINT
    - Stop audit cleanup scheduler
    - Close all SSH connections
    - Mark running tasks as interrupted
    - Mark active terminal sessions as interrupted
    - Flush logs
    - Shutdown HTTP server
    """
    logger.info("Received shutdown signal", signal=signum)
    print(f"\n\n🛑 Received shutdown signal {signum}, shutting down gracefully...")

    try:
        # Stop audit cleanup scheduler
        logger.info("Stopping audit cleanup scheduler")
        audit_scheduler = get_audit_cleanup_scheduler()
        audit_scheduler.stop()

        # Mark active terminal sessions as interrupted
        logger.info("Marking active terminal sessions as interrupted")
        try:
            sessions = db.get_terminal_sessions(status="active")
            for session in sessions:
                db.end_terminal_session(session["id"], status="interrupted")
            logger.info(f"Marked {len(sessions)} terminal sessions as interrupted")
        except Exception as e:
            logger.error("Failed to mark terminal sessions as interrupted", error=str(e))

        # Mark running tasks as interrupted
        logger.info("Marking running tasks as interrupted")
        try:
            tasks = db.get_tasks(status="running")
            for task in tasks:
                db.update_task_status(
                    task_id=task["id"], status="interrupted", finished_at=datetime.utcnow().isoformat() + "Z"
                )
            logger.info(f"Marked {len(tasks)} tasks as interrupted")
        except Exception as e:
            logger.error("Failed to mark tasks as interrupted", error=str(e))

        # Close all SSH connections
        logger.info("Closing all SSH connections")
        try:
            ssh.ssh_pool.close_all()
        except Exception as e:
            logger.error("Failed to close SSH connections", error=str(e))

        # Shutdown plugin system
        logger.info("Shutting down plugin system")
        try:
            plugin_manager.shutdown()
        except Exception as e:
            logger.error("Failed to shutdown plugins", error=str(e))

        # Shutdown HTTP server
        if http_server:
            logger.info("Shutting down HTTP server")
            http_server.shutdown()

        logger.info("Graceful shutdown complete")
        print("✓ Graceful shutdown complete")

    except Exception as e:
        logger.error("Error during graceful shutdown", error=str(e))
        print(f"⚠️  Error during shutdown: {e}")


if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)

    # Validate configuration and secrets
    startup_validation.validate_configuration()

    # Initialize database
    db.init_database()

    # Run startup recovery for tasks and terminal sessions
    recovery_result = run_startup_recovery()

    # Cleanup expired sessions (older than 7 days)
    cleanup_result = db.cleanup_expired_sessions()

    # Start audit cleanup scheduler
    audit_scheduler = get_audit_cleanup_scheduler()
    audit_scheduler.start()

    # Initialize plugin system
    logger.info("Initializing plugin system")
    plugin_manager.startup(
        {
            "server": "central_api",
            "port": PORT,
            "version": "v4",
            "plugins_enabled": plugin_manager.enabled,
            "plugins_loaded": list(plugin_manager.plugins.keys()),
        }
    )

    # Log startup
    logger.info(
        "Starting Central API Server",
        port=PORT,
        sessions_cleaned=cleanup_result["deleted"],
        tasks_recovered=recovery_result["tasks"]["recovered"],
        terminal_sessions_recovered=recovery_result["terminal_sessions"]["recovered"],
        audit_cleanup_enabled=audit_scheduler.enabled,
        audit_retention_days=audit_scheduler.retention_days,
        plugins_enabled=plugin_manager.enabled,
        plugins_loaded=list(plugin_manager.plugins.keys()),
        version="v4",
    )

    # Security Note: Binding to 0.0.0.0 is intentional for central monitoring API
    # This allows connections from all network interfaces for multi-server monitoring
    # Production deployments should use firewall rules, reverse proxy, or VPN
    http_server = HTTPServer(("0.0.0.0", PORT), CentralAPIHandler)  # nosec B104
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Central Multi-Server Monitoring API v4                  ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"\n🚀 Server running on http://0.0.0.0:{PORT}")
    print("🔒 Authentication: Enabled (sessions expire after 7 days)")
    print(f'🧹 Cleaned up {cleanup_result["deleted"]} expired sessions')
    if recovery_result["total_recovered"] > 0:
        print(f'🔄 Recovered {recovery_result["total_recovered"]} interrupted tasks/sessions')
    if plugin_manager.enabled:
        plugins_list = ", ".join(plugin_manager.plugins.keys()) if plugin_manager.plugins else "none"
        print(f"🔌 Plugins: {len(plugin_manager.plugins)} loaded ({plugins_list})")
    print("\n📡 API Endpoints:")
    print("   Observability (Phase 6):")
    print(f"   • GET  /api/health                 - Liveness check (public)")
    print(f"   • GET  /api/ready                  - Readiness check (public)")
    print(f"   • GET  /api/metrics                - Prometheus/JSON metrics (admin/localhost)")
    print(f"   Auth:")
    print(f"   • POST /api/auth/login             - Admin login")
    print(f"   • POST /api/auth/logout            - Admin logout")
    print(f"   • GET  /api/auth/verify            - Verify session token")
    print(f"   Servers:")
    print(f"   • GET  /api/servers                - List all servers (public)")
    print(f"   • POST /api/servers                - Add new server (auth)")
    print(f"   • GET  /api/servers/<id>           - Get server details")
    print(f"   • PUT  /api/servers/<id>           - Update server (auth)")
    print(f"   • DELETE /api/servers/<id>         - Delete server (auth)")
    print(f"   • POST /api/servers/test           - Test SSH connection (auth)")
    print(f"   Monitoring:")
    print(f"   • GET  /api/remote/stats/<id>      - Get server monitoring data")
    print(f"   • GET  /api/remote/stats/all       - Get all servers data")
    print(f"   Agent:")
    print(f"   • POST /api/remote/agent/deploy/<id>    - Deploy agent to server (auth)")
    print(f"   • POST /api/remote/agent/start/<id>     - Start agent on server (auth)")
    print(f"   • POST /api/remote/agent/install/<id>   - Install agent with systemd (auth)")
    print(f"   • POST /api/remote/agent/uninstall/<id> - Uninstall agent (auth)")
    print(f"   • POST /api/remote/agent/info/<id>      - Get agent status (auth)")
    print(f"   • POST /api/remote/check-port/<id>      - Check port availability (auth)")
    print(f"   • POST /api/remote/suggest-port/<id>    - Suggest available port (auth)")
    print(f"   • POST /api/remote/action/<id>          - Execute remote action (auth)")
    print(f"   Snippets:")
    print(f"   • GET  /api/snippets               - List all command snippets")
    print(f"   • POST /api/snippets               - Create snippet (auth)")
    print(f"   • GET  /api/snippets/<id>          - Get snippet details")
    print(f"   • PUT  /api/snippets/<id>          - Update snippet (auth)")
    print(f"   • DELETE /api/snippets/<id>        - Delete snippet (auth)")
    print(f"   SSH Keys:")
    print(f"   • GET  /api/ssh-keys               - List all SSH keys (auth)")
    print(f"   • POST /api/ssh-keys               - Add new SSH key (auth)")
    print(f"   • GET  /api/ssh-keys/<id>          - Get SSH key details (auth)")
    print(f"   • POST /api/ssh-keys               - Add new SSH key to vault (auth)")
    print(f"   • DELETE /api/ssh-keys/<id>        - Delete SSH key (admin only)")
    print(f"\n   Terminal Sessions (Phase 4 Module 2):")
    print(f"   • GET  /api/terminal/sessions      - Get terminal sessions (auth)")
    print(f"   • POST /api/terminal/sessions/<id>/stop - Stop terminal session (auth)")
    print(f"\n   Audit Logs (Phase 4 Module 6):")
    print(f"   • GET  /api/audit-logs             - Get audit logs (admin only)")
    print(f"   • GET  /api/export/audit/csv       - Export audit logs as CSV (admin only)")
    print(f"   • GET  /api/export/audit/json      - Export audit logs as JSON (admin only)")
    print(f"\n   Documentation:")
    print(f"   • GET  /docs                       - Swagger UI (API documentation)")
    print(f"   • GET  /api/openapi.yaml           - OpenAPI specification")
    print(f"\n   Other:")
    print(f"   • GET  /api/ssh/pubkey             - Get SSH public key")
    print(f"   • GET  /api/stats/overview         - Get overview statistics")
    print(f"   • GET  /api/alerts                 - Get alerts")
    print(f"\n✨ Press Ctrl+C to stop")

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")
        graceful_shutdown(signal.SIGINT, None)
