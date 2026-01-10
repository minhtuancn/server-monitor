#!/usr/bin/env python3

"""
Event Model - Unified event schema for audit logs, webhooks, and notifications
Provides standardized event structure across the system
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
import json


@dataclass
class Event:
    """
    Unified event model for system-wide event handling

    Used by:
    - Audit logs
    - Webhook dispatching
    - Plugin system
    - Recent activity feed
    - Notification dispatchers
    """

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""  # e.g., 'server.created', 'task.finished', 'terminal.connect'
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    user_id: Optional[int] = None
    username: Optional[str] = None
    server_id: Optional[int] = None
    server_name: Optional[str] = None
    target_type: str = ""  # e.g., 'server', 'task', 'ssh_key', 'user'
    target_id: str = ""
    action: str = ""  # Legacy field for audit_logs compatibility
    meta: Dict[str, Any] = field(default_factory=dict)
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    severity: str = "info"  # 'info', 'warning', 'error', 'critical'

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_audit_log(cls, audit_log: Dict[str, Any]) -> "Event":
        """
        Create Event from existing audit log entry
        Ensures backward compatibility
        """
        return cls(
            event_id=audit_log.get("id", str(uuid.uuid4())),
            event_type=audit_log.get("action", ""),
            timestamp=audit_log.get("created_at", datetime.utcnow().isoformat() + "Z"),
            user_id=audit_log.get("user_id"),
            target_type=audit_log.get("target_type", ""),
            target_id=str(audit_log.get("target_id", "")),
            action=audit_log.get("action", ""),
            meta=json.loads(audit_log.get("meta_json", "{}")) if audit_log.get("meta_json") else {},
            ip=audit_log.get("ip"),
            user_agent=audit_log.get("user_agent"),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create Event from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# Event type constants for consistency
class EventTypes:
    """Standard event type constants"""

    # Server events
    SERVER_CREATED = "server.created"
    SERVER_UPDATED = "server.updated"
    SERVER_DELETED = "server.deleted"
    SERVER_STATUS_CHANGED = "server.status_changed"

    # Task events
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_FINISHED = "task.finished"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"

    # Terminal events
    TERMINAL_CONNECT = "terminal.connect"
    TERMINAL_DISCONNECT = "terminal.disconnect"
    TERMINAL_COMMAND = "terminal.command"

    # Inventory events
    INVENTORY_COLLECTED = "inventory.collected"
    INVENTORY_UPDATED = "inventory.updated"

    # SSH Key events
    SSH_KEY_CREATED = "ssh_key.created"
    SSH_KEY_DELETED = "ssh_key.deleted"
    SSH_KEY_USED = "ssh_key.used"

    # User events
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"

    # Settings events
    SETTINGS_UPDATED = "settings.updated"

    # Alert events
    ALERT_TRIGGERED = "alert.triggered"
    ALERT_RESOLVED = "alert.resolved"

    # Audit events
    AUDIT_EXPORT = "audit.export"
    AUDIT_CLEANUP = "audit.cleanup"

    # Webhook events
    WEBHOOK_CREATED = "webhook.created"
    WEBHOOK_UPDATED = "webhook.updated"
    WEBHOOK_DELETED = "webhook.deleted"
    WEBHOOK_DELIVERED = "webhook.delivered"
    WEBHOOK_FAILED = "webhook.failed"


class EventSeverity:
    """Standard severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


def create_event(
    event_type: str,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    server_id: Optional[int] = None,
    server_name: Optional[str] = None,
    target_type: str = "",
    target_id: str = "",
    meta: Optional[Dict[str, Any]] = None,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    severity: str = EventSeverity.INFO,
) -> Event:
    """
    Helper function to create events with consistent structure
    """
    # Map event_type to action for audit_logs backward compatibility
    action = event_type.replace(".", "_")

    return Event(
        event_type=event_type,
        action=action,
        user_id=user_id,
        username=username,
        server_id=server_id,
        server_name=server_name,
        target_type=target_type,
        target_id=target_id,
        meta=meta or {},
        ip=ip,
        user_agent=user_agent,
        severity=severity,
    )
