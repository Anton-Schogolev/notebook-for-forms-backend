from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlmodel import select

from src.api.tab.dto import TabContentUpdate, TabDetailOut
from src.api.tab.model import InfoField, TabContent
from src.api.tabs.exceptions import TabNotFound
from src.api.tabs.model import Tab
from src.api.tabs.repository import TabRepositoryDep
from src.dependencies.database import SessionDep


class TabContentRepository:
    def __init__(self, session: SessionDep, tab_repository: TabRepositoryDep) -> None:
        self.session = session
        self.tab_repository = tab_repository

    async def get(self, tab_id: UUID, user_id: int) -> TabDetailOut:
        query_result = await self.session.exec(
            select(Tab, TabContent)
            .outerjoin(TabContent)
            .where(Tab.id == tab_id, Tab.user_id == user_id)
        )
        result = query_result.one_or_none()
        if not result:
            raise TabNotFound()
        tab, tab_content = result
        content = []
        if tab_content and len(tab_content.items):
            content = [InfoField.model_validate(field) for field in tab_content.items]
        return TabDetailOut(**tab.model_dump(), content=content)

    async def update(
        self, tab_id: UUID, data: TabContentUpdate, user_id: int
    ) -> TabDetailOut:
        query_result = await self.session.exec(
            select(Tab, TabContent)
            .outerjoin(TabContent)
            .where(Tab.id == tab_id, Tab.user_id == user_id)
        )
        result = query_result.one_or_none()
        if not result:
            raise TabNotFound()
        tab, tab_content = result
        if not tab_content:
            tab_content = TabContent(tab_id=tab_id, items=[])
        tab.version = tab.version + 1
        print(data)
        tab_content.items = jsonable_encoder(data.content)
        print(tab_content)
        self.session.add(tab)
        self.session.add(tab_content)
        await self.session.commit()
        return TabDetailOut(**tab.model_dump(), content=data.content)


TabContentRepositoryDep = Annotated[TabContentRepository, Depends(TabContentRepository)]
