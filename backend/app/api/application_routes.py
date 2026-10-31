"""
Simulated application integrations (banking, IoT, digital identity) plus
the QRNG-vs-CSPRNG comparison lab and the audit log endpoint.

None of these demos connect to any real bank, real IoT device, or real
identity provider. They exist purely to show how an application would
request trusted key material from the Q-Key platform.
"""
import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services import key_service
from app.services.crypto_service import encrypt_message
from app.services.qrng_service import qrng_service
from app.services.csprng_service import csprng_service
from app.services.entropy_service import analyze
from app.services.audit_service import log_event, get_logs

router = APIRouter(tags=["applications"])


@router.get("/applications/status")
async def applications_status(db: Session = Depends(get_db)):
    qrng_health = await qrng_service.health_check()
    return {
        "qrng_status": qrng_health["status"],
        "available_demos": ["banking", "iot", "identity"],
    }


@router.post("/applications/banking/demo")
async def banking_demo(db: Session = Depends(get_db)):
    steps = []

    tx_id = f"TX-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:6].upper()}"
    steps.append({"step": "Transaction received", "detail": f"{tx_id} | Demo User | INR 10,000"})

    key_record = await key_service.generate_key(db, source="qrng", label=f"banking-session-{tx_id}")
    steps.append({"step": "Quantum entropy requested", "detail": f"source={key_record.source}"})
    steps.append({"step": "Entropy validated", "detail": "statistical tests evaluated during key generation"})
    steps.append({"step": "Session key generated", "detail": f"key_id={key_record.key_id}"})

    key_material = key_service.get_raw_key_material(db, key_record.key_id)
    enc = encrypt_message(key_material, f"TRANSACTION:{tx_id}:AMOUNT:10000:CURRENCY:INR")
    steps.append({"step": "Transaction protected", "detail": "AES-256-GCM authenticated encryption applied"})

    log_event(db, "KEY_GENERATED", status="SUCCESS", source=key_record.source,
               details=f"banking demo tx={tx_id} key_id={key_record.key_id}")

    return {
        "transaction_id": tx_id,
        "user": "Demo User",
        "amount": "INR 10,000",
        "key_id": key_record.key_id,
        "key_source": key_record.source,
        "ciphertext": enc["ciphertext"],
        "steps": steps,
        "note": "Simulated integration - not connected to any real bank.",
    }


@router.post("/applications/iot/demo")
async def iot_demo(db: Session = Depends(get_db)):
    device_id = "IOT-SENSOR-001"
    steps = [{"step": "Device registration requested", "detail": device_id}]

    key_record = await key_service.generate_key(db, source="qrng", label=f"iot-{device_id}")
    steps.append({"step": "QRNG entropy acquired", "detail": f"source={key_record.source}"})
    steps.append({"step": "Key generated", "detail": f"key_id={key_record.key_id}"})
    steps.append({"step": "Device identity bound", "detail": device_id})
    steps.append({"step": "Secure communication session established", "detail": "AES-256-GCM channel ready"})

    log_event(db, "KEY_GENERATED", status="SUCCESS", source=key_record.source,
               details=f"iot demo device={device_id} key_id={key_record.key_id}")

    return {
        "device_id": device_id,
        "status": "ONLINE",
        "authenticated": True,
        "key_active": True,
        "key_id": key_record.key_id,
        "steps": steps,
        "note": "Simulated IoT device - no physical hardware is connected.",
    }


@router.post("/applications/identity/demo")
async def identity_demo(db: Session = Depends(get_db)):
    steps = [{"step": "User login initiated", "detail": "Demo User (no real credentials stored)"}]

    key_record = await key_service.generate_key(db, source="qrng", label="identity-session")
    steps.append({"step": "Secure session key requested", "detail": ""})
    steps.append({"step": "Quantum entropy acquired", "detail": f"source={key_record.source}"})
    steps.append({"step": "Key generated", "detail": f"key_id={key_record.key_id}"})
    steps.append({"step": "Session secured", "detail": "AES-256-GCM session key active"})

    log_event(db, "KEY_GENERATED", status="SUCCESS", source=key_record.source,
               details=f"identity demo key_id={key_record.key_id}")

    return {
        "session_id": f"SESSION-{uuid.uuid4().hex[:8].upper()}",
        "user": "Demo User",
        "key_id": key_record.key_id,
        "steps": steps,
        "note": "Simulated authentication flow - no real credentials are stored or verified.",
    }


@router.get("/comparison/qrng-csprng")
async def comparison(db: Session = Depends(get_db), n_bits: int = 100000):
    n_bytes = n_bits // 8

    from app.services.qrng_service import QRNGUnavailableError

    qrng_latency = None
    qrng_analysis = None
    qrng_error = None
    try:
        start = time.perf_counter()
        qrng_raw = await qrng_service.get_random_bytes(n_bytes)
        qrng_latency = round((time.perf_counter() - start) * 1000, 2)
        qrng_analysis = analyze(bytes.fromhex(qrng_raw["hex"]))
    except QRNGUnavailableError as exc:
        qrng_error = str(exc)
        log_event(db, "QRNG_FAILURE", status="FAILURE", source="QRNG", details=qrng_error)

    start = time.perf_counter()
    csprng_raw = csprng_service.get_random_bytes(n_bytes)
    csprng_latency = round((time.perf_counter() - start) * 1000, 2)
    csprng_analysis = analyze(bytes.fromhex(csprng_raw["hex"]))

    log_event(db, "ENTROPY_ANALYSIS", status="SUCCESS", source="COMPARISON",
               details=f"n_bits={n_bits} qrng_available={qrng_error is None}")

    return {
        "n_bits": n_bits,
        "qrng": {
            "available": qrng_error is None,
            "error": qrng_error,
            "latency_ms": qrng_latency,
            "throughput_bytes_per_sec": round(n_bytes / (qrng_latency / 1000), 2) if qrng_latency else None,
            "analysis": qrng_analysis,
        },
        "csprng": {
            "available": True,
            "latency_ms": csprng_latency,
            "throughput_bytes_per_sec": round(n_bytes / (csprng_latency / 1000), 2) if csprng_latency else None,
            "analysis": csprng_analysis,
        },
        "note": (
            "Both QRNG and properly designed CSPRNG output can appear statistically random. "
            "QRNG's distinguishing property is its physical quantum entropy source, not simply "
            "passing statistical tests."
        ),
    }


@router.get("/audit/logs")
def audit_logs(limit: int = 200, db: Session = Depends(get_db)):
    logs = get_logs(db, limit=limit)
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "event": log.event_type,
            "source": log.source,
            "status": log.status,
            "details": log.details,
        }
        for log in logs
    ]
