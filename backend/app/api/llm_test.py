from fastapi import APIRouter, HTTPException

from app.core.logging import logger
from app.llm.manager import get_llm

router = APIRouter()


@router.get("/llm-test")
async def llm_test():
    """Development-only live provider check."""
    try:
        llm = get_llm()
        response = await llm.chat(
            [{"role": "user", "content": "你好，请简单介绍一下自己"}]
        )
    except Exception:
        logger.exception("LLM test call failed")
        raise HTTPException(
            status_code=502,
            detail="LLM 调用失败，请检查 API Key、模型和网络配置",
        )

    return {"response": response}
