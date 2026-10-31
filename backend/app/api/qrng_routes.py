from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.schemas.qrng_schema import RandomRequest, RandomResponse, QRNGStatusResponse
from app.services.qrng_service import qrng_service, QRNGUnavailableError
from app.services.csprng_service import csprng_service
from app.services.audit_service import log_event
from app.services.health_service import record_fallback
from app.security.validators import validate_source
from app.config import settings

router = APIRouter(prefix="/qrng", tags=["qrng"])


@router.get("/status", response_model=QRNGStatusResponse)
async def qrng_status():
    health = await qrng_service.health_check()
    return QRNGStatusResponse(
        provider=qrng_service.provider,
        status=health["status"],
        last_success=qrng_service.last_success_ts,
        last_failure=qrng_service.last_failure_ts,
        total_requests=qrng_service.total_requests,
        failed_requests=qrng_service.failed_requests,
        fallback_count=0,
        allow_fallback=settings.ALLOW_CSPRNG_FALLBACK,
    )


@router.post("/random", response_model=RandomResponse)
async def get_random(payload: RandomRequest, db: Session = Depends(get_db)):
    source = validate_source(payload.source)

    if source == "csprng":
        result = csprng_service.get_random_bytes(payload.n_bytes)
        log_event(db, "QRNG_REQUEST", status="SUCCESS", source="CSPRNG", details=f"bytes={payload.n_bytes}")
        return RandomResponse(**result, fallback_used=False)

    try:
        result = await qrng_service.get_random_bytes(payload.n_bytes)
        log_event(db, "QRNG_REQUEST", status="SUCCESS", source="QRNG", details=f"bytes={payload.n_bytes}")
        return RandomResponse(**result, fallback_used=False)
    except QRNGUnavailableError as exc:
        log_event(db, "QRNG_FAILURE", status="FAILURE", source="QRNG", details=str(exc))
        if not settings.ALLOW_CSPRNG_FALLBACK:
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail=f"QRNG unavailable: {exc}")

        record_fallback()
        result = csprng_service.get_random_bytes(payload.n_bytes)
        log_event(db, "CSPRNG_FALLBACK", status="WARNING", source="CSPRNG",
                   details=f"QRNG unavailable, fell back to CSPRNG: {exc}")
        return RandomResponse(
            **result,
            fallback_used=True,
            warning="External QRNG was unavailable. This response used the CSPRNG fallback, "
                    "clearly labeled as such - it was NOT silently presented as quantum data.",
        )
