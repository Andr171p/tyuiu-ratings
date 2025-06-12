from fastapi import APIRouter, status, HTTPException

from dishka.integrations.fastapi import DishkaRoute, FromDishka as Depends

from .base import ApplicantRepository
from .dto import RerankedPriority, CreatedApplicant
from .exceptions import ApplicantsReadingError


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
