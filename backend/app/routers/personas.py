from typing import List

from fastapi import APIRouter

from app.data.seed import PERSONAS
from app.models.schemas import Persona

router = APIRouter(tags=["personas"])


@router.get("/personas", response_model=List[Persona])
def list_personas():
    return PERSONAS
