#!/usr/bin/env python3

"""
Startup Validation Module
Validates critical configuration and secrets before starting services
"""

import os
import sys

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class ValidationError(Exception):
    """Custom exception for validation failures"""

    pass


def validate_secret(name: str, min_length: int = 32, required: bool = True) -> bool:
    """
    Validate a secret environment variable

    Args:
        name: Environment variable name
        min_length: Minimum required length
        required: Whether the secret is required

    Returns:
        True if valid

    Raises:
        ValidationError if validation fails and required=True
    """
    value = os.environ.get(name)

    if not value:
        if required:
            raise ValidationError(
                f"SECURITY ERROR: {name} is required but not set. "
                f'Generate with: python3 -c "import secrets; print(secrets.token_urlsafe({min_length}))"'
            )
        return False

    # Check for placeholder values
    if value == "REPLACE_WITH_SECURE_RANDOM_VALUE" or value == "your-secret-key":
        raise ValidationError(
            f"SECURITY ERROR: {name} still has placeholder value. "
            f'Generate with: python3 -c "import secrets; print(secrets.token_urlsafe({min_length}))"'
        )

    # Check length
    if len(value) < min_length:
        raise ValidationError(
            f"SECURITY ERROR: {name} is too short (minimum {min_length} characters). "
            f'Generate with: python3 -c "import secrets; print(secrets.token_urlsafe({min_length}))"'
        )

    return True


def validate_production_mode() -> bool:
    """
    Check if we're in production mode

    Returns:
        True if in production
    """
    env = os.environ.get("ENVIRONMENT", "").lower()
    return env in ["production", "prod"]


def validate_all_secrets(fail_fast: bool = True):
    """
    Validate all critical secrets

    Args:
        fail_fast: If True, exit on first error. If False, collect all errors.

    Raises:
        ValidationError with all errors if fail_fast=False
    """
    is_production = validate_production_mode()
    errors = []
    warnings = []

    # Critical secrets (always required in production)
    critical_secrets = [
        ("JWT_SECRET", 32),
        ("ENCRYPTION_KEY", 24),
        ("KEY_VAULT_MASTER_KEY", 32),
    ]

    for secret_name, min_length in critical_secrets:
        try:
            validate_secret(secret_name, min_length, required=is_production)
        except ValidationError as e:
            if fail_fast:
                raise
            errors.append(str(e))

    # In development, just warn if secrets are not set
    if not is_production:
        for secret_name, min_length in critical_secrets:
            value = os.environ.get(secret_name)
            if not value or value == "REPLACE_WITH_SECURE_RANDOM_VALUE":
                warnings.append(
                    f"WARNING: {secret_name} not properly configured. "
                    f"This is OK for development but MUST be set in production."
                )

    # Print warnings
    for warning in warnings:
        print(warning, file=sys.stderr)

    # If we have errors and not fail_fast, raise them all
    if errors:
        raise ValidationError("\n".join(errors))

    return True


def validate_configuration():
    """
    Validate all configuration on startup

    Raises:
        ValidationError if any validation fails
    """
    is_production = validate_production_mode()

    if is_production:
        print("🔒 Running in PRODUCTION mode - validating secrets...")
        try:
            validate_all_secrets(fail_fast=True)
            print("✓ All secrets validated successfully")
        except ValidationError as e:
            print(f"\n❌ SECRET VALIDATION FAILED:\n{e}\n", file=sys.stderr)
            print("Please set all required environment variables before starting in production.", file=sys.stderr)
            sys.exit(1)
    else:
        print("🔧 Running in DEVELOPMENT mode - secrets validation relaxed")
        try:
            validate_all_secrets(fail_fast=False)
        except ValidationError as e:
            # In dev, just warn
            print(f"\n⚠️  SECRET WARNINGS:\n{e}\n", file=sys.stderr)


if __name__ == "__main__":
    # Test validation
    try:
        validate_configuration()
        print("\n✓ Configuration validation passed")
    except ValidationError as e:
        print(f"\n✗ Configuration validation failed:\n{e}")
        sys.exit(1)
