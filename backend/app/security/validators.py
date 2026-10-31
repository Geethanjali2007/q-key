"""
Input validation helpers used by API routes, beyond what Pydantic already
enforces on field types/ranges.
"""
from fastapi import HTTPException

ALLOWED_SOURCES = {"qrng", "csprng", "fusion"}


def validate_source(source: str) -> str:
    source = (source or "").lower()
    if source not in ALLOWED_SOURCES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source '{source}'. Must be one of {sorted(ALLOWED_SOURCES)}.",
        )
    return source


def validate_key_id(key_id: str) -> str:
    if not key_id or not key_id.startswith("QK-") or len(key_id) > 64:
        raise HTTPException(status_code=400, detail="Invalid key_id format.")
    return key_id
