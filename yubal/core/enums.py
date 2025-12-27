from enum import Enum


class JobStatus(str, Enum):
    """Status of a background job."""

    PENDING = "pending"  # Waiting to start
    FETCHING_INFO = "fetching_info"  # Extracting album metadata
    DOWNLOADING = "downloading"  # Downloading tracks (0-80%)
    IMPORTING = "importing"  # Beets import (80-100%)
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProgressStep(str, Enum):
    """Steps in the sync workflow. Values match JobStatus."""

    FETCHING_INFO = "fetching_info"
    DOWNLOADING = "downloading"
    IMPORTING = "importing"
    COMPLETED = "completed"
    FAILED = "failed"
