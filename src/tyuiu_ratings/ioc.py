from collections.abc import AsyncIterable

from dishka import Provider, provide, Scope, from_context, make_async_container

from faststream.rabbit import RabbitBroker

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .settings import Settings
from .core.interfaces import ApplicantRepository, ProfileRepository, RatingPositionRepository
from .infrastructure.database.session import create_session_maker
from .infrastructure.database.repositories import (
    SQLApplicantRepository,
    SQLProfileRepository,
    SQLRatingPositionRepository
)
from .core.services import NotificationMaker


class AppProvider(Provider):
    config = from_context(provides=Settings, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_amqp_broker(self, config: Settings) -> RabbitBroker:
        return RabbitBroker(config.rabbit.rabbit_url)

    @provide(scope=Scope.APP)
    def get_session_maker(self, config: Settings) -> async_sessionmaker[AsyncSession]:
        return create_session_maker(config.postgres)

    @provide(scope=Scope.REQUEST)
    async def get_session(
            self,
            session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def get_applicant_repository(self, session: AsyncSession) -> ApplicantRepository:
        return SQLApplicantRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_profile_repository(self, session: AsyncSession) -> ProfileRepository:
        return SQLProfileRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_rating_position_repository(self, session: AsyncSession) -> RatingPositionRepository:
        return SQLRatingPositionRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_notification_maker(self, profile_repository: ...) -> ...:
        ...


settings = Settings()

container = make_async_container(AppProvider(), context={Settings: settings})
