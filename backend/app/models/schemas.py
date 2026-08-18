from typing import List, Optional

from pydantic import BaseModel, Field


class PersonaTrait(BaseModel):
    label: str
    value: float = Field(ge=0, le=1)


class Persona(BaseModel):
    id: str
    name: str
    tagline: str
    bio: str
    color: str
    traits: List[PersonaTrait]
    preferred_genres: List[str]
    avoid_tags: List[str] = Field(default_factory=list)
    explanation_tone: str


class CandidateTrack(BaseModel):
    id: str
    title: str
    artist: str
    album: str
    spotify_uri: Optional[str] = None
    spotify_url: Optional[str] = None
    album_image_url: Optional[str] = None
    release_date: Optional[str] = None
    popularity: Optional[int] = Field(default=None, ge=0, le=100)
    explicit: bool = False
    tags: List[str] = Field(default_factory=list)


class RecommendationRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=500)
    persona_ids: Optional[List[str]] = None
    candidate_sources: List[str] = Field(
        default_factory=lambda: ["saved_tracks", "playlists", "search"]
    )
    limit: int = Field(default=8, ge=1, le=30)


class TrackRecommendation(BaseModel):
    track: CandidateTrack
    persona_id: str
    score: int = Field(ge=0, le=100)
    confidence: str
    reasons: List[str]
    concerns: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class PersonaRecommendationGroup(BaseModel):
    persona: Persona
    recommendations: List[TrackRecommendation]


class PlaylistDraft(BaseModel):
    name: str
    description: str
    track_ids: List[str]
    default_public: bool = False


class RecommendationResponse(BaseModel):
    session_id: str
    prompt: str
    candidate_sources: List[str]
    persona_results: List[PersonaRecommendationGroup]
    playlist_draft: PlaylistDraft


class AiSocialComment(BaseModel):
    id: str
    author_persona_id: str
    comment_type: str
    body: str
    attached_track: Optional[CandidateTrack] = None


class AiSocialPost(BaseModel):
    id: str
    author_persona_id: str
    status: str
    topic: str
    body: str
    attached_track: CandidateTrack
    tags: List[str] = Field(default_factory=list)
    source_context: str
    created_at: str
    comments: List[AiSocialComment] = Field(default_factory=list)


class AiCollabTrack(BaseModel):
    position: int
    track: CandidateTrack
    selected_by: List[str]
    consensus_note: str


class AiCollabPlaylist(BaseModel):
    id: str
    title: str
    status: str
    theme: str
    personas: List[str]
    tracks: List[AiCollabTrack]
    observer_note: str


class DiscussionGenerationRequest(BaseModel):
    topic: str = Field(default="비 오는 밤의 첫 곡", min_length=1, max_length=160)


class GeneratedDiscussion(BaseModel):
    topic: str
    posts: List[AiSocialPost]
    collab_playlist: AiCollabPlaylist
