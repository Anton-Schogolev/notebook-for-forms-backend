from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from src.api.user.model import UserRole


class TokenUser(BaseModel):
    username: str
    role: UserRole
    id: int


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenUser:
    return TokenUser(username="test", id=-1, role=UserRole.USER)


CurrentUserDep = Annotated[TokenUser, Depends(get_current_user)]
