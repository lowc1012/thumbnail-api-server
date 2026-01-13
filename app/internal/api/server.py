from typing import Optional

import uvicorn
from fastapi import FastAPI

from app.internal.api.v1 import router
from app.internal.configuration.settings import Settings, get_settings


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    """Create FastAPI application with configuration."""

    if settings is None:
        settings = get_settings()

    # TODO: Log the configuration

    application = FastAPI(
        title="thumbnail-api-server",
        description="Building a long-running job API which accepts image files, creates thumbnails, and allows the thumbnails to be fetched when done processing.",
        version="0.1.0",
        debug=settings.DEBUG
    )

    # TODO: Add rate limiting state and exception handler

    # TODO: Configure middlewares

    # Create API router
    application.include_router(router.api_v1)
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
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.ACCESS_LOG,
        loop=settings.EVENT_LOOP
    )
