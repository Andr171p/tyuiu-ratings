from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Query

from dishka.integrations.fastapi import DishkaRoute, FromDishka as Depends

from .base import ApplicantRepository
from .use_cases import RecommendDirectionsUseCase
from .dto import RerankedPriority, CreatedApplicant, PredictedRecommendation, CompetitionList
from .exceptions import ApplicantsReadingError, DirectionsRecommendationError

from ..constants import MIN_TOP_N, MAX_TOP_N


applicants_router = APIRouter(
    prefix="/api/v1/applicants",
    tags=["Applicants"],
    route_class=DishkaRoute
)


@applicants_router.get(
    path="/{applicant_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[CreatedApplicant],
    summary="Возвращает абитуриентов отсортированных по приоритетам"
)
async def get_applicants(
        applicant_id: int,
        applicant_repository: Depends[ApplicantRepository]
) -> list[CreatedApplicant]:
    try:
        applicants = await applicant_repository.read(applicant_id)
        if not applicants:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicants not found"
            )
        return applicants
    except ApplicantsReadingError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while receiving applicants"
        )


@applicants_router.get(
    path="/{applicant_id}",
    status_code=status.HTTP_200_OK,
    response_model=CreatedApplicant,
    summary="Возвращает абитуриента по его ID и направлению подготовки"
)
async def get_applicant(
        applicant_id: int,
        direction: Annotated[str, Query(..., description="Направление подготовки")],
        applicant_repository: Depends[ApplicantRepository]
) -> CreatedApplicant:
    try:
        applicant = await applicant_repository.get_applicant(applicant_id, direction)
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        return applicant
    except ApplicantsReadingError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while receiving applicants"
        )


@applicants_router.get(
    path="/{applicant_id}/competition-list",
    status_code=status.HTTP_200_OK,
    response_model=CompetitionList,
    summary="Возвращает интерактивный конкурсный список на направление подготовки"
)
async def get_competition_list(
        applicant_id: int,
        direction: Annotated[str, Query(..., description="Направление подготовки")],
        applicant_repository: Depends[ApplicantRepository]
) -> CompetitionList:
    try:
        applicants = await applicant_repository.get_applicants_by_direction(direction)
        if not applicants:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No applicants yet"
            )
        return CompetitionList(
            applicant_id=applicant_id,
            institute=applicants[0].institute,
            direction=direction,
            applicants=applicants
        )
    except ApplicantsReadingError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while receiving competition list"
        )


@applicants_router.get(
    path="/{applicant_id}/rerank-priorities",
    status_code=status.HTTP_200_OK,
    response_model=list[RerankedPriority],
    summary="Расставляет приоритеты по вероятности поступления"
)
async def rerank_priorities(
        applicant_id: int,
        applicant_repository: Depends[ApplicantRepository]
) -> list[RerankedPriority]:
    applicants = await applicant_repository.sort_by_probability(applicant_id)
    if not applicants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error while reranking priorities"
        )
    return applicants


@applicants_router.get(
    path="/{applicant_id}/recommend-directions",
    status_code=status.HTTP_200_OK,
    response_model=list[PredictedRecommendation],
    summary="Возвращает размеченный список рекомендаций"
)
async def recommend_directions(
        applicant_id: int,
        top_n: Annotated[
            int,
            Query(
                ge=MIN_TOP_N,
                le=MAX_TOP_N,
                description="Величина выборки рекомендаций"
            )
        ],
        recommend_directions_use_case: Depends[RecommendDirectionsUseCase]
) -> list[PredictedRecommendation]:
    try:
        recommendations = await recommend_directions_use_case(applicant_id, top_n=top_n)
        return recommendations
    except DirectionsRecommendationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while recommend directions: {e}"
        )
