"""
QRNG Service - integration with an EXTERNAL Quantum Random Number Generator
provider.

This module never generates randomness itself. It calls an external API
(default: ANU Quantum Random Numbers Server, which derives randomness from
measurements of vacuum fluctuations) and returns the bytes it receives,
tagged with source metadata.

If the external provider is unreachable, this service raises a
QRNGUnavailableError - it is the caller's responsibility to decide whether to
fall back to a CSPRNG (and if so, to clearly label the result as such).
"""
import base64
import uuid
import binascii
from datetime import datetime, timezone
from typing import Dict, Any

import httpx

from app.config import settings


class QRNGUnavailableError(Exception):
    """Raised when the external QRNG provider cannot supply usable data."""


class QRNGService:
    """Thin, well-documented client for an external QRNG provider."""

    def __init__(self):
        self.provider = settings.QRNG_PROVIDER
        self.api_url = settings.QRNG_API_URL
        self.api_key = settings.QRNG_API_KEY
        self.timeout = settings.QRNG_TIMEOUT_SECONDS

        # In-process counters used for the health/status dashboard.
        self.total_requests = 0
        self.failed_requests = 0
        self.last_success_ts: str | None = None
        self.last_failure_ts: str | None = None

    async def health_check(self) -> Dict[str, Any]:
        """Attempt a minimal request to confirm the provider is reachable."""
        try:
            await self.get_random_bytes(4)
            return {"status": "ONLINE", "provider": self.provider}
        except QRNGUnavailableError as exc:
            return {"status": "OFFLINE", "provider": self.provider, "error": str(exc)}

    async def get_random_bytes(self, n: int) -> Dict[str, Any]:
        """
        Request `n` random bytes from the external QRNG provider.

        Returns a metadata dict:
        {
            "source": "external_qrng",
            "provider": "anu",
            "bytes": n,
            "bits": n * 8,
            "hex": "...",
            "timestamp": "...",
            "request_id": "..."
        }
        """
        self.total_requests += 1
        request_id = f"qrng-{uuid.uuid4().hex[:12]}"

        try:
            raw_bytes = await self._fetch_from_provider(n)
        except (httpx.TimeoutException,) as exc:
            self.failed_requests += 1
            self.last_failure_ts = datetime.now(timezone.utc).isoformat()
            raise QRNGUnavailableError(f"QRNG provider timed out: {exc}") from exc
        except (httpx.HTTPError, ValueError, KeyError, binascii.Error) as exc:
            self.failed_requests += 1
            self.last_failure_ts = datetime.now(timezone.utc).isoformat()
            raise QRNGUnavailableError(f"QRNG provider request failed: {exc}") from exc

        if raw_bytes is None or len(raw_bytes) < n:
            self.failed_requests += 1
            self.last_failure_ts = datetime.now(timezone.utc).isoformat()
            raise QRNGUnavailableError("QRNG provider returned malformed or insufficient data")

        self.last_success_ts = datetime.now(timezone.utc).isoformat()

        return {
            "source": "external_qrng",
            "provider": self.provider,
            "bytes": n,
            "bits": n * 8,
            "hex": raw_bytes[:n].hex(),
            "timestamp": self.last_success_ts,
            "request_id": request_id,
        }

    async def get_random_bits(self, n_bits: int) -> Dict[str, Any]:
        n_bytes = (n_bits + 7) // 8
        result = await self.get_random_bytes(n_bytes)
        result["bits_requested"] = n_bits
        return result

    async def _fetch_from_provider(self, n: int) -> bytes:
        """
        Provider-specific fetch logic. Currently supports the ANU QRNG API,
        which returns JSON of the form:
            {"type":"uint8","length":N,"data":[...],"success":true}
        """
        if self.provider == "anu":
            params = {"length": n, "type": "uint8"}
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.api_url, params=params, headers=headers)
                resp.raise_for_status()
                payload = resp.json()

            if not payload.get("success"):
                raise ValueError(f"Provider reported failure: {payload}")

            data = payload.get("data")
            if not isinstance(data, list) or len(data) < n:
                raise ValueError("Provider response missing expected 'data' array")

            return bytes(int(b) & 0xFF for b in data[:n])

        raise ValueError(f"Unsupported QRNG_PROVIDER '{self.provider}'")


# Singleton instance used across the app so request counters accumulate.
qrng_service = QRNGService()
