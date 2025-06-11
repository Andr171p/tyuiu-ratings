from collections.abc import AsyncIterable

from dishka import Provider, provide, Scope, from_context, make_async_container

from faststream.rabbit import RabbitBroker

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .settings import Settings

from .core.factories import NotificationFactory
from .core.base import (
    ApplicantRepository,
    ProfileRepository,
    RatingRepository,
    ClassifierService,
    RecommendationService
)
from .core.use_cases.applicant import RerankPrioritiesUseCase, RecommendDirectionsUseCase
from .core.use_cases.competition_list import GetCompetitionListUseCase, UpdateCompetitionListUseCase
from .core.use_cases.notification import BroadcastNotificationsUseCase
from .core.use_cases.rating_history import GetRatingHistoryUseCase

from .infrastructure.rest import ClassifierAPI, RecommendationAPI
from .infrastructure.database.session import create_session_maker
from .infrastructure.database.repositories import (
    SQLApplicantRepository,
    SQLProfileRepository,
    SQLRatingRepository
)


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
    def get_rating_repository(self, session: AsyncSession) -> RatingRepository:
        return SQLRatingRepository(session)

    @provide(scope=Scope.APP)
    def get_classifier_service(self, config: Settings) -> ClassifierService:
        return ClassifierAPI(config.api.CLASSIFIER_URL)

    @provide(scope=Scope.APP)
    def get_recommendation_service(self, config: Settings) -> RecommendationService:
        return RecommendationAPI(config.api.REC_SYS)

    @provide(scope=Scope.REQUEST)
    def get_notification_maker(self, profile_repository: ProfileRepository) -> NotificationFactory:
        return NotificationFactory(profile_repository)

    @provide(scope=Scope.REQUEST)
    def get_rerank_priorities_use_case(
            self,
            applicant_repository: ApplicantRepository,
            profile_repository: ProfileRepository
    ) -> RerankPrioritiesUseCase:
        return RerankPrioritiesUseCase(
            applicant_repository=applicant_repository,
            profile_repository=profile_repository
        )

    @provide(scope=Scope.REQUEST)
    def get_recommend_directions_use_case(
            self,
            applicant_repository: ApplicantRepository,
            profile_repository: ProfileRepository,
            classifier_service: ClassifierService,
            recommendation_service: RecommendationService
    ) -> RecommendDirectionsUseCase:
        return RecommendDirectionsUseCase(
            applicant_repository=applicant_repository,
            profile_repository=profile_repository,
            classifier_service=classifier_service,
            recommendation_service=recommendation_service
        )

    @provide(scope=Scope.REQUEST)
    def get_competition_list_use_case(
            self,
            profile_repository: ProfileRepository,
            applicant_repository: ApplicantRepository
    ) -> GetCompetitionListUseCase:
        return GetCompetitionListUseCase(
            profile_repository=profile_repository,
            applicant_repository=applicant_repository
        )

    @provide(scope=Scope.REQUEST)
    def get_update_competition_list_use_case(
            self,
            classifier_service: ClassifierService,
            applicant_repository: ApplicantRepository,
            rating_repository: RatingRepository
    ) -> UpdateCompetitionListUseCase:
        return UpdateCompetitionListUseCase(
            classifier_service=classifier_service,
            applicant_repository=applicant_repository,
            rating_repository=rating_repository
        )

    @provide(scope=Scope.REQUEST)
    def get_broadcast_notification_use_case(
            self,
            applicant_repository: ApplicantRepository,
            rating_repository: RatingRepository,
            notification_factory: NotificationFactory,
            broker: RabbitBroker
    ) -> BroadcastNotificationsUseCase:
        return BroadcastNotificationsUseCase(
            applicant_repository=applicant_repository,
            rating_repository=rating_repository,
            notification_factory=notification_factory,
            broker=broker
        )

    @provide(scope=Scope.REQUEST)
    def get_rating_history_use_case(
            self,
            profile_repository: ProfileRepository,
            applicant_repository: ApplicantRepository,
            rating_repository: RatingRepository
    ) -> GetRatingHistoryUseCase:
        return GetRatingHistoryUseCase(
            profile_repository=profile_repository,
            applicant_repository=applicant_repository,
            rating_repository=rating_repository
        )


settings = Settings()

container = make_async_container(AppProvider(), context={Settings: settings})
