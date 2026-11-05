import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.logging import logger
from app.rag.chroma_client import chroma_client

router = APIRouter()


@router.get("/rag-health")
async def rag_health():
    """Check whether the Chroma collection can be reached."""
    try:
        collection = await asyncio.to_thread(chroma_client.get_collection)
    except Exception:
        logger.warning("RAG health check failed: Chroma unavailable")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "chroma": "unavailable"},
        )

    return {
        "status": "healthy",
        "chroma": "ok",
        "collection": collection.name,
    }
