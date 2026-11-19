from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .dependencies.config import Settings

settings = Settings()

app = FastAPI()


@app.get("/")
async def root() -> Any:
    return settings


app.add_middleware(
    CORSMiddleware,
    # allow_private_network=True,
    allow_credentials=False,
    expose_headers=[],
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["GET", "PUT", "POST", "DELETE"],
)
