from fastapi import APIRouter
from app.internal.api.v1 import jobs, thumbnails

api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(thumbnails.router, tags=["thumbnails"])
api_v1.include_router(jobs.router, tags=["jobs"])
