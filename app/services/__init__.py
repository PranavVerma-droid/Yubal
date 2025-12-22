"""Services module."""
from .downloader import Downloader, AlbumInfo, DownloadResult
from .tagger import Tagger, TagResult

__all__ = [
    "Downloader",
    "AlbumInfo",
    "DownloadResult",
    "Tagger",
    "TagResult",
]
