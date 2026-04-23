# Signing & Key Management

Capacium supports Ed25519 cryptographic signing for capability verification. This provides trust and authenticity guarantees beyond fingerprint integrity checks.

## Key Management

### Generate a Keypair

```bash
cap key generate mykey
```

Keys are stored in `~/.capacium/keys/`:
- `mykey.key` — Private key (keep secret)
- `mykey.pub` — Public key

### List Keys

```bash
cap key list
```

### Export Public Key

```bash
cap key export mykey
```

Outputs the PEM-formatted public key for sharing.

### Import a Key

```bash
cap key import mykey /path/to/key.pem
```

## Signing Capabilities

### Sign a Capability

```bash
cap sign my-skill --key mykey
```

This signs the capability's SHA-256 fingerprint with the private key:
1. Recomputes the fingerprint of the capability's install directory
2. Signs the fingerprint bytes with Ed25519
3. Stores the signature in the registry

For bundles, the bundle fingerprint (computed from sub-cap fingerprints) is signed.

### Verify a Signature

```bash
cap verify my-skill --key mykey
cap verify --all --key mykey
```

Verification:
1. Loads the public key for `mykey`
2. Retrieves the stored signature from the registry
3. Recomputes the capability's fingerprint
4. Verifies the Ed25519 signature over the fingerprint

## Backend Selection

Capacium auto-selects the best available crypto backend:

1. **cryptography** (preferred) — `pip install cryptography`
2. **PyNaCl** — `pip install pynacl`
3. **OpenSSL** (fallback) — Uses `openssl` CLI via subprocess

No backend installation is required for basic operation; OpenSSL is used as a default fallback on most systems.

## Trust Model

```
capability directory
        │
        ▼
  SHA-256 fingerprint  ────►  Ed25519 sign  ────►  signature
        │                                              │
        ▼                                              ▼
  cap verify checks                            cap verify --key verifies
  file integrity only                          fingerprint + signature
```

- **Fingerprint verification** (`cap verify`) detects file tampering
- **Signature verification** (`cap verify --key`) proves authenticity and origin
