from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.schemas.entropy_schema import (
    EntropyAnalyzeRequest,
    EntropyAnalysisResponse,
    FusionRequest,
    FusionResponse,
    EntropyHealthResponse,
)
from app.services.qrng_service import qrng_service, QRNGUnavailableError
from app.services.csprng_service import csprng_service
from app.services.entropy_service import analyze
from app.services.fusion_service import fuse_entropy
from app.services.health_service import get_health_snapshot, record_analysis, record_fallback
from app.services.audit_service import log_event
from app.security.validators import validate_source
from app.config import settings

router = APIRouter(prefix="/entropy", tags=["entropy"])


@router.post("/analyze", response_model=EntropyAnalysisResponse)
async def analyze_entropy(payload: EntropyAnalyzeRequest, db: Session = Depends(get_db)):
    source = validate_source(payload.source)
    fallback_used = False
    actual_source = source.upper()

    if source == "csprng":
        raw = csprng_service.get_random_bytes(payload.n_bytes)
        data = bytes.fromhex(raw["hex"])
    elif source == "fusion":
        fusion = await fuse_entropy(min(payload.n_bytes, 256))
        data = bytes.fromhex(fusion["output_hex"])
        actual_source = "FUSION"
    else:
        try:
            raw = await qrng_service.get_random_bytes(payload.n_bytes)
            data = bytes.fromhex(raw["hex"])
        except QRNGUnavailableError as exc:
            log_event(db, "QRNG_FAILURE", status="FAILURE", source="QRNG", details=str(exc))
            if not settings.ALLOW_CSPRNG_FALLBACK:
                raise HTTPException(status_code=503, detail=f"QRNG unavailable: {exc}")
            record_fallback()
            log_event(db, "CSPRNG_FALLBACK", status="WARNING", source="CSPRNG", details=str(exc))
            raw = csprng_service.get_random_bytes(payload.n_bytes)
            data = bytes.fromhex(raw["hex"])
            fallback_used = True
            actual_source = "CSPRNG_FALLBACK"

    result = analyze(data)
    record_analysis(result["overall_quality"], result["shannon_entropy_bits_per_byte"], result["tests"])
    log_event(db, "ENTROPY_ANALYSIS", status="SUCCESS", source=actual_source,
               details=f"quality={result['overall_quality']} n_bytes={payload.n_bytes}")

    return EntropyAnalysisResponse(source=actual_source, fallback_used=fallback_used, **result)


@router.post("/fuse", response_model=FusionResponse)
async def fuse(payload: FusionRequest, db: Session = Depends(get_db)):
    result = await fuse_entropy(payload.n_bytes)
    log_event(db, "ENTROPY_ANALYSIS", status="SUCCESS", source="FUSION",
               details=f"quantum={result['quantum_source']} classical={result['classical_source']}")
    return FusionResponse(**result)


@router.get("/health", response_model=EntropyHealthResponse)
async def entropy_health():
    snapshot = await get_health_snapshot()
    return EntropyHealthResponse(**snapshot)
