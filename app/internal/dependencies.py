from fastapi import Depends

from app.internal.configuration.settings import Settings, get_settings
from app.internal.services.storage import StorageService


def get_storage_service(settings: Settings = Depends(get_settings)) -> StorageService:
    return StorageService(settings)
