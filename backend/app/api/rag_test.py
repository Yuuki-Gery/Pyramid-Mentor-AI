from fastapi import APIRouter, HTTPException

from app.core.logging import logger
from app.rag.retriever import retriever

router = APIRouter()


@router.get("/rag-test")
async def rag_test():
    """Development-only retrieval check."""
    try:
        result = retriever.search("SCQA是什么")
    except Exception:
        logger.exception("RAG test query failed")
        raise HTTPException(
            status_code=503,
            detail="RAG 检索失败，请检查 Chroma 和 embedding 服务",
        )

    return {"result": result}
