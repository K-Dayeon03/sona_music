import os
from functools import lru_cache
from typing import List

from dotenv import load_dotenv

load_dotenv()


DEFAULT_SPOTIFY_SCOPES = [
    "user-library-read",
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-read-recently-played",
    "user-top-read",
    "playlist-modify-private",
    "user-read-playback-state",
    "user-modify-playback-state",
]


class Settings:
    def __init__(self):
        self.spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID", "")
        self.spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "")
        self.spotify_redirect_uri = os.getenv(
            "SPOTIFY_REDIRECT_URI",
            "http://127.0.0.1:8000/api/auth/spotify/callback",
        )
        self.spotify_scopes = _parse_scopes(os.getenv("SPOTIFY_SCOPES", ""))
        self.frontend_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:8443")

    @property
    def spotify_is_configured(self) -> bool:
        return bool(
            self.spotify_client_id
            and self.spotify_client_secret
            and self.spotify_redirect_uri
        )


def _parse_scopes(raw_scopes: str) -> List[str]:
    if not raw_scopes.strip():
        return DEFAULT_SPOTIFY_SCOPES

    return [scope for scope in raw_scopes.split() if scope]


@lru_cache
def get_settings() -> Settings:
    return Settings()
