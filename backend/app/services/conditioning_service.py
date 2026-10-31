"""
Entropy conditioning service.

Conditioning passes raw entropy through a cryptographic hash / KDF to
whiten it (remove statistical bias) and to derive key material of a
specific length.

IMPORTANT: Conditioning does NOT create entropy. If the input has, say,
100 bits of real min-entropy spread across 256 raw bits, the output of
SHA-256/HKDF is at most as unpredictable as that input entropy - hashing
cannot manufacture unpredictability that was not already present upstream.
Conditioning only improves the *statistical* distribution of the output.
"""
import hashlib
import hmac
from typing import Optional


def condition_entropy(data: bytes) -> bytes:
    """
    Whiten raw entropy with SHA-256.

    raw entropy -> SHA-256 -> conditioned entropy (32 bytes)
    """
    return hashlib.sha256(data).digest()


def hkdf_extract(salt: bytes, input_key_material: bytes) -> bytes:
    if not salt:
        salt = b"\x00" * hashlib.sha256().digest_size
    return hmac.new(salt, input_key_material, hashlib.sha256).digest()


def hkdf_expand(pseudo_random_key: bytes, info: bytes, length: int) -> bytes:
    hash_len = hashlib.sha256().digest_size
    n = (length + hash_len - 1) // hash_len
    if n > 255:
        raise ValueError("Requested length too large for HKDF-SHA256")

    t = b""
    okm = b""
    for i in range(1, n + 1):
        t = hmac.new(pseudo_random_key, t + info + bytes([i]), hashlib.sha256).digest()
        okm += t
    return okm[:length]


def derive_key_material(
    data: bytes,
    length: int = 32,
    salt: Optional[bytes] = None,
    info: bytes = b"q-key-derivation",
) -> bytes:
    """
    Derive `length` bytes of key material from raw entropy using
    HKDF-SHA256 (RFC 5869): extract-then-expand.
    """
    salt = salt or b""
    prk = hkdf_extract(salt, data)
    return hkdf_expand(prk, info, length)
