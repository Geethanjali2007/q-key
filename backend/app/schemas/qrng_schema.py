from pydantic import BaseModel, Field
from typing import Optional


class RandomRequest(BaseModel):
    n_bytes: int = Field(32, ge=1, le=1024, description="Number of random bytes requested")
    source: str = Field("qrng", description="'qrng' or 'csprng'")


class RandomResponse(BaseModel):
    source: str
    provider: Optional[str] = None
    bytes: int
    bits: int
    hex: str
    timestamp: str
    request_id: str
    fallback_used: bool = False
    warning: Optional[str] = None


class QRNGStatusResponse(BaseModel):
    provider: str
    status: str  # ONLINE | OFFLINE | DEGRADED
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    total_requests: int
    failed_requests: int
    fallback_count: int
    allow_fallback: bool
