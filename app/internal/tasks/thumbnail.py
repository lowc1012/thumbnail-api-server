"""Celery tasks for thumbnail generation"""
from botocore.exceptions import ClientError
from app.internal.tasks.celery import celery_app
from app.internal.log.logger import get_logger
from app.internal.configuration.settings import get_settings
from app.internal.services.image import ImageService
from app.internal.services.storage import StorageService

logger = get_logger()
settings = get_settings()


@celery_app.task(bind=True, name="thumbnail.generate")
def generate_thumbnail(self, image_path: str):
    """Generate thumbnail from image"""
    logger.info("Generating thumbnail", task_id=self.request.id, image_path=image_path)

    desired_size = (100, 100)
    try:
        self.update_state(state="PROGRESS")
        # Load image from storage
        storage_service = StorageService(settings)
        image_bytes = storage_service.load(image_path)

        # Resize image
        image_service = ImageService()
        thumbnail_bytes, thumbnail_format = image_service.resize(image_bytes, desired_size)

        # Save thumbnail to storage
        thumbnail_path = f"thumbnail/{self.request.id}.{thumbnail_format.lower()}"
        thumbnail_key = storage_service.save(thumbnail_path, thumbnail_bytes)

        return {
            "job_id": self.request.id,
            "endpoint_url": storage_service.endpoint_url,
            "bucket": storage_service.bucket_name,
            "key": thumbnail_key,
        }

    except (ClientError, IOError) as e:
        logger.error(f"Retryable error: {e}", task_id=self.request.id, error=str(e))
        self.retry(countdown=60, max_retries=3, exc=e)
    except Exception as e:
        logger.error(
            f"Thumbnail generation failed: {e}", task_id=self.request.id, error=str(e)
        )
        raise e
