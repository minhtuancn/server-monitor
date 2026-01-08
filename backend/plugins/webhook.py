#!/usr/bin/env python3

"""
Webhook Plugin - Example plugin for dispatching events to external webhooks
Demonstrates the plugin interface and provides webhook integration
"""

import sys
import os
import json
import hmac
import hashlib
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugin_system import PluginInterface
from event_model import Event, EventTypes
from observability import StructuredLogger


logger = StructuredLogger('plugin:webhook')


class WebhookPlugin(PluginInterface):
    """
    Webhook Plugin - Dispatches events to configured webhook URLs
    
    Configuration (via PLUGIN_WEBHOOK_CONFIG environment variable as JSON):
    {
        "url": "https://example.com/webhook",
        "secret": "your-webhook-secret",
        "event_types": ["task.finished", "alert.triggered"],  # Optional filter
        "timeout": 10,  # Request timeout in seconds
        "retry_max": 3  # Max retry attempts
    }
    
    Example:
        export PLUGINS_ENABLED=true
        export PLUGINS_ALLOWLIST=webhook
        export PLUGIN_WEBHOOK_CONFIG='{"url":"https://example.com/webhook","secret":"mysecret"}'
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        self.url = self.config.get('url')
        self.secret = self.config.get('secret')
        self.event_types = set(self.config.get('event_types', []))  # Empty = all events
        self.timeout = self.config.get('timeout', 10)
        self.retry_max = self.config.get('retry_max', 3)
        
        # Validate configuration
        if not self.url:
            logger.warning('Webhook plugin: No URL configured, plugin disabled')
            self.enabled = False
        elif not self.url.startswith(('http://', 'https://')):
            # Security Note: Only allow http/https schemes for webhook URLs
            logger.warning('Webhook plugin: Invalid URL scheme, must be http or https',
                          url=self.url)
            self.enabled = False
        
        if self.enabled:
            logger.info('Webhook plugin initialized',
                       url=self.url,
                       has_secret=bool(self.secret),
                       event_filter=list(self.event_types) if self.event_types else 'all')
    
    def on_startup(self, ctx: Dict[str, Any]) -> None:
        """Log startup"""
        if self.enabled:
            logger.info('Webhook plugin started', config=self._safe_config())
    
    def on_event(self, event: Event) -> None:
        """
        Dispatch event to webhook if it matches filter
        
        Args:
            event: Event to potentially dispatch
        """
        if not self.enabled:
            return
        
        # Filter events if event_types is configured
        if self.event_types and event.event_type not in self.event_types:
            return
        
        self._send_webhook(event)
    
    def _send_webhook(self, event: Event) -> None:
        """
        Send event to webhook URL with HMAC signature
        
        Args:
            event: Event to send
        """
        try:
            payload = event.to_json()
            payload_bytes = payload.encode('utf-8')
            
            # Calculate HMAC signature if secret is configured
            signature = None
            if self.secret:
                signature = hmac.new(
                    self.secret.encode('utf-8'),
                    payload_bytes,
                    hashlib.sha256
                ).hexdigest()
            
            # Build request
            headers = {
                'Content-Type': 'application/json',
                'X-SM-Event-Id': event.event_id,
                'X-SM-Event-Type': event.event_type,
                'User-Agent': 'ServerMonitor-Webhook/1.0'
            }
            
            if signature:
                headers['X-SM-Signature'] = f'sha256={signature}'
            
            req = urllib.request.Request(
                self.url,
                data=payload_bytes,
                headers=headers,
                method='POST'
            )
            
            # Send with retry logic
            last_error = None
            for attempt in range(1, self.retry_max + 1):
                try:
                    # Security Note: URL validated in __init__ to ensure http/https only (line 59)
                    with urllib.request.urlopen(req, timeout=self.timeout) as response:  # nosec B310
                        status_code = response.getcode()
                        logger.info('Webhook delivered',
                                   event_id=event.event_id,
                                   event_type=event.event_type,
                                   url=self.url,
                                   status_code=status_code,
                                   attempt=attempt)
                        return  # Success
                except urllib.error.HTTPError as e:
                    last_error = e
                    logger.warning('Webhook HTTP error',
                                 event_id=event.event_id,
                                 event_type=event.event_type,
                                 url=self.url,
                                 status_code=e.code,
                                 attempt=attempt,
                                 max_attempts=self.retry_max)
                    if e.code < 500:  # Don't retry client errors
                        break
                except Exception as e:
                    last_error = e
                    logger.warning('Webhook delivery error',
                                 event_id=event.event_id,
                                 event_type=event.event_type,
                                 url=self.url,
                                 error=str(e),
                                 attempt=attempt,
                                 max_attempts=self.retry_max)
                
                # Exponential backoff before retry
                if attempt < self.retry_max:
                    import time
                    time.sleep(2 ** (attempt - 1))
            
            # All retries failed
            logger.error('Webhook delivery failed after retries',
                        event_id=event.event_id,
                        event_type=event.event_type,
                        url=self.url,
                        attempts=self.retry_max,
                        last_error=str(last_error))
            
        except Exception as e:
            logger.error('Webhook processing error',
                        event_id=event.event_id,
                        event_type=event.event_type,
                        error=str(e))
    
    def _safe_config(self) -> Dict[str, Any]:
        """Get config with sensitive data redacted"""
        safe = self.config.copy()
        if 'secret' in safe:
            safe['secret'] = '***REDACTED***'
        return safe
