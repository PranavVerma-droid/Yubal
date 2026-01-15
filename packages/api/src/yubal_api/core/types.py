"""Shared type definitions for the application."""

from collections.abc import Callable
from datetime import datetime

# Audio file extensions (includes vorbis as .ogg, weba for WebM audio)
AUDIO_EXTENSIONS = frozenset(
    {
        ".opus",
        ".mp3",
        ".m4a",
        ".aac",
        ".flac",
        ".wav",
        ".ogg",
        ".weba",
    }
)

# Callable type aliases for dependency injection
type Clock = Callable[[], datetime]
type IdGenerator = Callable[[], str]
