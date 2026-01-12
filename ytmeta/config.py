"""Configuration for ytmeta."""

from dataclasses import dataclass


@dataclass(frozen=True)
class APIConfig:
    """YouTube Music API configuration.

    Attributes:
        search_limit: Maximum number of search results to return.
        ignore_spelling: Whether to ignore spelling in search queries.
    """

    search_limit: int = 1
    ignore_spelling: bool = True


# Default configuration instance
default_config = APIConfig()
