from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dishka.integrations.fastapi import setup_dishka

from .lifespan import lifespan
from .v1.routers import (
    profiles_router,
    applicants_router,
    rating_history_router,
    competition_lists_router
)

from ..ioc import container


def create_fastapi_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(profiles_router)
    app.include_router(applicants_router)
    app.include_router(rating_history_router)
    app.include_router(competition_lists_router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    setup_dishka(container=container, app=app)
    return app
