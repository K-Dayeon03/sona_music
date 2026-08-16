import base64
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx

from app.config import Settings

SPOTIFY_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

_pending_states = set()
_token_store: Dict[str, Any] = {}


def build_authorization_url(settings: Settings) -> str:
    state = secrets.token_urlsafe(24)
    _pending_states.add(state)

    params = {
        "response_type": "code",
        "client_id": settings.spotify_client_id,
        "scope": " ".join(settings.spotify_scopes),
        "redirect_uri": settings.spotify_redirect_uri,
        "state": state,
    }
    return f"{SPOTIFY_AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code_for_token(
    settings: Settings,
    code: str,
    state: str,
) -> Dict[str, Any]:
    if state not in _pending_states:
        raise ValueError("state_mismatch")

    _pending_states.discard(state)
    auth_header = _basic_auth_header(settings.spotify_client_id, settings.spotify_client_secret)

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            SPOTIFY_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.spotify_redirect_uri,
            },
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

    response.raise_for_status()
    token_payload = response.json()
    _save_token(token_payload)
    return token_payload


def get_current_token() -> Optional[Dict[str, Any]]:
    if not _token_store:
        return None

    return dict(_token_store)


def clear_current_token() -> None:
    _token_store.clear()


def _basic_auth_header(client_id: str, client_secret: str) -> str:
    token = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    return f"Basic {token}"


def _save_token(token_payload: Dict[str, Any]) -> None:
    expires_in = int(token_payload.get("expires_in", 3600))
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    _token_store.clear()
    _token_store.update(token_payload)
    _token_store["expires_at"] = expires_at.isoformat() + "Z"
