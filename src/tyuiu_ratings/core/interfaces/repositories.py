from uuid import UUID
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import Profile, Applicant
from ..dto import ProfileReadDTO, ApplicantReadDTO


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
    @abstractmethod
    async def create(self, applicant: Applicant) -> None: pass

    @abstractmethod
    async def bulk_create(self, applicants: List[Applicant]) -> None: pass

    @abstractmethod
    async def read(self, applicant_id: int) -> Optional[ApplicantReadDTO]: pass

    @abstractmethod
    async def update(self, applicant: Applicant) -> None: pass

    @abstractmethod
    async def delete(self, applicant_id: int) -> int: pass

    @abstractmethod
    async def bulk_update(self, applicants: List[Applicant]) -> None: pass

    @abstractmethod
    async def get_by_direction(self, direction: str) -> List[Applicant]: pass

    @abstractmethod
    async def paginate_by_direction(self, direction: str, page: int, limit: int) -> List[Applicant]: pass


class HistoryRepository(ABC):
    ...
