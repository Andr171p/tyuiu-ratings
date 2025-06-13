from collections.abc import AsyncIterable

from dishka import Provider, provide, Scope, from_context, make_async_container

from faststream.rabbit import RabbitBroker

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .database import create_session_factory

from .applicant.base import ApplicantRepository, ClassifierService, RecommendationService
from .applicant.use_cases import UpdateApplicantsUseCase, RecommendDirectionsUseCase
from .applicant.rest import ClassifierAPI, RecommendationAPI
from .profile.base import ProfileRepository
from .rating.base import RatingRepository
from .applicant.repository import SQLApplicantRepository
from .profile.repository import SQLProfileRepository
from .rating.repository import SQLRatingRepository

from .settings import Settings


class AppProvider(Provider):
    config = from_context(provides=Settings, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_rabbit_broker(self, config: Settings) -> RabbitBroker:
        return RabbitBroker(config.rabbit.rabbit_url)

    @provide(scope=Scope.APP)
    def get_session_factory(self, config: Settings) -> async_sessionmaker[AsyncSession]:
        return create_session_factory(config.postgres)

    @provide(scope=Scope.REQUEST)
    async def get_session(self, session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
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
        return RecommendationAPI(config.api.REC_SYS_URL)

    @provide(scope=Scope.REQUEST)
    def get_update_applicants_use_case(
            self,
            classifier_service: ClassifierService,
            applicant_repository: ApplicantRepository,
            rating_repository: RatingRepository
    ) -> UpdateApplicantsUseCase:
        return UpdateApplicantsUseCase(
            classifier_service=classifier_service,
            applicant_repository=applicant_repository,
            rating_repository=rating_repository
        )

    @provide(scope=Scope.REQUEST)
    def get_recommend_directions_use_case(
            self,
            classifier_service: ClassifierService,
            recommendation_service: RecommendationService,
            applicant_repository: ApplicantRepository
    ) -> RecommendDirectionsUseCase:
        return RecommendDirectionsUseCase(
            classifier_service=classifier_service,
            recommendation_service=recommendation_service,
            applicant_repository=applicant_repository
        )


settings = Settings()

container = make_async_container(AppProvider(), context={Settings: settings})
