from fastapi import UploadFile, File, Form
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from typing import Optional
from enum import Enum


class ThumbnailStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ThumbnailResp(BaseModel):
    job_id: str = Field(description="job identifier")
    status: ThumbnailStatus = Field(description="job status")
    thumbnail_url: Optional[str] = Field(default=None, description="URL to newly-created thumbnail")
    message: Optional[str] = Field(default=None, description="status message")


async def upload(
        image: UploadFile = File(...),
        length: int = Form(default=200, ge=1, le=2000),
        format: str = Form(default="jpeg"),
        quality: int = Form(default=85, ge=1, le=100)
):
    # TODO: validate the input parameters
    # TODO: implement long-running API for thumbnail generation
    return JSONResponse("{}")
