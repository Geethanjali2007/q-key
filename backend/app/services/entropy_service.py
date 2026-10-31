"""
Entropy analysis service.

Implements statistically meaningful randomness tests on a byte buffer:

  - Shannon entropy (bits/byte)
  - Min-entropy estimate
  - Bit distribution (ones/zeros ratio)
  - Frequency (Monobit) test - NIST SP 800-22 style
  - Runs test - NIST SP 800-22 style
  - Block frequency test - NIST SP 800-22 style
  - Autocorrelation (lag-1) analysis
  - Approximate entropy test (ApEn, m=2)

IMPORTANT: Passing these tests indicates the data is statistically
well-distributed. It does NOT prove the data originated from a quantum
process - that property depends entirely on the physical source that
produced it, not on any statistical test performed after the fact.
"""
import math
from collections import Counter
from typing import List, Dict, Any

from scipy import special


def _bytes_to_bits(data: bytes) -> List[int]:
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def shannon_entropy(data: bytes) -> float:
    """Shannon entropy in bits per byte (max = 8.0)."""
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    entropy = 0.0
    for count in counts.values():
        p = count / n
        entropy -= p * math.log2(p)
    return entropy


def min_entropy(data: bytes) -> float:
    """
    Min-entropy estimate in bits per byte, based on the probability of the
    single most frequent byte value: H_min = -log2(p_max).
    """
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    p_max = max(counts.values()) / n
    if p_max <= 0:
        return 0.0
    return -math.log2(p_max)


def bit_distribution(bits: List[int]) -> Dict[str, float]:
    n = len(bits)
    if n == 0:
        return {"ones_ratio": 0.0, "zeros_ratio": 0.0}
    ones = sum(bits)
    return {"ones_ratio": ones / n, "zeros_ratio": (n - ones) / n}


def frequency_monobit_test(bits: List[int]) -> Dict[str, Any]:
    """NIST SP 800-22 Frequency (Monobit) Test."""
    n = len(bits)
    s = sum(1 if b == 1 else -1 for b in bits)
    s_obs = abs(s) / math.sqrt(n)
    p_value = math.erfc(s_obs / math.sqrt(2))
    return {
        "name": "Frequency (Monobit) Test",
        "statistic": round(s_obs, 6),
        "p_value": round(p_value, 6),
        "passed": p_value >= 0.01,
        "threshold": "p_value >= 0.01",
    }


def runs_test(bits: List[int]) -> Dict[str, Any]:
    """NIST SP 800-22 Runs Test."""
    n = len(bits)
    ones = sum(bits)
    pi = ones / n

    # Pre-test: if the proportion of ones is far from 0.5, the runs test
    # is not applicable and automatically fails.
    if abs(pi - 0.5) >= (2 / math.sqrt(n)):
        return {
            "name": "Runs Test",
            "statistic": 0.0,
            "p_value": 0.0,
            "passed": False,
            "threshold": "p_value >= 0.01 (pre-test on proportion failed)",
        }

    v_obs = 1
    for i in range(1, n):
        if bits[i] != bits[i - 1]:
            v_obs += 1

    numerator = abs(v_obs - 2 * n * pi * (1 - pi))
    denominator = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    p_value = math.erfc(numerator / denominator) if denominator > 0 else 0.0

    return {
        "name": "Runs Test",
        "statistic": float(v_obs),
        "p_value": round(p_value, 6),
        "passed": p_value >= 0.01,
        "threshold": "p_value >= 0.01",
    }


def block_frequency_test(bits: List[int], block_size: int = 128) -> Dict[str, Any]:
    """NIST SP 800-22 Block Frequency Test."""
    n = len(bits)
    num_blocks = n // block_size
    if num_blocks == 0:
        return {
            "name": "Block Frequency Test",
            "statistic": 0.0,
            "p_value": 0.0,
            "passed": False,
            "threshold": "insufficient data for block size",
        }

    chi_sq = 0.0
    for i in range(num_blocks):
        block = bits[i * block_size:(i + 1) * block_size]
        pi_i = sum(block) / block_size
        chi_sq += (pi_i - 0.5) ** 2

    chi_sq *= 4 * block_size
    p_value = special.gammaincc(num_blocks / 2, chi_sq / 2)

    return {
        "name": "Block Frequency Test",
        "statistic": round(chi_sq, 6),
        "p_value": round(float(p_value), 6),
        "passed": p_value >= 0.01,
        "threshold": "p_value >= 0.01",
    }


def autocorrelation_test(bits: List[int], lag: int = 1) -> Dict[str, Any]:
    """
    Lag-1 autocorrelation of the +1/-1 mapped bit sequence. For truly random
    bits, the autocorrelation should be close to zero.
    """
    n = len(bits)
    mapped = [1 if b == 1 else -1 for b in bits]
    if n <= lag:
        return {
            "name": "Autocorrelation Test (lag=1)",
            "statistic": 0.0,
            "p_value": None,
            "passed": False,
            "threshold": "insufficient data",
        }

    numerator = sum(mapped[i] * mapped[i + lag] for i in range(n - lag))
    autocorr = numerator / (n - lag)

    # Under the null hypothesis of independence, autocorr ~ N(0, 1/(n-lag))
    std_err = 1 / math.sqrt(n - lag)
    z = autocorr / std_err
    p_value = math.erfc(abs(z) / math.sqrt(2))

    return {
        "name": "Autocorrelation Test (lag=1)",
        "statistic": round(autocorr, 6),
        "p_value": round(p_value, 6),
        "passed": p_value >= 0.01,
        "threshold": "p_value >= 0.01",
    }


def approximate_entropy_test(bits: List[int], m: int = 2) -> Dict[str, Any]:
    """NIST SP 800-22 style Approximate Entropy Test."""
    n = len(bits)

    def phi(m_val: int) -> float:
        if m_val <= 0:
            return 0.0
        extended = bits + bits[: m_val - 1]
        counts: Dict[tuple, int] = {}
        for i in range(n):
            pattern = tuple(extended[i:i + m_val])
            counts[pattern] = counts.get(pattern, 0) + 1
        total = n
        phi_val = 0.0
        for c in counts.values():
            freq = c / total
            phi_val += freq * math.log(freq)
        return phi_val

    phi_m = phi(m)
    phi_m1 = phi(m + 1)
    ap_en = phi_m - phi_m1

    chi_sq = 2 * n * (math.log(2) - ap_en)
    p_value = special.gammaincc(2 ** (m - 1), chi_sq / 2) if chi_sq > 0 else 1.0

    return {
        "name": "Approximate Entropy Test (m=2)",
        "statistic": round(ap_en, 6),
        "p_value": round(float(p_value), 6),
        "passed": p_value >= 0.01,
        "threshold": "p_value >= 0.01",
    }


def classify_quality(tests: List[Dict[str, Any]], shannon: float) -> str:
    """
    Derive a simple, transparent quality label from the number of tests
    passed and the observed Shannon entropy. This is a heuristic summary
    for the dashboard, NOT a formal cryptographic security proof.
    """
    passed = sum(1 for t in tests if t["passed"])
    total = len(tests)
    ratio = passed / total if total else 0

    if ratio == 1.0 and shannon >= 7.9:
        return "Excellent"
    if ratio >= 0.8 and shannon >= 7.5:
        return "Good"
    if ratio >= 0.5:
        return "Warning"
    return "Critical"


def analyze(data: bytes) -> Dict[str, Any]:
    """Run the full statistical analysis suite on a byte buffer."""
    bits = _bytes_to_bits(data)
    shannon = shannon_entropy(data)
    minH = min_entropy(data)
    dist = bit_distribution(bits)

    tests = [
        frequency_monobit_test(bits),
        runs_test(bits),
        block_frequency_test(bits),
        autocorrelation_test(bits),
        approximate_entropy_test(bits),
    ]

    quality = classify_quality(tests, shannon)

    return {
        "n_bytes": len(data),
        "n_bits": len(bits),
        "shannon_entropy_bits_per_byte": round(shannon, 6),
        "min_entropy_bits_per_byte": round(minH, 6),
        "ones_ratio": round(dist["ones_ratio"], 6),
        "zeros_ratio": round(dist["zeros_ratio"], 6),
        "tests": tests,
        "overall_quality": quality,
    }
