import uuid

from fastapi import APIRouter, HTTPException

from app.agents.orchestrator import MentorOrchestrator
from app.core.logging import logger

router = APIRouter()

mentor = MentorOrchestrator()


@router.get("/agent-test")
async def agent_test(
    message: str = "我想创业，但是不知道做什么方向",
    session_id: str | None = None,
):
    """Development-only end-to-end agent pipeline check."""
    if not session_id:
        session_id = str(uuid.uuid4())

    try:
        result = await mentor.run(message, session_id)
    except Exception:
        logger.exception("Agent test pipeline failed for session_id={}", session_id)
        raise HTTPException(status_code=503, detail="Agent 调用失败，请稍后重试")

    return {"session_id": session_id, **result}
