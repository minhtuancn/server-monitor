#!/usr/bin/env python3
"""
System Settings Manager
Handles system-wide configuration settings
"""

import sqlite3
import json
import os
from typing import Dict, Optional, List
from datetime import datetime

# Import DB_PATH from database module to use the same database path
try:
    from database import DB_PATH as _DEFAULT_DB_PATH
except ImportError:
    # Fallback if database module is not available
    _DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "servers.db")


# Default settings
DEFAULT_SETTINGS = {
    "timezone": "UTC",
    "date_format": "YYYY-MM-DD",
    "time_format": "24h",
    "language": "en",
    "theme": "auto",  # light, dark, auto
    "number_format": "en-US",  # locale for number formatting
    "currency": "USD",
    "items_per_page": 20,
    "session_timeout": 24,  # hours
    "enable_2fa": False,
    "smtp_enabled": False,
    "telegram_enabled": False,
    "slack_enabled": False,
}

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "vi": "Tiếng Việt",
    "zh-CN": "简体中文",
    "ja": "日本語",
    "ko": "한국어",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
}

# Timezone options (common timezones)
TIMEZONES = [
    "UTC",
    "America/New_York",
    "America/Chicago",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Seoul",
    "Asia/Singapore",
    "Asia/Ho_Chi_Minh",
    "Australia/Sydney",
]

# Date format options
DATE_FORMATS = ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY", "DD.MM.YYYY"]


class SettingsManager:
    def __init__(self, db_path: str = None):
        # Use provided path or environment-configured path from database module
        if db_path is None:
            db_path = _DEFAULT_DB_PATH
        self.db_path = db_path
        self._ensure_tables()
        self._initialize_defaults()

    def _ensure_tables(self):
        """Ensure settings table exists"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check if system_settings table exists
        c.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='system_settings'
        """
        )

        if not c.fetchone():
            # Create table
            c.execute(
                """
                CREATE TABLE system_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    type TEXT DEFAULT 'string',
                    updated_at TEXT,
                    updated_by INTEGER
                )
            """
            )

        conn.commit()
        conn.close()

    def _initialize_defaults(self):
        """Initialize default settings if not exists"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        for key, value in DEFAULT_SETTINGS.items():
            c.execute("SELECT key FROM system_settings WHERE key = ?", (key,))
            if not c.fetchone():
                value_type = type(value).__name__
                value_str = json.dumps(value) if isinstance(value, (dict, list, bool)) else str(value)

                c.execute(
                    """
                    INSERT INTO system_settings (key, value, type, updated_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (key, value_str, value_type, datetime.now().isoformat()),
                )

        conn.commit()
        conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_setting(self, key: str) -> Optional[any]:
        """Get a single setting value"""
        try:
            conn = self._get_connection()
            c = conn.cursor()

            c.execute("SELECT value, type FROM system_settings WHERE key = ?", (key,))
            row = c.fetchone()
            conn.close()

            if not row:
                # Return default if exists
                return DEFAULT_SETTINGS.get(key)

            # Convert value based on type
            value = row["value"]
            value_type = row["type"]

            if value_type == "bool":
                return json.loads(value)
            elif value_type == "int":
                return int(value)
            elif value_type == "float":
                return float(value)
            elif value_type in ("dict", "list"):
                return json.loads(value)
            else:
                return value

        except Exception as e:
            print(f"Error getting setting {key}: {e}")
            return DEFAULT_SETTINGS.get(key)

    def get_all_settings(self) -> Dict:
        """Get all settings as dictionary"""
        try:
            conn = self._get_connection()
            c = conn.cursor()

            c.execute("SELECT key, value, type, updated_at FROM system_settings")
            rows = c.fetchall()
            conn.close()

            settings = {}
            for row in rows:
                key = row["key"]
                value = row["value"]
                value_type = row["type"]

                # Convert value based on type
                if value_type == "bool":
                    settings[key] = json.loads(value)
                elif value_type == "int":
                    settings[key] = int(value)
                elif value_type == "float":
                    settings[key] = float(value)
                elif value_type in ("dict", "list"):
                    settings[key] = json.loads(value)
                else:
                    settings[key] = value

            return settings

        except Exception as e:
            print(f"Error getting all settings: {e}")
            return DEFAULT_SETTINGS.copy()

    def update_setting(self, key: str, value: any, user_id: Optional[int] = None) -> tuple:
        """
        Update a setting value
        Returns: (success, message)
        """
        try:
            # Validate key
            if key not in DEFAULT_SETTINGS:
                return False, f"Invalid setting key: {key}"

            # Validate value based on key
            if key == "timezone" and value not in TIMEZONES:
                return False, f"Invalid timezone. Must be one of: {', '.join(TIMEZONES)}"

            if key == "date_format" and value not in DATE_FORMATS:
                return False, f"Invalid date format. Must be one of: {', '.join(DATE_FORMATS)}"

            if key == "language" and value not in SUPPORTED_LANGUAGES:
                return False, f"Invalid language. Must be one of: {', '.join(SUPPORTED_LANGUAGES.keys())}"

            if key == "theme" and value not in ["light", "dark", "auto"]:
                return False, "Theme must be 'light', 'dark', or 'auto'"

            if key == "time_format" and value not in ["12h", "24h"]:
                return False, "Time format must be '12h' or '24h'"

            # Determine type
            value_type = type(value).__name__
            value_str = json.dumps(value) if isinstance(value, (dict, list, bool)) else str(value)

            conn = self._get_connection()
            c = conn.cursor()

            # Update or insert
            c.execute(
                """
                INSERT OR REPLACE INTO system_settings 
                (key, value, type, updated_at, updated_by)
                VALUES (?, ?, ?, ?, ?)
            """,
                (key, value_str, value_type, datetime.now().isoformat(), user_id),
            )

            conn.commit()
            conn.close()

            return True, "Setting updated successfully"

        except Exception as e:
            return False, f"Database error: {str(e)}"

    def update_multiple_settings(self, settings: Dict, user_id: Optional[int] = None) -> tuple:
        """
        Update multiple settings at once
        Returns: (success, message, failed_keys)
        """
        failed = []

        for key, value in settings.items():
            success, msg = self.update_setting(key, value, user_id)
            if not success:
                failed.append({"key": key, "error": msg})

        if failed:
            return False, f"Failed to update {len(failed)} settings", failed

        return True, f"Updated {len(settings)} settings successfully", []

    def reset_to_defaults(self) -> tuple:
        """Reset all settings to defaults"""
        try:
            conn = self._get_connection()
            c = conn.cursor()

            for key, value in DEFAULT_SETTINGS.items():
                value_type = type(value).__name__
                value_str = json.dumps(value) if isinstance(value, (dict, list, bool)) else str(value)

                c.execute(
                    """
                    INSERT OR REPLACE INTO system_settings 
                    (key, value, type, updated_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (key, value_str, value_type, datetime.now().isoformat()),
                )

            conn.commit()
            conn.close()

            return True, "All settings reset to defaults"

        except Exception as e:
            return False, f"Database error: {str(e)}"

    def get_options(self) -> Dict:
        """Get all available options for settings"""
        return {
            "timezones": TIMEZONES,
            "date_formats": DATE_FORMATS,
            "time_formats": ["12h", "24h"],
            "languages": SUPPORTED_LANGUAGES,
            "themes": ["light", "dark", "auto"],
        }


# Singleton instance
_settings_manager = None


def get_settings_manager(db_path: str = None) -> SettingsManager:
    """Get SettingsManager singleton instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager(db_path)
    return _settings_manager
