from typing import Annotated

from fastapi import Depends

from yubal.services.job_store import JobStore, job_store
from yubal.settings import Settings, get_settings


def get_job_store() -> JobStore:
    return job_store


SettingsDep = Annotated[Settings, Depends(get_settings)]
JobStoreDep = Annotated[JobStore, Depends(get_job_store)]
