from faststream import FastStream
from faststream.rabbit import RabbitBroker

from dishka.integrations.faststream import setup_dishka

from .ioc import container

from .applicants.broker import applicants_router


async def create_faststream_app() -> FastStream:
    broker = await container.get(RabbitBroker)
    broker.include_router(applicants_router)
    app = FastStream(broker)
    setup_dishka(container=container, app=app, auto_inject=True)
    return app
