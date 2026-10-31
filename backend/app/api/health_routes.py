from fastapi import APIRouter
from datetime import datetime, timezone

from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "demo_mode": settings.DEMO_MODE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
