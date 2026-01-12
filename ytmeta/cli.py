#!/usr/bin/env python3
"""Command-line interface for ytmeta.

This CLI is primarily for debugging and development.
For production use, import ytmeta as a library.
"""

import json
import logging
import sys

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from ytmeta.client import YTMusicClient
from ytmeta.exceptions import YTMetaError
from ytmeta.models.domain import TrackMetadata
from ytmeta.services import MetadataExtractorService

logger = logging.getLogger("ytmeta")


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with Rich handler.

    Args:
        verbose: Enable debug logging if True.
    """
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
    )


def print_table(tracks: list[TrackMetadata]) -> None:
    """Print tracks as a Rich table.

    Args:
        tracks: List of track metadata to display.
    """
    console = Console()
    table = Table(show_header=True, header_style="bold")

    table.add_column("OMV ID")
    table.add_column("ATV ID")
    table.add_column("Title")
    table.add_column("Artist")
    table.add_column("Album")
    table.add_column("Year")
    table.add_column("#", justify="right")
    table.add_column("Type")

    for t in tracks:
        table.add_row(
            t.omv_video_id,
            t.atv_video_id or "",
            t.title,
            t.artist,
            t.album,
            t.year or "",
            str(t.tracknumber) if t.tracknumber else "",
            t.video_type,
        )

    console.print(table)
    console.print(f"\nExtracted {len(tracks)} track(s)")


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging.")
def main(verbose: bool) -> None:
    """Extract metadata from YouTube Music playlists."""
    setup_logging(verbose)


@main.command(name="meta")
@click.argument("url", metavar="PLAYLIST_URL")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def meta_cmd(url: str, as_json: bool) -> None:
    """Extract structured metadata from a playlist.

    PLAYLIST_URL should be a full YouTube Music playlist URL like:
    https://music.youtube.com/playlist?list=PLxxxxxxxx
    """
    try:
        client = YTMusicClient()
        service = MetadataExtractorService(client)
        tracks = service.extract(url)

        if as_json:
            data = [t.model_dump() for t in tracks]
            json.dump(data, sys.stdout, indent=2, ensure_ascii=False, default=str)
        else:
            print_table(tracks)

    except YTMetaError as e:
        logger.error(str(e))
        raise click.ClickException(str(e)) from e
    except Exception as e:
        logger.exception("Unexpected error")
        raise click.ClickException(f"Unexpected error: {e}") from e


if __name__ == "__main__":
    main()
