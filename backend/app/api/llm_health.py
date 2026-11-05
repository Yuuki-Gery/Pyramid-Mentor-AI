from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.logging import logger
from app.llm.manager import get_llm

router = APIRouter()


@router.get("/llm-health")
async def llm_health():
    """Report provider configuration without making a paid model call."""
    try:
        llm = get_llm()
    except Exception:
        logger.exception("LLM provider configuration is invalid")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "provider": "invalid", "configured": False},
        )

    provider = llm.__class__.__name__
    if not llm.is_configured:
        return {
            "status": "not_configured",
            "provider": provider,
            "configured": False,
        }

    return {
        "status": "healthy",
        "provider": provider,
        "configured": True,
    }
