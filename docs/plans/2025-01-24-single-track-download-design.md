# Single Track Download Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Support downloading individual tracks from YouTube Music watch URLs (`?v=VIDEO_ID`).

**Architecture:** Add URL parsing for video IDs, wrap `get_watch_playlist()` API in client, create single-track extraction method that reuses existing `_extract_single_track()` logic, and integrate into the download service.

**Tech Stack:** Python 3.12, pydantic, ytmusicapi, pytest

---

## Task 1: URL Parsing - Add `parse_video_id()` function

**Files:**
- Modify: `packages/yubal/src/yubal/utils/url.py`
- Modify: `packages/yubal/tests/test_utils.py`

**Step 1: Write the failing tests**

Add to `packages/yubal/tests/test_utils.py`:

```python
class TestParseVideoId:
    """Tests for parse_video_id function."""

    def test_extracts_from_music_youtube_url(self) -> None:
        """Should extract video ID from music.youtube.com URL."""
        url = "https://music.youtube.com/watch?v=Vgpv5PtWsn4"
        assert parse_video_id(url) == "Vgpv5PtWsn4"

    def test_extracts_from_youtube_url(self) -> None:
        """Should extract video ID from youtube.com URL."""
        url = "https://www.youtube.com/watch?v=GkTWxDB21cA"
        assert parse_video_id(url) == "GkTWxDB21cA"

    def test_extracts_from_url_with_extra_params(self) -> None:
        """Should extract video ID when URL has extra parameters."""
        url = "https://music.youtube.com/watch?v=abc123&si=xyz789"
        assert parse_video_id(url) == "abc123"

    def test_returns_none_for_playlist_url(self) -> None:
        """Should return None for playlist URLs (no video ID)."""
        url = "https://music.youtube.com/playlist?list=PLtest123"
        assert parse_video_id(url) is None

    def test_returns_none_for_url_with_list_and_v(self) -> None:
        """Should return None when URL has both list= and v= (playlist priority)."""
        url = "https://music.youtube.com/watch?v=abc123&list=PLtest123"
        assert parse_video_id(url) is None

    def test_returns_none_for_empty_url(self) -> None:
        """Should return None for empty URLs."""
        assert parse_video_id("") is None

    def test_returns_none_for_malformed_v_param(self) -> None:
        """Should return None when v param is empty."""
        url = "https://music.youtube.com/watch?v="
        assert parse_video_id(url) is None
```

Also add the import at the top of the test file:
```python
from yubal.utils import format_artists, get_square_thumbnail, parse_playlist_id, parse_video_id
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest packages/yubal/tests/test_utils.py::TestParseVideoId -v`
Expected: FAIL with "ImportError" or "cannot import name 'parse_video_id'"

**Step 3: Write the implementation**

Update `packages/yubal/src/yubal/utils/url.py`:

```python
"""URL parsing utilities."""

import re

from yubal.exceptions import PlaylistParseError

PLAYLIST_ID_PATTERN = re.compile(r"list=([A-Za-z0-9_-]+)")
VIDEO_ID_PATTERN = re.compile(r"v=([A-Za-z0-9_-]+)")


def parse_playlist_id(url: str) -> str:
    """Extract playlist ID from YouTube Music URL.

    Args:
        url: Full YouTube Music playlist URL.

    Returns:
        The playlist ID string.

    Raises:
        PlaylistParseError: If playlist ID cannot be extracted.
    """
    if match := PLAYLIST_ID_PATTERN.search(url):
        return match.group(1)
    raise PlaylistParseError(f"Could not extract playlist ID from: {url}")


def parse_video_id(url: str) -> str | None:
    """Extract video ID from YouTube Music URL if it's a single track.

    Returns None if the URL contains a playlist ID (list= parameter takes priority)
    or if no video ID is found.

    Args:
        url: Full YouTube Music URL.

    Returns:
        The video ID string, or None if not a single track URL.
    """
    # Playlist URLs take priority - return None if list= is present
    if PLAYLIST_ID_PATTERN.search(url):
        return None

    if match := VIDEO_ID_PATTERN.search(url):
        return match.group(1)
    return None
```

**Step 4: Export the function**

Update `packages/yubal/src/yubal/utils/__init__.py` to export `parse_video_id`:

Check current exports and add `parse_video_id` to the imports and `__all__`.

**Step 5: Run tests to verify they pass**

Run: `uv run pytest packages/yubal/tests/test_utils.py::TestParseVideoId -v`
Expected: All 7 tests PASS

**Step 6: Commit**

```bash
git add packages/yubal/src/yubal/utils/url.py packages/yubal/tests/test_utils.py packages/yubal/src/yubal/utils/__init__.py
git commit -m "feat(url): add parse_video_id for single track URLs"
```

---

## Task 2: Client - Add `get_track()` method wrapping `get_watch_playlist()`

**Files:**
- Modify: `packages/yubal/src/yubal/client.py`
- Modify: `packages/yubal/src/yubal/models/ytmusic.py`
- Create: `packages/yubal/tests/test_client_track.py`

**Step 1: Write the failing test**

Create `packages/yubal/tests/test_client_track.py`:

```python
"""Tests for YTMusicClient.get_track() method."""

import pytest
from unittest.mock import MagicMock, patch

from yubal.client import YTMusicClient
from yubal.exceptions import APIError, TrackNotFoundError


class TestGetTrack:
    """Tests for get_track method."""

    def test_returns_playlist_track_for_valid_video_id(self) -> None:
        """Should return a PlaylistTrack for a valid video ID."""
        mock_ytm = MagicMock()
        mock_ytm.get_watch_playlist.return_value = {
            "tracks": [
                {
                    "videoId": "Vgpv5PtWsn4",
                    "title": "A COLD PLAY",
                    "artists": [{"name": "The Kid LAROI", "id": "UC123"}],
                    "album": {"name": "A COLD PLAY", "id": "MPREb_123"},
                    "videoType": "MUSIC_VIDEO_TYPE_ATV",
                    "thumbnails": [{"url": "https://example.com/thumb.jpg", "width": 120, "height": 120}],
                    "duration_seconds": 180,
                }
            ]
        }

        client = YTMusicClient(ytmusic=mock_ytm)
        track = client.get_track("Vgpv5PtWsn4")

        assert track.video_id == "Vgpv5PtWsn4"
        assert track.title == "A COLD PLAY"
        assert track.video_type == "MUSIC_VIDEO_TYPE_ATV"
        assert track.album is not None
        assert track.album.id == "MPREb_123"
        mock_ytm.get_watch_playlist.assert_called_once_with("Vgpv5PtWsn4")

    def test_raises_for_empty_video_id(self) -> None:
        """Should raise ValueError for empty video ID."""
        client = YTMusicClient(ytmusic=MagicMock())

        with pytest.raises(ValueError, match="video_id cannot be empty"):
            client.get_track("")

    def test_raises_track_not_found_for_no_tracks(self) -> None:
        """Should raise TrackNotFoundError when API returns no tracks."""
        mock_ytm = MagicMock()
        mock_ytm.get_watch_playlist.return_value = {"tracks": []}

        client = YTMusicClient(ytmusic=mock_ytm)

        with pytest.raises(TrackNotFoundError, match="Track not found"):
            client.get_track("invalid123")

    def test_raises_api_error_on_exception(self) -> None:
        """Should raise APIError when ytmusicapi raises an exception."""
        mock_ytm = MagicMock()
        mock_ytm.get_watch_playlist.side_effect = Exception("API failure")

        client = YTMusicClient(ytmusic=mock_ytm)

        with pytest.raises(APIError, match="Failed to fetch track"):
            client.get_track("abc123")
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest packages/yubal/tests/test_client_track.py -v`
Expected: FAIL with "ImportError" (TrackNotFoundError) or AttributeError (get_track)

**Step 3: Add TrackNotFoundError exception**

Update `packages/yubal/src/yubal/exceptions.py`, add after `PlaylistNotFoundError`:

```python
class TrackNotFoundError(YTMetaError):
    """Track not found or inaccessible.

    Raised when the track doesn't exist or is unavailable.
    """

    status_code: int = 404  # Not Found
```

**Step 4: Add get_track method to client**

Update `packages/yubal/src/yubal/client.py`:

1. Add import for TrackNotFoundError:
```python
from yubal.exceptions import (
    APIError,
    AuthenticationRequiredError,
    PlaylistNotFoundError,
    TrackNotFoundError,
    UnsupportedPlaylistError,
    YTMetaError,
)
```

2. Add to YTMusicProtocol:
```python
    def get_track(self, video_id: str) -> PlaylistTrack:
        """Fetch a single track by video ID."""
        ...
```

3. Add import for PlaylistTrack in the imports section:
```python
from yubal.models.ytmusic import Album, Playlist, PlaylistTrack, SearchResult
```

4. Add the method to YTMusicClient class (after search_songs method):

```python
    def get_track(self, video_id: str) -> PlaylistTrack:
        """Fetch a single track by video ID.

        Uses get_watch_playlist() which returns track data in the same format
        as get_playlist() tracks, enabling reuse of extraction logic.

        Args:
            video_id: YouTube video ID.

        Returns:
            Parsed PlaylistTrack model.

        Raises:
            ValueError: If video_id is empty.
            TrackNotFoundError: If track doesn't exist or is unavailable.
            APIError: If API request fails.
        """
        if not video_id or not video_id.strip():
            raise ValueError("video_id cannot be empty")

        logger.debug("Fetching track: %s", video_id)
        try:
            data = self._ytm.get_watch_playlist(video_id)
        except Exception as e:
            logger.exception("Failed to fetch track %s: %s", video_id, e)
            raise APIError(f"Failed to fetch track: {e}") from e

        tracks = data.get("tracks") or []
        if not tracks:
            raise TrackNotFoundError(f"Track not found: {video_id}")

        # First track in watch playlist is the requested track
        track_data = tracks[0]
        return PlaylistTrack.model_validate(track_data)
```

**Step 5: Run tests to verify they pass**

Run: `uv run pytest packages/yubal/tests/test_client_track.py -v`
Expected: All 4 tests PASS

**Step 6: Commit**

```bash
git add packages/yubal/src/yubal/client.py packages/yubal/src/yubal/exceptions.py packages/yubal/tests/test_client_track.py
git commit -m "feat(client): add get_track method for single track fetching"
```

---

## Task 3: Extractor - Add `extract_track()` method for single tracks

**Files:**
- Modify: `packages/yubal/src/yubal/services/extractor.py`
- Create: `packages/yubal/tests/test_extractor_track.py`

**Step 1: Write the failing test**

Create `packages/yubal/tests/test_extractor_track.py`:

```python
"""Tests for MetadataExtractorService.extract_track() method."""

import pytest
from yubal.models.domain import ContentKind, VideoType
from yubal.models.ytmusic import Album, AlbumRef, AlbumTrack, Artist, PlaylistTrack, SearchResult, Thumbnail
from yubal.services.extractor import MetadataExtractorService


class MockClientForTrack:
    """Mock client for single track tests."""

    def __init__(
        self,
        track: PlaylistTrack | None = None,
        album: Album | None = None,
        search_results: list[SearchResult] | None = None,
    ) -> None:
        self._track = track
        self._album = album
        self._search_results = search_results or []
        self.get_track_calls: list[str] = []
        self.get_album_calls: list[str] = []
        self.search_songs_calls: list[str] = []

    def get_track(self, video_id: str) -> PlaylistTrack:
        self.get_track_calls.append(video_id)
        if self._track is None:
            raise ValueError("No track configured")
        return self._track

    def get_album(self, album_id: str) -> Album:
        self.get_album_calls.append(album_id)
        if self._album is None:
            raise ValueError("No album configured")
        return self._album

    def search_songs(self, query: str) -> list[SearchResult]:
        self.search_songs_calls.append(query)
        return self._search_results


@pytest.fixture
def atv_track() -> PlaylistTrack:
    """ATV track with album info."""
    return PlaylistTrack.model_validate({
        "videoId": "Vgpv5PtWsn4",
        "videoType": "MUSIC_VIDEO_TYPE_ATV",
        "title": "A COLD PLAY",
        "artists": [{"name": "The Kid LAROI", "id": "UC123"}],
        "album": {"id": "MPREb_123", "name": "A COLD PLAY"},
        "thumbnails": [{"url": "https://example.com/thumb.jpg", "width": 544, "height": 544}],
        "duration_seconds": 180,
    })


@pytest.fixture
def sample_album() -> Album:
    """Album with matching track."""
    return Album.model_validate({
        "title": "A COLD PLAY",
        "artists": [{"name": "The Kid LAROI", "id": "UC123"}],
        "year": "2025",
        "thumbnails": [{"url": "https://example.com/album.jpg", "width": 544, "height": 544}],
        "tracks": [{
            "videoId": "Vgpv5PtWsn4",
            "title": "A COLD PLAY",
            "artists": [{"name": "The Kid LAROI", "id": "UC123"}],
            "trackNumber": 1,
            "duration_seconds": 180,
        }],
    })


class TestExtractTrack:
    """Tests for extract_track method."""

    def test_extracts_atv_track_with_album(self, atv_track: PlaylistTrack, sample_album: Album) -> None:
        """Should extract ATV track and enrich with album metadata."""
        client = MockClientForTrack(track=atv_track, album=sample_album)
        extractor = MetadataExtractorService(client)

        result = extractor.extract_track("https://music.youtube.com/watch?v=Vgpv5PtWsn4")

        assert result is not None
        assert result.track.title == "A COLD PLAY"
        assert result.track.year == "2025"
        assert result.track.track_number == 1
        assert result.track.video_type == VideoType.ATV
        assert result.playlist_info.kind == ContentKind.TRACK
        assert client.get_track_calls == ["Vgpv5PtWsn4"]
        assert client.get_album_calls == ["MPREb_123"]

    def test_returns_none_for_ugc_track(self) -> None:
        """Should return None for UGC (non-music) tracks."""
        ugc_track = PlaylistTrack.model_validate({
            "videoId": "jNQXAC9IVRw",
            "videoType": "MUSIC_VIDEO_TYPE_UGC",
            "title": "Me at the zoo",
            "artists": [{"name": "jawed", "id": None}],
            "album": None,
            "thumbnails": [{"url": "https://example.com/thumb.jpg", "width": 120, "height": 90}],
            "duration_seconds": 19,
        })
        client = MockClientForTrack(track=ugc_track)
        extractor = MetadataExtractorService(client)

        result = extractor.extract_track("https://youtube.com/watch?v=jNQXAC9IVRw")

        assert result is None

    def test_extracts_from_youtube_url(self, atv_track: PlaylistTrack, sample_album: Album) -> None:
        """Should work with regular youtube.com URLs."""
        client = MockClientForTrack(track=atv_track, album=sample_album)
        extractor = MetadataExtractorService(client)

        result = extractor.extract_track("https://www.youtube.com/watch?v=Vgpv5PtWsn4")

        assert result is not None
        assert result.track.title == "A COLD PLAY"
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest packages/yubal/tests/test_extractor_track.py -v`
Expected: FAIL with AttributeError (no extract_track method)

**Step 3: Add ContentKind.TRACK enum value**

Update `packages/yubal/src/yubal/models/domain.py`, add to ContentKind enum:

```python
class ContentKind(StrEnum):
    """Type of music content (album vs playlist vs track)."""

    ALBUM = "album"
    PLAYLIST = "playlist"
    TRACK = "track"
```

**Step 4: Add SingleTrackResult model**

Add to `packages/yubal/src/yubal/models/domain.py` (after ExtractProgress class):

```python
class SingleTrackResult(BaseModel):
    """Result of extracting a single track.

    Attributes:
        track: Extracted track metadata.
        playlist_info: Synthetic playlist info for the track (kind=TRACK).
    """

    model_config = ConfigDict(frozen=True)

    track: TrackMetadata
    playlist_info: PlaylistInfo
```

**Step 5: Add extract_track method to extractor**

Update `packages/yubal/src/yubal/services/extractor.py`:

1. Add import for SingleTrackResult:
```python
from yubal.models.domain import (
    ContentKind,
    ExtractProgress,
    PlaylistInfo,
    SingleTrackResult,
    SkipReason,
    TrackMetadata,
    UnavailableTrack,
    VideoType,
)
```

2. Add import for parse_video_id:
```python
from yubal.utils.url import parse_playlist_id, parse_video_id
```

3. Add new exception import:
```python
from yubal.exceptions import TrackParseError
```

4. Add the method after `extract_all()`:

```python
    def extract_track(self, url: str) -> SingleTrackResult | None:
        """Extract metadata for a single track from a watch URL.

        Args:
            url: YouTube Music watch URL with video ID.

        Returns:
            SingleTrackResult with track metadata and synthetic playlist info,
            or None if the track has an unsupported video type (e.g., UGC).

        Raises:
            TrackParseError: If URL doesn't contain a video ID.
            TrackNotFoundError: If track doesn't exist.
            APIError: If API requests fail.
        """
        video_id = parse_video_id(url)
        if not video_id:
            raise TrackParseError(f"Could not extract video ID from: {url}")

        logger.debug("Extracting metadata for track: %s", video_id)

        # Fetch track using get_watch_playlist (same format as playlist tracks)
        track = self._client.get_track(video_id)

        # Process through existing single track extraction logic
        metadata = self._extract_single_track(track)

        # Return None for unsupported video types (UGC, etc.)
        if metadata is None:
            return None

        # Create synthetic playlist info for single track
        playlist_info = PlaylistInfo(
            playlist_id=video_id,
            title=metadata.title,
            cover_url=metadata.cover_url,
            kind=ContentKind.TRACK,
            author=None,
            unavailable_tracks=[],
        )

        return SingleTrackResult(track=metadata, playlist_info=playlist_info)
```

**Step 6: Add TrackParseError exception**

Update `packages/yubal/src/yubal/exceptions.py`, add after PlaylistParseError:

```python
class TrackParseError(YTMetaError):
    """Failed to parse track URL.

    Raised when the provided URL doesn't contain a valid video ID.
    """

    status_code: int = 400  # Bad Request
```

**Step 7: Update YTMusicProtocol to include get_track**

The protocol in `client.py` already has `get_track` from Task 2.

**Step 8: Run tests to verify they pass**

Run: `uv run pytest packages/yubal/tests/test_extractor_track.py -v`
Expected: All 3 tests PASS

**Step 9: Commit**

```bash
git add packages/yubal/src/yubal/services/extractor.py packages/yubal/src/yubal/models/domain.py packages/yubal/src/yubal/exceptions.py packages/yubal/tests/test_extractor_track.py
git commit -m "feat(extractor): add extract_track method for single tracks"
```

---

## Task 4: Integration - Wire up single track support in download service

**Files:**
- Modify: `packages/yubal/src/yubal/services/playlist.py`
- Create: `packages/yubal/tests/test_download_track.py`

**Step 1: Write the failing test**

Create `packages/yubal/tests/test_download_track.py`:

```python
"""Tests for single track download support."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from yubal.config import PlaylistDownloadConfig, DownloadConfig
from yubal.models.domain import ContentKind, DownloadStatus, SingleTrackResult, TrackMetadata, PlaylistInfo, VideoType
from yubal.services.playlist import PlaylistDownloadService


@pytest.fixture
def single_track_result() -> SingleTrackResult:
    """Single track extraction result."""
    track = TrackMetadata(
        atv_video_id="Vgpv5PtWsn4",
        omv_video_id=None,
        title="A COLD PLAY",
        artists=["The Kid LAROI"],
        album="A COLD PLAY",
        album_artists=["The Kid LAROI"],
        track_number=1,
        total_tracks=1,
        year="2025",
        cover_url="https://example.com/cover.jpg",
        video_type=VideoType.ATV,
    )
    playlist_info = PlaylistInfo(
        playlist_id="Vgpv5PtWsn4",
        title="A COLD PLAY",
        cover_url="https://example.com/cover.jpg",
        kind=ContentKind.TRACK,
    )
    return SingleTrackResult(track=track, playlist_info=playlist_info)


class TestDownloadTrack:
    """Tests for downloading single tracks."""

    def test_download_single_track_url(self, single_track_result: SingleTrackResult, tmp_path: Path) -> None:
        """Should download a single track from a watch URL."""
        config = PlaylistDownloadConfig(
            download=DownloadConfig(base_path=tmp_path),
            generate_m3u=False,
            save_cover=False,
        )

        mock_extractor = MagicMock()
        mock_extractor.extract_track.return_value = single_track_result

        mock_downloader = MagicMock()
        mock_download_result = MagicMock()
        mock_download_result.result.status = DownloadStatus.SUCCESS
        mock_download_result.result.track = single_track_result.track
        mock_download_result.current = 1
        mock_download_result.total = 1
        mock_downloader.download_tracks.return_value = iter([mock_download_result])

        service = PlaylistDownloadService(
            config=config,
            extractor=mock_extractor,
            downloader=mock_downloader,
        )

        # Consume the generator
        progress_updates = list(service.download_playlist("https://music.youtube.com/watch?v=Vgpv5PtWsn4"))

        # Verify extract_track was called (not extract)
        mock_extractor.extract_track.assert_called_once()
        mock_extractor.extract.assert_not_called()

        # Verify download was called with the track
        mock_downloader.download_tracks.assert_called_once()
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest packages/yubal/tests/test_download_track.py -v`
Expected: FAIL (extract_track not called, extract called instead)

**Step 3: Update PlaylistDownloadService to detect single tracks**

Update `packages/yubal/src/yubal/services/playlist.py`:

1. Add imports:
```python
from yubal.models.domain import (
    CancelToken,
    DownloadResult,
    DownloadStatus,
    PlaylistDownloadResult,
    PlaylistInfo,
    PlaylistProgress,
    SingleTrackResult,
    TrackMetadata,
    aggregate_skip_reasons,
)
from yubal.utils.url import parse_video_id
```

2. Update `download_playlist` method to detect single track URLs. Replace the extraction phase call:

```python
    def download_playlist(
        self,
        url: str,
        cancel_token: CancelToken | None = None,
    ) -> Iterator[PlaylistProgress]:
        # ... existing docstring ...

        # Check for cancellation before starting
        self._check_cancellation(cancel_token)

        # Log pipeline start
        logger.info(
            "Starting new download",
            extra={"header": "New Download"},
        )

        # Check if this is a single track URL
        video_id = parse_video_id(url)
        if video_id:
            # Single track flow
            yield from self._execute_single_track_extraction(url, cancel_token)
        else:
            # Playlist flow (existing)
            yield from (
                progress for progress in self._execute_extraction_phase(url, cancel_token)
            )

        tracks, playlist_info = self._get_extraction_results()

        # ... rest of method unchanged ...
```

3. Add the single track extraction method:

```python
    def _execute_single_track_extraction(
        self,
        url: str,
        cancel_token: CancelToken | None,
    ) -> Iterator[PlaylistProgress]:
        """Execute single track extraction.

        Args:
            url: YouTube Music watch URL.
            cancel_token: Optional cancellation token.

        Yields:
            PlaylistProgress with phase="extracting".
        """
        logger.info(
            "Fetching track metadata",
            extra={"phase": "extracting", "phase_num": 1},
        )

        self._extracted_tracks = []
        self._playlist_info = None

        result = self._extractor.extract_track(url)

        if result is None:
            # Unsupported video type (UGC, etc.)
            logger.warning("Track has unsupported video type, skipping")
            return

        self._extracted_tracks = [result.track]
        self._playlist_info = result.playlist_info

        # Yield single progress update
        from yubal.models.domain import ExtractProgress

        progress = ExtractProgress(
            current=1,
            total=1,
            playlist_total=1,
            skipped_by_reason={},
            track=result.track,
            playlist_info=result.playlist_info,
        )

        yield PlaylistProgress(
            phase="extracting",
            current=1,
            total=1,
            extract_progress=progress,
        )

        logger.info("Track: %s", result.track.title)
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest packages/yubal/tests/test_download_track.py -v`
Expected: PASS

**Step 5: Run all tests**

Run: `uv run pytest packages/yubal/tests/ -v`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add packages/yubal/src/yubal/services/playlist.py packages/yubal/tests/test_download_track.py
git commit -m "feat(service): integrate single track download support"
```

---

## Task 5: Export new public API

**Files:**
- Modify: `packages/yubal/src/yubal/__init__.py`
- Modify: `packages/yubal/src/yubal/utils/__init__.py`

**Step 1: Check current exports**

Read `packages/yubal/src/yubal/__init__.py` and `packages/yubal/src/yubal/utils/__init__.py`.

**Step 2: Update exports**

In `packages/yubal/src/yubal/utils/__init__.py`, add `parse_video_id` to exports.

In `packages/yubal/src/yubal/__init__.py`, add new exceptions:
- `TrackNotFoundError`
- `TrackParseError`

And add new model:
- `SingleTrackResult`

**Step 3: Run tests to verify nothing breaks**

Run: `uv run pytest packages/yubal/tests/ -v`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add packages/yubal/src/yubal/__init__.py packages/yubal/src/yubal/utils/__init__.py
git commit -m "feat: export single track API components"
```

---

## Task 6: Manual testing with real URLs

**Step 1: Test ATV track**

```bash
uv run python -c "
from yubal import create_playlist_downloader
from yubal.config import PlaylistDownloadConfig, DownloadConfig
from pathlib import Path

config = PlaylistDownloadConfig(
    download=DownloadConfig(base_path=Path('./test_output')),
    generate_m3u=False,
    save_cover=False,
)
service = create_playlist_downloader(config)

for progress in service.download_playlist('https://music.youtube.com/watch?v=Vgpv5PtWsn4'):
    print(f'[{progress.phase}] {progress.current}/{progress.total}')

result = service.get_result()
if result:
    print(f'Downloaded: {result.success_count}')
"
```

**Step 2: Test OMV track**

```bash
uv run python -c "
from yubal import create_playlist_downloader
from yubal.config import PlaylistDownloadConfig, DownloadConfig
from pathlib import Path

config = PlaylistDownloadConfig(
    download=DownloadConfig(base_path=Path('./test_output')),
    generate_m3u=False,
    save_cover=False,
)
service = create_playlist_downloader(config)

for progress in service.download_playlist('https://music.youtube.com/watch?v=GkTWxDB21cA'):
    print(f'[{progress.phase}] {progress.current}/{progress.total}')

result = service.get_result()
if result:
    print(f'Downloaded: {result.success_count}')
"
```

**Step 3: Test UGC track (should skip)**

```bash
uv run python -c "
from yubal import create_playlist_downloader
from yubal.config import PlaylistDownloadConfig, DownloadConfig
from pathlib import Path

config = PlaylistDownloadConfig(
    download=DownloadConfig(base_path=Path('./test_output')),
)
service = create_playlist_downloader(config)

for progress in service.download_playlist('https://www.youtube.com/watch?v=jNQXAC9IVRw'):
    print(f'[{progress.phase}] {progress.current}/{progress.total}')

result = service.get_result()
print(f'Result: {result}')  # Should be None
"
```

**Step 4: Verify playlist URLs still work**

```bash
uv run python -c "
from yubal import create_playlist_downloader
from yubal.config import PlaylistDownloadConfig, DownloadConfig
from pathlib import Path

config = PlaylistDownloadConfig(
    download=DownloadConfig(base_path=Path('./test_output')),
    max_items=1,  # Just test first track
)
service = create_playlist_downloader(config)

for progress in service.download_playlist('https://music.youtube.com/playlist?list=PLbE6wFkAlDUfy14yaVjdfGv4wDGmbebH4'):
    print(f'[{progress.phase}] {progress.current}/{progress.total}')
"
```

**Step 5: Clean up test output**

```bash
rm -rf ./test_output
```

---

Plan complete and saved to `docs/plans/2025-01-24-single-track-download-design.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
