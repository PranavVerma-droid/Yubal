from typing import Annotated

from fastapi import Depends

from yubal.services.job_store import JobStore, job_store
from yubal.services.sync import SyncService
from yubal.settings import Settings, get_settings


def get_job_store() -> JobStore:
    return job_store


def get_sync_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SyncService:
    return SyncService(
        library_dir=settings.library_dir,
        beets_config=settings.beets_config,
        audio_format=settings.audio_format,
    )


SettingsDep = Annotated[Settings, Depends(get_settings)]
JobStoreDep = Annotated[JobStore, Depends(get_job_store)]
SyncServiceDep = Annotated[SyncService, Depends(get_sync_service)]
