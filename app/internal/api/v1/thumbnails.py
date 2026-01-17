import uuid
from http import HTTPStatus
from typing import Optional

from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.internal.configuration.settings import get_settings
from app.internal.log.logger import get_logger
from app.internal.tasks.thumbnail import generate_thumbnail
from app.internal.services.storage import StorageService

logger = get_logger()


class ThumbnailResp(BaseModel):
    job_id: str = Field(description="job identifier")
    thumbnail_url: Optional[str] = Field(
        default=None, description="URL to newly-created thumbnail"
    )
    message: Optional[str] = Field(default=None, description="status message")


async def upload(
        image: UploadFile = File(...),
        length: int = Form(default=200, ge=1, le=2000),
        img_format: str = Form(default="jpeg"),
        quality: int = Form(default=85, ge=1, le=100),
):
    """Upload image and start thumbnail generation task"""

    # TODO: validate the input data

    job_id = str(uuid.uuid4())
    logger.debug(f"Job ID: {job_id}")
    try:
        content = await image.read()
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid file")

    try:
        settings = get_settings()
        file_extension = (
            image.filename.split(".")[-1] if "." in image.filename else "jpg"
        )
        key = f"original/{job_id}.{file_extension}"
        storage_service = StorageService(settings)
        storage_service.save(key, content)
    except Exception as e:
        logger.error(f"Failed to upload image: {e}", job_id=job_id)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to upload image")

    # Submit task to Celery
    try:
        task = generate_thumbnail.apply_async(
            args=[key, length, img_format, quality], task_id=job_id
        )
    except Exception as e:
        logger.error("Failed to submit task", job_id=job_id, error=str(e))
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail="Failed to submit task")

    logger.info("Task submitted", job_id=job_id)

    # Return response
    response = ThumbnailResp(
        job_id=task.id,
        message="Started to generating thumbnail",
    )

    return response
