from fastapi import APIRouter
from app.internal.api.v1 import health, thumbnails

api_v1 = APIRouter(prefix="/api/v1")
api_v1.get("/health/")(health.check_status)
api_v1.post("/thumbnails/")(thumbnails.upload)
