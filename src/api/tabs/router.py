from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.tabs.dto import TabIn, TabOut, TabUpdate
from src.api.tabs.exceptions import TabIdTaken, TabNotFound
from src.api.tabs.service import TabServiceDep
from src.dependencies.auth import CurrentUserDep

router = APIRouter(prefix="/tabs", tags=["tabs"])


@router.post("", status_code=status.HTTP_201_CREATED)
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


@router.put("/{tab_id}/metadata")
async def update_tab(
    tab_id: UUID,
    data: TabUpdate,
    current_user: CurrentUserDep,
    tabs_service: TabServiceDep,
) -> TabOut:
    try:
        return await tabs_service.update_tab(
            data, tab_id=tab_id, user_id=current_user.id
        )
    except TabNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tab not found") from exc
