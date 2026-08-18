import base64
import os
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import httpx
from fastapi import HTTPException, status

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass

from app.models.schemas import CandidateTrack


SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"
DEFAULT_MARKET = os.getenv("SPOTIFY_MARKET", "US")

_TOKEN_CACHE: Dict[str, object] = {
    "access_token": "",
    "expires_at": 0.0,
}


def spotify_is_configured() -> bool:
    return bool(_client_id() and _client_secret())


def search_tracks(query: str, limit: int = 10, market: Optional[str] = None) -> List[CandidateTrack]:
    cleaned_query = " ".join(query.strip().split())
    if not cleaned_query:
        return []

    token = _get_app_access_token()
    response = _spotify_get(
        "/search",
        token=token,
        params={
            "q": cleaned_query,
            "type": "track",
            "limit": max(1, min(limit, 50)),
            "market": market or DEFAULT_MARKET,
        },
    )

    items = response.get("tracks", {}).get("items", [])
    return [_track_from_item(item, source_query=cleaned_query) for item in items if item]


def search_tracks_for_queries(
    queries: Iterable[str],
    limit_per_query: int = 8,
    total_limit: int = 32,
    market: Optional[str] = None,
) -> List[CandidateTrack]:
    tracks: List[CandidateTrack] = []
    seen_track_ids = set()

    for query in queries:
        for track in search_tracks(query, limit=limit_per_query, market=market):
            if track.id in seen_track_ids:
                continue
            seen_track_ids.add(track.id)
            tracks.append(track)
            if len(tracks) >= total_limit:
                return tracks

    return tracks


def _get_app_access_token() -> str:
    cached_token = str(_TOKEN_CACHE.get("access_token") or "")
    expires_at = float(_TOKEN_CACHE.get("expires_at") or 0)
    if cached_token and time.time() < expires_at:
        return cached_token

    client_id = _client_id()
    client_secret = _client_secret()
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Spotify API 설정이 필요합니다. backend/.env 또는 배포 환경 변수에 "
                "SPOTIFY_CLIENT_ID와 SPOTIFY_CLIENT_SECRET을 추가해주세요."
            ),
        )

    basic_token = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode(
        "utf-8"
    )

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                SPOTIFY_TOKEN_URL,
                headers={
                    "Authorization": f"Basic {basic_token}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={"grant_type": "client_credentials"},
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as error:
        detail = _spotify_error_detail(error.response)
        raise HTTPException(
            status_code=_mapped_spotify_status(error.response.status_code),
            detail=f"Spotify 토큰 발급에 실패했습니다: {detail}",
        ) from error
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Spotify 토큰 서버에 연결하지 못했습니다.",
        ) from error

    payload = response.json()
    access_token = payload.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Spotify 토큰 응답에 access_token이 없습니다.",
        )

    expires_in = int(payload.get("expires_in") or 3600)
    _TOKEN_CACHE["access_token"] = access_token
    _TOKEN_CACHE["expires_at"] = time.time() + max(60, expires_in - 60)
    return access_token


def _spotify_get(path: str, token: str, params: Dict[str, object]) -> Dict[str, object]:
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{SPOTIFY_API_BASE_URL}{path}",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
            )
            if response.status_code == status.HTTP_401_UNAUTHORIZED:
                _TOKEN_CACHE["access_token"] = ""
                response = client.get(
                    f"{SPOTIFY_API_BASE_URL}{path}",
                    headers={"Authorization": f"Bearer {_get_app_access_token()}"},
                    params=params,
                )
            response.raise_for_status()
    except httpx.HTTPStatusError as error:
        detail = _spotify_error_detail(error.response)
        raise HTTPException(
            status_code=_mapped_spotify_status(error.response.status_code),
            detail=f"Spotify 검색에 실패했습니다: {detail}",
        ) from error
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Spotify 검색 서버에 연결하지 못했습니다.",
        ) from error

    return response.json()


def _track_from_item(item: Dict[str, object], source_query: str) -> CandidateTrack:
    album = item.get("album") if isinstance(item.get("album"), dict) else {}
    artists = item.get("artists") if isinstance(item.get("artists"), list) else []
    artist_names = [
        str(artist.get("name"))
        for artist in artists
        if isinstance(artist, dict) and artist.get("name")
    ]
    images = album.get("images") if isinstance(album.get("images"), list) else []
    image_url = None
    if images and isinstance(images[0], dict):
        image_url = images[0].get("url")

    external_urls = item.get("external_urls") if isinstance(item.get("external_urls"), dict) else {}

    return CandidateTrack(
        id=str(item.get("id") or item.get("uri") or item.get("href")),
        title=str(item.get("name") or "Untitled track"),
        artist=", ".join(artist_names) or "Unknown artist",
        album=str(album.get("name") or "Unknown album"),
        spotify_uri=str(item.get("uri")) if item.get("uri") else None,
        spotify_url=str(external_urls.get("spotify")) if external_urls.get("spotify") else None,
        album_image_url=str(image_url) if image_url else None,
        release_date=str(album.get("release_date")) if album.get("release_date") else None,
        popularity=item.get("popularity") if isinstance(item.get("popularity"), int) else None,
        explicit=bool(item.get("explicit") or False),
        tags=_tags_from_query(source_query),
    )


def _tags_from_query(query: str) -> List[str]:
    lowered_query = query.lower()
    tags = []
    for token, tag in {
        "rain": "rain",
        "night": "night",
        "late": "late-night",
        "indie": "indie",
        "experimental": "experimental",
        "texture": "texture",
        "ambient": "instrumental",
        "instrumental": "instrumental",
        "focus": "focus",
        "study": "focus",
        "work": "work",
        "dance": "dance",
        "house": "dance",
        "electronic": "rhythm",
        "pulse": "rhythm",
        "drive": "city",
        "pop": "bright",
    }.items():
        if token in lowered_query and tag not in tags:
            tags.append(tag)
    return tags


def _mapped_spotify_status(status_code: int) -> int:
    if status_code in {
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
        status.HTTP_404_NOT_FOUND,
        status.HTTP_429_TOO_MANY_REQUESTS,
    }:
        return status_code
    return status.HTTP_502_BAD_GATEWAY


def _spotify_error_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        message = response.text.strip()
    else:
        error_payload = payload.get("error") if isinstance(payload, dict) else None
        if isinstance(error_payload, dict):
            message = str(error_payload.get("message") or payload)
        else:
            message = str(payload)

    if "Active premium subscription required" in message:
        return (
            "Spotify 앱 소유자 계정에 활성 Premium 구독이 필요합니다. "
            "구독 상태가 바뀐 뒤 반영까지 몇 시간이 걸릴 수 있습니다."
        )

    return message[:300] or f"HTTP {response.status_code}"


def _client_id() -> str:
    return os.getenv("SPOTIFY_CLIENT_ID", "").strip()


def _client_secret() -> str:
    return os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()
