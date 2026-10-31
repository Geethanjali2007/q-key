"""
ORM model for cryptographic key metadata.

IMPORTANT: In this hackathon prototype, if key material is persisted at all,
it is stored ENCRYPTED-AT-REST using a local wrapping key (see
app/security/key_manager.py) and clearly labeled as prototype storage. This
is not a production-grade HSM / key-vault replacement.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, timezone

from app.models.database import Base


class KeyRecord(Base):
    __tablename__ = "keys"

    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(String(64), unique=True, index=True, nullable=False)
    algorithm = Column(String(32), nullable=False, default="AES-256-GCM")
    key_size = Column(Integer, nullable=False, default=256)
    key_version = Column(Integer, nullable=False, default=1)
    source = Column(String(32), nullable=False)  # QRNG | CSPRNG | FUSION
    status = Column(String(16), nullable=False, default="ACTIVE")  # ACTIVE/ROTATED/REVOKED/EXPIRED
    # Encrypted key material at rest (prototype only). Never returned via API.
    wrapped_key = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    rotated_from = Column(String(64), nullable=True)
