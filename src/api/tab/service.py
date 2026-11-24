from typing import Annotated

from fastapi import Depends

from .repository import TabContentRepositoryDep


class TabContentService:
    def __init__(self, repository: TabContentRepositoryDep) -> None:
        self.repository = repository


TabContentServiceDep = Annotated[TabContentService, Depends(TabContentService)]
