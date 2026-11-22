from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel, ValidationError

from src.api.auth.exceptions import JWTException
from src.api.user.model import UserRole
from src.dependencies.config import SettingsDep


class TokenUser(BaseModel):
    role: UserRole
    id: int


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
ALGORITHM = "HS256"

type TokenGenerator = Callable[[TokenUser], str]


def get_token_generator(settings: SettingsDep) -> TokenGenerator:
    def generate_token(userData: TokenUser) -> str:
        to_encode = userData.model_dump()
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret, algorithm=ALGORITHM)
        return encoded_jwt

    return generate_token


TokenGeneratorDep = Annotated[TokenGenerator, Depends(get_token_generator)]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], settings: SettingsDep
) -> TokenUser:
    try:
        payload = jwt.decode(token, settings.secret, algorithms=[ALGORITHM])
        return TokenUser.model_validate(payload)
    except (InvalidTokenError, ValidationError) as exc:
        raise JWTException() from exc


CurrentUserDep = Annotated[TokenUser, Depends(get_current_user)]
