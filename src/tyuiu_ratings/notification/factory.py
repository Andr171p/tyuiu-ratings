from typing import Optional

from ..profile.base import ProfileRepository
from ..applicant.dto import CreatedApplicant
from ..rating.schemas import Rating

from .schemas import Notification
from .rules import (
    PositiveConditionalHandler,
    WarningConditionalHandler,
    CriticalConditionalHandler
)


class NotificationFactory:
    def __init__(self, profile_repository: ProfileRepository) -> None:
        self._profile_repository = profile_repository

    async def create_notification(
            self,
            applicant: CreatedApplicant,
            ratings: list[Rating]
    ) -> Optional[Notification]:
        profile = await self._profile_repository.get_by_applicant_id(applicant.applicant_id)
        if not profile:
            return None
        condition_chain = PositiveConditionalHandler(
            WarningConditionalHandler(
                CriticalConditionalHandler(None)
            )
        )
        condition_result = condition_chain.check(applicant, ratings)
        return Notification(
            level=condition_result.level,
            user_id=profile.user_id,
            text=condition_result.message
        )
