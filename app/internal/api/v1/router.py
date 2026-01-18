from fastapi import APIRouter
from app.internal.api.v1 import health, thumbnails

api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(health.router, tags=["health"])
api_v1.include_router(thumbnails.router, tags=["thumbnails"])
