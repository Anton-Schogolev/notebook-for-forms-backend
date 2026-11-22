from typing import Annotated

from fastapi import Depends
from fastapi.concurrency import run_in_threadpool
from pwdlib import PasswordHash

from src.api.auth.dto import RegisterIn, TokenOut
from src.api.auth.exceptions import InvalidCredentials, JWTException
from src.api.user.model import User
from src.api.user.repository import UserRepositoryDep
from src.dependencies.auth import TokenGeneratorDep, TokenUser

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")


class AuthService:
    def __init__(
        self, repository: UserRepositoryDep, create_token: TokenGeneratorDep
    ) -> None:
        self.user_repository = repository
        self.create_token = create_token

    async def register(self, user: RegisterIn) -> None:
        hashed_password = await self.get_password_hash(user.password)
        await self.user_repository.create(
            user=User(
                username=user.username,
                hashed_password=hashed_password,
                is_encryption_enabled=user.is_encryption_enabled,
            )
        )

    async def login(self, username: str, password: str) -> TokenOut:
        user = await self.user_repository.get_by_username(username=username)
        if not user:
            await self.verify_password(password, DUMMY_HASH)
            raise InvalidCredentials()
        is_correct_password = await self.verify_password(password, user.hashed_password)
        if not is_correct_password:
            raise InvalidCredentials()
        token = self.create_token(TokenUser(id=user.id, role=user.role.value))
        return TokenOut(access_token=token, token_type="bearer")

    async def get_profile(self, id: int) -> User:
        user = await self.user_repository.get_by_id(id=id)
        if not user:
            raise JWTException()
        return user

    async def get_password_hash(self, password: str) -> str:
        return await run_in_threadpool(password_hash.hash, password)

    async def verify_password(self, plain: str, hash: str) -> bool:
        return await run_in_threadpool(password_hash.verify, password=plain, hash=hash)


AuthServiceDep = Annotated[AuthService, Depends(AuthService)]
