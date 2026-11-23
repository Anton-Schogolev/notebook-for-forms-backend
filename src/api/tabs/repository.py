from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.api.tabs.dto import TabIn
from src.api.tabs.exceptions import TabIdTaken, TabNotFound
from src.api.tabs.model import Tab
from src.dependencies.database import SessionDep


class TabRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session

    async def create(self, tab: TabIn, user_id: int) -> Tab:
        try:
            new_tab = Tab(id=tab.id, title=tab.title, version=1, user_id=user_id)
            self.session.add(new_tab)
            await self.session.commit()
            return new_tab
        except IntegrityError as exc:
            await self.session.rollback()
            original = exc.orig
            if (
                isinstance(original, UniqueViolation)
                and original.diag.constraint_name == "tab_pkey"
            ):
                raise TabIdTaken() from exc
            raise

    async def get_all(self, user_id: int) -> Sequence[Tab]:
        result = await self.session.exec(select(Tab).where(Tab.user_id == user_id))
        return result.all()

    async def get_one(self, user_id: int, tab_id: UUID) -> Tab | None:
        result = await self.session.exec(
            select(Tab).where(Tab.user_id == user_id, Tab.id == tab_id)
        )
        return result.one_or_none()

    async def update(self, user_id: int, tab_id: UUID, title: str) -> Tab:
        tab = await self.get_one(user_id, tab_id)
        if not tab:
            raise TabNotFound()
        if tab.title == title:
            return tab
        tab.title = title
        tab.version = tab.version + 1
        self.session.add(tab)
        await self.session.commit()
        return tab

    async def delete(self, tab_id: UUID, user_id: int) -> None:
        tab = await self.get_one(user_id, tab_id)
        if not tab:
            raise TabNotFound()
        await self.session.delete(tab)
        await self.session.commit()


TabRepositoryDep = Annotated[TabRepository, Depends(TabRepository)]
