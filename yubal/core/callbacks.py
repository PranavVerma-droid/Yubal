"""Callback types for progress reporting."""

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field

from yubal.core.enums import ProgressStep


class ProgressEvent(BaseModel):
    """A progress update event."""

    step: ProgressStep
    message: str
    progress: float | None = None  # 0-100 for percentage progress
    details: dict[str, Any] = Field(default_factory=dict)


ProgressCallback = Callable[[ProgressEvent], None]
"""Type alias for progress callback functions."""

CancelCheck = Callable[[], bool]
"""Type alias for cancellation check functions."""
