"""Progress reporting system for CLI and API."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol


class ProgressStep(str, Enum):
    """Steps in the sync workflow. Values match JobStatus."""

    FETCHING_INFO = "fetching_info"
    DOWNLOADING = "downloading"
    IMPORTING = "importing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProgressEvent:
    """A progress update event."""

    step: ProgressStep
    message: str
    progress: float | None = None  # 0-100 for percentage progress
    details: dict[str, Any] = field(default_factory=dict)


class ProgressCallback(Protocol):
    """Protocol for progress callback functions."""

    def __call__(self, event: ProgressEvent) -> None:
        """Handle a progress event."""
        ...
