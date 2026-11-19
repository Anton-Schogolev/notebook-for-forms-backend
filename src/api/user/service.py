from typing import Annotated

from fastapi import Depends

from .repository import UserRepositoryDep


class UserService:
    """User application logic. TODO: add operations as requirements are defined."""

    def __init__(self, repository: UserRepositoryDep) -> None:
        self.repository = repository


UserServiceDep = Annotated[UserService, Depends(UserService)]
