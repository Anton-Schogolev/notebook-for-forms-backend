from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from src.api.tabs.dto import TabIn, TabOut, TabUpdate
from src.api.tabs.exceptions import TabIdTaken
from src.api.tabs.service import TabServiceDep

router = APIRouter(prefix="/tabs", tags=["tabs"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_tab(tab: TabIn, tabs_service: TabServiceDep) -> TabOut:
    try:
        return await tabs_service.add_tab(tab)
    except TabIdTaken as exc:
        raise HTTPException(status.HTTP_409_CONFLICT) from exc


@router.get("")
async def get_tabs(tabs_service: TabServiceDep) -> list[TabOut]:
    return []


@router.put("/{tab_id}/metadata")
async def update_tab(tab_id: UUID, data: TabUpdate) -> TabOut:
    return TabOut(title="", id=uuid4(), version=0)
