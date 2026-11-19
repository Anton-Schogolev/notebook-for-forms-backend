from typing import Annotated

from fastapi import Depends

from src.api.user.repository import UserRepositoryDep


class AuthService:
    """Authentication logic. TODO: define credential and token operations."""

    def __init__(self, repository: UserRepositoryDep) -> None:
        self.repository = repository


AuthServiceDep = Annotated[AuthService, Depends(AuthService)]
