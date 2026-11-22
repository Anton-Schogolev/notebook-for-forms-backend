from typing import Literal

from pydantic import BaseModel, Field

from src.api.user.model import UserBase

password_validation = Field(min_length=4, max_length=16)


class RegisterIn(UserBase):
    username: str = Field(min_length=4, max_length=12, pattern=r"^[a-z0-9_]+$")
    password: str = password_validation


class TokenErrorOut(BaseModel):
    error: Literal["invalid_request", "unsupported_grant_type", "invalid_grant"]
    error_description: str | None = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str


class CurrentUserOut(UserBase):
    username: str
