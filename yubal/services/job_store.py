import asyncio
import uuid
from collections import OrderedDict
from datetime import UTC, datetime
from typing import Any

from yubal.core.enums import JobStatus
from yubal.core.models import AlbumInfo, Job, LogEntry


class JobStore:
    """Thread-safe in-memory job store with capacity limit."""

    MAX_JOBS = 50
    MAX_LOGS = 100
    TIMEOUT_SECONDS = 30 * 60  # 30 minutes

    def __init__(self) -> None:
        self._jobs: OrderedDict[str, Job] = OrderedDict()
        self._lock = asyncio.Lock()
        self._active_job_id: str | None = None
        self._cancellation_requested: set[str] = set()

    async def create_job(self, url: str, audio_format: str = "mp3") -> Job | None:
        """
        Create a new job.

        Returns None if a job is already running (caller should return 409).
        """
        async with self._lock:
            # Check if there's an active job
            if self._active_job_id is not None:
                active = self._jobs.get(self._active_job_id)
                if active and active.status not in (
                    JobStatus.COMPLETED,
                    JobStatus.FAILED,
                    JobStatus.CANCELLED,
                ):
                    return None  # Job already running

            # Prune old jobs if at capacity
            while len(self._jobs) >= self.MAX_JOBS:
                # Remove oldest job (first item in OrderedDict)
                oldest_id = next(iter(self._jobs))
                del self._jobs[oldest_id]

            # Create new job
            job = Job(
                id=str(uuid.uuid4()),
                url=url,
                audio_format=audio_format,
            )
            self._jobs[job.id] = job
            self._active_job_id = job.id

            return job

    async def get_job(self, job_id: str) -> Job | None:
        """Get a job by ID. Also checks for timeout."""
        async with self._lock:
            job = self._jobs.get(job_id)
            if job:
                self._check_timeout(job)
            return job

    async def get_all_jobs(self) -> list[Job]:
        """Get all jobs, most recent first."""
        async with self._lock:
            # Check timeouts on all active jobs
            for job in self._jobs.values():
                self._check_timeout(job)
            return list(reversed(self._jobs.values()))

    async def get_active_job(self) -> Job | None:
        """Get the currently active job, if any."""
        async with self._lock:
            if self._active_job_id:
                job = self._jobs.get(self._active_job_id)
                if job:
                    self._check_timeout(job)
                return job
            return None

    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running job.

        Returns False if job doesn't exist or is already finished.
        """
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False

            # Cannot cancel already finished jobs
            if job.status in (
                JobStatus.COMPLETED,
                JobStatus.FAILED,
                JobStatus.CANCELLED,
            ):
                return False

            # Mark as cancelled
            self._cancellation_requested.add(job_id)
            job.status = JobStatus.CANCELLED
            job.message = "Job cancelled by user"
            job.completed_at = datetime.now(UTC)

            # Clear active job if it matches
            if self._active_job_id == job_id:
                self._active_job_id = None

            return True

    def is_cancelled(self, job_id: str) -> bool:
        """Check if cancellation was requested for a job."""
        return job_id in self._cancellation_requested

    async def update_job(
        self,
        job_id: str,
        status: JobStatus | None = None,
        progress: float | None = None,
        message: str | None = None,
        album_info: AlbumInfo | None = None,
        current_track: int | None = None,
        total_tracks: int | None = None,
        error: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> Job | None:
        """Update job fields. Cancelled jobs cannot be updated."""
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None

            # Don't update cancelled jobs (prevents race conditions)
            if job.status == JobStatus.CANCELLED:
                return job

            if status is not None:
                job.status = status
            if progress is not None:
                job.progress = progress
            if message is not None:
                job.message = message
            if album_info is not None:
                job.album_info = album_info
            if current_track is not None:
                job.current_track = current_track
            if total_tracks is not None:
                job.total_tracks = total_tracks
            if error is not None:
                job.error = error
            if started_at is not None:
                job.started_at = started_at
            if completed_at is not None:
                job.completed_at = completed_at

            # Clear active job if completed, failed, or cancelled
            if job.status in (
                JobStatus.COMPLETED,
                JobStatus.FAILED,
                JobStatus.CANCELLED,
            ):
                job.completed_at = job.completed_at or datetime.now(UTC)
                if self._active_job_id == job_id:
                    self._active_job_id = None

            return job

    async def add_log(
        self,
        job_id: str,
        step: str,
        message: str,
        progress: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Add a log entry to a job. Trims to MAX_LOGS if exceeded."""
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return

            # Don't add logs to cancelled jobs (prevents stale updates)
            if job.status == JobStatus.CANCELLED:
                return

            entry = LogEntry(
                timestamp=datetime.now(UTC),
                step=step,
                message=message,
                progress=progress,
                details=details,
            )
            job.logs.append(entry)

            # Trim logs if exceeded
            if len(job.logs) > self.MAX_LOGS:
                job.logs = job.logs[-self.MAX_LOGS :]

    async def delete_job(self, job_id: str) -> bool:
        """
        Delete a job.

        Returns False if job doesn't exist or is still running.
        """
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False

            if job.status not in (
                JobStatus.COMPLETED,
                JobStatus.FAILED,
                JobStatus.CANCELLED,
            ):
                return False  # Cannot delete running job

            del self._jobs[job_id]
            # Also remove from cancellation set if present
            self._cancellation_requested.discard(job_id)
            return True

    async def clear_completed(self) -> int:
        """
        Clear all completed/failed/cancelled jobs.

        Returns the number of jobs removed.
        """
        async with self._lock:
            to_remove = [
                job_id
                for job_id, job in self._jobs.items()
                if job.status
                in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED)
            ]
            for job_id in to_remove:
                del self._jobs[job_id]
                self._cancellation_requested.discard(job_id)
            return len(to_remove)

    def _check_timeout(self, job: Job) -> bool:
        """
        Check if job has timed out. Must be called with lock held.

        Returns True if job was timed out.
        """
        if job.started_at and job.status not in (
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        ):
            elapsed = datetime.now(UTC) - job.started_at
            if elapsed.total_seconds() > self.TIMEOUT_SECONDS:
                job.status = JobStatus.FAILED
                job.error = "Job timed out after 30 minutes"
                job.completed_at = datetime.now(UTC)
                if self._active_job_id == job.id:
                    self._active_job_id = None
                return True
        return False


# Global singleton instance
job_store = JobStore()
