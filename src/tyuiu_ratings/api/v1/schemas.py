from typing import Annotated

from fastapi import Query

from src.tyuiu_ratings.constants import AVAILABLE_DIRECTIONS, MIN_TOP_N, MAX_TOP_N


DirectionQuery = Annotated[AVAILABLE_DIRECTIONS, Query(..., description="Направление подготовки")]

TopNQuery = Annotated[
    int,
    Query(
        ...,
        ge=MIN_TOP_N,
        le=MAX_TOP_N,
        description="Количество рекомендаций для поиска лучших рекомендаций"
    )
]
