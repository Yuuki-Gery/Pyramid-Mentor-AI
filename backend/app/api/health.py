import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.logging import logger
from app.memory.redis_client import redis_client

router = APIRouter()


@router.get("/health")
async def health_check():
    """Liveness/readiness check for the API and its state store."""
    try:
        value = await asyncio.to_thread(redis_client.ping)
        if not value:
            raise RuntimeError("unexpected Redis ping response")
    except Exception:
        logger.warning("Health check failed: Redis unavailable")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "redis": "unavailable"},
        )

    return {"status": "healthy", "redis": "ok"}
