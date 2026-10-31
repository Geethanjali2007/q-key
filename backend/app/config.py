"""
Application configuration.

All configuration is read from environment variables so that no secrets or
environment-specific values are ever hardcoded in source code.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load a .env file if present (useful for local development on Windows/Mac/Linux)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    # --- QRNG provider ---
    # "anu" uses the ANU Quantum Random Numbers Server (qrng.anu.edu.au), a
    # publicly documented service that derives randomness from measurements
    # of the quantum vacuum. This is an EXTERNAL physical entropy source -
    # this backend does not contain quantum hardware itself.
    QRNG_PROVIDER: str = os.getenv("QRNG_PROVIDER", "anu")
    QRNG_API_URL: str = os.getenv(
        "QRNG_API_URL", "https://qrng.anu.edu.au/API/jsonI.php"
    )
    QRNG_API_KEY: str = os.getenv("QRNG_API_KEY", "")
    QRNG_TIMEOUT_SECONDS: float = float(os.getenv("QRNG_TIMEOUT_SECONDS", "6.0"))

    # --- Fallback / demo behaviour ---
    ALLOW_CSPRNG_FALLBACK: bool = _get_bool("ALLOW_CSPRNG_FALLBACK", True)
    DEMO_MODE: bool = _get_bool("DEMO_MODE", True)

    # --- Database ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./qkey.db")

    # --- CORS ---
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

    # --- Key lifecycle ---
    DEFAULT_KEY_EXPIRY_DAYS: int = int(os.getenv("DEFAULT_KEY_EXPIRY_DAYS", "30"))

    # --- App metadata ---
    APP_NAME: str = "Q-Key: Quantum Randomness Security & Trusted Key Platform"
    APP_VERSION: str = "1.0.0"


settings = Settings()
