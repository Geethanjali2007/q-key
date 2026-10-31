from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_random_endpoint_csprng_source():
    resp = client.post("/qrng/random", json={"n_bytes": 16, "source": "csprng"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["bytes"] == 16
    assert len(bytes.fromhex(body["hex"])) == 16


def test_random_endpoint_invalid_source_returns_400():
    resp = client.post("/qrng/random", json={"n_bytes": 16, "source": "bogus"})
    assert resp.status_code == 400


def test_entropy_analyze_csprng():
    resp = client.post("/entropy/analyze", json={"source": "csprng", "n_bytes": 256})
    assert resp.status_code == 200
    body = resp.json()
    assert "tests" in body
    assert len(body["tests"]) == 5


def test_generate_list_and_get_key():
    gen_resp = client.post("/keys/generate", json={"source": "csprng", "algorithm": "AES-256-GCM"})
    assert gen_resp.status_code == 200
    key = gen_resp.json()
    assert key["key_id"].startswith("QK-")
    assert key["status"] == "ACTIVE"

    list_resp = client.get("/keys")
    assert list_resp.status_code == 200
    assert any(k["key_id"] == key["key_id"] for k in list_resp.json())

    get_resp = client.get(f"/keys/{key['key_id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["key_id"] == key["key_id"]


def test_key_not_found_returns_404():
    resp = client.get("/keys/QK-DOESNOTEXIST00")
    assert resp.status_code == 404


def test_key_rotation_creates_new_key_and_revokes_old():
    gen_resp = client.post("/keys/generate", json={"source": "csprng"})
    key_id = gen_resp.json()["key_id"]

    rotate_resp = client.post(f"/keys/{key_id}/rotate")
    assert rotate_resp.status_code == 200
    new_key = rotate_resp.json()
    assert new_key["key_id"] != key_id
    assert new_key["rotated_from"] == key_id

    old_key_resp = client.get(f"/keys/{key_id}")
    assert old_key_resp.json()["status"] == "ROTATED"


def test_key_revocation():
    gen_resp = client.post("/keys/generate", json={"source": "csprng"})
    key_id = gen_resp.json()["key_id"]

    revoke_resp = client.post(f"/keys/{key_id}/revoke")
    assert revoke_resp.status_code == 200
    assert revoke_resp.json()["status"] == "REVOKED"


def test_encrypt_decrypt_via_api():
    gen_resp = client.post("/keys/generate", json={"source": "csprng"})
    key_id = gen_resp.json()["key_id"]

    enc_resp = client.post("/crypto/encrypt", json={"key_id": key_id, "plaintext": "Quantum-secured transaction"})
    assert enc_resp.status_code == 200
    enc = enc_resp.json()

    dec_resp = client.post(
        "/crypto/decrypt",
        json={"key_id": key_id, "ciphertext": enc["ciphertext"], "nonce": enc["nonce"], "tag": enc["tag"]},
    )
    assert dec_resp.status_code == 200
    assert dec_resp.json()["plaintext"] == "Quantum-secured transaction"


def test_encrypt_with_revoked_key_fails():
    gen_resp = client.post("/keys/generate", json={"source": "csprng"})
    key_id = gen_resp.json()["key_id"]
    client.post(f"/keys/{key_id}/revoke")

    enc_resp = client.post("/crypto/encrypt", json={"key_id": key_id, "plaintext": "hello"})
    assert enc_resp.status_code == 400


def test_audit_logs_endpoint():
    resp = client.get("/audit/logs")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_applications_status_endpoint():
    resp = client.get("/applications/status")
    assert resp.status_code == 200
    assert "qrng_status" in resp.json()
