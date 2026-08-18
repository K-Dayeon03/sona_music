from typing import List

from fastapi import APIRouter, Query

from app.models.schemas import CandidateTrack
from app.services.spotify_catalog_service import search_tracks


router = APIRouter(prefix="/spotify", tags=["spotify"])


@router.get("/search-tracks", response_model=List[CandidateTrack])
def search_spotify_tracks(
    q: str = Query(..., min_length=1, max_length=160),
    limit: int = Query(default=10, ge=1, le=50),
):
    return search_tracks(q, limit=limit)
