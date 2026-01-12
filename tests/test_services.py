"""Tests for services."""

import pytest

from tests.conftest import MockYTMusicClient
from ytmeta.models.domain import VideoType
from ytmeta.models.ytmusic import Album, Playlist, SearchResult
from ytmeta.services import MetadataExtractorService


class TestMetadataExtractorService:
    """Tests for MetadataExtractorService."""

    def test_extract_basic(
        self,
        mock_client: MockYTMusicClient,
    ) -> None:
        """Should extract metadata from a playlist."""
        service = MetadataExtractorService(mock_client)
        tracks = service.extract(
            "https://music.youtube.com/playlist?list=PLtest123"
        )

        assert len(tracks) == 1
        assert tracks[0].title == "Test Song"
        assert mock_client.get_playlist_calls == ["PLtest123"]

    def test_extract_with_album_lookup(
        self,
        mock_client: MockYTMusicClient,
        sample_playlist: Playlist,
    ) -> None:
        """Should look up album details."""
        service = MetadataExtractorService(mock_client)
        tracks = service.extract(
            "https://music.youtube.com/playlist?list=PLtest"
        )

        # Should have called get_album for the track's album
        assert len(mock_client.get_album_calls) == 1
        assert tracks[0].album == "Test Album"
        assert tracks[0].year == "2024"

    def test_extract_determines_video_type_atv(
        self,
        mock_client: MockYTMusicClient,
    ) -> None:
        """Should detect ATV video type."""
        service = MetadataExtractorService(mock_client)
        tracks = service.extract(
            "https://music.youtube.com/playlist?list=PLtest"
        )

        # Sample playlist track has MUSIC_VIDEO_TYPE_ATV
        assert tracks[0].video_type == VideoType.ATV

    def test_extract_with_progress_callback(
        self,
        mock_client: MockYTMusicClient,
    ) -> None:
        """Should call progress callback."""
        progress_calls: list[tuple[int, int]] = []

        def on_progress(current: int, total: int) -> None:
            progress_calls.append((current, total))

        service = MetadataExtractorService(mock_client)
        service.extract(
            "https://music.youtube.com/playlist?list=PLtest",
            on_progress=on_progress,
        )

        assert len(progress_calls) == 1
        assert progress_calls[0] == (1, 1)  # 1 of 1 tracks

    def test_extract_handles_missing_album(
        self,
        sample_playlist: Playlist,
        sample_search_result: SearchResult,
        sample_album: Album,
    ) -> None:
        """Should search for album when not in playlist track."""
        # Create a playlist track without album
        playlist_no_album = Playlist.model_validate(
            {
                "tracks": [
                    {
                        "videoId": "v1",
                        "videoType": "MUSIC_VIDEO_TYPE_OMV",
                        "title": "Test Song",
                        "artists": [{"name": "Artist", "id": "a1"}],
                        "thumbnails": [
                            {"url": "https://t.jpg", "width": 120, "height": 90}
                        ],
                        "duration_seconds": 180,
                        # No album field
                    }
                ]
            }
        )

        mock = MockYTMusicClient(
            playlist=playlist_no_album,
            album=sample_album,
            search_results=[sample_search_result],
        )

        service = MetadataExtractorService(mock)
        tracks = service.extract("https://music.youtube.com/playlist?list=PLtest")

        # Should have searched for the song
        assert len(mock.search_songs_calls) == 1
        assert "Artist" in mock.search_songs_calls[0]
        assert "Test Song" in mock.search_songs_calls[0]

    def test_extract_fallback_when_no_album_found(
        self,
    ) -> None:
        """Should create fallback metadata when album can't be found."""
        playlist = Playlist.model_validate(
            {
                "tracks": [
                    {
                        "videoId": "v1",
                        "title": "Unknown Song",
                        "artists": [{"name": "Unknown Artist"}],
                        "thumbnails": [
                            {"url": "https://t.jpg", "width": 120, "height": 90}
                        ],
                        "duration_seconds": 180,
                    }
                ]
            }
        )

        # No album in search results
        mock = MockYTMusicClient(
            playlist=playlist,
            album=None,
            search_results=[],
        )

        service = MetadataExtractorService(mock)
        tracks = service.extract("https://music.youtube.com/playlist?list=PLtest")

        assert len(tracks) == 1
        assert tracks[0].title == "Unknown Song"
        assert tracks[0].album == ""  # No album found
        assert tracks[0].tracknumber is None

    def test_extract_continues_on_track_error(
        self,
    ) -> None:
        """Should continue processing when one track fails."""
        playlist = Playlist.model_validate(
            {
                "tracks": [
                    {
                        "videoId": "v1",
                        "title": "Good Song",
                        "artists": [{"name": "Artist"}],
                        "album": {"id": "alb1", "name": "Album"},
                        "thumbnails": [
                            {"url": "https://t.jpg", "width": 120, "height": 90}
                        ],
                        "duration_seconds": 180,
                    },
                    {
                        "videoId": "v2",
                        "title": "Another Song",
                        "artists": [{"name": "Artist"}],
                        "thumbnails": [
                            {"url": "https://t.jpg", "width": 120, "height": 90}
                        ],
                        "duration_seconds": 200,
                    },
                ]
            }
        )

        # Album lookup will fail
        mock = MockYTMusicClient(
            playlist=playlist,
            album=None,
            search_results=[],
        )

        service = MetadataExtractorService(mock)
        tracks = service.extract("https://music.youtube.com/playlist?list=PLtest")

        # Both tracks should be returned (with fallback for the one without album)
        assert len(tracks) == 2

    def test_extract_matches_track_in_album_by_title(
        self,
        sample_playlist: Playlist,
        sample_album: Album,
    ) -> None:
        """Should match playlist track to album track by title."""
        mock = MockYTMusicClient(
            playlist=sample_playlist,
            album=sample_album,
            search_results=[],
        )

        service = MetadataExtractorService(mock)
        tracks = service.extract("https://music.youtube.com/playlist?list=PLtest")

        # Should have gotten track number from album track
        assert tracks[0].tracknumber == 5

    def test_extract_atv_id_from_search(
        self,
    ) -> None:
        """Should capture ATV video ID from search results."""
        playlist = Playlist.model_validate(
            {
                "tracks": [
                    {
                        "videoId": "omv123",
                        "videoType": "MUSIC_VIDEO_TYPE_OMV",
                        "title": "Test Song",
                        "artists": [{"name": "Artist"}],
                        "thumbnails": [
                            {"url": "https://t.jpg", "width": 120, "height": 90}
                        ],
                        "duration_seconds": 180,
                    }
                ]
            }
        )

        search_result = SearchResult.model_validate(
            {
                "videoId": "atv456",
                "videoType": "MUSIC_VIDEO_TYPE_ATV",
                "album": {"id": "alb1", "name": "Album"},
            }
        )

        album = Album.model_validate(
            {
                "title": "Album",
                "artists": [{"name": "Artist"}],
                "thumbnails": [{"url": "https://t.jpg", "width": 544, "height": 544}],
                "tracks": [
                    {
                        "videoId": "albumtrack1",
                        "title": "Test Song",
                        "artists": [{"name": "Artist"}],
                        "trackNumber": 1,
                        "duration_seconds": 180,
                    }
                ],
            }
        )

        mock = MockYTMusicClient(
            playlist=playlist,
            album=album,
            search_results=[search_result],
        )

        service = MetadataExtractorService(mock)
        tracks = service.extract("https://music.youtube.com/playlist?list=PLtest")

        # Should have captured the ATV ID from search
        assert tracks[0].atv_video_id == "atv456"
        assert tracks[0].video_type == VideoType.OMV
