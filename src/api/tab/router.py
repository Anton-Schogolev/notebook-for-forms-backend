from uuid import UUID

from fastapi import APIRouter, status

from src.api.tab.dto import TabContentUpdate, TabDetailOut
from src.api.tab.service import TabContentServiceDep
from src.dependencies.auth import CurrentUserDep

router = APIRouter(
    prefix="/tabs",
    tags=["tabs"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid bearer token"
        },
        status.HTTP_404_NOT_FOUND: {"description": "Tab not found"},
    },
)


@router.get("/{tab_id}", status_code=status.HTTP_200_OK)
async def get_tab(
    tab_id: UUID, tab_service: TabContentServiceDep, current_user: CurrentUserDep
) -> TabDetailOut:
    return await tab_service.get_tab_content(tab_id=tab_id, user_id=current_user.id)


@router.put("/{tab_id}/content", status_code=status.HTTP_200_OK)
async def update_tab_content(
    tab_id: UUID,
    data: TabContentUpdate,
    tab_service: TabContentServiceDep,
    current_user: CurrentUserDep,
) -> TabDetailOut:
    return await tab_service.update_tab_content(
        tab_id=tab_id, user_id=current_user.id, data=data
    )
