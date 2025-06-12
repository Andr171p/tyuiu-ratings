from faststream import Logger
from faststream.rabbit import RabbitRouter

from dishka.integrations.base import FromDishka

from .dto import ApplicantUpdateEvent
from .use_cases import UpdateApplicantsUseCase


applicants_router = RabbitRouter()


@applicants_router.subscriber("applicants")
async def update_applicants(
        applicants: list[ApplicantUpdateEvent],
        update_applicants_use_case: FromDishka[UpdateApplicantsUseCase],
        logger: Logger
) -> None:
    logger.info("Start update applicants")
    await update_applicants_use_case(applicants)
    logger.info("Finished updating applicants")
