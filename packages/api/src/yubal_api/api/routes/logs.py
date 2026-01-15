"""Log streaming endpoints."""

from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from yubal_api.services.log_buffer import get_log_buffer

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/sse")
async def stream_logs() -> StreamingResponse:
    """Stream log lines via Server-Sent Events.

    Sends all existing buffered lines on connect, then streams new lines
    as they arrive. Lines include Rich ANSI formatting codes.
    """
    buffer = get_log_buffer()

    async def event_generator() -> AsyncIterator[str]:
        async with buffer.subscribe() as queue:
            # Send existing lines first
            for line in buffer.get_lines():
                yield f"data: {line}\n\n"

            # Stream new lines as they arrive
            while True:
                line = await queue.get()
                yield f"data: {line}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
