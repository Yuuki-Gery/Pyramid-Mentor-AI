from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import configure_logging, logger

configure_logging()


def _find_frontend_dir() -> Path | None:
    """Resolve the frontend directory for both local and Docker runs."""
    candidates = [
        Path.cwd() / "frontend",
        Path.cwd().parent / "frontend",
        Path(__file__).resolve().parents[2] / "frontend",
    ]
    for candidate in candidates:
        if (candidate / "index.html").is_file():
            return candidate
    return None


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Database failures are fatal: starting without a database would make the
    # authentication and growth APIs silently unusable.
    from app.database import init_db

    try:
        await init_db()
        logger.info("Database initialized")
    except Exception:
        logger.exception("Database initialization failed")
        raise

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="4.0.0",
    description="以金字塔思维为核心的 AI Mentor 系统",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

frontend_dir = _find_frontend_dir()
if frontend_dir:
    app.mount("/frontend", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
else:
    logger.warning("Frontend directory not found; /frontend will not be mounted")

# Core routers
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.growth import router as growth_router
from app.api.growth_memory import router as growth_memory_router
from app.api.health import router as health_router
from app.api.llm_health import router as llm_router
from app.api.quota import router as quota_router
from app.api.rag_health import router as rag_router

app.include_router(health_router)
app.include_router(rag_router)
app.include_router(llm_router)
app.include_router(auth_router)
app.include_router(growth_router)
app.include_router(growth_memory_router)
app.include_router(quota_router)
app.include_router(chat_router)

# Debug/test routes are convenient locally, but must not be exposed by default
# in production: several of them call paid LLM providers or mutate Chroma.
debug_enabled = settings.ENABLE_DEBUG_ENDPOINTS and not settings.is_production
if debug_enabled:
    from app.api import agent_test, knowledge_test, rag_test
    from app.api.expert_test import router as expert_test_router
    from app.api.llm_test import router as llm_test_router

    app.include_router(llm_test_router)
    app.include_router(agent_test.router)
    app.include_router(rag_test.router)
    app.include_router(knowledge_test.router)
    app.include_router(expert_test_router)
    logger.info("Debug endpoints enabled")
else:
    logger.info("Debug endpoints disabled")


@app.get("/")
async def root():
    return {
        "project": settings.APP_NAME,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }
