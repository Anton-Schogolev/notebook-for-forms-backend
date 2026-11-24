from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.api.tab.dto import TabContentUpdate, TabDetailOut

from .repository import TabContentRepositoryDep


class TabContentService:
    def __init__(self, repository: TabContentRepositoryDep) -> None:
        self.tab_detail_repository = repository

    async def get_tab_content(self, tab_id: UUID, user_id: int) -> TabDetailOut:
        return await self.tab_detail_repository.get(tab_id=tab_id, user_id=user_id)

    async def update_tab_content(
        self, tab_id: UUID, user_id: int, data: TabContentUpdate
    ) -> TabDetailOut:
        return await self.tab_detail_repository.update(
            tab_id=tab_id, user_id=user_id, data=data
        )


TabContentServiceDep = Annotated[TabContentService, Depends(TabContentService)]
