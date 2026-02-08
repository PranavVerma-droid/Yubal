"""Tests for API schemas."""

import pytest
from yubal_api.schemas.jobs import validate_youtube_music_url


class TestValidateYouTubeMusicUrl:
    """Tests for YouTube Music URL validation."""

    @pytest.mark.parametrize(
        "url",
        [
            # Playlist URLs
            "https://music.youtube.com/playlist?list=OLAK5uy_test123",
            "https://www.youtube.com/playlist?list=PLtest123",
            "https://music.youtube.com/browse/MPREb_test123",
            # Single track URLs
            "https://music.youtube.com/watch?v=Vgpv5PtWsn4",
            "https://www.youtube.com/watch?v=GkTWxDB21cA",
            "https://youtube.com/watch?v=GkTWxDB21cA",
            # URLs with extra params
            "https://music.youtube.com/watch?v=abc123&si=xyz789",
            "https://music.youtube.com/watch?v=abc123&list=PLtest123",
        ],
        ids=[
            "music_youtube_playlist",
            "youtube_playlist",
            "music_youtube_browse",
            "music_youtube_watch",
            "youtube_watch",
            "youtube_watch_no_www",
            "watch_extra_params",
            "watch_with_list",
        ],
    )
    def test_accepts_valid_urls(self, url: str) -> None:
        """Should accept valid YouTube Music URLs."""
        assert validate_youtube_music_url(url) == url

    @pytest.mark.parametrize(
        "url",
        [
            "https://example.com/test",
            "",
            "https://music.youtube.com/",
            "https://music.youtube.com/watch",
        ],
        ids=["random_url", "empty_url", "youtube_homepage", "watch_no_video_id"],
    )
    def test_rejects_invalid_urls(self, url: str) -> None:
        """Should reject invalid URLs."""
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_youtube_music_url(url)

    def test_strips_whitespace(self) -> None:
        """Should strip whitespace from URL."""
        url = "  https://music.youtube.com/watch?v=abc123  "
        assert validate_youtube_music_url(url) == url.strip()
