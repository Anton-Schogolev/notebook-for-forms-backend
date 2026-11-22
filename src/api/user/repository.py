from typing import Annotated

from fastapi import Depends
from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.api.user.exceptions import UsernameAlreadyTaken
from src.api.user.model import User
from src.dependencies.database import SessionDep


class UserRepository:
    """User persistence boundary. TODO: add queries once the model is defined."""

    def __init__(self, session: SessionDep) -> None:
        self.session = session

    async def get_by_id(self, id: int) -> User | None:
        return await self.session.get(User, id)

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.exec(select(User).where(User.username == username))
        return result.one_or_none()

    async def create(self, user: User) -> None:
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            original = exc.orig
            if (
                isinstance(original, UniqueViolation)
                and original.diag.constraint_name == "user_username_key"
            ):
                raise UsernameAlreadyTaken() from exc
            raise


UserRepositoryDep = Annotated[UserRepository, Depends(UserRepository)]
