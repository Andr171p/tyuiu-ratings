from faststream import FastStream
from faststream.rabbit import RabbitBroker

from dishka.integrations.faststream import setup_dishka

from .routers import applicants_router
from src.tyuiu_ratings.ioc import container


async def create_faststream_app() -> FastStream:
    broker = await container.get(RabbitBroker)
    broker.include_routers(applicants_router)
    app = FastStream(broker)
    setup_dishka(container=container, app=app, auto_inject=True)
    return app
