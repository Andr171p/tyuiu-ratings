from faststream import Logger
from faststream.rabbit import RabbitRouter
from dishka.integrations.base import FromDishka

from src.tyuiu_ratings.core.domain import Applicant
from src.tyuiu_ratings.core.use_cases import RatingUpdater


applicants_router = RabbitRouter()


@applicants_router.subscriber("ratings.applicants")
async def update_applicants(
        applicants: list[Applicant],
        rating_updater: FromDishka[RatingUpdater],
        logger: Logger
) -> None:
    logger.info("Receiving %s applicants", len(applicants))
    await rating_updater.update(applicants)
    logger.info("Successfully update rating of applicants")
