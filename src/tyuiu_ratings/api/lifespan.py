from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import logging

from fastapi import FastAPI

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis

from ..settings import RedisSettings
from ..infrastructure.tasks import create_scheduler_app
from ..infrastructure.broker.app import create_faststream_app


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Инициализация Redis cache:
    redis = aioredis.from_url(RedisSettings().redis_url)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    logger.info("Redis cache initialized")
    # Запуск Faststream приложения:
    faststream_app = await create_faststream_app()
    await faststream_app.broker.start()
    logger.info("Broker started")
    # Запуск задач по расписанию:
    scheduler = create_scheduler_app()
    scheduler.start()
    logger.info("Scheduler started")
    yield
    await faststream_app.broker.close()
    logger.info("Broker closed")
    scheduler.shutdown()
