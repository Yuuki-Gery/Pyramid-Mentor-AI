import sys

from loguru import logger

from app.core.config import settings


def configure_logging() -> None:
    """Configure the project's single Loguru sink.

    Keep the format compact and never log request bodies or credentials here.
    """
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL.upper(),
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | "
            "{name}:{function}:{line} | {message}"
        ),
        enqueue=False,
        backtrace=False,
        diagnose=False,
    )


__all__ = ["configure_logging", "logger"]
