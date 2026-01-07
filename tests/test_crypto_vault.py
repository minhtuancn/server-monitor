#!/usr/bin/env python3

"""
Unit tests for CryptoVault
Tests AES-256-GCM encryption/decryption
"""

import sys
import os
import secrets

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from crypto_vault import CryptoVault


class TestCryptoVault:
    """Test suite for CryptoVault"""
    
    @staticmethod
    def test_encrypt_decrypt_roundtrip():
        """Test basic encryption and decryption"""
        print("Test 1: Encrypt/Decrypt Roundtrip")
        
        # Create vault with test key
        test_key = secrets.token_urlsafe(32)
        vault = CryptoVault(master_key=test_key)
        
        # Test data
        test_data = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBTEST_DATA_HERE
-----END OPENSSH PRIVATE KEY-----"""
        
        # Encrypt
        ciphertext, iv, tag = vault.encrypt(test_data)
        
        # Verify sizes
        assert len(iv) == 12, f"IV should be 12 bytes, got {len(iv)}"
        assert len(tag) == 16, f"Tag should be 16 bytes, got {len(tag)}"
        assert len(ciphertext) > 0, "Ciphertext should not be empty"
        
        # Decrypt
        decrypted = vault.decrypt(ciphertext, iv, tag)
        
        # Verify
        assert decrypted == test_data, "Decryption should match original"
        
        print("  ✓ Encrypt/decrypt works correctly")
    
    @staticmethod
    def test_wrong_key_fails():
        """Test that wrong key fails decryption"""
        print("\nTest 2: Wrong Key Fails")
        
        # Create vault and encrypt
        key1 = secrets.token_urlsafe(32)
        vault1 = CryptoVault(master_key=key1)
        test_data = "Secret SSH Key Data"
        ciphertext, iv, tag = vault1.encrypt(test_data)
        
        # Try to decrypt with different key
        key2 = secrets.token_urlsafe(32)
        vault2 = CryptoVault(master_key=key2)
        
        try:
            vault2.decrypt(ciphertext, iv, tag)
            raise AssertionError("Decryption should fail with wrong key")
        except ValueError as e:
            assert "Decryption failed" in str(e), f"Expected decryption error, got: {e}"
            print("  ✓ Wrong key correctly rejected")
    
    @staticmethod
    def test_tampered_ciphertext_fails():
        """Test that tampered ciphertext fails decryption"""
        print("\nTest 3: Tampered Ciphertext Fails")
        
        # Create vault and encrypt
        test_key = secrets.token_urlsafe(32)
        vault = CryptoVault(master_key=test_key)
        test_data = "Secret SSH Key Data"
        ciphertext, iv, tag = vault.encrypt(test_data)
        
        # Tamper with ciphertext
        tampered = bytearray(ciphertext)
        tampered[0] ^= 0xFF  # Flip all bits in first byte
        
        try:
            vault.decrypt(bytes(tampered), iv, tag)
            raise AssertionError("Decryption should fail with tampered ciphertext")
        except ValueError as e:
            assert "Decryption failed" in str(e), f"Expected decryption error, got: {e}"
            print("  ✓ Tampered ciphertext correctly rejected")
    
    @staticmethod
    def test_tampered_tag_fails():
        """Test that tampered auth tag fails decryption"""
        print("\nTest 4: Tampered Auth Tag Fails")
        
        # Create vault and encrypt
        test_key = secrets.token_urlsafe(32)
        vault = CryptoVault(master_key=test_key)
        test_data = "Secret SSH Key Data"
        ciphertext, iv, tag = vault.encrypt(test_data)
        
        # Tamper with tag
        tampered_tag = bytearray(tag)
        tampered_tag[0] ^= 0xFF
        
        try:
            vault.decrypt(ciphertext, iv, bytes(tampered_tag))
            raise AssertionError("Decryption should fail with tampered tag")
        except ValueError as e:
            assert "Decryption failed" in str(e), f"Expected decryption error, got: {e}"
            print("  ✓ Tampered auth tag correctly rejected")
    
    @staticmethod
    def test_tampered_iv_fails():
        """Test that tampered IV fails decryption"""
        print("\nTest 5: Tampered IV Fails")
        
        # Create vault and encrypt
        test_key = secrets.token_urlsafe(32)
        vault = CryptoVault(master_key=test_key)
        test_data = "Secret SSH Key Data"
        ciphertext, iv, tag = vault.encrypt(test_data)
        
        # Tamper with IV
        tampered_iv = bytearray(iv)
        tampered_iv[0] ^= 0xFF
        
        try:
            vault.decrypt(ciphertext, bytes(tampered_iv), tag)
            raise AssertionError("Decryption should fail with tampered IV")
        except ValueError as e:
            assert "Decryption failed" in str(e), f"Expected decryption error, got: {e}"
            print("  ✓ Tampered IV correctly rejected")
    
    @staticmethod
    def test_empty_plaintext_fails():
        """Test that empty plaintext is rejected"""
        print("\nTest 6: Empty Plaintext Fails")
        
        test_key = secrets.token_urlsafe(32)
        vault = CryptoVault(master_key=test_key)
        
        try:
            vault.encrypt("")
            raise AssertionError("Empty plaintext should be rejected")
        except ValueError as e:
            assert "cannot be empty" in str(e).lower(), f"Expected empty error, got: {e}"
            print("  ✓ Empty plaintext correctly rejected")
    
    @staticmethod
    def test_base64_encoding():
        """Test base64 encoding/decoding helpers"""
        print("\nTest 7: Base64 Encoding/Decoding")
        
        test_key = secrets.token_urlsafe(32)
        vault = CryptoVault(master_key=test_key)
        test_data = "Secret SSH Key Data"
        
        # Encrypt to base64
        ciphertext_b64, iv_b64, tag_b64 = vault.encrypt_to_base64(test_data)
        
        # Verify base64 format (ASCII strings)
        assert isinstance(ciphertext_b64, str), "Ciphertext should be string"
        assert isinstance(iv_b64, str), "IV should be string"
        assert isinstance(tag_b64, str), "Tag should be string"
        
        # Decrypt from base64
        decrypted = vault.decrypt_from_base64(ciphertext_b64, iv_b64, tag_b64)
        
        # Verify
        assert decrypted == test_data, "Base64 roundtrip should work"
        print("  ✓ Base64 encoding/decoding works correctly")
    
    @staticmethod
    def test_deterministic_key_derivation():
        """Test that same master key produces same derived key"""
        print("\nTest 8: Deterministic Key Derivation")
        
        test_key = "my-test-master-key"
        
        # Create two vaults with same master key
        vault1 = CryptoVault(master_key=test_key)
        vault2 = CryptoVault(master_key=test_key)
        
        test_data = "Test data"
        
        # Encrypt with vault1
        ciphertext, iv, tag = vault1.encrypt(test_data)
        
        # Decrypt with vault2 (should work if keys match)
        decrypted = vault2.decrypt(ciphertext, iv, tag)
        
        assert decrypted == test_data, "Same master key should allow decryption"
        print("  ✓ Key derivation is deterministic")
    
    @staticmethod
    def test_unique_iv_per_encryption():
        """Test that each encryption uses a unique IV"""
        print("\nTest 9: Unique IV per Encryption")
        
        test_key = secrets.token_urlsafe(32)
        vault = CryptoVault(master_key=test_key)
        test_data = "Test data"
        
        # Encrypt same data multiple times
        _, iv1, _ = vault.encrypt(test_data)
        _, iv2, _ = vault.encrypt(test_data)
        _, iv3, _ = vault.encrypt(test_data)
        
        # Verify IVs are different
        assert iv1 != iv2, "IVs should be unique"
        assert iv2 != iv3, "IVs should be unique"
        assert iv1 != iv3, "IVs should be unique"
        
        print("  ✓ Each encryption uses unique IV")


def run_all_tests():
    """Run all test cases"""
    print("=" * 60)
    print("CryptoVault Unit Tests")
    print("=" * 60)
    
    test_cases = [
        TestCryptoVault.test_encrypt_decrypt_roundtrip,
        TestCryptoVault.test_wrong_key_fails,
        TestCryptoVault.test_tampered_ciphertext_fails,
        TestCryptoVault.test_tampered_tag_fails,
        TestCryptoVault.test_tampered_iv_fails,
        TestCryptoVault.test_empty_plaintext_fails,
        TestCryptoVault.test_base64_encoding,
        TestCryptoVault.test_deterministic_key_derivation,
        TestCryptoVault.test_unique_iv_per_encryption,
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
