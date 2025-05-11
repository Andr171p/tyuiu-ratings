import logging

from typing import List

from faststream.rabbit import RabbitRouter
from dishka.integrations.base import FromDishka

from src.tyuiu_ratings.core.entities import Applicant
from src.tyuiu_ratings.core.interfaces import ApplicantRepository


logger = logging.getLogger(__name__)

applicants_router = RabbitRouter()


@applicants_router.subscriber("ratings.applicants")
async def update_applicants(
        applicants: List[Applicant],
        applicant_repository: FromDishka[ApplicantRepository]
) -> None:
    logger.info("Receiving %s applicants", len(applicants))
    await applicant_repository.bulk_create(applicants)
    logger.info("Successfully saved applicants")
