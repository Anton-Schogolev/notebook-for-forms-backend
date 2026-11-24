from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine

from src.api.auth.router import router as auth_router
from src.api.exception_handlers import EXCEPTION_HANDLERS
from src.api.tab.router import router as tab_router
from src.api.tabs.router import router as tabs_router
from src.api.user.router import router as user_router

from .dependencies.config import Settings, get_settings


class NotebookAPI(FastAPI):
    def openapi(self) -> dict[str, Any]:
        schema = super().openapi()
        # The token route maps FastAPI form validation errors to OAuth 400 responses.
        schema["paths"]["/auth/token"]["post"]["responses"].pop("422", None)
        return schema


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = get_settings() if settings is None else settings

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        engine = create_async_engine(app_settings.database_url, pool_pre_ping=True)
        app.state.engine = engine
        try:
            yield
        finally:
            await engine.dispose()

    app = NotebookAPI(lifespan=lifespan, exception_handlers=EXCEPTION_HANDLERS)
    app.include_router(router=auth_router)
    app.include_router(router=user_router)
    app.include_router(router=tabs_router)
    app.include_router(router=tab_router)

    # @app.get("/", response_model=None)
    # async def root() -> Settings:
    #     return app_settings

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=False,
        expose_headers=[],
        allow_origins=app_settings.origins,
        allow_headers=["*"],
        allow_methods=["GET", "PUT", "POST", "DELETE"],
    )
    return app
