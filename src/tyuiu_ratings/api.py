from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dishka.integrations.fastapi import setup_dishka

from .ioc import container
from .broker import create_faststream_app

from .profile.router import profiles_router
from .applicant.router import applicants_router


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    faststream_app = await create_faststream_app()
    await faststream_app.broker.start()
    logger.info("Broker started")
    yield
    await faststream_app.broker.close()
    logger.info("Broker closed")


def create_fastapi_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(profiles_router)
    app.include_router(applicants_router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    setup_dishka(container=container, app=app)
    return app
