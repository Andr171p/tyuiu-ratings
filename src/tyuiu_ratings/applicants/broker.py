from faststream import Logger
from faststream.rabbit import RabbitRouter

from dishka.integrations.base import FromDishka as Depends

from .dto import ApplicantUpdateEvent
from .use_cases import UpdateApplicantsUseCase


applicants_router = RabbitRouter()


@applicants_router.subscriber("applicants")
async def update_applicants(
        applicants: list[ApplicantUpdateEvent],
        update_applicants_use_case: Depends[UpdateApplicantsUseCase],
        logger: Logger
) -> None:
    logger.info("Start update applicants")
    logger.info(f"{applicants[0]}")
    await update_applicants_use_case(applicants)
    logger.info("Finished updating applicants")
