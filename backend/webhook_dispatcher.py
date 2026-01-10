#!/usr/bin/env python3

"""
Webhook Dispatcher - Manages webhook delivery for managed webhooks (DB-backed)
Integrates with plugin system and database for extensible webhook support
"""

import sys
import os
import json
import hmac
import hashlib
import urllib.request
import urllib.error
import ipaddress
from urllib.parse import urlparse
from typing import Dict, Any, Optional
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
from event_model import Event
from observability import StructuredLogger


logger = StructuredLogger("webhook_dispatcher")


def is_safe_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Validate URL to prevent SSRF attacks

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_safe, error_message)
    """
    try:
        parsed = urlparse(url)

        # Check scheme
        if parsed.scheme not in ["http", "https"]:
            return False, f"Invalid scheme '{parsed.scheme}'. Only http and https are allowed."

        # Check hostname exists
        if not parsed.hostname:
            return False, "Missing hostname in URL"

        hostname = parsed.hostname.lower()

        # Block localhost and loopback addresses
        # Security Note: '0.0.0.0' here is a string constant for validation, not a bind address
        localhost_variants = [  # nosec B104
            "localhost",
            "localhost.localdomain",
            "127.0.0.1",
            "0.0.0.0",
            "::1",
            "0:0:0:0:0:0:0:1",
        ]

        if hostname in localhost_variants:
            return False, "Internal/localhost URLs are not allowed"

        # Check for IPv4/IPv6 addresses that might be internal
        try:
            ip = ipaddress.ip_address(hostname)

            # Block loopback
            if ip.is_loopback:
                return False, "Loopback addresses are not allowed"

            # Block private networks
            if ip.is_private:
                return False, "Private network addresses are not allowed"

            # Block link-local
            if ip.is_link_local:
                return False, "Link-local addresses are not allowed"

            # Block reserved
            if ip.is_reserved:
                return False, "Reserved addresses are not allowed"

        except ValueError:
            # Not an IP address, it's a hostname - that's fine
            # But check for common internal patterns
            internal_patterns = [
                ".local",
                ".internal",
                ".lan",
                "localhost",
            ]

            for pattern in internal_patterns:
                if pattern in hostname:
                    return False, f"Internal hostname patterns are not allowed"

        return True, None

    except Exception as e:
        return False, f"Invalid URL: {str(e)}"


def dispatch_to_webhooks(event: Event) -> None:
    """
    Dispatch event to all enabled webhooks from database

    This function is called by the audit event dispatcher after plugin events.
    It fetches webhooks from the database and delivers the event to each matching webhook.

    Args:
        event: Event object to dispatch
    """
    try:
        webhooks = db.get_webhooks(enabled_only=True)

        if not webhooks:
            logger.debug("No enabled webhooks configured")
            return

        logger.debug(
            f"Dispatching event to {len(webhooks)} webhook(s)", event_id=event.event_id, event_type=event.event_type
        )

        for webhook in webhooks:
            try:
                # Check if webhook is interested in this event type
                event_types = webhook.get("event_types")
                if event_types:  # If event_types is set (not None/empty), filter
                    if event.event_type not in event_types:
                        logger.debug(
                            "Skipping webhook (event type not in filter)",
                            webhook_id=webhook["id"],
                            event_type=event.event_type,
                            allowed_types=event_types,
                        )
                        continue

                # Deliver webhook (with retries)
                _deliver_webhook(webhook, event)

            except Exception as e:
                logger.error("Webhook delivery error", webhook_id=webhook["id"], event_id=event.event_id, error=str(e))

    except Exception as e:
        # Don't let webhook errors break the main request
        logger.error("Webhook dispatcher error", event_id=event.event_id, error=str(e))


def _deliver_webhook(webhook: Dict[str, Any], event: Event) -> None:
    """
    Deliver event to a single webhook with retries

    Args:
        webhook: Webhook configuration dict from database
        event: Event to deliver
    """
    webhook_id = webhook["id"]
    webhook_url = webhook["url"]

    # Validate URL for SSRF protection
    is_safe, error_msg = is_safe_url(webhook_url)
    if not is_safe:
        logger.error("Webhook URL failed SSRF validation", webhook_id=webhook_id, url=webhook_url, error=error_msg)

        # Log failed delivery
        db.log_webhook_delivery(
            webhook_id=webhook_id,
            event_id=event.event_id,
            event_type=event.event_type,
            status="failed",
            error=f"SSRF protection: {error_msg}",
            attempt=1,
        )
        return

    # Prepare payload
    payload = event.to_json()
    payload_bytes = payload.encode("utf-8")

    # Calculate HMAC signature if secret is configured
    signature = None
    secret = webhook.get("secret")
    if secret:
        signature = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

    # Build request headers
    headers = {
        "Content-Type": "application/json",
        "X-SM-Event-Id": event.event_id,
        "X-SM-Event-Type": event.event_type,
        "User-Agent": "ServerMonitor-Webhook/2.3.0",
    }

    if signature:
        headers["X-SM-Signature"] = f"sha256={signature}"

    req = urllib.request.Request(webhook_url, data=payload_bytes, headers=headers, method="POST")

    # Get retry configuration
    retry_max = webhook.get("retry_max", 3)
    timeout = webhook.get("timeout", 10)

    # Retry loop with exponential backoff
    last_error = None
    for attempt in range(1, retry_max + 1):
        try:
            # Security Note: URL is validated by is_safe_url() at line 168 before reaching here
            # SSRF protection ensures only http/https to public IPs
            with urllib.request.urlopen(req, timeout=timeout) as response:  # nosec B310
                status_code = response.getcode()
                response_body = response.read().decode("utf-8", errors="ignore")

                # Log successful delivery
                db.log_webhook_delivery(
                    webhook_id=webhook_id,
                    event_id=event.event_id,
                    event_type=event.event_type,
                    status="success",
                    status_code=status_code,
                    response_body=response_body[:1000],  # Truncate to 1000 chars
                    attempt=attempt,
                )

                # Update last triggered timestamp
                db.update_webhook_last_triggered(webhook_id)

                logger.info(
                    "Webhook delivered successfully",
                    webhook_id=webhook_id,
                    event_id=event.event_id,
                    event_type=event.event_type,
                    status_code=status_code,
                    attempt=attempt,
                )
                return  # Success - exit retry loop

        except urllib.error.HTTPError as e:
            last_error = e
            error_body = ""
            try:
                error_body = e.read().decode("utf-8", errors="ignore")[:1000]
            except:
                pass

            # Log failed/retrying delivery
            status = "failed" if attempt == retry_max else "retrying"
            db.log_webhook_delivery(
                webhook_id=webhook_id,
                event_id=event.event_id,
                event_type=event.event_type,
                status=status,
                status_code=e.code,
                error=f"HTTP {e.code}: {error_body}",
                attempt=attempt,
            )

            # Don't retry 4xx errors (client errors)
            if 400 <= e.code < 500:
                logger.warning(
                    "Webhook delivery failed (client error, no retry)",
                    webhook_id=webhook_id,
                    event_id=event.event_id,
                    status_code=e.code,
                    attempt=attempt,
                )
                return

            logger.warning(
                "Webhook delivery failed (server error)",
                webhook_id=webhook_id,
                event_id=event.event_id,
                status_code=e.code,
                attempt=attempt,
                max_attempts=retry_max,
            )

        except Exception as e:
            last_error = e

            # Log error
            status = "failed" if attempt == retry_max else "retrying"
            db.log_webhook_delivery(
                webhook_id=webhook_id,
                event_id=event.event_id,
                event_type=event.event_type,
                status=status,
                error=str(e)[:1000],
                attempt=attempt,
            )

            logger.warning(
                "Webhook delivery error",
                webhook_id=webhook_id,
                event_id=event.event_id,
                error=str(e),
                attempt=attempt,
                max_attempts=retry_max,
            )

        # Exponential backoff before retry (don't wait after last attempt)
        if attempt < retry_max:
            sleep_time = 2 ** (attempt - 1)
            logger.debug(f"Backing off for {sleep_time}s before retry", webhook_id=webhook_id, attempt=attempt)
            time.sleep(sleep_time)

    # All retries exhausted
    logger.error(
        "Webhook delivery failed after all retries",
        webhook_id=webhook_id,
        event_id=event.event_id,
        attempts=retry_max,
        last_error=str(last_error),
    )
