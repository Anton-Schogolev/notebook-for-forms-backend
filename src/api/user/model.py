from enum import StrEnum

from sqlmodel import Field, SQLModel


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


class UserBase(SQLModel):
    is_encryption_enabled: bool


class User(UserBase, table=True):
    id: int = Field(primary_key=True)
    username: str = Field(unique=True)
    hashed_password: str
    role: UserRole = UserRole.USER
