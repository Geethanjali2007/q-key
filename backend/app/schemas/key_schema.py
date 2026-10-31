from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class KeyGenerateRequest(BaseModel):
    source: str = Field("qrng", description="'qrng', 'csprng', or 'fusion'")
    algorithm: str = Field("AES-256-GCM")
    label: Optional[str] = Field(None, description="Optional human-readable label")


class KeyResponse(BaseModel):
    key_id: str
    algorithm: str
    key_size: int
    key_version: int
    source: str
    status: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    rotated_from: Optional[str] = None
    demo_preview: Optional[str] = Field(
        None,
        description="Masked preview of key material, ONLY present when DEMO_MODE=true",
    )

    class Config:
        from_attributes = True


class KeyActionResponse(BaseModel):
    key_id: str
    status: str
    message: str
