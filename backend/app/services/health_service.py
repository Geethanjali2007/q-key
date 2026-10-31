"""
Entropy-source health monitoring service.

Aggregates counters from the QRNG/CSPRNG services and the most recent
statistical analysis into a single health snapshot for the dashboard.

The "entropy health score" produced here is a transparent heuristic for
demo/monitoring purposes. It is NOT a formal cryptographic security proof.
"""
from typing import Dict, Any, Optional

from app.services.qrng_service import qrng_service

# Simple in-process state updated whenever an entropy analysis runs.
_last_analysis: Dict[str, Any] = {
    "quality": "Unknown",
    "shannon_entropy": 0.0,
    "tests_passed": 0,
    "tests_failed": 0,
}
_fallback_count = 0


def record_analysis(quality: str, shannon_entropy: float, tests: list):
    _last_analysis["quality"] = quality
    _last_analysis["shannon_entropy"] = shannon_entropy
    _last_analysis["tests_passed"] = sum(1 for t in tests if t["passed"])
    _last_analysis["tests_failed"] = sum(1 for t in tests if not t["passed"])


def record_fallback():
    global _fallback_count
    _fallback_count += 1


async def get_health_snapshot() -> Dict[str, Any]:
    qrng_health = await qrng_service.health_check()
    total_bits = (qrng_service.total_requests - qrng_service.failed_requests) * 32 * 8

    entropy_score = round(_last_analysis["shannon_entropy"] / 8.0, 4) if _last_analysis["shannon_entropy"] else 0.0

    return {
        "qrng_status": qrng_health["status"],
        "entropy_quality": _last_analysis["quality"],
        "latest_entropy_score": entropy_score,
        "last_successful_request": qrng_service.last_success_ts,
        "total_bits_generated": max(total_bits, 0),
        "failed_requests": qrng_service.failed_requests,
        "fallback_count": _fallback_count,
        "tests_passed": _last_analysis["tests_passed"],
        "tests_failed": _last_analysis["tests_failed"],
    }
