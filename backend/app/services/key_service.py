"""
Key generation and lifecycle management service.

Pipeline for a new key:

    entropy source (QRNG / CSPRNG / fusion)
        -> entropy validation (statistical tests)
        -> conditioning (SHA-256 / HKDF)
        -> 256-bit key material
        -> wrapped-at-rest storage
        -> key_id issued to caller
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.models.key_model import KeyRecord
from app.services.qrng_service import qrng_service, QRNGUnavailableError
from app.services.csprng_service import csprng_service
from app.services.conditioning_service import derive_key_material
from app.services.entropy_service import analyze
from app.services.fusion_service import fuse_entropy
from app.security.key_manager import wrap_key_material, unwrap_key_material
from app.security.secure_utils import new_key_id, mask_hex
from app.services.audit_service import log_event
from app.services.health_service import record_analysis, record_fallback


async def _acquire_raw_entropy(source: str, db: Session, n_bytes: int = 32):
    """Returns (raw_bytes, actual_source_label, fallback_used)."""
    if source == "fusion":
        fusion = await fuse_entropy(n_bytes)
        return bytes.fromhex(fusion["output_hex"]), "FUSION", fusion["quantum_source"] == "unavailable"

    if source == "csprng":
        result = csprng_service.get_random_bytes(n_bytes)
        return bytes.fromhex(result["hex"]), "CSPRNG", False

    # source == "qrng"
    try:
        result = await qrng_service.get_random_bytes(n_bytes)
        return bytes.fromhex(result["hex"]), "QRNG", False
    except QRNGUnavailableError as exc:
        log_event(db, "QRNG_FAILURE", status="FAILURE", source="QRNG", details=str(exc))
        if not settings.ALLOW_CSPRNG_FALLBACK:
            raise HTTPException(status_code=503, detail="QRNG unavailable and fallback disabled") from exc
        record_fallback()
        log_event(db, "CSPRNG_FALLBACK", status="WARNING", source="CSPRNG",
                   details="Fell back to CSPRNG because QRNG was unavailable")
        result = csprng_service.get_random_bytes(n_bytes)
        return bytes.fromhex(result["hex"]), "CSPRNG_FALLBACK", True


async def generate_key(db: Session, source: str, algorithm: str = "AES-256-GCM", label: Optional[str] = None) -> KeyRecord:
    raw_entropy, actual_source, fallback_used = await _acquire_raw_entropy(source, db)

    # Validate entropy quality before using it for key material.
    analysis = analyze(raw_entropy)
    record_analysis(analysis["overall_quality"], analysis["shannon_entropy_bits_per_byte"], analysis["tests"])
    log_event(db, "ENTROPY_ANALYSIS", status="SUCCESS", source=actual_source,
               details=f"quality={analysis['overall_quality']}")

    # Condition raw entropy into 32 bytes (256 bits) of key material.
    key_material = derive_key_material(raw_entropy, length=32, info=b"q-key-aes256-gcm")

    key_id = new_key_id()
    wrapped = wrap_key_material(key_material)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.DEFAULT_KEY_EXPIRY_DAYS)

    record = KeyRecord(
        key_id=key_id,
        algorithm=algorithm,
        key_size=256,
        key_version=1,
        source=actual_source,
        status="ACTIVE",
        wrapped_key=wrapped,
        expires_at=expires_at,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    log_event(db, "KEY_GENERATED", status="SUCCESS", source=actual_source,
               details=f"key_id={key_id} algorithm={algorithm} label={label or ''}")

    return record


def get_key(db: Session, key_id: str) -> KeyRecord:
    record = db.query(KeyRecord).filter(KeyRecord.key_id == key_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Key not found")
    return record


def list_keys(db: Session):
    _expire_stale_keys(db)
    return db.query(KeyRecord).order_by(KeyRecord.created_at.desc()).all()


def _expire_stale_keys(db: Session):
    now = datetime.now(timezone.utc)
    stale = (
        db.query(KeyRecord)
        .filter(KeyRecord.status == "ACTIVE", KeyRecord.expires_at.isnot(None))
        .all()
    )
    changed = False
    for k in stale:
        expires_at = k.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            k.status = "EXPIRED"
            changed = True
    if changed:
        db.commit()


async def rotate_key(db: Session, key_id: str) -> KeyRecord:
    old = get_key(db, key_id)
    if old.status not in ("ACTIVE",):
        raise HTTPException(status_code=400, detail=f"Cannot rotate a key with status {old.status}")

    old.status = "ROTATED"
    db.commit()

    new_record = await generate_key(db, source="qrng" if old.source.startswith("QRNG") else old.source.lower())
    new_record.key_version = old.key_version + 1
    new_record.rotated_from = old.key_id
    db.commit()
    db.refresh(new_record)

    log_event(db, "KEY_ROTATED", status="SUCCESS", source=new_record.source,
               details=f"old={old.key_id} new={new_record.key_id}")
    return new_record


def revoke_key(db: Session, key_id: str) -> KeyRecord:
    record = get_key(db, key_id)
    if record.status == "REVOKED":
        return record
    record.status = "REVOKED"
    db.commit()
    db.refresh(record)
    log_event(db, "KEY_REVOKED", status="SUCCESS", source=record.source, details=f"key_id={key_id}")
    return record


def get_raw_key_material(db: Session, key_id: str) -> bytes:
    record = get_key(db, key_id)
    if record.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Key '{key_id}' is not ACTIVE (status={record.status})")
    return unwrap_key_material(record.wrapped_key)


def demo_preview_for(record: KeyRecord) -> Optional[str]:
    """Only ever called when DEMO_MODE=true; returns a masked preview, never the raw key."""
    if not settings.DEMO_MODE:
        return None
    try:
        raw = unwrap_key_material(record.wrapped_key)
        return mask_hex(raw.hex())
    except Exception:
        return None
