from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from yubal.core.enums import JobStatus
from yubal.core.models import AlbumInfo


@dataclass
class LogEntry:
    """A log entry for a job."""

    timestamp: datetime
    step: str
    message: str
    progress: float | None = None
    details: dict[str, Any] | None = None


@dataclass
class Job:
    """A background sync job."""

    id: str
    url: str
    audio_format: str = "mp3"
    phase: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    message: str = ""
    album_info: AlbumInfo | None = None
    current_track: int | None = None  # 1-based track number being processed
    total_tracks: int | None = None  # Total tracks in album
    logs: list[LogEntry] = field(default_factory=list)
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
