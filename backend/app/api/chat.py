import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.agents.orchestrator import MentorOrchestrator
from app.core.logging import logger

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    session_id: str | None = Field(default=None, max_length=128)

    @field_validator("message", "session_id")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("不能为空")
        return value


class ChatResponse(BaseModel):
    session_id: str
    mentor_response: str
    is_casual: bool = False


mentor = MentorOrchestrator()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat interface: casual conversation and structured mentoring."""
    session_id = request.session_id or str(uuid.uuid4())
    try:
        result = await mentor.run(request.message, session_id)
    except Exception:
        # Do not expose internal traces or provider details to the client.
        logger.exception("Chat pipeline failed for session_id={}", session_id)
        raise HTTPException(
            status_code=503,
            detail="导师服务暂时不可用，请稍后重试",
        )

    return {
        "session_id": session_id,
        "mentor_response": result.get("mentor_response", ""),
        "is_casual": result.get("is_casual", False),
    }
