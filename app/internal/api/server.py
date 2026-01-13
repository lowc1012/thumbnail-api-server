import time
import uvicorn

from app.internal.api.v1 import router
from app.internal.configuration.settings import Settings, get_settings
from app.internal.log.logger import get_logger
from typing import Optional
from fastapi import FastAPI, Request

logger = get_logger()


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    """Create FastAPI application with configuration."""

    if settings is None:
        settings = get_settings()

    # Configure logging first
    logger.info(f"Creating FastAPI app - Environment: {settings.ENVIRONMENT}")

    application = FastAPI(
        title="thumbnail-api-server",
        description="Building a long-running job API which accepts image files, creates thumbnails, and allows the thumbnails to be fetched when done processing.",
        version="0.1.0",
        debug=settings.DEBUG
    )

    # TODO: Configure middlewares
    @application.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            "HTTP Request",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=f"{process_time:.4f}s",
            client_ip=request.client.host if request.client else None
        )
        return response

    # Create API router
    application.include_router(router.api_v1)
    logger.info("FastAPI application created successfully")
    return application


def start_server(settings: Optional[Settings] = None) -> None:
    """Start the uvicorn server with the FastAPI application."""
    if settings is None:
        settings = get_settings()

    app = create_app(settings)

    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_config=None,
        access_log=settings.ACCESS_LOG,
        loop=settings.EVENT_LOOP
    )
