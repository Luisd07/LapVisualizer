"""Logging configuration: route all application logging through Loguru."""

import logging
import sys
from types import FrameType

from loguru import logger

from backend.app.core.config import settings

# Standard-library loggers whose records are funnelled into Loguru so that
# uvicorn and SQLAlchemy output shares one consistent format and sink.
_INTERCEPTED_LOGGERS = (
    "uvicorn",
    "uvicorn.access",
    "uvicorn.error",
    "sqlalchemy.engine",
)


class InterceptHandler(logging.Handler):
    """A `logging` handler that re-emits standard-library records via Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Forward one standard-library log record to Loguru."""
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        # Walk back to the frame that originated the log call, so Loguru
        # reports the real caller rather than the logging machinery.
        frame: FrameType | None = logging.currentframe()
        depth = 2
        while frame is not None and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def configure_logging() -> None:
    """Make Loguru the single logging sink for the whole application."""
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.log_level,
        backtrace=False,
        diagnose=False,
    )
    intercept = InterceptHandler()
    logging.basicConfig(handlers=[intercept], level=logging.NOTSET, force=True)
    for name in _INTERCEPTED_LOGGERS:
        std_logger = logging.getLogger(name)
        std_logger.handlers = [intercept]
        std_logger.propagate = False
