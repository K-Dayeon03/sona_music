from typing import List

from fastapi import APIRouter

from app.models.schemas import (
    AiCollabPlaylist,
    AiSocialPost,
    DiscussionGenerationRequest,
    GeneratedDiscussion,
)
from app.services.discussion_service import (
    DEFAULT_TOPICS,
    generate_discussion,
)
from app.services.storage_service import list_collabs, list_posts, save_discussion

router = APIRouter(tags=["social"])


@router.get("/feed", response_model=List[AiSocialPost])
def list_ai_feed():
    seed_default_discussions()
    return list_posts()


@router.get("/collabs", response_model=List[AiCollabPlaylist])
def list_collab_playlists():
    seed_default_discussions()
    return list_collabs()


@router.post("/discussions/generate", response_model=GeneratedDiscussion)
def create_discussion(request: DiscussionGenerationRequest):
    discussion = generate_discussion(request.topic)
    save_discussion(discussion)
    return discussion


def seed_default_discussions() -> None:
    if list_posts() and list_collabs():
        return

    for topic in DEFAULT_TOPICS:
        save_discussion(generate_discussion(topic))
