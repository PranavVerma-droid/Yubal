"""Progress reporting system for API."""

from dataclasses import dataclass, field
from typing import Any, Protocol

from yubal.core.enums import ProgressStep


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
