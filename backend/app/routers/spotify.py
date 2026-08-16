from fastapi import APIRouter

from app.models.schemas import PlaybackRequest
from app.services.spotify_api_service import get_available_devices, start_track_playback

router = APIRouter(prefix="/spotify", tags=["spotify"])


@router.get("/devices")
async def spotify_devices():
    return {"devices": await get_available_devices()}


@router.post("/play")
async def spotify_play(request: PlaybackRequest):
    return await start_track_playback(
        spotify_uri=request.spotify_uri,
        device_id=request.device_id,
    )
