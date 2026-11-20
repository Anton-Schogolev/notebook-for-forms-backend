from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine

from src.api.auth.router import router as auth_router
from src.api.user.router import router as user_router

from .dependencies.config import Settings, get_settings


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

    app = FastAPI(lifespan=lifespan)
    app.include_router(router=auth_router)
    app.include_router(router=user_router)

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
