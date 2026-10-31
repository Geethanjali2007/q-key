"""
ORM model for security / audit events.

Never store plaintext passwords, plaintext secret keys, or authentication
tokens in this table - only high-level metadata about what happened.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, timezone

from app.models.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    event_type = Column(String(64), nullable=False, index=True)
    status = Column(String(16), nullable=False, default="SUCCESS")  # SUCCESS | FAILURE | WARNING
    source = Column(String(32), nullable=True)  # QRNG | CSPRNG | FUSION | SYSTEM
    details = Column(Text, nullable=True)
