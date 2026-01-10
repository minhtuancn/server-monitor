"""
Tests for User Management & Settings Manager  
Phase 6 - Module 2: Constants and configuration tests
Coverage target: user_management.py 19%→25%, settings_manager.py 32%→40%
"""

import pytest
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Suppress warnings during import
os.environ["SKIP_DEFAULT_ADMIN"] = "true"

from user_management import UserManagement, ROLES
from settings_manager import DEFAULT_SETTINGS, SUPPORTED_LANGUAGES, TIMEZONES, DATE_FORMATS


# ==================== USER MANAGEMENT TESTS ====================

class TestRoles:
    """Test role constants and permissions"""

    def test_roles_defined(self):
        """Test that all roles are defined"""
        assert "admin" in ROLES
        assert "user" in ROLES
        assert "operator" in ROLES
        assert "auditor" in ROLES

    def test_admin_permissions(self):
        """Test admin has all permissions"""
        assert ROLES["admin"]["permissions"] == ["*"]
        assert ROLES["admin"]["name"] == "Administrator"

    def test_user_permissions(self):
        """Test user has basic permissions"""
        permissions = ROLES["user"]["permissions"]
        assert "server.view" in permissions
        assert "server.edit" in permissions
        assert "terminal.use" in permissions
        assert "alerts.view" in permissions

    def test_operator_permissions(self):
        """Test operator has elevated permissions"""
        permissions = ROLES["operator"]["permissions"]
        assert "server.view" in permissions
        assert "server.edit" in permissions
        assert "terminal.use" in permissions
        assert "alerts.view" in permissions
        assert "alerts.edit" in permissions

    def test_auditor_permissions(self):
        """Test auditor has read-only permissions"""
        permissions = ROLES["auditor"]["permissions"]
        assert "server.view" in permissions
        assert "alerts.view" in permissions
        assert "audit.view" in permissions


class TestPasswordHashing:
    """Test password hashing functionality"""

    def test_hash_password_creates_valid_hash(self):
        """Test that password hashing works"""
        um = UserManagement(db_path=":memory:")
        
        password = "testpassword123"
        hashed = um._hash_password(password)
        
        # Hash should contain salt separator
        assert "$" in hashed
        # Hash should be reasonably long
        assert len(hashed) > 60

    def test_hash_password_uses_random_salt(self):
        """Test that each hash uses different salt"""
        um = UserManagement(db_path=":memory:")
        
        password = "testpassword123"
        hash1 = um._hash_password(password)
        hash2 = um._hash_password(password)
        
        # Different salts = different hashes
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        um = UserManagement(db_path=":memory:")
        
        password = "correctpassword"
        hashed = um._hash_password(password)
        
        assert um._verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with wrong password"""
        um = UserManagement(db_path=":memory:")
        
        password = "correctpassword"
        hashed = um._hash_password(password)
        
        assert um._verify_password("wrongpassword", hashed) is False


class TestGetRoles:
    """Test get_roles method"""

    def test_get_roles_returns_all_roles(self):
        """Test that get_roles returns complete role list"""
        um = UserManagement(db_path=":memory:")
        
        roles = um.get_roles()
        
        assert isinstance(roles, dict)
        assert "admin" in roles
        assert "user" in roles
        assert "operator" in roles
        assert "auditor" in roles


# ==================== SETTINGS MANAGER TESTS ====================

class TestDefaultSettings:
    """Test default settings constants"""

    def test_all_default_settings_exist(self):
        """Test that all default settings are defined"""
        required_settings = [
            "timezone", "date_format", "time_format", "language", 
            "theme", "number_format", "currency", "items_per_page",
            "session_timeout", "enable_2fa", "smtp_enabled",
            "telegram_enabled", "slack_enabled"
        ]
        
        for setting in required_settings:
            assert setting in DEFAULT_SETTINGS

    def test_timezone_default(self):
        """Test default timezone"""
        assert DEFAULT_SETTINGS["timezone"] == "UTC"

    def test_language_default(self):
        """Test default language"""
        assert DEFAULT_SETTINGS["language"] == "en"

    def test_theme_default(self):
        """Test default theme"""
        assert DEFAULT_SETTINGS["theme"] == "auto"

    def test_items_per_page_default(self):
        """Test default pagination"""
        assert DEFAULT_SETTINGS["items_per_page"] == 20
        assert isinstance(DEFAULT_SETTINGS["items_per_page"], int)

    def test_session_timeout_default(self):
        """Test default session timeout"""
        assert DEFAULT_SETTINGS["session_timeout"] == 24
        assert isinstance(DEFAULT_SETTINGS["session_timeout"], int)

    def test_2fa_disabled_by_default(self):
        """Test 2FA is disabled by default"""
        assert DEFAULT_SETTINGS["enable_2fa"] is False

    def test_smtp_disabled_by_default(self):
        """Test SMTP is disabled by default"""
        assert DEFAULT_SETTINGS["smtp_enabled"] is False

    def test_telegram_disabled_by_default(self):
        """Test Telegram is disabled by default"""
        assert DEFAULT_SETTINGS["telegram_enabled"] is False

    def test_slack_disabled_by_default(self):
        """Test Slack is disabled by default"""
        assert DEFAULT_SETTINGS["slack_enabled"] is False


class TestSupportedLanguages:
    """Test supported languages"""

    def test_supported_languages_defined(self):
        """Test that supported languages list exists"""
        assert isinstance(SUPPORTED_LANGUAGES, dict)
        assert len(SUPPORTED_LANGUAGES) > 0

    def test_english_supported(self):
        """Test English is supported"""
        assert "en" in SUPPORTED_LANGUAGES
        assert SUPPORTED_LANGUAGES["en"] == "English"

    def test_vietnamese_supported(self):
        """Test Vietnamese is supported"""
        assert "vi" in SUPPORTED_LANGUAGES
        assert SUPPORTED_LANGUAGES["vi"] == "Tiếng Việt"

    def test_chinese_supported(self):
        """Test Chinese is supported"""
        assert "zh-CN" in SUPPORTED_LANGUAGES

    def test_japanese_supported(self):
        """Test Japanese is supported"""
        assert "ja" in SUPPORTED_LANGUAGES


class TestTimezones:
    """Test timezone constants"""

    def test_timezones_list_exists(self):
        """Test timezones list is defined"""
        assert isinstance(TIMEZONES, list)
        assert len(TIMEZONES) > 0

    def test_utc_included(self):
        """Test UTC is in timezone list"""
        assert "UTC" in TIMEZONES

    def test_common_timezones_included(self):
        """Test common timezones are included"""
        common_zones = [
            "America/New_York",
            "Europe/London",
            "Asia/Tokyo",
            "Asia/Shanghai"
        ]
        
        for zone in common_zones:
            assert zone in TIMEZONES


class TestDateFormats:
    """Test date format constants"""

    def test_date_formats_list_exists(self):
        """Test date formats list is defined"""
        assert isinstance(DATE_FORMATS, list)
        assert len(DATE_FORMATS) > 0

    def test_iso_format_included(self):
        """Test ISO 8601 format is included"""
        assert "YYYY-MM-DD" in DATE_FORMATS

    def test_common_formats_included(self):
        """Test common date formats are included"""
        common_formats = [
            "DD/MM/YYYY",
            "MM/DD/YYYY",
            "DD.MM.YYYY"
        ]
        
        for fmt in common_formats:
            assert fmt in DATE_FORMATS
