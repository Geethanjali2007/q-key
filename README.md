# Q-Key — Quantum Randomness Security & Trusted Key Platform

A hackathon-ready software prototype that acquires entropy from an
**external quantum random number generator (QRNG)**, validates and
conditions it, fuses it with classical entropy, and uses it to generate,
manage, and use AES-256-GCM cryptographic keys — with a full REST API,
React dashboard, and simulated banking / IoT / identity applications.

> **This project uses an external QRNG source and does not itself
> implement physical quantum hardware.** The backend calls a public
> QRNG provider (default: the ANU Quantum Random Numbers Server) over
> HTTPS, the same way it would call any other external API.

---

## 1. Problem Statement

Pseudo-random generators used for cryptographic keys are deterministic
algorithms — when correctly implemented and seeded (e.g. Python's
`secrets` module), they are cryptographically secure, but they remain a
single point of trust in the entropy pipeline. Quantum random number
generation derives entropy from physical quantum measurement, giving
security architects a second, independent physical entropy source that
can be validated, monitored, and fused with classical entropy for
higher-assurance key material in banking, identity, IoT, and defence
systems.

## 2. Solution

Q-Key is a deployable service that:

1. Requests raw bytes from an external QRNG provider.
2. Requests raw bytes from the OS-level CSPRNG (`secrets` module) as a
   comparison / fallback / fusion input.
3. Runs NIST-SP-800-22-style statistical tests on either source (Shannon
   entropy, min-entropy, monobit, runs, block frequency, autocorrelation,
   approximate entropy).
4. Conditions raw entropy with SHA-256 / HKDF-SHA256.
5. Optionally fuses QRNG + CSPRNG via `SHA-256(qrng || csprng)`.
6. Derives AES-256 key material, wraps it at rest, and issues a `key_id`.
7. Exposes full key lifecycle management (generate / rotate / revoke /
   expire) and AES-256-GCM authenticated encryption/decryption.
8. Logs every security-relevant event to an audit trail.
9. Ships simulated Banking, IoT, and Digital Identity integrations.
10. Provides a "QRNG vs CSPRNG" laboratory that runs identical tests on
    equal-sized samples from both sources and reports both fairly.

## 3. Why QRNG? (and why CSPRNG is *not* "insecure")

- **CSPRNG** (`secrets`, backed by the OS's own CSPRNG) is
  cryptographically secure when correctly implemented. It is the
  standard, correct choice for the vast majority of software today.
- **QRNG** provides a *physically* unpredictable entropy source, derived
  from quantum measurement rather than an algorithm. Its value is
  architectural: it gives systems an independent, non-algorithmic
  entropy input that can be monitored, fused, and audited alongside a
  CSPRNG, reducing reliance on any single generator.
- Passing statistical randomness tests does **not** prove data is of
  quantum origin — well-designed CSPRNG output can pass the same tests.
  QRNG's distinguishing property is its physical source, not its
  statistical appearance. Q-Key's UI states this explicitly wherever
  test results are shown.
- Quantum randomness does not make AES "unbreakable," and QRNG alone
  does not "automatically" strengthen a system — cryptographic strength
  also depends on key management, algorithm choice, implementation
  correctness, and overall system security.

## 4. Architecture

```
React Frontend (Vite)
        |
        | REST API (JSON over HTTPS/HTTP)
        v
FastAPI Backend
        |
        +--------------------+
        |                    |
        v                    v
External QRNG          OS CSPRNG
(ANU QRNG API)         (secrets module)
        |                    |
        +---------+----------+
                  |
                  v
          Entropy Manager
                  |
         +--------+--------+
         |                 |
         v                 v
  Statistical Tests    Health Monitor
         |                 |
         +--------+--------+
                  |
                  v
            Conditioning
          (SHA-256 / HKDF)
                  |
                  v
           Key Generation
                  |
                  v
          Key Management
        (wrapped at rest, SQLite)
                  |
                  v
           AES-256-GCM
                  |
         +--------+--------+--------+
         |        |                 |
         v        v                 v
      Banking    IoT             Identity
      Demo       Demo              Demo
```

## 5. Features

- External QRNG integration with timeout/failure handling
- CSPRNG comparison and configurable fallback (audited, never silently
  relabeled as "quantum")
- 5-test statistical randomness suite + Shannon/min-entropy estimates
- SHA-256 and HKDF-SHA256 conditioning
- QRNG + CSPRNG entropy fusion
- AES-256-GCM key generation, rotation, revocation, expiry
- Encrypted-at-rest key storage (prototype-grade, clearly labeled)
- AES-256-GCM encrypt/decrypt with unique nonces and tamper detection
- Full REST API with OpenAPI docs (`/docs`)
- Banking / IoT / Digital Identity simulations
- QRNG vs CSPRNG comparison lab with charts
- Security event audit log (no secrets ever logged)
- Dark, technical React dashboard with live status, charts, and tables
- 24 pytest tests across QRNG, entropy, conditioning, crypto, and the API
- Docker + docker-compose for one-command startup

## 6. Technology Stack

**Frontend:** React, Vite, Recharts, Lucide React, plain CSS (no
component framework) served from `frontend/`.

**Backend:** Python, FastAPI, Pydantic, httpx, `cryptography`, `hashlib`,
`secrets`, `scipy` (for statistical p-values), SQLAlchemy + SQLite.

**Testing:** pytest, pytest-asyncio, FastAPI `TestClient`.

**Deployment:** Docker, docker-compose.

## 7. Folder Structure

```
q-key/
├── backend/
│   ├── app/
│   │   ├── main.py, config.py
│   │   ├── api/            # FastAPI routers
│   │   ├── services/       # QRNG, CSPRNG, entropy, conditioning, fusion,
│   │   │                   # key, crypto, health, audit services
│   │   ├── security/       # key_manager, validators, secure_utils
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   └── tests/          # pytest suite
│   ├── requirements.txt, Dockerfile, .env.example
├── frontend/
│   ├── src/
│   │   ├── main.jsx, App.jsx, App.css, api.js
│   │   ├── components/     # Navbar, Sidebar, StatusCard, MetricCard, SecurityBadge
│   │   └── pages/          # Dashboard + 9 feature pages
│   ├── package.json, vite.config.js, Dockerfile, .env.example
├── docker-compose.yml
├── README.md
└── .gitignore
```

## 8. Installation

### Prerequisites
- Python 3.11+ (works on Windows, macOS, Linux)
- Node.js 20+
- (Optional) Docker Desktop, if you prefer containers

### Backend setup

```bash
cd backend
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux
```

The default `.env` values work out of the box: the ANU QRNG API does not
require an API key for light hackathon usage.

### Frontend setup

```bash
cd frontend
npm install
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux
```

## 9. Running the Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API root: http://localhost:8000
- Interactive API docs (Swagger): http://localhost:8000/docs

## 10. Running the Frontend

```bash
cd frontend
npm run dev
```

- Dashboard: http://localhost:5173

## 11. API Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Backend health check |
| GET | `/qrng/status` | QRNG provider status + counters |
| POST | `/qrng/random` | Request raw random bytes (qrng/csprng) |
| POST | `/entropy/analyze` | Run statistical tests on a fresh sample |
| POST | `/entropy/fuse` | Fuse QRNG + CSPRNG entropy |
| GET | `/entropy/health` | Entropy health snapshot |
| POST | `/keys/generate` | Generate an AES-256-GCM key |
| GET | `/keys` | List all keys |
| GET | `/keys/{key_id}` | Get key metadata |
| POST | `/keys/{key_id}/rotate` | Rotate a key |
| POST | `/keys/{key_id}/revoke` | Revoke a key |
| POST | `/crypto/encrypt` | AES-256-GCM encrypt |
| POST | `/crypto/decrypt` | AES-256-GCM decrypt |
| GET | `/audit/logs` | Security audit log |
| GET | `/applications/status` | Application/demo availability |
| POST | `/applications/banking/demo` | Simulated banking flow |
| POST | `/applications/iot/demo` | Simulated IoT flow |
| POST | `/applications/identity/demo` | Simulated identity flow |
| GET | `/comparison/qrng-csprng` | QRNG vs CSPRNG lab |

Full interactive documentation is auto-generated at `/docs`.

## 12. Testing

```bash
cd backend
pytest -v
```

24 tests cover QRNG response parsing/timeout/failure handling, CSPRNG
generation, entropy calculations and statistical tests, SHA-256/HKDF
conditioning, AES-256-GCM encryption/decryption (including wrong-key and
tampered-ciphertext failure cases), key rotation/revocation, and the full
REST API surface. Network calls to the real QRNG provider are mocked so
the suite runs offline and deterministically.

## 13. Docker Setup

```bash
docker-compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

SQLite data persists in the `qkey-data` Docker volume.

## 14. Security Considerations

- No hardcoded secrets; all configuration comes from environment
  variables (`.env` files, never committed).
- CSPRNG only ever uses Python's `secrets` module — never `random`.
- AES-GCM comes from the `cryptography` library; AES is never
  hand-implemented. A unique nonce is generated for every encryption.
- Generated key material is never returned by the API in production
  mode; `DEMO_MODE=true` only shows a masked preview for demonstration.
- Key material is encrypted at rest with a local wrapping key
  (prototype-grade — see limitations below).
- Plaintext passwords, secret keys, and auth tokens are never written to
  the audit log.
- CORS is restricted to configured origins.
- Input validation is enforced via Pydantic schemas and explicit
  validators.

## 15. Limitations

- This is a **hackathon prototype**, not a production key-management
  system. The at-rest key wrapping mechanism uses a locally-stored
  wrapping key rather than an HSM or cloud KMS.
- The external QRNG provider is a shared public service — it is
  suitable for demonstration and comparison, not for high-volume
  production key issuance without a commercial/dedicated QRNG source.
- Rate limiting is not implemented beyond basic input validation.
- The "entropy health score" and "quality" labels are transparent
  heuristics for dashboards/monitoring, not formal cryptographic proofs.

## 16. Future Improvements

- Pluggable QRNG provider abstraction (support multiple commercial QRNG
  vendors with automatic failover between them).
- Hardware Security Module (HSM) / cloud KMS integration for production
  key storage.
- Role-based access control and API authentication.
- Per-tenant rate limiting and quota management.
- Continuous statistical monitoring with alerting on entropy drift.

## 17. Hackathon Demo Flow

1. **Dashboard** — show QRNG online, entropy healthy.
2. **Quantum Randomness** — generate 256 bits from QRNG, show hex output.
3. **Entropy Analysis** — run the full statistical test suite.
4. **QRNG vs CSPRNG** — generate equal-sized samples, compare charts.
5. **Key Management** — generate a trusted AES-256-GCM key from QRNG.
6. **Encryption Demo** — encrypt "Quantum-secured transaction", then
   decrypt it back to the original message.
7. **Applications → Banking** — run the simulated transaction flow.
8. **Applications → IoT** — authenticate the simulated device.
9. Stop the backend's internet access (or set an invalid `QRNG_API_URL`)
   to show the QRNG-offline / CSPRNG-fallback / degraded-mode flow.
10. **Audit Logs** — show the full trail of everything that just happened.
