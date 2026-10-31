"""
Entropy fusion service.

Combines quantum (external QRNG) and classical (OS CSPRNG) entropy into a
single output via a cryptographic hash:

    combined = SHA-256(qrng_bytes || csprng_bytes)

Rationale: if either source is ever weaker than expected, the fused output
is no weaker than the best of the two inputs (assuming SHA-256 behaves as a
random oracle). This is a defense-in-depth design choice, not a formal
mathematical guarantee against every conceivable failure mode of either
underlying source.
"""
import hashlib
from typing import Dict, Any

from app.services.qrng_service import qrng_service, QRNGUnavailableError
from app.services.csprng_service import csprng_service


async def fuse_entropy(n_bytes: int = 32) -> Dict[str, Any]:
    classical = csprng_service.get_random_bytes(n_bytes)
    classical_bytes = bytes.fromhex(classical["hex"])

    quantum_available = True
    quantum_bytes = b""
    try:
        quantum = await qrng_service.get_random_bytes(n_bytes)
        quantum_bytes = bytes.fromhex(quantum["hex"])
    except QRNGUnavailableError:
        quantum_available = False

    if quantum_available:
        combined = hashlib.sha256(quantum_bytes + classical_bytes).digest()
    else:
        # Quantum source unavailable: fuse using classical entropy alone,
        # clearly reported as such rather than silently mislabeled.
        combined = hashlib.sha256(classical_bytes).digest()

    return {
        "quantum_source": "available" if quantum_available else "unavailable",
        "classical_source": "available",
        "fusion_method": "SHA-256",
        "output_bits": len(combined) * 8,
        "output_hex": combined.hex(),
    }
