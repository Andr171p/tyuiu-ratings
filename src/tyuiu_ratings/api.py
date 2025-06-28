from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dishka.integrations.fastapi import setup_dishka

from .ioc import container
from .broker import create_faststream_app

from .profiles.router import profiles_router
from .applicants.router import applicants_router
from .notifications.tasks import create_scheduler_app

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    faststream_app = await create_faststream_app()
    scheduler_app = create_scheduler_app()
    await faststream_app.broker.start()
    logger.info("Broker started")
    scheduler_app.start()
    logger.info("Scheduler started")
    yield
    await faststream_app.broker.close()
    logger.info("Broker closed")
    scheduler_app.shutdown()
    logger.info("Scheduler stoped")


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
