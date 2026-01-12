"""Tests for async functionality."""

import pytest

from tests.conftest import MockYTMusicClient
from ytmeta.services import MetadataExtractorService


class TestAsyncExtract:
    """Tests for async extract method."""

    @pytest.mark.asyncio
    async def test_extract_async_returns_same_as_sync(
        self,
        mock_client: MockYTMusicClient,
    ) -> None:
        """Async extract should return same results as sync."""
        service = MetadataExtractorService(mock_client)

        sync_result = service.extract(
            "https://music.youtube.com/playlist?list=PLtest123"
        )
        async_result = await service.extract_async(
            "https://music.youtube.com/playlist?list=PLtest123"
        )

        assert len(async_result) == len(sync_result)
        assert async_result[0].title == sync_result[0].title

    @pytest.mark.asyncio
    async def test_extract_async_with_progress(
        self,
        mock_client: MockYTMusicClient,
    ) -> None:
        """Async extract should support progress callback."""
        progress_calls: list[tuple[int, int]] = []

        def on_progress(current: int, total: int) -> None:
            progress_calls.append((current, total))

        service = MetadataExtractorService(mock_client)
        await service.extract_async(
            "https://music.youtube.com/playlist?list=PLtest",
            on_progress=on_progress,
        )

        assert len(progress_calls) == 1
        assert progress_calls[0] == (1, 1)
