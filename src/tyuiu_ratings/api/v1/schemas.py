from typing import Annotated

from fastapi import Query

from pydantic import BaseModel

from src.tyuiu_ratings.core.dto import RerankedPriorityDTO, RecommendationDTO
from src.tyuiu_ratings.constants import AVAILABLE_DIRECTIONS


DirectionQuery = Annotated[AVAILABLE_DIRECTIONS, Query(..., description="Направление подготовки")]


class RerankedPrioritiesResponse(BaseModel):
    priorities: list[RerankedPriorityDTO]


class RecommendationsResponse(BaseModel):
    recommendations: list[RecommendationDTO]
