from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.schemas.key_schema import KeyGenerateRequest, KeyResponse, KeyActionResponse
from app.security.validators import validate_source, validate_key_id
from app.services import key_service

router = APIRouter(prefix="/keys", tags=["keys"])


def _to_response(record) -> KeyResponse:
    return KeyResponse(
        key_id=record.key_id,
        algorithm=record.algorithm,
        key_size=record.key_size,
        key_version=record.key_version,
        source=record.source,
        status=record.status,
        created_at=record.created_at,
        expires_at=record.expires_at,
        rotated_from=record.rotated_from,
        demo_preview=key_service.demo_preview_for(record),
    )


@router.post("/generate", response_model=KeyResponse)
async def generate_key(payload: KeyGenerateRequest, db: Session = Depends(get_db)):
    source = validate_source(payload.source)
    record = await key_service.generate_key(db, source=source, algorithm=payload.algorithm, label=payload.label)
    return _to_response(record)


@router.get("", response_model=List[KeyResponse])
def list_keys(db: Session = Depends(get_db)):
    records = key_service.list_keys(db)
    return [_to_response(r) for r in records]


@router.get("/{key_id}", response_model=KeyResponse)
def get_key(key_id: str, db: Session = Depends(get_db)):
    key_id = validate_key_id(key_id)
    record = key_service.get_key(db, key_id)
    return _to_response(record)


@router.post("/{key_id}/rotate", response_model=KeyResponse)
async def rotate_key(key_id: str, db: Session = Depends(get_db)):
    key_id = validate_key_id(key_id)
    record = await key_service.rotate_key(db, key_id)
    return _to_response(record)


@router.post("/{key_id}/revoke", response_model=KeyActionResponse)
def revoke_key(key_id: str, db: Session = Depends(get_db)):
    key_id = validate_key_id(key_id)
    record = key_service.revoke_key(db, key_id)
    return KeyActionResponse(key_id=record.key_id, status=record.status, message="Key revoked successfully.")
