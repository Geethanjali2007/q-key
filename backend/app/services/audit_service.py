"""
Audit service - writes security events to the audit_logs table.

Never pass plaintext passwords, plaintext secret keys, or authentication
tokens into `details` - only high-level metadata.
"""
from sqlalchemy.orm import Session

from app.models.audit_model import AuditLog


def log_event(db: Session, event_type: str, status: str = "SUCCESS", source: str = "SYSTEM", details: str = ""):
    entry = AuditLog(event_type=event_type, status=status, source=source, details=details)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_logs(db: Session, limit: int = 200):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )
