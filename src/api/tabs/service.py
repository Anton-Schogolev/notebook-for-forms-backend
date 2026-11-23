from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.api.tabs.dto import TabIn, TabOut, TabUpdate

from .repository import TabRepositoryDep


class TabsService:
    def __init__(self, repository: TabRepositoryDep) -> None:
        self.tab_repository = repository

    async def add_tab(self, tab: TabIn, user_id: int) -> TabOut:
        result = await self.tab_repository.create(tab, user_id=user_id)
        return TabOut(title=result.title, id=result.id, version=result.version)

    async def get_tabs(self, user_id: int) -> list[TabOut]:
        result = await self.tab_repository.get_all(user_id=user_id)
        return [
            TabOut(id=tab.id, version=tab.version, title=tab.title) for tab in result
        ]

    async def update_tab(self, data: TabUpdate, tab_id: UUID, user_id: int) -> TabOut:
        updated_tab = await self.tab_repository.update(
            tab_id=tab_id, user_id=user_id, title=data.title
        )
        return TabOut(**updated_tab.model_dump())

    async def delete_tab(self, tab_id: UUID, user_id: int) -> None:
        await self.tab_repository.delete(tab_id=tab_id, user_id=user_id)


TabServiceDep = Annotated[TabsService, Depends(TabsService)]
