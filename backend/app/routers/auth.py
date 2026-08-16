from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from httpx import HTTPStatusError

from app.config import get_settings
from app.services.spotify_api_service import get_current_user_profile
from app.services.spotify_auth_service import (
    build_authorization_url,
    clear_current_token,
    exchange_code_for_token,
    get_current_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/spotify/status")
def spotify_status():
    settings = get_settings()
    token = get_current_token()

    return {
        "configured": settings.spotify_is_configured,
        "connected": token is not None,
        "expires_at": token.get("expires_at") if token else None,
        "scopes": settings.spotify_scopes,
    }


@router.get("/spotify/login")
def spotify_login():
    settings = get_settings()
    if not settings.spotify_is_configured:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Spotify credentials are not configured.",
        )

    return RedirectResponse(build_authorization_url(settings))


@router.get("/spotify/callback")
async def spotify_callback(
    code: str = Query(default=""),
    state: str = Query(default=""),
    error: str = Query(default=""),
):
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Spotify authorization failed: {error}",
        )

    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Spotify callback is missing code or state.",
        )

    settings = get_settings()
    try:
        await exchange_code_for_token(settings, code=code, state=state)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Spotify token exchange failed: {exc.response.text}",
        ) from exc

    return RedirectResponse(f"{settings.frontend_url}/?spotify=connected")


@router.get("/spotify/me")
async def spotify_me():
    return await get_current_user_profile()


@router.post("/spotify/logout")
def spotify_logout():
    clear_current_token()
    return {"connected": False}
