"""
AES-256-GCM authenticated encryption service.

Uses the `cryptography` library's AESGCM implementation - AES is NEVER
implemented manually here. A fresh, cryptographically random 96-bit nonce
is generated for every single encryption operation, as required for
GCM's security guarantees.
"""
import base64
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from fastapi import HTTPException


def encrypt_message(key: bytes, plaintext: str) -> dict:
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)  # 96-bit nonce, unique per encryption
    plaintext_bytes = plaintext.encode("utf-8")

    # AESGCM.encrypt() returns ciphertext with the 16-byte auth tag appended.
    ct_with_tag = aesgcm.encrypt(nonce, plaintext_bytes, associated_data=None)
    ciphertext, tag = ct_with_tag[:-16], ct_with_tag[-16:]

    return {
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "tag": base64.b64encode(tag).decode(),
    }


def decrypt_message(key: bytes, ciphertext_b64: str, nonce_b64: str, tag_b64: str) -> str:
    try:
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        tag = base64.b64decode(tag_b64)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid base64 encoding in request") from exc

    aesgcm = AESGCM(key)
    try:
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext + tag, associated_data=None)
    except InvalidTag as exc:
        raise HTTPException(
            status_code=400,
            detail="Decryption failed: authentication tag mismatch (wrong key, tampered ciphertext, or wrong nonce).",
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Decryption failed: {exc}") from exc

    return plaintext_bytes.decode("utf-8")
