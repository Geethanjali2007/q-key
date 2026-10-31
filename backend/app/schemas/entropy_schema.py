from pydantic import BaseModel, Field
from typing import Optional, List


class EntropyAnalyzeRequest(BaseModel):
    source: str = Field("qrng", description="'qrng' or 'csprng'")
    n_bytes: int = Field(256, ge=32, le=65536)


class StatisticalTestResult(BaseModel):
    name: str
    statistic: float
    p_value: Optional[float] = None
    passed: bool
    threshold: str


class EntropyAnalysisResponse(BaseModel):
    source: str
    fallback_used: bool = False
    n_bytes: int
    n_bits: int
    shannon_entropy_bits_per_byte: float
    min_entropy_bits_per_byte: float
    ones_ratio: float
    zeros_ratio: float
    tests: List[StatisticalTestResult]
    overall_quality: str  # Excellent | Good | Warning | Critical
    note: str = (
        "Statistical tests evaluate observed randomness quality; "
        "they do not prove quantum origin."
    )


class FusionRequest(BaseModel):
    n_bytes: int = Field(32, ge=16, le=256)


class FusionResponse(BaseModel):
    quantum_source: str  # available | unavailable
    classical_source: str  # available | unavailable
    fusion_method: str
    output_bits: int
    output_hex: str
    note: str = (
        "Fusion combines quantum and classical entropy via a cryptographic "
        "hash; this reduces single-source dependency but is not a formal "
        "guarantee against every possible failure scenario."
    )


class EntropyHealthResponse(BaseModel):
    qrng_status: str
    entropy_quality: str
    latest_entropy_score: float
    last_successful_request: Optional[str]
    total_bits_generated: int
    failed_requests: int
    fallback_count: int
    tests_passed: int
    tests_failed: int
