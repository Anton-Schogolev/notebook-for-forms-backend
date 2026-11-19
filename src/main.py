from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth.router import router as auth_router

from .dependencies.config import get_settings
from .dependencies.database import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(router=auth_router)


@app.get("/")
async def root() -> Any:
    return settings


app.add_middleware(
    CORSMiddleware,
    # allow_private_network=True,
    allow_credentials=False,
    expose_headers=[],
    allow_origins=settings.origins,
    allow_headers=["*"],
    allow_methods=["GET", "PUT", "POST", "DELETE"],
)
