"""Celery tasks for thumbnail generation"""

from celery import Task
from celery.exceptions import Retry

from app.internal.tasks.celery import celery_app
from app.internal.log.logger import get_logger
from app.internal.configuration.settings import get_settings
from app.internal.services.storage import StorageService

logger = get_logger()
settings = get_settings()


@celery_app.task(bind=True, name="thumbnail.generate")
def generate_thumbnail(self, image_path: str, length: int, format: str, quality: int):
    """Generate thumbnail from image"""
    logger.info("Generating thumbnail", task_id=self.request.id, image_path=image_path)
    try:
        self.update_state(state="PROGRESS")
        # Load image from storage
        storage_service = StorageService(settings)
        image_data = storage_service.load(image_path)

        # Resize image
        # TODO: Implement image resizing

        # Save thumbnail to storage
        thumbnail_path = f"thumbnail/{self.request.id}.{format}"
        thumbnail_url = storage_service.save(thumbnail_path, image_data)

        result = {
            "thumbnail_url": thumbnail_url,
            "status": "completed",
        }

        logger.info("Thumbnail generated", task_id=self.request.id, result=result)
        return result

    except Exception as e:
        logger.error(
            "Thumbnail generation failed", task_id=self.request.id, error=str(e)
        )
        self.retry(countdown=60 * 1, max_retries=3, exc=e)
