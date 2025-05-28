from dishka import Provider, provide, Scope, from_context, make_async_container

from .settings import Settings


class AppProvider(Provider):
    ...


settings = Settings()

container = make_async_container(AppProvider(), context={Settings: settings})
