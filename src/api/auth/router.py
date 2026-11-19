from typing import Any

from fastapi import APIRouter

router = APIRouter(tags=["auth"], prefix="/auth")


@router.get("/me")
def get_profile() -> Any:
    return {}
