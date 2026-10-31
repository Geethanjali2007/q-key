"""
Key Manager - PROTOTYPE at-rest protection for generated key material.

This is a hackathon prototype, not a production key-vault / HSM. Generated
AES-256-GCM keys are themselves encrypted ("wrapped") with a local wrapping
key before being stored in SQLite, using AES-256-GCM. The wrapping key is
derived once from a local secret file (created automatically on first run)
so plaintext key material is never written to disk.

Limitations (documented, not hidden):
  - The wrapping key itself lives on the same machine as the database, so
    this does not protect against full local compromise the way a real
    HSM / cloud KMS would.
  - There is no key-rotation-of-the-wrapping-key mechanism in this
    prototype.
"""
import os
import secrets
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_WRAP_KEY_PATH = Path(__file__).resolve().parent.parent.parent / ".wrap_key"


def _load_or_create_wrap_key() -> bytes:
    if _WRAP_KEY_PATH.exists():
        return bytes.fromhex(_WRAP_KEY_PATH.read_text().strip())
    key = secrets.token_bytes(32)
    _WRAP_KEY_PATH.write_text(key.hex())
    try:
        os.chmod(_WRAP_KEY_PATH, 0o600)
    except OSError:
        pass  # best-effort on platforms (e.g. some Windows setups) without POSIX perms
    return key


_wrap_key = _load_or_create_wrap_key()


def wrap_key_material(plaintext_key: bytes) -> str:
    """Encrypt raw key material for storage. Returns 'nonce_hex:ciphertext_hex'."""
    aesgcm = AESGCM(_wrap_key)
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext_key, associated_data=b"qkey-wrap-v1")
    return f"{nonce.hex()}:{ciphertext.hex()}"


def unwrap_key_material(wrapped: str) -> bytes:
    """Decrypt key material previously produced by wrap_key_material()."""
    aesgcm = AESGCM(_wrap_key)
    nonce_hex, ciphertext_hex = wrapped.split(":")
    nonce = bytes.fromhex(nonce_hex)
    ciphertext = bytes.fromhex(ciphertext_hex)
    return aesgcm.decrypt(nonce, ciphertext, associated_data=b"qkey-wrap-v1")
