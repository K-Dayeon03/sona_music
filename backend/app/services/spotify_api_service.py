from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException, status

from app.models.schemas import CandidateTrack
from app.services.spotify_auth_service import get_current_token

SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"


def _get_token_or_raise() -> Dict[str, Any]:
    token = get_current_token()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Spotify is not connected yet.",
        )
    return token


async def get_current_user_profile() -> Dict[str, Any]:
    token = _get_token_or_raise()

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{SPOTIFY_API_BASE_URL}/me",
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Spotify token is expired or invalid. Please reconnect.",
        )

    response.raise_for_status()
    return response.json()


async def get_available_devices() -> List[Dict[str, Any]]:
    token = _get_token_or_raise()

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{SPOTIFY_API_BASE_URL}/me/player/devices",
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Spotify token is expired or invalid. Please reconnect.",
        )

    response.raise_for_status()
    return response.json().get("devices", [])


async def start_track_playback(spotify_uri: str, device_id: Optional[str] = None) -> Dict[str, Any]:
    token = _get_token_or_raise()

    params = {"device_id": device_id} if device_id else None

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.put(
            f"{SPOTIFY_API_BASE_URL}/me/player/play",
            params=params,
            json={"uris": [spotify_uri]},
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Spotify token is expired or invalid. Please reconnect.",
        )

    if response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Playback requires a Spotify Premium account and playback permission.",
        )

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active Spotify device found. Open Spotify on your computer or phone first.",
        )

    response.raise_for_status()
    return {"playing": True, "spotify_uri": spotify_uri}


async def search_tracks(query: str, limit: int = 10) -> List[CandidateTrack]:
    token = _get_token_or_raise()
    safe_limit = max(1, min(limit, 10))

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{SPOTIFY_API_BASE_URL}/search",
            params={
                "q": query,
                "type": "track",
                "limit": safe_limit,
            },
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

    _raise_for_spotify_response(response)
    items = response.json().get("tracks", {}).get("items", [])
    return [_track_from_spotify_item(item, source_tag="spotify-search") for item in items]


async def get_saved_tracks(limit: int = 10) -> List[CandidateTrack]:
    token = _get_token_or_raise()
    safe_limit = max(1, min(limit, 50))

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{SPOTIFY_API_BASE_URL}/me/tracks",
            params={"limit": safe_limit},
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

    _raise_for_spotify_response(response)
    items = response.json().get("items", [])
    return [
        _track_from_spotify_item(item["track"], source_tag="saved-track")
        for item in items
        if item.get("track")
    ]


def _raise_for_spotify_response(response: httpx.Response) -> None:
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Spotify token is expired or invalid. Please reconnect.",
        )
    response.raise_for_status()


def _track_from_spotify_item(item: Dict[str, Any], source_tag: str) -> CandidateTrack:
    album = item.get("album") or {}
    artists = item.get("artists") or []
    external_urls = item.get("external_urls") or {}
    album_external_urls = album.get("external_urls") or {}
    images = album.get("images") or []

    return CandidateTrack(
        id=item.get("id") or item.get("uri") or item.get("name", "unknown"),
        title=item.get("name", "Unknown title"),
        artist=", ".join(artist.get("name", "Unknown artist") for artist in artists)
        or "Unknown artist",
        album=album.get("name", "Unknown album"),
        spotify_uri=item.get("uri"),
        spotify_url=external_urls.get("spotify") or album_external_urls.get("spotify"),
        album_image_url=images[0].get("url") if images else None,
        release_date=album.get("release_date"),
        popularity=item.get("popularity"),
        explicit=bool(item.get("explicit", False)),
        tags=[source_tag],
    )
