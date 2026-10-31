import secrets

from app.services.csprng_service import CSPRNGService
from app.services.entropy_service import (
    shannon_entropy,
    frequency_monobit_test,
    runs_test,
    _bytes_to_bits,
    analyze,
)


def test_csprng_generates_requested_length():
    service = CSPRNGService()
    result = service.get_random_bytes(32)
    assert result["bytes"] == 32
    assert result["bits"] == 256
    assert len(bytes.fromhex(result["hex"])) == 32


def test_csprng_health_check_online():
    service = CSPRNGService()
    health = service.health_check()
    assert health["status"] == "ONLINE"


def test_shannon_entropy_of_uniform_bytes_is_high():
    data = secrets.token_bytes(4096)
    entropy = shannon_entropy(data)
    assert entropy > 7.0  # close to the theoretical max of 8.0


def test_shannon_entropy_of_constant_bytes_is_zero():
    data = bytes([0x42]) * 1000
    entropy = shannon_entropy(data)
    assert entropy == 0.0


def test_frequency_monobit_test_passes_on_random_data():
    data = secrets.token_bytes(2048)
    bits = _bytes_to_bits(data)
    result = frequency_monobit_test(bits)
    assert result["passed"] is True
    assert 0 <= result["p_value"] <= 1


def test_frequency_monobit_test_fails_on_all_ones():
    bits = [1] * 2048
    result = frequency_monobit_test(bits)
    assert result["passed"] is False


def test_runs_test_structure():
    data = secrets.token_bytes(2048)
    bits = _bytes_to_bits(data)
    result = runs_test(bits)
    assert "p_value" in result
    assert "passed" in result


def test_analyze_returns_all_expected_fields():
    data = secrets.token_bytes(1024)
    result = analyze(data)
    assert result["n_bytes"] == 1024
    assert len(result["tests"]) == 5
    assert result["overall_quality"] in ("Excellent", "Good", "Warning", "Critical")
