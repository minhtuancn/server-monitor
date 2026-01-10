#!/usr/bin/env python3

"""
Cryptographic Key Vault for SSH Private Keys
Provides AES-256-GCM encryption/decryption with secure key management
"""

import os
import secrets
import hashlib
import base64
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class CryptoVault:
    """
    Secure encryption/decryption for SSH private keys using AES-256-GCM

    Security Features:
    - AES-256-GCM for authenticated encryption
    - Random 12-byte IV per encryption (no IV reuse)
    - 16-byte authentication tag for integrity
    - PBKDF2-HMAC-SHA256 for key derivation (100,000 iterations)
    - No plaintext storage
    - Keys only decrypted in RAM when needed
    """

    # Constants
    IV_SIZE = 12  # 96 bits for GCM (recommended)
    TAG_SIZE = 16  # 128 bits
    KEY_SIZE = 32  # 256 bits
    PBKDF2_ITERATIONS = 100000
    PBKDF2_SALT = b"server-monitor-ssh-vault-v1"  # Fixed salt for deterministic key derivation

    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize crypto vault with master key

        Args:
            master_key: Master key from environment or provided explicitly

        Raises:
            ValueError: If no master key is available
        """
        # Get master key from environment or parameter
        env_key = os.environ.get("KEY_VAULT_MASTER_KEY")
        if master_key:
            self.master_key_str = master_key
        elif env_key:
            self.master_key_str = env_key
        else:
            raise ValueError(
                "KEY_VAULT_MASTER_KEY not set in environment. "
                'Generate one with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"'
            )

        # Derive encryption key using PBKDF2
        self.encryption_key = self._derive_key(self.master_key_str)

        # Create AESGCM cipher
        self.cipher = AESGCM(self.encryption_key)

    def _derive_key(self, master_key: str) -> bytes:
        """
        Derive encryption key from master key using PBKDF2-HMAC-SHA256

        Args:
            master_key: Master key string

        Returns:
            32-byte derived key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=self.PBKDF2_SALT,
            iterations=self.PBKDF2_ITERATIONS,
            backend=default_backend(),
        )
        return kdf.derive(master_key.encode("utf-8"))

    def encrypt(self, plaintext: str) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt plaintext using AES-256-GCM

        Args:
            plaintext: Data to encrypt (SSH private key)

        Returns:
            Tuple of (ciphertext, iv, auth_tag)
            - ciphertext: Encrypted data
            - iv: Initialization vector (12 bytes)
            - auth_tag: Authentication tag (16 bytes)

        Raises:
            ValueError: If plaintext is empty
        """
        if not plaintext:
            raise ValueError("Plaintext cannot be empty")

        # Generate random IV (never reuse!)
        iv = secrets.token_bytes(self.IV_SIZE)

        # Encrypt with AESGCM (returns ciphertext + tag)
        plaintext_bytes = plaintext.encode("utf-8")
        ciphertext_with_tag = self.cipher.encrypt(iv, plaintext_bytes, None)

        # Split ciphertext and tag
        # AESGCM appends 16-byte tag to ciphertext
        ciphertext = ciphertext_with_tag[: -self.TAG_SIZE]
        auth_tag = ciphertext_with_tag[-self.TAG_SIZE :]

        return ciphertext, iv, auth_tag

    def decrypt(self, ciphertext: bytes, iv: bytes, auth_tag: bytes) -> str:
        """
        Decrypt ciphertext using AES-256-GCM

        Args:
            ciphertext: Encrypted data
            iv: Initialization vector (12 bytes)
            auth_tag: Authentication tag (16 bytes)

        Returns:
            Decrypted plaintext string

        Raises:
            ValueError: If decryption fails (wrong key, tampered data, etc.)
        """
        if not ciphertext:
            raise ValueError("Ciphertext cannot be empty")

        if len(iv) != self.IV_SIZE:
            raise ValueError(f"IV must be {self.IV_SIZE} bytes")

        if len(auth_tag) != self.TAG_SIZE:
            raise ValueError(f"Auth tag must be {self.TAG_SIZE} bytes")

        try:
            # AESGCM expects ciphertext + tag concatenated
            ciphertext_with_tag = ciphertext + auth_tag

            # Decrypt and verify authentication tag
            plaintext_bytes = self.cipher.decrypt(iv, ciphertext_with_tag, None)

            return plaintext_bytes.decode("utf-8")
        except Exception as e:
            # Don't leak details about why decryption failed
            raise ValueError("Decryption failed: invalid key or tampered data")

    def encrypt_to_base64(self, plaintext: str) -> Tuple[str, str, str]:
        """
        Encrypt and encode to base64 for database storage

        Args:
            plaintext: Data to encrypt

        Returns:
            Tuple of (ciphertext_b64, iv_b64, tag_b64)
        """
        ciphertext, iv, tag = self.encrypt(plaintext)
        return (
            base64.b64encode(ciphertext).decode("ascii"),
            base64.b64encode(iv).decode("ascii"),
            base64.b64encode(tag).decode("ascii"),
        )

    def decrypt_from_base64(self, ciphertext_b64: str, iv_b64: str, tag_b64: str) -> str:
        """
        Decrypt from base64-encoded values

        Args:
            ciphertext_b64: Base64-encoded ciphertext
            iv_b64: Base64-encoded IV
            tag_b64: Base64-encoded auth tag

        Returns:
            Decrypted plaintext string
        """
        ciphertext = base64.b64decode(ciphertext_b64)
        iv = base64.b64decode(iv_b64)
        tag = base64.b64decode(tag_b64)
        return self.decrypt(ciphertext, iv, tag)


def get_vault() -> CryptoVault:
    """
    Get singleton CryptoVault instance

    Returns:
        CryptoVault instance

    Raises:
        ValueError: If KEY_VAULT_MASTER_KEY is not set
    """
    return CryptoVault()


# Test helper function (for development only)
def _test_crypto():
    """Test encryption/decryption (development only)"""
    print("Testing CryptoVault...")

    # Test with temporary key
    test_key = secrets.token_urlsafe(32)
    vault = CryptoVault(master_key=test_key)

    # Test data
    test_data = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBTEST_DATA_HERE
-----END OPENSSH PRIVATE KEY-----"""

    # Encrypt
    print("1. Encrypting test SSH key...")
    ciphertext, iv, tag = vault.encrypt(test_data)
    print(f"   ✓ Ciphertext: {len(ciphertext)} bytes")
    print(f"   ✓ IV: {len(iv)} bytes")
    print(f"   ✓ Tag: {len(tag)} bytes")

    # Decrypt
    print("2. Decrypting...")
    decrypted = vault.decrypt(ciphertext, iv, tag)
    print(f"   ✓ Decrypted: {len(decrypted)} bytes")

    # Verify
    assert decrypted == test_data, "Decryption mismatch!"
    print("   ✓ Decryption matches original")

    # Test wrong key fails
    print("3. Testing wrong key...")
    wrong_vault = CryptoVault(master_key="wrong_key_12345678901234567890")
    try:
        wrong_vault.decrypt(ciphertext, iv, tag)
        print("   ✗ FAILED: Wrong key should fail!")
    except ValueError:
        print("   ✓ Wrong key correctly rejected")

    # Test tampered data fails
    print("4. Testing tampered data...")
    tampered_ciphertext = bytearray(ciphertext)
    tampered_ciphertext[0] ^= 0xFF  # Flip bits
    try:
        vault.decrypt(bytes(tampered_ciphertext), iv, tag)
        print("   ✗ FAILED: Tampered data should fail!")
    except ValueError:
        print("   ✓ Tampered data correctly rejected")

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    _test_crypto()
