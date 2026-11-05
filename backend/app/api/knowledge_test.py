from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.rag.loader import document_loader
from app.rag.splitter import text_splitter
from app.rag.knowledge import knowledge_base

router = APIRouter()

BACKEND_ROOT = Path(__file__).resolve().parents[2]


def _scqa_pdf_path() -> Path:
    """Locate the optional local SCQA PDF in Docker and local layouts."""
    candidates = [
        BACKEND_ROOT / "docs" / "scqa.pdf",
        BACKEND_ROOT.parent / "docs" / "scqa.pdf",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise HTTPException(
        status_code=404,
        detail="未找到 docs/scqa.pdf，请先添加你有权使用的知识库文件",
    )


def _pyramid_text_path() -> Path:
    return BACKEND_ROOT / "app" / "rag" / "knowledge_data" / "pyramid_principle.txt"


@router.post("/knowledge-load")
async def load_knowledge():
    """Load the optional SCQA PDF into Chroma (development only)."""
    documents = document_loader.load_pdf(str(_scqa_pdf_path()))
    chunks = text_splitter.split(documents)
    count = knowledge_base.add_documents(chunks)
    return {"status": "success", "chunks": count}


@router.post("/knowledge-load-pyramid")
async def load_pyramid_knowledge():
    """Load the bundled pyramid-principle notes into Chroma."""
    documents = document_loader.load_text(
        str(_pyramid_text_path()),
        source="pyramid_principle",
        category="pyramid_principle",
        chapter="全书",
    )
    chunks = text_splitter.split(documents)
    count = knowledge_base.add_documents(chunks)
    return {"status": "success", "chunks": count}


@router.post("/knowledge-load-all")
async def load_all_knowledge():
    result_scqa = await load_knowledge()
    result_pyramid = await load_pyramid_knowledge()
    return {
        "status": "success",
        "scqa_chunks": result_scqa["chunks"],
        "pyramid_principles_chunks": result_pyramid["chunks"],
        "total_chunks": result_scqa["chunks"] + result_pyramid["chunks"],
    }
