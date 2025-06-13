from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dishka.integrations.fastapi import setup_dishka

from .ioc import container

from .profile.router import profiles_router


def create_fastapi_app() -> FastAPI:
    app = FastAPI()
    app.include_router(profiles_router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    setup_dishka(container=container, app=app)
    return app
