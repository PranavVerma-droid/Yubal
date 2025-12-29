"""Cookies management endpoints."""

from fastapi import APIRouter, HTTPException

from yubal.api.dependencies import SettingsDep
from yubal.schemas.cookies import (
    CookiesStatusResponse,
    CookiesUploadRequest,
    CookiesUploadResponse,
)

router = APIRouter(prefix="/cookies", tags=["cookies"])


@router.get("/status", response_model=CookiesStatusResponse)
async def cookies_status(settings: SettingsDep) -> CookiesStatusResponse:
    """Check if cookies file is configured."""
    return CookiesStatusResponse(configured=settings.cookies_file.exists())


@router.post("", response_model=CookiesUploadResponse)
async def upload_cookies(
    body: CookiesUploadRequest, settings: SettingsDep
) -> CookiesUploadResponse:
    """Upload cookies.txt content (Netscape format)."""
    if not body.content.strip():
        raise HTTPException(400, "Empty cookie file")
    # Basic validation: Netscape cookie format starts with comment or domain
    first_line = body.content.split("\n")[0]
    if not (first_line.startswith("#") or first_line.startswith(".")):
        raise HTTPException(
            400, "Invalid cookie file format (expected Netscape format)"
        )

    settings.ytdlp_dir.mkdir(parents=True, exist_ok=True)
    settings.cookies_file.write_text(body.content)
    return CookiesUploadResponse(status="ok")


@router.delete("", response_model=CookiesUploadResponse)
async def delete_cookies(settings: SettingsDep) -> CookiesUploadResponse:
    """Delete cookies file."""
    if settings.cookies_file.exists():
        settings.cookies_file.unlink()
    return CookiesUploadResponse(status="ok")
