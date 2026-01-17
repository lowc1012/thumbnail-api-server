import logging
import sys
from typing import Optional

from loguru import logger

from app.internal.configuration.settings import Settings

_app_logger = None


class InterceptHandler(logging.Handler):
    """Intercept standard logging and redirect to loguru"""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
            if frame is None:  # Prevent infinite loop
                break

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class AppLogger:
    """Application logger using loguru"""

    _instance: Optional["AppLogger"] = None
    _configured = False

    def __new__(cls, settings: Optional[Settings] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, settings: Optional[Settings] = None):
        if not self._configured and settings:
            self.configure(settings)

    def configure(self, settings: Settings) -> None:
        """Configure logger with application settings."""
        if self._configured:
            return

        # Remove all existing handlers
        logger.remove()

        # Intercept standard logging
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

        # Configure all existing loggers to use our handler
        for name in logging.root.manager.loggerDict.keys():
            logging.getLogger(name).handlers = []
            logging.getLogger(name).propagate = True

        # Configure log output
        if settings.ENVIRONMENT == "production":
            logger.add(
                sys.stdout,
                level=settings.LOG_LEVEL,
                serialize=True,
                colorize=False,
                enqueue=True,
                catch=True,
                backtrace=False,
                diagnose=False,
            )
        else:
            logger.add(
                sys.stdout,
                format=(
                    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:"
                    "<cyan>{line}</cyan> - "
                    "<level>{message}</level>"
                ),
                level=settings.LOG_LEVEL,
                colorize=True,
                enqueue=True,
                catch=True,
                backtrace=settings.DEBUG,
                diagnose=settings.DEBUG,
            )

        self._configured = True
        logger.info(
            "Logger configured",
            level=settings.LOG_LEVEL,
            debug=settings.DEBUG,
            environment=settings.ENVIRONMENT,
        )

    def get_logger(self):
        return logger


def get_logger():
    """Get the configured loguru logger instance"""
    global _app_logger
    if _app_logger is None:
        _app_logger = AppLogger()
    return _app_logger.get_logger()
