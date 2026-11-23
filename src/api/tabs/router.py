from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.tabs.dto import TabIn, TabOut, TabUpdate
from src.api.tabs.exceptions import TabIdTaken
from src.api.tabs.service import TabServiceDep
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


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "Tab ID already exists"}},
)
async def create_tab(
    tab: TabIn, tabs_service: TabServiceDep, current_user: CurrentUserDep
) -> TabOut:
    try:
        return await tabs_service.add_tab(tab, user_id=current_user.id)
    except TabIdTaken as exc:
        raise HTTPException(status.HTTP_409_CONFLICT) from exc


@router.get("")
async def get_tabs(
    tabs_service: TabServiceDep, current_user: CurrentUserDep
) -> list[TabOut]:
    return await tabs_service.get_tabs(user_id=current_user.id)


@router.put(
    "/{tab_id}/metadata",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Tab not found"}},
)
async def update_tab(
    tab_id: UUID,
    data: TabUpdate,
    current_user: CurrentUserDep,
    tabs_service: TabServiceDep,
) -> TabOut:
    return await tabs_service.update_tab(data, tab_id=tab_id, user_id=current_user.id)


@router.delete("/{tab_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tab(
    tab_id: UUID, current_user: CurrentUserDep, tabs_service: TabServiceDep
) -> None:
    await tabs_service.delete_tab(tab_id=tab_id, user_id=current_user.id)
