from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..applicant.dto import CreatedApplicant
    from ..rating.schemas import Rating

from abc import ABC, abstractmethod

from uuid import UUID

from .schemas import Profile
from .dto import CreatedProfile


class ProfileRepository(ABC):
    @abstractmethod
    async def create(self, profile: Profile) -> CreatedProfile: pass

    @abstractmethod
    async def read(self, user_id: UUID) -> Optional[CreatedProfile]: pass

    @abstractmethod
    async def update(self, user_id: UUID, **kwargs) -> Optional[CreatedProfile]: pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool: pass

    @abstractmethod
    async def get_by_applicant_id(self, applicant_id: int) -> Optional[CreatedProfile]: pass

    @abstractmethod
    async def get_applicants(self, user_id: UUID) -> list["CreatedApplicant"]: pass

    @abstractmethod
    async def get_ratings(self, user_id: UUID, direction: str) -> list["Rating"]: pass
