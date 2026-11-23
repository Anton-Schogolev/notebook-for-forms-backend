from typing import Annotated

from fastapi import Depends

from src.api.tabs.dto import TabIn, TabOut

from .repository import TabRepositoryDep


class TabsService:
    def __init__(self, repository: TabRepositoryDep) -> None:
        self.tab_repository = repository

    async def add_tab(self, tab: TabIn) -> TabOut:
        result = await self.tab_repository.create(tab)
        return TabOut(title=result.title, id=result.id, version=result.version)


TabServiceDep = Annotated[TabsService, Depends(TabsService)]
