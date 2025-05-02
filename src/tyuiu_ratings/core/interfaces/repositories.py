from uuid import UUID
from abc import ABC, abstractmethod
from typing import Any, Optional, List

from ..entities import Profile
from ..dto import ProfileReadDTO


class ProfileRepository(ABC):
    @abstractmethod
    async def create(self, profile: Profile) -> ProfileReadDTO: pass

    @abstractmethod
    async def read(self, user_id: UUID) -> Optional[ProfileReadDTO]: pass

    @abstractmethod
    async def update(self, profile: Profile) -> Optional[ProfileReadDTO]: pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> Optional[ProfileReadDTO]: pass

    @abstractmethod
    async def list(self) -> List[ProfileReadDTO]: pass

    @abstractmethod
    async def get_by_applicant_id(self, applicant_id: int) -> Optional[ProfileReadDTO]: pass


class ApplicantRepository(ABC):
    ...


class HistoryRepository(ABC):
    ...
