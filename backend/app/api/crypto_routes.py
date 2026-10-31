from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.schemas.crypto_schema import EncryptRequest, EncryptResponse, DecryptRequest, DecryptResponse
from app.security.validators import validate_key_id
from app.services import key_service
from app.services.crypto_service import encrypt_message, decrypt_message
from app.services.audit_service import log_event

router = APIRouter(prefix="/crypto", tags=["crypto"])


@router.post("/encrypt", response_model=EncryptResponse)
def encrypt(payload: EncryptRequest, db: Session = Depends(get_db)):
    key_id = validate_key_id(payload.key_id)
    key_material = key_service.get_raw_key_material(db, key_id)
    result = encrypt_message(key_material, payload.plaintext)
    log_event(db, "ENCRYPTION", status="SUCCESS", source="AES-256-GCM", details=f"key_id={key_id}")
    return EncryptResponse(key_id=key_id, algorithm="AES-256-GCM", **result)


@router.post("/decrypt", response_model=DecryptResponse)
def decrypt(payload: DecryptRequest, db: Session = Depends(get_db)):
    key_id = validate_key_id(payload.key_id)
    key_material = key_service.get_raw_key_material(db, key_id)
    plaintext = decrypt_message(key_material, payload.ciphertext, payload.nonce, payload.tag)
    log_event(db, "DECRYPTION", status="SUCCESS", source="AES-256-GCM", details=f"key_id={key_id}")
    return DecryptResponse(key_id=key_id, plaintext=plaintext)
