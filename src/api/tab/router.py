from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.tab.dto import TabContentUpdate, TabDetailOut
from src.dependencies.auth import CurrentUserDep

router = APIRouter(
    prefix="/tabs",
    tags=["tabs"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid bearer token"
        },
    },
)


@router.get("/{tab_id}", status_code=status.HTTP_200_OK)
async def get_tab(tab_id: UUID, current_user: CurrentUserDep) -> TabDetailOut:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@router.put("/{tab_id}/content", status_code=status.HTTP_200_OK)
async def update_tab_content(
    tab_id: UUID, data: TabContentUpdate, current_user: CurrentUserDep
) -> TabDetailOut:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
