import sqlite3
from pathlib import Path
from typing import List

from app.models.schemas import AiCollabPlaylist, AiSocialPost, GeneratedDiscussion


DATABASE_PATH = Path(__file__).resolve().parents[2] / ".sona" / "sona_spotify.sqlite3"


def save_discussion(discussion: GeneratedDiscussion) -> None:
    _ensure_schema()
    with _connect() as connection:
        for post in discussion.posts:
            connection.execute(
                """
                INSERT OR REPLACE INTO social_posts (id, topic, payload, created_at)
                VALUES (?, ?, ?, datetime('now'))
                """,
                (post.id, discussion.topic, _model_to_json(post)),
            )
        connection.execute(
            """
            INSERT OR REPLACE INTO collab_playlists (id, topic, payload, created_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (
                discussion.collab_playlist.id,
                discussion.topic,
                _model_to_json(discussion.collab_playlist),
            ),
        )


def list_posts() -> List[AiSocialPost]:
    _ensure_schema()
    with _connect() as connection:
        rows = connection.execute(
            "SELECT payload FROM social_posts ORDER BY created_at DESC, id DESC"
        ).fetchall()
    return [_post_from_json(row["payload"]) for row in rows]


def list_collabs() -> List[AiCollabPlaylist]:
    _ensure_schema()
    with _connect() as connection:
        rows = connection.execute(
            "SELECT payload FROM collab_playlists ORDER BY created_at DESC, id DESC"
        ).fetchall()
    return [_collab_from_json(row["payload"]) for row in rows]


def reset_store() -> None:
    _ensure_schema()
    with _connect() as connection:
        connection.execute("DELETE FROM social_posts")
        connection.execute("DELETE FROM collab_playlists")


def _connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _ensure_schema() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS social_posts (
              id TEXT PRIMARY KEY,
              topic TEXT NOT NULL,
              payload TEXT NOT NULL,
              created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS collab_playlists (
              id TEXT PRIMARY KEY,
              topic TEXT NOT NULL,
              payload TEXT NOT NULL,
              created_at TEXT NOT NULL
            )
            """
        )


def _model_to_json(model) -> str:
    if hasattr(model, "model_dump_json"):
        return model.model_dump_json()
    return model.json()


def _post_from_json(raw: str) -> AiSocialPost:
    if hasattr(AiSocialPost, "model_validate_json"):
        return AiSocialPost.model_validate_json(raw)
    return AiSocialPost.parse_raw(raw)


def _collab_from_json(raw: str) -> AiCollabPlaylist:
    if hasattr(AiCollabPlaylist, "model_validate_json"):
        return AiCollabPlaylist.model_validate_json(raw)
    return AiCollabPlaylist.parse_raw(raw)
