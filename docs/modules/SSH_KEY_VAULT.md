# Module 1: SSH Key Vault

## Overview
Secure storage and management of SSH private keys with AES-256-GCM encryption for use with terminal and remote command execution.

## Security Requirements

### Encryption
- **Algorithm:** AES-256-GCM (Galois/Counter Mode)
- **Key Size:** 256 bits (32 bytes)
- **IV Size:** 12 bytes (96 bits) - random per encryption
- **Auth Tag:** 16 bytes (128 bits)
- **Master Key:** From environment variable `KEY_VAULT_MASTER_KEY`
- **Key Derivation:** PBKDF2-HMAC-SHA256 with 100,000 iterations

### Security Properties
- ✅ Confidentiality: AES-256 encryption
- ✅ Integrity: GCM authentication tag prevents tampering
- ✅ Freshness: Random IV per encryption prevents replay
- ✅ No plaintext storage: Keys only decrypted in RAM when needed
- ✅ Database compromise: Encrypted keys unreadable without master key
- ✅ No logging: Private keys never logged

## Database Schema

```sql
CREATE TABLE ssh_keys (
    id TEXT PRIMARY KEY,              -- UUID v4
    name TEXT NOT NULL UNIQUE,        -- User-friendly name
    description TEXT,                 -- Optional description
    public_key TEXT,                  -- SSH public key (for display/fingerprint)
    private_key_enc BLOB NOT NULL,    -- Encrypted private key
    iv BLOB NOT NULL,                 -- Initialization vector (12 bytes)
    auth_tag BLOB NOT NULL,           -- Authentication tag (16 bytes)
    key_type TEXT DEFAULT 'rsa',      -- rsa, ed25519, ecdsa, etc.
    fingerprint TEXT,                 -- SSH key fingerprint (SHA256)
    created_by_user_id INTEGER,       -- User who created this key
    created_at TEXT NOT NULL,         -- ISO 8601 timestamp
    updated_at TEXT NOT NULL,         -- ISO 8601 timestamp
    deleted_at TEXT,                  -- Soft delete timestamp
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_ssh_keys_created_by ON ssh_keys(created_by_user_id);
CREATE INDEX idx_ssh_keys_deleted_at ON ssh_keys(deleted_at);
```

## API Endpoints

### 1. List SSH Keys
```
GET /api/ssh-keys
Authorization: Bearer <token>
Permission: admin, operator

Response 200:
{
  "keys": [
    {
      "id": "uuid",
      "name": "Production Key",
      "description": "...",
      "key_type": "rsa",
      "fingerprint": "SHA256:...",
      "created_at": "2026-01-07T...",
      "created_by": "admin"
    }
  ]
}
```

### 2. Create SSH Key
```
POST /api/ssh-keys
Authorization: Bearer <token>
Permission: admin, operator
Content-Type: application/json

Request:
{
  "name": "Production Key",
  "description": "Key for production servers",
  "private_key": "-----BEGIN OPENSSH PRIVATE KEY-----\n..."
}

Response 201:
{
  "id": "uuid",
  "name": "Production Key",
  "fingerprint": "SHA256:...",
  "message": "SSH key created successfully"
}
```

### 3. Get SSH Key (metadata only)
```
GET /api/ssh-keys/{id}
Authorization: Bearer <token>
Permission: admin, operator

Response 200:
{
  "id": "uuid",
  "name": "Production Key",
  "description": "...",
  "key_type": "rsa",
  "fingerprint": "SHA256:...",
  "public_key": "ssh-rsa AAAA...",
  "created_at": "...",
  "created_by": "admin"
}
```

### 4. Delete SSH Key (soft delete)
```
DELETE /api/ssh-keys/{id}
Authorization: Bearer <token>
Permission: admin

Response 200:
{
  "message": "SSH key deleted successfully"
}
```

### 5. Get Decrypted Key (internal use only)
```
Internal function: get_decrypted_key(key_id: str) -> str
- Only used server-side for SSH connections
- Never exposed via HTTP API
- Decrypts key in RAM and returns as string
- Should be cleared from memory after use (best-effort)
```

## Testing Requirements

### Unit Tests
1. **Encryption/Decryption**
   - Test encrypt → decrypt roundtrip
   - Test wrong key fails decryption
   - Test tampered ciphertext fails (auth tag)
   - Test tampered IV fails
   - Test empty/invalid input handling

2. **Key Management**
   - Test create key with valid SSH private key
   - Test reject invalid SSH key format
   - Test list keys (metadata only)
   - Test get key (no private key in response)
   - Test soft delete
   - Test fingerprint calculation

### Integration Tests
1. Create key → Use in terminal connection
2. Create key → List keys → Delete key
3. Test RBAC (viewer cannot access)

## Environment Setup
```bash
# Generate secure master key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
KEY_VAULT_MASTER_KEY=<generated_key>
```
