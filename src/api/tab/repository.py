from typing import Annotated

from fastapi import Depends

from src.dependencies.database import SessionDep


class TabContentRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session


TabContentRepositoryDep = Annotated[TabContentRepository, Depends(TabContentRepository)]
