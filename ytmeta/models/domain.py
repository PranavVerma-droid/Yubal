"""Domain models for ytmeta.

These are the public models that represent the output of the library.
"""

from enum import StrEnum

from pydantic import BaseModel


class VideoType(StrEnum):
    """YouTube Music video types."""

    ATV = "ATV"  # Audio Track Video (album version)
    OMV = "OMV"  # Official Music Video


class TrackMetadata(BaseModel):
    """Metadata for a single track."""

    omv_video_id: str | None = None
    atv_video_id: str | None = None
    title: str
    artist: str
    album: str
    album_artist: str
    track_number: int | None = None
    total_tracks: int | None = None
    year: str | None = None
    cover_url: str | None = None
    video_type: VideoType
