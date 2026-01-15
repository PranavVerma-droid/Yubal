"""Global log buffer for capturing and streaming ANSI-formatted output."""

import asyncio
import logging
import threading
from collections import deque
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from io import StringIO

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import Traceback


class LogBuffer:
    """Thread-safe global buffer for log lines with SSE subscription support.

    Captures Rich-formatted output and makes it available for streaming
    to clients via Server-Sent Events.
    """

    MAX_LINES = 500

    def __init__(self) -> None:
        self._lines: deque[str] = deque(maxlen=self.MAX_LINES)
        self._lock = threading.Lock()
        self._subscribers: list[asyncio.Queue[str]] = []
        self._subscribers_lock = threading.Lock()

    def append(self, line: str) -> None:
        """Append a line to the buffer and notify subscribers."""
        with self._lock:
            self._lines.append(line)

        # Notify SSE subscribers (non-blocking)
        with self._subscribers_lock:
            for queue in self._subscribers:
                try:
                    queue.put_nowait(line)
                except asyncio.QueueFull:
                    pass  # Drop if subscriber is too slow

    def get_lines(self) -> list[str]:
        """Get all buffered lines."""
        with self._lock:
            return list(self._lines)

    def clear(self) -> None:
        """Clear all buffered lines."""
        with self._lock:
            self._lines.clear()

    @asynccontextmanager
    async def subscribe(self) -> AsyncIterator[asyncio.Queue[str]]:
        """Subscribe to new log lines via context manager."""
        queue: asyncio.Queue[str] = asyncio.Queue()
        with self._subscribers_lock:
            self._subscribers.append(queue)
        try:
            yield queue
        finally:
            with self._subscribers_lock:
                self._subscribers.remove(queue)


class BufferHandler(RichHandler):
    """Captures RichHandler output as ANSI instead of printing to console."""

    def __init__(self, buffer: LogBuffer) -> None:
        console = Console(
            file=StringIO(),
            force_terminal=True,
            width=10000,  # Prevent line wrapping (SSE doesn't handle multiline)
            legacy_windows=False,
            color_system="truecolor",
        )
        super().__init__(
            console=console,
            rich_tracebacks=True,
            show_path=False,
            log_time_format="[%X]",  # Time only, consistent with terminal
        )
        self._buffer = buffer

    def emit(self, record: logging.LogRecord) -> None:
        """Render log with RichHandler styling and export as ANSI."""
        try:
            self.console.file = StringIO()  # Reset buffer

            # Handle traceback like RichHandler.emit() does
            traceback = None
            if (
                self.rich_tracebacks
                and record.exc_info
                and record.exc_info != (None, None, None)
            ):
                exc_type, exc_value, exc_traceback = record.exc_info
                if exc_type is not None and exc_value is not None:
                    traceback = Traceback.from_exception(
                        exc_type, exc_value, exc_traceback
                    )

            # Use RichHandler's render() - handles all styling automatically
            output = self.render(
                record=record,
                traceback=traceback,
                message_renderable=self.render_message(record, record.getMessage()),
            )

            self.console.print(output, highlight=True)
            # Get ANSI output (frontend will convert to HTML)
            file = self.console.file
            assert isinstance(file, StringIO)
            ansi_output = file.getvalue().rstrip()
            self._buffer.append(ansi_output)
        except Exception:
            self.handleError(record)


# Global singleton
_log_buffer: LogBuffer | None = None


def get_log_buffer() -> LogBuffer:
    """Get the global log buffer singleton."""
    global _log_buffer
    if _log_buffer is None:
        _log_buffer = LogBuffer()
    return _log_buffer


def clear_log_buffer() -> None:
    """Clear the global log buffer singleton."""
    global _log_buffer
    _log_buffer = None
