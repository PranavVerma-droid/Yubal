"""Services module."""

from .downloader import AlbumInfo, Downloader, DownloadResult
from .tagger import Tagger, TagResult

__all__ = [
    "AlbumInfo",
    "DownloadResult",
    "Downloader",
    "TagResult",
    "Tagger",
]
