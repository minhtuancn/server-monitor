#!/usr/bin/env python3

"""
Security middleware for Server Monitor API
Adds rate limiting, CORS restrictions, security headers, and RBAC
"""

import os
import time
import jwt
import json
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Optional, Dict

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Check if running in CI environment
# Accepts CI=true, CI=1, or CI=yes (common CI environment variable values)
IS_CI_ENVIRONMENT = os.environ.get("CI", "").lower() in ("true", "1", "yes")

# Check if rate limiting should be completely disabled (for E2E testing)
# DISABLE_RATE_LIMIT=true will completely bypass rate limiting
# WARNING: Only use in test/dev environments, NEVER in production
DISABLE_RATE_LIMIT = os.environ.get("DISABLE_RATE_LIMIT", "").lower() in ("true", "1", "yes")

# Rate limiting configuration
# CI rate limits are set high to avoid blocking test IPs during automated testing
RATE_LIMIT_CI_UNLIMITED = 100000  # Effectively unlimited for CI
# Production rate limits
RATE_LIMIT_PROD_REQUESTS = 100  # requests per window
RATE_LIMIT_PROD_LOGIN = 5  # login attempts per window

# Apply appropriate rate limits based on environment
RATE_LIMIT_REQUESTS = RATE_LIMIT_CI_UNLIMITED if IS_CI_ENVIRONMENT else RATE_LIMIT_PROD_REQUESTS
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_LOGIN = RATE_LIMIT_CI_UNLIMITED if IS_CI_ENVIRONMENT else RATE_LIMIT_PROD_LOGIN
RATE_LIMIT_LOGIN_WINDOW = 300  # 5 minutes

# CORS configuration
# Base allowed origins
ALLOWED_ORIGINS = [
    "http://172.22.0.103:9081",
    "http://localhost:9081",
    "http://127.0.0.1:9081",
    "https://localhost:9081",
    "https://127.0.0.1:9081",
]

# Add custom domains from environment variable (e.g., ALLOWED_FRONTEND_DOMAINS=mon.go7s.net,example.com)
CUSTOM_DOMAINS = (
    os.environ.get("ALLOWED_FRONTEND_DOMAINS", "").split(",") if os.environ.get("ALLOWED_FRONTEND_DOMAINS") else []
)
for domain in CUSTOM_DOMAINS:
    domain = domain.strip()
    if domain:
        # Support both HTTP and HTTPS, with common ports
        ALLOWED_ORIGINS.extend(
            [f"http://{domain}", f"https://{domain}", f"http://{domain}:9081", f"https://{domain}:9081"]
        )

# Allow dynamic CORS in development (checks for specific patterns)
# Set CORS_ALLOW_ALL=true in environment to allow all origins (development only)
CORS_ALLOW_ALL = os.environ.get("CORS_ALLOW_ALL", "").lower() in ("true", "1", "yes")

# Rate limiting storage (in-memory for now)
request_counts = defaultdict(lambda: {"count": 0, "reset_time": time.time() + RATE_LIMIT_WINDOW})
login_attempts = defaultdict(lambda: {"count": 0, "reset_time": time.time() + RATE_LIMIT_LOGIN_WINDOW})
blocked_ips = {}  # IP -> until_time


class RateLimiter:
    """Rate limiting middleware"""

    @staticmethod
    def check_rate_limit(ip_address, endpoint="/"):
        """Check if IP has exceeded rate limit"""
        current_time = time.time()

        # Check if IP is blocked
        if ip_address in blocked_ips:
            if current_time < blocked_ips[ip_address]:
                remaining = int(blocked_ips[ip_address] - current_time)
                return {
                    "allowed": False,
                    "error": f"IP blocked. Try again in {remaining} seconds",
                    "retry_after": remaining,
                }
            else:
                # Unblock IP
                del blocked_ips[ip_address]

        # Special handling for login endpoint
        if endpoint == "/api/auth/login":
            data = login_attempts[ip_address]

            # Reset counter if window expired
            if current_time > data["reset_time"]:
                data["count"] = 0
                data["reset_time"] = current_time + RATE_LIMIT_LOGIN_WINDOW

            # Check limit
            if data["count"] >= RATE_LIMIT_LOGIN:
                # Block IP for 15 minutes after repeated login failures
                block_until = current_time + 900
                blocked_ips[ip_address] = block_until
                return {
                    "allowed": False,
                    "error": "Too many login attempts. IP blocked for 15 minutes",
                    "retry_after": 900,
                }

            # Increment counter
            data["count"] += 1

            return {"allowed": True, "remaining": RATE_LIMIT_LOGIN - data["count"], "reset_time": data["reset_time"]}

        # General rate limiting
        data = request_counts[ip_address]

        # Reset counter if window expired
        if current_time > data["reset_time"]:
            data["count"] = 0
            data["reset_time"] = current_time + RATE_LIMIT_WINDOW

        # Check limit
        if data["count"] >= RATE_LIMIT_REQUESTS:
            remaining = int(data["reset_time"] - current_time)
            return {
                "allowed": False,
                "error": f"Rate limit exceeded. Try again in {remaining} seconds",
                "retry_after": remaining,
            }

        # Increment counter
        data["count"] += 1

        return {"allowed": True, "remaining": RATE_LIMIT_REQUESTS - data["count"], "reset_time": data["reset_time"]}

    @staticmethod
    def record_failed_login(ip_address):
        """Record a failed login attempt"""
        current_time = time.time()
        data = login_attempts[ip_address]

        if current_time > data["reset_time"]:
            data["count"] = 1
            data["reset_time"] = current_time + RATE_LIMIT_LOGIN_WINDOW
        else:
            data["count"] += 1


class CORS:
    """CORS middleware"""

    @staticmethod
    def is_origin_allowed(origin):
        """Check if origin is in allowed list"""
        if not origin:
            return False

        # Allow all origins if CORS_ALLOW_ALL is enabled (development mode)
        if CORS_ALLOW_ALL:
            return True

        # Check exact match
        if origin in ALLOWED_ORIGINS:
            return True

        # Allow any origin on port 9081 (frontend port) for flexibility
        if origin.endswith(":9081"):
            return True

        return False

    @staticmethod
    def get_cors_headers(origin):
        """Get CORS headers for response"""
        # Determine allowed origin
        if CORS.is_origin_allowed(origin):
            allowed_origin = origin
        elif ALLOWED_ORIGINS:
            allowed_origin = ALLOWED_ORIGINS[0]
        else:
            allowed_origin = "*"

        return {
            "Access-Control-Allow-Origin": allowed_origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Expose-Headers": "Content-Length, Content-Disposition, X-Request-Id",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400",
        }


class SecurityHeaders:
    """Security headers middleware"""

    @staticmethod
    def get_security_headers():
        """Get security headers for response"""
        return {
            # Content Security Policy - Updated for offline mode (no CDN)
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "font-src 'self' data:; "
                "img-src 'self' data:; "
                "connect-src 'self' ws: wss:"
            ),
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            # XSS Protection
            "X-XSS-Protection": "1; mode=block",
            # Referrer Policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            # Permissions Policy
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }


class InputSanitizer:
    """Input sanitization utilities"""

    @staticmethod
    def sanitize_string(value, max_length=255):
        """Sanitize string input"""
        if not isinstance(value, str):
            return str(value)

        # Remove null bytes
        value = value.replace("\x00", "")

        # Trim whitespace
        value = value.strip()

        # Limit length
        if len(value) > max_length:
            value = value[:max_length]

        return value

    @staticmethod
    def sanitize_html(value):
        """Remove HTML tags from input"""
        import re

        # Remove HTML tags
        value = re.sub(r"<[^>]+>", "", value)
        return InputSanitizer.sanitize_string(value)

    @staticmethod
    def validate_ip(ip_address):
        """Validate IP address format"""
        import re

        pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        if not re.match(pattern, ip_address):
            return False

        # Check each octet is 0-255
        octets = ip_address.split(".")
        return all(0 <= int(octet) <= 255 for octet in octets)

    @staticmethod
    def validate_hostname(hostname):
        """Validate hostname format (not IP)"""
        import re

        # Reject if it looks like an IP address (delegate to validate_ip for proper validation)
        if re.match(r"^(\d{1,3}\.){3}\d{1,3}$", hostname):
            # It looks like an IP, so validate it as IP
            return InputSanitizer.validate_ip(hostname)
        # Allow alphanumeric, dots, hyphens for hostnames
        pattern = r"^[a-zA-Z0-9.-]+$"
        return bool(re.match(pattern, hostname)) and len(hostname) <= 255

    @staticmethod
    def validate_port(port):
        """Validate port number"""
        try:
            port = int(port)
            return 1 <= port <= 65535
        except (ValueError, TypeError):
            return False


def apply_security_middleware(handler, method="GET"):
    """
    Apply security middleware to request handler
    Returns dict with status and headers if request should be blocked
    """
    ip_address = handler.client_address[0]
    path = handler.path

    # Get origin from headers
    origin = handler.headers.get("Origin", "")

    # Check rate limit (skip if DISABLE_RATE_LIMIT is enabled)
    if not DISABLE_RATE_LIMIT:
        rate_limit_result = RateLimiter.check_rate_limit(ip_address, path)

        if not rate_limit_result["allowed"]:
            return {
                "block": True,
                "status": 429,
                "headers": {"Retry-After": str(rate_limit_result.get("retry_after", 60)), **CORS.get_cors_headers(origin)},
                "body": {"error": rate_limit_result["error"], "retry_after": rate_limit_result.get("retry_after")},
            }
    else:
        # Rate limiting disabled, create a fake result for header generation
        rate_limit_result = {"allowed": True}

    # Build headers
    headers = {**CORS.get_cors_headers(origin), **SecurityHeaders.get_security_headers()}

    # Add rate limit info to headers (only if rate limiting is enabled)
    if not DISABLE_RATE_LIMIT and "remaining" in rate_limit_result:
        headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
        headers["X-RateLimit-Remaining"] = str(rate_limit_result["remaining"])
        headers["X-RateLimit-Reset"] = str(int(rate_limit_result["reset_time"]))

    return {"block": False, "headers": headers}


def cleanup_old_entries():
    """Cleanup old entries from rate limiting storage (call periodically)"""
    current_time = time.time()

    # Cleanup request counts
    expired_ips = [ip for ip, data in request_counts.items() if current_time > data["reset_time"] + 3600]
    for ip in expired_ips:
        del request_counts[ip]

    # Cleanup login attempts
    expired_ips = [ip for ip, data in login_attempts.items() if current_time > data["reset_time"] + 3600]
    for ip in expired_ips:
        del login_attempts[ip]

    # Cleanup blocked IPs
    unblocked = [ip for ip, until_time in blocked_ips.items() if current_time > until_time]
    for ip in unblocked:
        del blocked_ips[ip]


def clear_rate_limit_state():
    """
    Clear all rate limiting state (useful for testing)

    Security: Only allowed in CI/test environments to prevent
    accidental clearing of rate limit state in production
    """
    if not IS_CI_ENVIRONMENT:
        raise RuntimeError(
            "clear_rate_limit_state() can only be called in CI/test environments. "
            "Set CI=true environment variable to enable this function."
        )
    request_counts.clear()
    login_attempts.clear()
    blocked_ips.clear()


# Statistics
def get_security_stats():
    """Get security statistics"""
    return {
        "rate_limited_ips": len(request_counts),
        "login_attempts_tracked": len(login_attempts),
        "blocked_ips": len(blocked_ips),
        "blocked_ips_list": [
            {
                "ip": ip,
                "until": datetime.fromtimestamp(until).isoformat(),
                "remaining_seconds": int(until - time.time()),
            }
            for ip, until in blocked_ips.items()
        ],
    }


# JWT Configuration - Use environment variable or generate a random default
# WARNING: Random default means tokens won't survive server restarts
_jwt_secret_env = os.environ.get("JWT_SECRET")
if _jwt_secret_env:
    JWT_SECRET = _jwt_secret_env
else:
    import secrets as _secrets

    JWT_SECRET = _secrets.token_urlsafe(32)
    print("WARNING: JWT_SECRET not set in environment. Using randomly generated secret.")
    print("         Tokens will not survive server restarts. Set JWT_SECRET in .env for production.")

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = int(os.environ.get("JWT_EXPIRATION", 24 * 60 * 60))  # 24 hours in seconds


class AuthMiddleware:
    """Authentication and authorization middleware"""

    @staticmethod
    def generate_token(user_data: Dict) -> str:
        """Generate JWT token for user"""
        payload = {
            "user_id": user_data["id"],
            "username": user_data["username"],
            "role": user_data["role"],
            "permissions": user_data.get("permissions", []),
            "exp": datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[Dict]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def extract_token_from_header(auth_header: str) -> Optional[str]:
        """Extract Bearer token from Authorization header"""
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]

    @staticmethod
    def require_auth(handler):
        """Decorator to require authentication"""

        @wraps(handler)
        def wrapper(self, *args, **kwargs):
            # Get Authorization header
            auth_header = self.headers.get("Authorization")
            if not auth_header:
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No authorization token provided"}).encode())
                return

            # Extract and validate token
            token = AuthMiddleware.extract_token_from_header(auth_header)
            if not token:
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid authorization header format"}).encode())
                return

            user_data = AuthMiddleware.decode_token(token)
            if not user_data:
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid or expired token"}).encode())
                return

            # Attach user data to request
            self.current_user = user_data

            # Call the handler
            return handler(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def require_role(*allowed_roles):
        """Decorator to require specific role(s)"""

        def decorator(handler):
            @wraps(handler)
            def wrapper(self, *args, **kwargs):
                # Check if user is authenticated
                if not hasattr(self, "current_user"):
                    self.send_response(401)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                    return

                # Check role
                user_role = self.current_user.get("role")
                if user_role not in allowed_roles:
                    self.send_response(403)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps({"error": f'Access denied. Required role: {", ".join(allowed_roles)}'}).encode()
                    )
                    return

                # Call the handler
                return handler(self, *args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def require_permission(permission: str):
        """Decorator to require specific permission"""

        def decorator(handler):
            @wraps(handler)
            def wrapper(self, *args, **kwargs):
                # Check if user is authenticated
                if not hasattr(self, "current_user"):
                    self.send_response(401)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
                    return

                # Check permission
                permissions = self.current_user.get("permissions", [])

                # Admin has all permissions
                if "*" in permissions:
                    return handler(self, *args, **kwargs)

                # Check exact permission or wildcard
                has_permission = permission in permissions or any(
                    p.endswith(".*") and permission.startswith(p[:-2]) for p in permissions
                )

                if not has_permission:
                    self.send_response(403)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps({"error": f"Access denied. Required permission: {permission}"}).encode()
                    )
                    return

                # Call the handler
                return handler(self, *args, **kwargs)

            return wrapper

        return decorator
