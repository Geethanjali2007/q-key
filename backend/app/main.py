"""
Q-Key backend entrypoint.

Run with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.database import init_db
from app.api import (
    health_routes,
    qrng_routes,
    entropy_routes,
    key_routes,
    crypto_routes,
    application_routes,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Q-Key is a software prototype that acquires, validates, conditions "
        "and delivers entropy from an EXTERNAL quantum random number "
        "generator (QRNG) for use as cryptographic key material, with a "
        "classical CSPRNG used for comparison and fallback. This service "
        "does not itself contain quantum hardware."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Avoid leaking internal implementation details beyond the intended message.
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app.include_router(health_routes.router)
app.include_router(qrng_routes.router)
app.include_router(entropy_routes.router)
app.include_router(key_routes.router)
app.include_router(crypto_routes.router)
app.include_router(application_routes.router)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "demo_mode": settings.DEMO_MODE,
    }
