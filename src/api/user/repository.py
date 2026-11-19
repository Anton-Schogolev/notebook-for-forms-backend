from typing import Annotated

from fastapi import Depends

from src.dependencies.database import SessionDep


class UserRepository:
    """User persistence boundary. TODO: add queries once the model is defined."""

    def __init__(self, session: SessionDep) -> None:
        self.session = session


UserRepositoryDep = Annotated[UserRepository, Depends(UserRepository)]
