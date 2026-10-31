"""
CSPRNG Service - classical cryptographically secure pseudorandom generator.

Uses Python's `secrets` module (which in turn draws from the operating
system's CSPRNG, e.g. /dev/urandom or CryptGenRandom). This is
cryptographically secure when used correctly and is NOT "insecure" or
"broken" - it is used here as:

  1. A comparison baseline against the external QRNG.
  2. An explicit, clearly-labeled fallback source when the QRNG is
     unavailable (only if ALLOW_CSPRNG_FALLBACK=true).
  3. One input into the entropy-fusion mechanism.

We deliberately never use the `random` module for any security-relevant
value.
"""
import secrets
import uuid
from datetime import datetime, timezone
from typing import Dict, Any


class CSPRNGService:
    def __init__(self):
        self.total_requests = 0

    def get_random_bytes(self, n: int) -> Dict[str, Any]:
        self.total_requests += 1
        raw = secrets.token_bytes(n)
        return {
            "source": "csprng",
            "provider": "os_csprng",
            "bytes": n,
            "bits": n * 8,
            "hex": raw.hex(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": f"csprng-{uuid.uuid4().hex[:12]}",
        }

    def get_random_bits(self, n_bits: int) -> Dict[str, Any]:
        n_bytes = (n_bits + 7) // 8
        result = self.get_random_bytes(n_bytes)
        result["bits_requested"] = n_bits
        return result

    def health_check(self) -> Dict[str, Any]:
        # The OS CSPRNG is treated as always available on any modern OS.
        try:
            secrets.token_bytes(4)
            return {"status": "ONLINE", "provider": "os_csprng"}
        except Exception as exc:  # pragma: no cover - practically unreachable
            return {"status": "OFFLINE", "provider": "os_csprng", "error": str(exc)}


csprng_service = CSPRNGService()
