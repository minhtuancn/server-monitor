#!/usr/bin/env python3

"""
Observability Module for Server Monitor
Provides structured logging, request correlation, health checks, and metrics
"""

import json
import time
import uuid
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from collections import defaultdict

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import database and crypto_vault for readiness checks
try:
    import database as db
except ImportError:
    db = None

try:
    import crypto_vault
except ImportError:
    crypto_vault = None

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class StructuredLogger:
    """
    Structured logging utility that outputs JSON-formatted logs
    """

    def __init__(self, service_name: str):
        self.service_name = service_name

    def _log(self, level: str, message: str, **kwargs):
        """Internal method to output structured log entries"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "service": self.service_name,
            "message": message,
        }

        # Add additional fields, filtering out None values and sensitive data
        for key, value in kwargs.items():
            if value is not None:
                # Don't log sensitive fields
                if key.lower() in ["password", "token", "secret", "key", "authorization"]:
                    log_entry[key] = "[REDACTED]"
                else:
                    log_entry[key] = value

        print(json.dumps(log_entry), flush=True)

    def info(self, message: str, **kwargs):
        """Log info level message"""
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning level message"""
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error level message"""
        self._log("ERROR", message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug level message"""
        self._log("DEBUG", message, **kwargs)

    def request(
        self,
        method: str,
        path: str,
        status_code: int,
        latency_ms: float,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ):
        """Log HTTP request with standard fields"""
        self._log(
            "INFO",
            f"{method} {path} {status_code}",
            action="http_request",
            method=method,
            path=path,
            status_code=status_code,
            latency_ms=round(latency_ms, 2),
            request_id=request_id,
            user_id=user_id,
            user_agent=user_agent,
            ip_address=ip_address,
        )


class RequestContext:
    """
    Request correlation utility for tracking requests across services
    """

    @staticmethod
    def get_or_generate_request_id(headers: Dict[str, str]) -> str:
        """
        Get request ID from headers or generate a new one

        Args:
            headers: Request headers (dict or http.server headers)

        Returns:
            Request ID string
        """
        # Handle both dict and http.server.BaseHTTPRequestHandler.headers
        if hasattr(headers, "get"):
            request_id = headers.get("X-Request-Id") or headers.get("x-request-id")
        else:
            request_id = None

        if not request_id:
            request_id = str(uuid.uuid4())

        return request_id

    @staticmethod
    def get_response_headers(request_id: str) -> Dict[str, str]:
        """
        Get headers to include in response for request correlation

        Args:
            request_id: Request ID to include

        Returns:
            Dict of headers to add to response
        """
        return {"X-Request-Id": request_id}


class MetricsCollector:
    """
    Simple metrics collector for monitoring
    Tracks request counts, latencies, connections, and tasks
    """

    def __init__(self):
        self.request_count = defaultdict(int)  # endpoint -> count
        self.request_latency = defaultdict(list)  # endpoint -> [latencies]
        self.websocket_connections = 0
        self.terminal_sessions = 0
        self.tasks_running = 0
        self.tasks_queued = 0
        self.start_time = time.time()

    def record_request(self, endpoint: str, latency_ms: float):
        """Record a completed request"""
        self.request_count[endpoint] += 1
        self.request_latency[endpoint].append(latency_ms)

        # Keep only last 1000 latencies per endpoint to avoid memory bloat
        if len(self.request_latency[endpoint]) > 1000:
            self.request_latency[endpoint] = self.request_latency[endpoint][-1000:]

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": int(time.time() - self.start_time),
            "requests": {"total": sum(self.request_count.values()), "by_endpoint": dict(self.request_count)},
            "latency": {},
            "websocket_connections": self.websocket_connections,
            "terminal_sessions": self.terminal_sessions,
            "tasks": {"running": self.tasks_running, "queued": self.tasks_queued},
        }

        # Calculate latency stats per endpoint
        for endpoint, latencies in self.request_latency.items():
            if latencies:
                metrics["latency"][endpoint] = {
                    "avg": round(sum(latencies) / len(latencies), 2),
                    "min": round(min(latencies), 2),
                    "max": round(max(latencies), 2),
                    "p95": (
                        round(sorted(latencies)[int(len(latencies) * 0.95)], 2)
                        if len(latencies) > 1
                        else round(latencies[0], 2)
                    ),
                }

        return metrics

    def to_prometheus(self) -> str:
        """
        Export metrics in Prometheus text format

        Returns:
            Metrics in Prometheus exposition format
        """
        lines = []

        # Uptime
        uptime = int(time.time() - self.start_time)
        lines.append("# HELP server_monitor_uptime_seconds Uptime in seconds")
        lines.append("# TYPE server_monitor_uptime_seconds counter")
        lines.append(f"server_monitor_uptime_seconds {uptime}")

        # Request counts
        lines.append("# HELP server_monitor_requests_total Total number of requests")
        lines.append("# TYPE server_monitor_requests_total counter")
        for endpoint, count in self.request_count.items():
            # Sanitize endpoint for Prometheus label
            sanitized = endpoint.replace('"', '\\"')
            lines.append(f'server_monitor_requests_total{{endpoint="{sanitized}"}} {count}')

        # Latencies
        lines.append("# HELP server_monitor_request_latency_ms Request latency in milliseconds")
        lines.append("# TYPE server_monitor_request_latency_ms summary")
        for endpoint, latencies in self.request_latency.items():
            if latencies:
                sanitized = endpoint.replace('"', '\\"')
                avg = sum(latencies) / len(latencies)
                lines.append(
                    f'server_monitor_request_latency_ms{{endpoint="{sanitized}",quantile="0.5"}} {round(avg, 2)}'
                )
                if len(latencies) > 1:
                    p95 = sorted(latencies)[int(len(latencies) * 0.95)]
                    lines.append(
                        f'server_monitor_request_latency_ms{{endpoint="{sanitized}",quantile="0.95"}} {round(p95, 2)}'
                    )

        # WebSocket connections
        lines.append("# HELP server_monitor_websocket_connections Current WebSocket connections")
        lines.append("# TYPE server_monitor_websocket_connections gauge")
        lines.append(f"server_monitor_websocket_connections {self.websocket_connections}")

        # Terminal sessions
        lines.append("# HELP server_monitor_terminal_sessions Current terminal sessions")
        lines.append("# TYPE server_monitor_terminal_sessions gauge")
        lines.append(f"server_monitor_terminal_sessions {self.terminal_sessions}")

        # Tasks
        lines.append("# HELP server_monitor_tasks_running Currently running tasks")
        lines.append("# TYPE server_monitor_tasks_running gauge")
        lines.append(f"server_monitor_tasks_running {self.tasks_running}")

        lines.append("# HELP server_monitor_tasks_queued Currently queued tasks")
        lines.append("# TYPE server_monitor_tasks_queued gauge")
        lines.append(f"server_monitor_tasks_queued {self.tasks_queued}")

        return "\n".join(lines) + "\n"


class HealthCheck:
    """
    Health and readiness check utilities
    """

    @staticmethod
    def liveness() -> Dict[str, Any]:
        """
        Liveness check - is the process running?

        Returns:
            Dict with status and timestamp
        """
        return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}

    @staticmethod
    def readiness() -> Dict[str, Any]:
        """
        Readiness check - is the service ready to handle requests?
        Checks:
        - Database connectivity and writability
        - Migrations applied
        - Vault master key exists
        - Critical configuration present

        Returns:
            Dict with status, checks, and details
        """
        checks = {}
        overall_status = "ready"

        # Check 1: Database connectivity and writability
        try:
            if db is None:
                checks["database"] = {"status": "error", "message": "Database module not available"}
                overall_status = "not_ready"
            else:
                # Try to query database
                conn = db.sqlite3.connect(db.DB_PATH)
                cursor = conn.cursor()

                # Check if tables exist (migrations applied)
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='servers'")
                if cursor.fetchone():
                    checks["database"] = {"status": "ok", "message": "Database readable and tables exist"}
                else:
                    checks["database"] = {"status": "error", "message": "Database tables not initialized"}
                    overall_status = "not_ready"

                # Try a write operation (safe test)
                try:
                    cursor.execute("SELECT COUNT(*) FROM servers")
                    cursor.fetchone()
                    checks["database_write"] = {"status": "ok", "message": "Database writable"}
                except Exception as e:
                    checks["database_write"] = {"status": "error", "message": f"Database not writable: {str(e)}"}
                    overall_status = "not_ready"

                conn.close()

        except Exception as e:
            checks["database"] = {"status": "error", "message": f"Database connection failed: {str(e)}"}
            overall_status = "not_ready"

        # Check 2: Vault master key exists
        vault_key = os.environ.get("KEY_VAULT_MASTER_KEY")
        if vault_key and len(vault_key) >= 32:
            checks["vault_master_key"] = {"status": "ok", "message": "Vault master key configured"}
        else:
            checks["vault_master_key"] = {
                "status": "warning",
                "message": "Vault master key not configured or too short",
            }
            # Don't fail readiness for this, just warn

        # Check 3: Critical configuration
        jwt_secret = os.environ.get("JWT_SECRET")
        if jwt_secret and len(jwt_secret) >= 32:
            checks["jwt_secret"] = {"status": "ok", "message": "JWT secret configured"}
        else:
            checks["jwt_secret"] = {"status": "warning", "message": "JWT secret not configured or too short"}

        encryption_key = os.environ.get("ENCRYPTION_KEY")
        if encryption_key and len(encryption_key) >= 16:
            checks["encryption_key"] = {"status": "ok", "message": "Encryption key configured"}
        else:
            checks["encryption_key"] = {"status": "warning", "message": "Encryption key not configured or too short"}

        return {"status": overall_status, "timestamp": datetime.utcnow().isoformat() + "Z", "checks": checks}


# Global metrics collector instance
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
