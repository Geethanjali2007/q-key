import secrets
import base64

import pytest
from fastapi import HTTPException

from app.services.crypto_service import encrypt_message, decrypt_message


def test_encrypt_decrypt_round_trip():
    key = secrets.token_bytes(32)
    plaintext = "Quantum-secured transaction"

    enc = encrypt_message(key, plaintext)
    decrypted = decrypt_message(key, enc["ciphertext"], enc["nonce"], enc["tag"])

    assert decrypted == plaintext


def test_nonce_is_unique_per_call():
    key = secrets.token_bytes(32)
    enc1 = encrypt_message(key, "same message")
    enc2 = encrypt_message(key, "same message")
    assert enc1["nonce"] != enc2["nonce"]
    assert enc1["ciphertext"] != enc2["ciphertext"]


def test_decrypt_with_wrong_key_fails():
    key = secrets.token_bytes(32)
    wrong_key = secrets.token_bytes(32)
    enc = encrypt_message(key, "top secret")

    with pytest.raises(HTTPException):
        decrypt_message(wrong_key, enc["ciphertext"], enc["nonce"], enc["tag"])


def test_decrypt_with_tampered_ciphertext_fails():
    key = secrets.token_bytes(32)
    enc = encrypt_message(key, "top secret")

    tampered_bytes = bytearray(base64.b64decode(enc["ciphertext"]))
    tampered_bytes[0] ^= 0xFF
    tampered_ciphertext = base64.b64encode(bytes(tampered_bytes)).decode()

    with pytest.raises(HTTPException):
        decrypt_message(key, tampered_ciphertext, enc["nonce"], enc["tag"])
