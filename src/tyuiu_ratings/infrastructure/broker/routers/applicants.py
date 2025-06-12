from faststream import Logger
from faststream.rabbit import RabbitRouter

from dishka.integrations.base import FromDishka

from src.tyuiu_ratings.core.domain import Applicant
from src.tyuiu_ratings.core.use_cases.competition_list import UpdateCompetitionListUseCase


applicants_router = RabbitRouter()


@applicants_router.subscriber("ratings.applicant")
async def update_applicants(
        applicants: list[Applicant],
        update_competition_list_use_case: FromDishka[UpdateCompetitionListUseCase],
        logger: Logger
) -> None:
    logger.info("Receiving %s applicant", len(applicants))
    await update_competition_list_use_case.update(applicants)
    logger.info("Successfully update rating of applicant")
