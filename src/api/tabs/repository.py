from typing import Annotated

from fastapi import Depends
from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from src.api.tabs.dto import TabIn
from src.api.tabs.exceptions import TabIdTaken
from src.api.tabs.model import Tab
from src.dependencies.database import SessionDep


class TabRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session

    async def create(self, tab: TabIn) -> Tab:
        try:
            new_tab = Tab(id=tab.id, title=tab.title, version=1)
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


TabRepositoryDep = Annotated[TabRepository, Depends(TabRepository)]
