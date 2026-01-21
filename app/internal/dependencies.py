from fastapi import Depends

from app.internal.configuration.settings import Settings, get_settings
from app.internal.database import get_session
from app.internal.services.storage import StorageService


def get_db_session(settings: Settings = Depends(get_settings)):
    """Get database session dependency"""
    yield from get_session(settings)


def get_storage_service(settings: Settings = Depends(get_settings)) -> StorageService:
    """Get Storage service dependency"""
    return StorageService(settings)
