import uuid
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.internal.dependencies import get_storage_service
from app.internal.log.logger import get_logger
from app.internal.tasks.thumbnail import generate_thumbnail
from app.internal.services.storage import StorageService

logger = get_logger()
router = APIRouter()


class ThumbnailResp(BaseModel):
    job_id: str = Field(description="job identifier")
    message: Optional[str] = Field(default=None, description="status message")


@router.post("/thumbnails/")
async def upload(
        image: UploadFile = File(...),
        storage_service: StorageService = Depends(get_storage_service),
):
    """Upload image and start thumbnail generation task"""

    # TODO: validate the input data
    try:
        content = await image.read()
        file_extension = (
            image.filename.split(".")[-1] if "." in image.filename else "jpg"
        )
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid file")
    finally:
        await image.close()

    # Upload original image to storage
    job_id = str(uuid.uuid4())
    logger.debug(f"Job ID: {job_id}")
    try:
        path = f"original/{job_id}.{file_extension}"
        content_type = f"image/{file_extension}"
        key = storage_service.save(path, content, content_type)
        logger.info(f"Image uploaded to: {key}", job_id=job_id)
    except Exception as e:
        logger.error(f"Failed to upload image: {e}", job_id=job_id)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to upload image")

    # Submit task to Celery
    try:
        task = generate_thumbnail.apply_async(args=[key], task_id=job_id)
    except Exception as e:
        logger.error("Failed to submit task", job_id=job_id, error=str(e))
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail="Failed to submit task")

    logger.info("Task submitted", job_id=job_id)

    # Return response
    response = ThumbnailResp(
        job_id=task.id,
        message="Started to generate thumbnail",
    )

    return response
