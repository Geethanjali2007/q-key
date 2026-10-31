from pydantic import BaseModel, Field


class EncryptRequest(BaseModel):
    key_id: str
    plaintext: str = Field(..., min_length=1, max_length=8192)


class EncryptResponse(BaseModel):
    key_id: str
    algorithm: str
    ciphertext: str  # base64
    nonce: str  # base64
    tag: str  # base64 (authentication tag)


class DecryptRequest(BaseModel):
    key_id: str
    ciphertext: str
    nonce: str
    tag: str


class DecryptResponse(BaseModel):
    key_id: str
    plaintext: str
