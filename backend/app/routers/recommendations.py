from fastapi import APIRouter

from app.models.schemas import RecommendationRequest, RecommendationResponse
from app.services.recommendation_service import create_recommendations as create_recommendation_result

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationResponse)
async def create_recommendations(request: RecommendationRequest):
    return await create_recommendation_result(request)
