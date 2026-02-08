"""Tests for data models."""

import pytest
from pydantic import ValidationError
from yubal.models.enums import VideoType
from yubal.models.track import TrackMetadata


class TestVideoType:
    """Tests for VideoType enum."""

    def test_all_video_types(self) -> None:
        """All video types should have correct values."""
        assert VideoType.ATV == "MUSIC_VIDEO_TYPE_ATV"
        assert VideoType.OMV == "MUSIC_VIDEO_TYPE_OMV"
        assert (
            VideoType.OFFICIAL_SOURCE_MUSIC == "MUSIC_VIDEO_TYPE_OFFICIAL_SOURCE_MUSIC"
        )
        assert VideoType.UGC == "MUSIC_VIDEO_TYPE_UGC"

    def test_parse_from_api_string(self) -> None:
        """Should parse from ytmusicapi raw string values."""
        assert VideoType("MUSIC_VIDEO_TYPE_ATV") == VideoType.ATV
        assert VideoType("MUSIC_VIDEO_TYPE_OMV") == VideoType.OMV
        assert VideoType("MUSIC_VIDEO_TYPE_UGC") == VideoType.UGC


class TestTrackMetadata:
    """Tests for TrackMetadata model."""

    def test_minimal_creation(self) -> None:
        """Should create with minimal required fields."""
        track = TrackMetadata(
            omv_video_id="abc123",
            title="Test Song",
            artists=["Test Artist"],
            album="Test Album",
            album_artists=["Test Artist"],
            video_type=VideoType.ATV,
        )
        assert track.omv_video_id == "abc123"
        assert track.atv_video_id is None
        assert track.track_number is None

    def test_full_creation(self) -> None:
        """Should create with all fields."""
        track = TrackMetadata(
            omv_video_id="omv123",
            atv_video_id="atv123",
            title="Test Song",
            artists=["Artist One", "Artist Two"],
            album="Test Album",
            album_artists=["Various Artists"],
            track_number=5,
            year="2024",
            cover_url="https://example.com/cover.jpg",
            video_type=VideoType.OMV,
        )
        assert track.atv_video_id == "atv123"
        assert track.track_number == 5
        assert track.year == "2024"
        # Test computed properties (delimiter is " / " for Jellyfin compatibility)
        assert track.artist == "Artist One / Artist Two"
        assert track.album_artist == "Various Artists"
        assert track.primary_album_artist == "Various Artists"

    def test_model_dump(self) -> None:
        """Should serialize to dict correctly."""
        track = TrackMetadata(
            omv_video_id="abc123",
            title="Test",
            artists=["Artist"],
            album="Album",
            album_artists=["Artist"],
            video_type=VideoType.ATV,
        )
        data = track.model_dump()
        assert data["omv_video_id"] == "abc123"
        assert data["video_type"] == "MUSIC_VIDEO_TYPE_ATV"
        assert data["artists"] == ["Artist"]
        assert data["album_artists"] == ["Artist"]

    def test_rejects_empty_album_artists(self) -> None:
        """Should reject empty album_artists list."""
        with pytest.raises(ValidationError, match="must have at least one entry"):
            TrackMetadata(
                omv_video_id="abc123",
                title="Test",
                artists=["Artist"],
                album="Album",
                album_artists=[],
                video_type=VideoType.ATV,
            )
