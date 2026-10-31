"""
Small security utility helpers shared across services.
"""
import uuid


def new_key_id() -> str:
    """Generate a public, non-secret identifier for a key record."""
    return f"QK-{uuid.uuid4().hex[:16].upper()}"


def mask_hex(hex_str: str, visible: int = 4) -> str:
    """Return a masked preview of hex-encoded secret material, e.g. 'a1b2****...****f9e0'."""
    if len(hex_str) <= visible * 2:
        return "*" * len(hex_str)
    return f"{hex_str[:visible]}{'*' * 8}{hex_str[-visible:]}"
