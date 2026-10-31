"""
Tests for the QRNG service. Network calls to the real external provider are
mocked so the test suite is deterministic and does not require internet
access.
"""
import pytest
import httpx

from app.services.qrng_service import QRNGService, QRNGUnavailableError


class FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=self)

    def json(self):
        return self._json


@pytest.mark.asyncio
async def test_qrng_parses_valid_response(monkeypatch):
    service = QRNGService()

    async def fake_get(self, url, params=None, headers=None):
        return FakeResponse({"success": True, "data": [1, 2, 3, 4, 5, 6, 7, 8]})

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    result = await service.get_random_bytes(8)
    assert result["source"] == "external_qrng"
    assert result["bytes"] == 8
    assert result["bits"] == 64
    assert len(result["hex"]) == 16


@pytest.mark.asyncio
async def test_qrng_timeout_raises_unavailable(monkeypatch):
    service = QRNGService()

    async def fake_get(self, url, params=None, headers=None):
        raise httpx.TimeoutException("timed out")

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    with pytest.raises(QRNGUnavailableError):
        await service.get_random_bytes(8)


@pytest.mark.asyncio
async def test_qrng_malformed_response_raises_unavailable(monkeypatch):
    service = QRNGService()

    async def fake_get(self, url, params=None, headers=None):
        return FakeResponse({"success": True, "data": "not-a-list"})

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    with pytest.raises(QRNGUnavailableError):
        await service.get_random_bytes(8)


@pytest.mark.asyncio
async def test_qrng_provider_failure_flag_raises_unavailable(monkeypatch):
    service = QRNGService()

    async def fake_get(self, url, params=None, headers=None):
        return FakeResponse({"success": False})

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    with pytest.raises(QRNGUnavailableError):
        await service.get_random_bytes(8)
