from celery import Celery
from app.internal.configuration.settings import get_settings


settings = get_settings()

# Instantiate global app
celery_app = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BACKEND_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    enable_utc=False,
    task_track_started=True,
)
